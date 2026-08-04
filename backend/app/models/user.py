"""Canonical User identity, Role, and Department RBAC data models."""

from datetime import datetime
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRole(str, Enum):
    """System roles for Role-Based Access Control (RBAC)."""

    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"


class BaseSchema(BaseModel):
    """Centralized base Pydantic model with default configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        extra="ignore",
    )


def _clean_str(val: Optional[str]) -> Optional[str]:
    """Helper to trim strings and convert empty or whitespace values to None."""
    if val is None:
        return None
    cleaned = val.strip()
    return cleaned if cleaned else None


class UserBase(BaseSchema):
    """Core domain attributes shared across user schemas."""

    email: EmailStr
    role: UserRole = UserRole.EMPLOYEE
    department_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("department_id", "first_name", "last_name", mode="before")
    @classmethod
    def clean_optional_strings(cls, v: Any) -> Optional[str]:
        if isinstance(v, str):
            return _clean_str(v)
        return v


class UserCreate(UserBase):
    """Schema for user creation and administrative user provisioning."""

    password: str = Field(..., min_length=8, description="Initial plaintext password")


class UserUpdate(BaseSchema):
    """Schema for partial administrative updates to user accounts."""

    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    department_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("department_id", "first_name", "last_name", mode="before")
    @classmethod
    def clean_optional_strings(cls, v: Any) -> Optional[str]:
        if isinstance(v, str):
            return _clean_str(v)
        return v


class UserInDB(UserBase):
    """Internal database representation matching Snowflake USERS table schema."""

    id: str
    password_hash: str
    created_at: datetime
    last_login_at: Optional[datetime] = None


class UserResponse(UserBase):
    """Public user profile response schema (excludes password_hash)."""

    id: str
    created_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None


class JWTUserPayload(BaseSchema):
    """Schema representing claims embedded inside signed JWT access and refresh tokens."""

    sub: str
    role: UserRole
    type: Literal["access", "refresh"]
    iss: str
    department_id: Optional[str] = None
    iat: Optional[datetime] = None
    exp: Optional[datetime] = None


class LoginRequest(BaseSchema):
    """Request payload for user authentication."""

    email: EmailStr
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class TokenRefreshRequest(BaseSchema):
    """Request payload for exchanging a refresh token."""

    refresh_token: str


class TokenResponse(BaseSchema):
    """Authentication response payload containing access/refresh token pair and user profile."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


__all__ = [
    "UserRole",
    "BaseSchema",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserResponse",
    "JWTUserPayload",
    "LoginRequest",
    "TokenRefreshRequest",
    "TokenResponse",
]
