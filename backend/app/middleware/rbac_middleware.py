"""FastAPI Role-Based Access Control (RBAC) and Department Authorization Dependencies."""

import logging
from typing import Any, Callable, Iterable, Optional

from fastapi import Depends, HTTPException, Request, status

from app.middleware.auth_middleware import get_current_user

logger = logging.getLogger("workmate.rbac")


def has_role(user_role: Optional[str], allowed_roles: Iterable[str]) -> bool:
    """Helper function to check if a user role matches any allowed role case-insensitively."""
    if not user_role:
        return False
    normalized_user_role = user_role.strip().lower()
    normalized_allowed = {role.strip().lower() for role in allowed_roles}
    return normalized_user_role in normalized_allowed


def require_role(*allowed_roles: str) -> Callable[..., Any]:
    """Dependency factory enforcing role-based access control (case-insensitive).

    Usage: Depends(require_role("admin")) or Depends(require_role("manager", "admin"))
    """

    async def role_checker(
        request: Request,
        current_user: dict[str, Any] = Depends(get_current_user),
    ) -> dict[str, Any]:
        user_role = current_user.get("role")
        if not has_role(user_role, allowed_roles):
            logger.warning(
                "RBAC Authorization failed: Insufficient role permissions [Path: %s, UserRole: '%s', RequiredRoles: %s]",
                request.url.path,
                user_role,
                allowed_roles,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error_code": "AUTH_FORBIDDEN",
                    "message": "Access forbidden: insufficient role permissions.",
                    "details": {
                        "required_roles": list(allowed_roles),
                        "user_role": user_role,
                    },
                },
            )
        return current_user

    return role_checker


def require_own_department(
    department_param: str = "department_id",
) -> Callable[..., Any]:
    """Dependency factory enforcing departmental boundary access control.

    Admins bypass department scope checks. Non-admins must match path/query department parameter.
    Usage: Depends(require_own_department())
    """

    async def department_checker(
        request: Request,
        current_user: dict[str, Any] = Depends(get_current_user),
    ) -> dict[str, Any]:
        user_role = current_user.get("role")
        user_dept = current_user.get("department_id")

        # Admin bypass
        if has_role(user_role, ("admin",)):
            return current_user

        # Extract target department_id from path parameters or query parameters
        target_dept = (
            request.path_params.get(department_param)
            or request.query_params.get(department_param)
        )

        if target_dept and user_dept:
            if target_dept.strip().lower() != user_dept.strip().lower():
                logger.warning(
                    "RBAC Department Scope Mismatch [Path: %s, UserDept: '%s', TargetDept: '%s']",
                    request.url.path,
                    user_dept,
                    target_dept,
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "error_code": "AUTH_FORBIDDEN",
                        "message": "Access forbidden: departmental scope mismatch.",
                        "details": {},
                    },
                )

        return current_user

    return department_checker
