"""Domain Authentication Service for WorkMate AI."""

import logging
from typing import Any

from snowflake.connector import SnowflakeConnection

from app.core.database import DatabaseQueryError
from app.core.security import (
    TokenExpiredError,
    TokenInvalidError,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.repositories.user_repository import UserRepository

logger = logging.getLogger("workmate.authentication")

__all__ = [
    "AuthenticationServiceError",
    "InvalidCredentialsError",
    "InactiveUserError",
    "InvalidRefreshTokenError",
    "UserNotFoundError",
    "AuthenticationService",
]


class AuthenticationServiceError(Exception):
    """Base domain exception for authentication service errors."""

    pass


class InvalidCredentialsError(AuthenticationServiceError):
    """Raised when authentication credentials (email or password) are invalid."""

    pass


class InactiveUserError(AuthenticationServiceError):
    """Raised when a user account is inactive or disabled."""

    pass


class InvalidRefreshTokenError(AuthenticationServiceError):
    """Raised when a refresh token is expired, malformed, or invalid type."""

    pass


class UserNotFoundError(AuthenticationServiceError):
    """Raised when a requested user account cannot be found."""

    pass


class AuthenticationService:
    """Business service orchestrating authentication, token pair lifecycle, and user identity."""

    def __init__(self, conn: SnowflakeConnection) -> None:
        """Initialize AuthenticationService with a Snowflake connection and UserRepository instance."""
        self.conn = conn
        self.user_repo = UserRepository(conn)

    def _sanitize_user(self, user: dict[str, Any]) -> dict[str, Any]:
        """Private helper to sanitize raw user records, stripping sensitive fields like password_hash."""
        sanitized = dict(user)
        sanitized.pop("password_hash", None)
        return sanitized

    def _build_token_response(self, user: dict[str, Any]) -> dict[str, Any]:
        """Private helper to generate access/refresh token pair and return token response payload."""
        user_id = user["id"]
        role = user["role"]
        department_id = user.get("department_id")

        access_token = create_access_token(
            user_id=user_id,
            role=role,
            department_id=department_id,
        )
        refresh_token = create_refresh_token(
            user_id=user_id,
            role=role,
            department_id=department_id,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": self._sanitize_user(user),
        }

    def login(self, email: str, password: str) -> dict[str, Any]:
        """Authenticate user credentials, update last_login timestamp, and issue token pair."""
        if not email or not password:
            raise InvalidCredentialsError("Invalid credentials")

        normalized_email = email.strip().lower()

        try:
            user = self.user_repo.get_user_by_email(normalized_email)
        except DatabaseQueryError as exc:
            logger.error("Database query failure during user lookup.")
            raise AuthenticationServiceError("Authentication service error.") from exc

        if not user or not user.get("password_hash"):
            logger.warning("Authentication failed: User account not found.")
            raise InvalidCredentialsError("Invalid credentials")

        if not verify_password(password, user["password_hash"]):
            logger.warning(
                "Authentication failed: Incorrect password [User ID: %s]",
                user["id"],
            )
            raise InvalidCredentialsError("Invalid credentials")

        if not user.get("is_active", True):
            logger.warning(
                "Authentication failed: Account inactive [User ID: %s]",
                user["id"],
            )
            raise InactiveUserError("User account is inactive.")

        # Update last_login timestamp (Write operation: explicit transaction commit/rollback)
        try:
            self.user_repo.update_last_login(user["id"])
            self.conn.commit()
        except Exception as exc:
            logger.error(
                "Failed to commit last_login update [User ID: %s]", user["id"]
            )
            try:
                self.conn.rollback()
            except Exception:
                pass
            raise AuthenticationServiceError(
                "Failed to update user session."
            ) from exc

        logger.info("User authenticated successfully [User ID: %s]", user["id"])
        return self._build_token_response(user)

    def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        """Validate refresh token, resolve user identity, and issue a fresh token pair."""
        if not refresh_token:
            raise InvalidRefreshTokenError("Refresh token is required.")

        try:
            payload = decode_token(refresh_token)
        except (TokenExpiredError, TokenInvalidError) as exc:
            logger.warning("Refresh token validation failed: %s", str(exc))
            raise InvalidRefreshTokenError(
                "Invalid or expired refresh token."
            ) from exc

        if payload.get("type") != "refresh":
            logger.warning(
                "Token type mismatch: Expected 'refresh', got '%s'",
                payload.get("type"),
            )
            raise InvalidRefreshTokenError(
                "Invalid token type. Refresh token required."
            )

        user_id = payload.get("sub")
        if not user_id:
            raise InvalidRefreshTokenError("Invalid refresh token payload.")

        try:
            user = self.user_repo.get_user_by_id(user_id)
        except DatabaseQueryError as exc:
            logger.error("Database query failure during user refresh lookup.")
            raise AuthenticationServiceError("Authentication service error.") from exc

        if not user:
            logger.warning(
                "Refresh token rejected: User no longer exists [User ID: %s]",
                user_id,
            )
            raise InvalidRefreshTokenError("User account no longer exists.")

        if not user.get("is_active", True):
            logger.warning(
                "Refresh token rejected: Account inactive [User ID: %s]",
                user_id,
            )
            raise InactiveUserError("User account is inactive.")

        logger.info("Tokens refreshed successfully [User ID: %s]", user_id)
        return self._build_token_response(user)

    def get_current_user_profile(self, user_id: str) -> dict[str, Any]:
        """Retrieve sanitized user profile for an authenticated user ID."""
        if not user_id:
            raise AuthenticationServiceError("User ID is required.")

        try:
            user = self.user_repo.get_user_by_id(user_id)
        except DatabaseQueryError as exc:
            logger.error("Database query failure during user profile lookup.")
            raise AuthenticationServiceError("Authentication service error.") from exc

        if not user:
            logger.warning(
                "User profile lookup failed: Account not found [User ID: %s]",
                user_id,
            )
            raise UserNotFoundError("User not found.")

        if not user.get("is_active", True):
            logger.warning(
                "User profile lookup failed: Account inactive [User ID: %s]",
                user_id,
            )
            raise InactiveUserError("User account is inactive.")

        return self._sanitize_user(user)
