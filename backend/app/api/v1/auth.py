"""Authentication API Router for WorkMate AI handling login, token refresh, and user profile endpoints."""

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from snowflake.connector import SnowflakeConnection

from app.core.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.services.authentication_service import (
    AuthenticationService,
    AuthenticationServiceError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    UserNotFoundError,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# --- OpenAPI Responses Metadata ---

COMMON_RESPONSES = {
    401: {"description": "Unauthorized — Missing, expired, or invalid credentials."},
    403: {"description": "Forbidden — Inactive or disabled user account."},
    500: {"description": "Internal Server Error — Unexpected authentication error."},
}

ME_RESPONSES = {
    **COMMON_RESPONSES,
    404: {"description": "Not Found — Authenticated user account not found."},
}


# --- Request & Response Schemas ---

class LoginRequest(BaseModel):
    """Request payload for user authentication."""

    email: EmailStr
    password: str


class TokenRefreshRequest(BaseModel):
    """Request payload for exchanging a refresh token."""

    refresh_token: str


class UserResponse(BaseModel):
    """Public user profile response schema."""

    id: str
    email: str
    role: str
    department_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None


class TokenResponse(BaseModel):
    """Authentication response payload containing access/refresh token pair and user profile."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


# --- Private Error Helper ---

def _raise_api_error(
    status_code: int,
    error_code: str,
    message: str,
    headers: Optional[dict[str, str]] = None,
) -> None:
    """Private helper to raise standardized HTTP exceptions."""
    raise HTTPException(
        status_code=status_code,
        detail={
            "error_code": error_code,
            "message": message,
            "details": {},
        },
        headers=headers,
    )


# --- Dependency Factory ---

def get_auth_service(
    conn: SnowflakeConnection = Depends(get_db),
) -> AuthenticationService:
    """FastAPI dependency creating a request-scoped AuthenticationService instance."""
    return AuthenticationService(conn)


# --- Endpoint Handlers ---

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user credentials",
    description="Validates employee or admin credentials and issues a JWT access and refresh token pair.",
    responses=COMMON_RESPONSES,
)
async def login(
    payload: LoginRequest,
    auth_service: AuthenticationService = Depends(get_auth_service),
) -> TokenResponse:
    """Authenticate user credentials and return JWT token pair."""
    try:
        token_data = auth_service.login(
            email=payload.email, password=payload.password
        )
        return TokenResponse(**token_data)
    except InvalidCredentialsError:
        _raise_api_error(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTH_INVALID",
            message="Invalid credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InactiveUserError:
        _raise_api_error(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTH_INACTIVE",
            message="User account is inactive.",
        )
    except AuthenticationServiceError:
        _raise_api_error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_ERROR",
            message="An internal authentication error occurred.",
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Exchange refresh token for new access token",
    description="Validates a refresh token and issues a new access/refresh token pair.",
    responses=COMMON_RESPONSES,
)
async def refresh_token(
    payload: TokenRefreshRequest,
    auth_service: AuthenticationService = Depends(get_auth_service),
) -> TokenResponse:
    """Exchange refresh token for a fresh token pair."""
    try:
        token_data = auth_service.refresh_token(
            refresh_token=payload.refresh_token
        )
        return TokenResponse(**token_data)
    except InvalidRefreshTokenError:
        _raise_api_error(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTH_INVALID",
            message="Invalid or expired refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InactiveUserError:
        _raise_api_error(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTH_INACTIVE",
            message="User account is inactive.",
        )
    except AuthenticationServiceError:
        _raise_api_error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_ERROR",
            message="An internal authentication error occurred.",
        )


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Returns the profile of the currently authenticated user based on Bearer token claims.",
    responses=ME_RESPONSES,
)
async def get_me(
    current_user: dict[str, Any] = Depends(get_current_user),
    auth_service: AuthenticationService = Depends(get_auth_service),
) -> UserResponse:
    """Retrieve identity profile of current authenticated user."""
    user_id = current_user.get("sub")
    if not user_id:
        _raise_api_error(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTH_INVALID",
            message="Invalid token subject.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_profile = auth_service.get_current_user_profile(user_id=user_id)
        return UserResponse(**user_profile)
    except UserNotFoundError:
        _raise_api_error(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="USER_NOT_FOUND",
            message="User not found.",
        )
    except InactiveUserError:
        _raise_api_error(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTH_INACTIVE",
            message="User account is inactive.",
        )
    except AuthenticationServiceError:
        _raise_api_error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_ERROR",
            message="An internal authentication error occurred.",
        )
