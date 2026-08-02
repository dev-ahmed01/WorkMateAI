# Role & Department Access Control Dependency Factories

from typing import List
from fastapi import Depends, Request
from app.middleware.auth_middleware import get_current_user
from app.exceptions.custom_exceptions import AuthorizationException

def require_role(allowed_roles: List[str]):
    """Enforces role-based access control against claims embedded in the verified JWT."""
    async def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise AuthorizationException(
                message=f"User with role '{user_role}' lacks required permissions ({', '.join(allowed_roles)})"
            )
        return current_user
    return role_checker

def require_department_match():
    """Validates that requested departmental scope matches the user's assigned department_id claim."""
    async def department_checker(request: Request, current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        user_dept = current_user.get("department_id")

        # Admins bypass departmental restriction checks
        if user_role == "admin":
            return current_user

        path_dept = request.path_params.get("department_id") or request.query_params.get("department_id")
        if path_dept and path_dept != user_dept:
            raise AuthorizationException(
                message=f"Access denied: User department '{user_dept}' cannot access scope '{path_dept}'"
            )
        return current_user
    return department_checker
