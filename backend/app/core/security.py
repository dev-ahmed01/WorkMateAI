# Password Hashing and JWT Token Management

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.exceptions.custom_exceptions import AuthenticationException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a stored bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: str, role: str, department_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """Generates an access JWT embedding user_id (sub), role, and department_id claims."""
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES))
    payload = {
        "sub": user_id,
        "role": role,
        "department_id": department_id,
        "type": "access",
        "exp": expire
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(user_id: str, role: str, department_id: str) -> str:
    """Generates a refresh JWT embedding identity and role claims."""
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "role": role,
        "department_id": department_id,
        "type": "refresh",
        "exp": expire
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_jwt_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT token, raising AuthenticationException on invalid/expired signatures."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        if "sub" not in payload or "role" not in payload:
            raise AuthenticationException(message="Invalid token claims")
        return payload
    except JWTError as exc:
        raise AuthenticationException(message=f"Could not validate credentials: {str(exc)}")
