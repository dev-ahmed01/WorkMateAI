"""Password Hashing and JWT Token Management for WorkMate AI."""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

REQUIRED_CLAIMS = ("sub", "role", "type", "iss")


class TokenExpiredError(Exception):
    """Raised when a JWT token has expired."""

    pass


class TokenInvalidError(Exception):
    """Raised when a JWT token signature, claims, or format is invalid."""

    pass


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a stored bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def _build_token_payload(
    user_id: str,
    role: str,
    token_type: str,
    department_id: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
) -> dict[str, Any]:
    """Internal helper to construct a standardized JWT payload dictionary."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    elif token_type == "access":
        expire = now + timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES)
    elif token_type == "refresh":
        expire = now + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
    else:
        expire = now + timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES)

    payload: dict[str, Any] = {
        "sub": user_id,
        "role": role,
        "type": token_type,
        "iss": settings.APP_NAME,
        "iat": now,
        "exp": expire,
    }
    if department_id is not None:
        payload["department_id"] = department_id

    return payload


def create_access_token(
    user_id: str,
    role: str,
    department_id: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Generates a short-lived access JWT embedding identity, role, and optional department_id."""
    payload = _build_token_payload(
        user_id=user_id,
        role=role,
        token_type="access",
        department_id=department_id,
        expires_delta=expires_delta,
    )
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    user_id: str,
    role: str,
    department_id: Optional[str] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Generates a long-lived refresh JWT for session token rotation."""
    payload = _build_token_payload(
        user_id=user_id,
        role=role,
        token_type="refresh",
        department_id=department_id,
        expires_delta=expires_delta,
    )
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decodes and validates a JWT token fail-fast.

    Raises TokenExpiredError on token expiration.
    Raises TokenInvalidError on invalid signature, issuer mismatch, or missing mandatory claims.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        missing_claims = [claim for claim in REQUIRED_CLAIMS if claim not in payload]
        if missing_claims:
            raise TokenInvalidError(
                f"Token payload missing required claims: {', '.join(missing_claims)}"
            )
        if payload.get("iss") != settings.APP_NAME:
            raise TokenInvalidError(
                f"Token issuer mismatch. Expected '{settings.APP_NAME}', got '{payload.get('iss')}'."
            )
        return payload
    except ExpiredSignatureError as exc:
        raise TokenExpiredError("Token has expired.") from exc
    except TokenInvalidError:
        raise
    except JWTError as exc:
        raise TokenInvalidError(f"Invalid token: {exc}") from exc
