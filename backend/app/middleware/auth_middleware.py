"""FastAPI Authentication Dependency Injection Module."""

import logging
from typing import Any, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import TokenExpiredError, TokenInvalidError, decode_token

logger = logging.getLogger("workmate.auth")

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> dict[str, Any]:
    """Mandatory authentication dependency extracting and verifying a JWT access token.

    Attaches claims to request.state.user and returns the claims dict.
    Raises HTTP 401 Unauthorized on missing, expired, or invalid credentials.
    """
    if not credentials or not credentials.credentials:
        logger.warning(
            "Authentication failed: Missing Bearer token [Path: %s]",
            request.url.path,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "AUTH_REQUIRED",
                "message": "Authentication credentials were not provided.",
                "details": {},
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        claims = decode_token(token)
    except TokenExpiredError:
        logger.warning(
            "Authentication failed: Expired token [Path: %s]",
            request.url.path,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "AUTH_EXPIRED",
                "message": "Authentication token has expired.",
                "details": {},
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    except TokenInvalidError as exc:
        logger.warning(
            "Authentication failed: Invalid token claims or signature [Path: %s, Reason: %s]",
            request.url.path,
            str(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "AUTH_INVALID",
                "message": "Invalid authentication token.",
                "details": {},
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Explicitly reject refresh tokens when an access token is required
    if claims.get("type") != "access":
        logger.warning(
            "Authentication failed: Invalid token type '%s' [Path: %s]",
            claims.get("type"),
            request.url.path,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "AUTH_INVALID",
                "message": "Invalid token type. Access token required.",
                "details": {},
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    request.state.user = claims
    return claims


async def get_optional_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
) -> Optional[dict[str, Any]]:
    """Optional authentication dependency for hybrid or public endpoints.

    Returns claims dict if valid access token is provided; returns None if unauthenticated.
    """
    if not credentials or not credentials.credentials:
        return None

    try:
        claims = decode_token(credentials.credentials)
        if claims.get("type") == "access":
            request.state.user = claims
            return claims
    except (TokenExpiredError, TokenInvalidError) as exc:
        logger.debug(
            "Optional authentication skipped [Path: %s, Reason: %s]",
            request.url.path,
            str(exc),
        )

    return None

