# FastAPI Authentication Dependency

from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_jwt_token
from app.exceptions.custom_exceptions import AuthenticationException

security_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> dict:
    """
    Extracts and validates Bearer token from headers.
    Attaches user claims to request.state and returns claims dictionary.
    """
    if not credentials or not credentials.credentials:
        raise AuthenticationException(message="Missing authentication credentials")

    claims = decode_jwt_token(credentials.credentials)
    request.state.user = claims
    return claims
