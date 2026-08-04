"""Repository executing user and permission lookup queries against Snowflake."""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from snowflake.connector import SnowflakeConnection
from snowflake.connector.cursor import DictCursor
from snowflake.connector.errors import Error as SnowflakeError

from app.core.database import DatabaseQueryError, execute_query

logger = logging.getLogger("workmate.repository.user")

# Centralized Table Constants
USERS_TABLE = "USERS"
ROLES_TABLE = "ROLES"  # Reserved for schema role definitions
USER_ROLES_TABLE = "USER_ROLES"  # Reserved for multi-role join mappings

__all__ = ["UserRepository"]


def _clean_str(val: Optional[str]) -> Optional[str]:
    """Helper to trim strings and convert empty/whitespace values to None."""
    if val is None:
        return None
    cleaned = val.strip()
    return cleaned if cleaned else None


class UserRepository:
    """Data access repository for User entities in Snowflake."""

    def __init__(self, conn: SnowflakeConnection) -> None:
        """Initialize UserRepository with an active Snowflake connection."""
        self.conn = conn

    def _execute(
        self,
        query: str,
        params: tuple[Any, ...] | dict[str, Any] | None = None,
        fetch_all: bool = True,
    ) -> Any:
        """Private helper executing SQL queries via execute_query."""
        try:
            return execute_query(
                self.conn,
                query,
                params=params,
                fetch_all=fetch_all,
                cursor_factory=DictCursor,
            )
        except (DatabaseQueryError, SnowflakeError) as exc:
            logger.exception("User repository query execution failed.")
            raise DatabaseQueryError("A database query error occurred.") from exc

    def get_user_by_email(self, email: str) -> Optional[dict[str, Any]]:
        """Retrieve user record by email address (case-insensitive).

        Returns dict of user claims/profile if found, or None if no record matches.
        """
        query = f"""
            SELECT id, email, password_hash, role, department_id, first_name, last_name, is_active, created_at, last_login_at
            FROM {USERS_TABLE}
            WHERE LOWER(email) = LOWER(%s)
            LIMIT 1;
        """
        results = self._execute(query, (email.strip(),), fetch_all=False)
        if not results or not isinstance(results, dict):
            return None
        return results

    def get_user_by_id(self, user_id: str) -> Optional[dict[str, Any]]:
        """Retrieve user record by primary key user_id.

        Returns dict of user claims/profile if found, or None if no record matches.
        """
        query = f"""
            SELECT id, email, password_hash, role, department_id, first_name, last_name, is_active, created_at, last_login_at
            FROM {USERS_TABLE}
            WHERE id = %s
            LIMIT 1;
        """
        results = self._execute(query, (user_id.strip(),), fetch_all=False)
        if not results or not isinstance(results, dict):
            return None
        return results

    def create_user(
        self,
        user_id: str,
        email: str,
        password_hash: str,
        role: str,
        department_id: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        is_active: bool = True,
    ) -> dict[str, Any]:
        """Insert a new user record into Snowflake."""
        now = datetime.now(timezone.utc)
        clean_dept = _clean_str(department_id)
        clean_first = _clean_str(first_name)
        clean_last = _clean_str(last_name)

        query = f"""
            INSERT INTO {USERS_TABLE} (id, email, password_hash, role, department_id, first_name, last_name, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        params = (
            user_id.strip(),
            email.strip().lower(),
            password_hash,
            role.strip().lower(),
            clean_dept,
            clean_first,
            clean_last,
            is_active,
            now,
        )

        self._execute(query, params, fetch_all=False)
        logger.info("Created user record successfully [User ID: %s]", user_id)

        return {
            "id": user_id,
            "email": email.strip().lower(),
            "role": role.strip().lower(),
            "department_id": clean_dept,
            "first_name": clean_first,
            "last_name": clean_last,
            "is_active": is_active,
            "created_at": now,
        }

    def update_last_login(self, user_id: str) -> None:
        """Update last_login_at timestamp for a user."""
        now = datetime.now(timezone.utc)
        query = f"""
            UPDATE {USERS_TABLE}
            SET last_login_at = %s
            WHERE id = %s;
        """
        self._execute(query, (now, user_id.strip()), fetch_all=False)
        logger.debug("Updated last login timestamp [User ID: %s]", user_id)
