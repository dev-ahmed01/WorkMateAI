"""Snowflake connection management and session handling (sole persistence layer)."""

import logging
from typing import Any, Generator
import snowflake.connector
from snowflake.connector import SnowflakeConnection
from snowflake.connector.cursor import DictCursor
from snowflake.connector.errors import Error as SnowflakeError

from app.core.config import settings

logger = logging.getLogger("workmate.database")


class DatabaseConnectionError(Exception):
    """Raised when establishing or re-establishing a database connection fails."""

    pass


class DatabaseQueryError(Exception):
    """Raised when a database query execution fails."""

    pass


def get_connection_params() -> dict[str, Any]:
    """Extract connection parameters from application settings."""
    params: dict[str, Any] = {
        "account": settings.SNOWFLAKE_ACCOUNT,
        "user": settings.SNOWFLAKE_USER,
        "password": settings.SNOWFLAKE_PASSWORD,
        "warehouse": settings.SNOWFLAKE_WAREHOUSE,
        "database": settings.SNOWFLAKE_DATABASE,
        "schema": settings.SNOWFLAKE_SCHEMA,
    }
    if settings.SNOWFLAKE_ROLE:
        params["role"] = settings.SNOWFLAKE_ROLE
    return params


def create_connection() -> SnowflakeConnection:
    """Create a new Snowflake database connection with 1 retry attempt on failure."""
    params = get_connection_params()
    max_retries = 1

    for attempt in range(max_retries + 1):
        try:
            logger.info(
                "Establishing Snowflake connection (attempt %d/%d)",
                attempt + 1,
                max_retries + 1,
            )
            logger.debug(
                "Snowflake target identifiers [account: %s, warehouse: %s, database: %s]",
                params.get("account"),
                params.get("warehouse"),
                params.get("database"),
            )
            conn: SnowflakeConnection = snowflake.connector.connect(**params)
            logger.info("Snowflake connection established successfully.")
            return conn
        except SnowflakeError as exc:
            logger.warning(
                "Snowflake connection attempt %d failed: %s",
                attempt + 1,
                str(exc),
            )
            if attempt == max_retries:
                logger.error(
                    "Failed to connect to Snowflake after %d attempts.",
                    max_retries + 1,
                )
                raise DatabaseConnectionError(
                    f"Failed to connect to Snowflake: {exc}"
                ) from exc

    # Unreachable fallback for safety
    raise DatabaseConnectionError("Failed to connect to Snowflake database.")


def get_connection() -> SnowflakeConnection:
    """Public connection accessor wrapping create_connection().

    Allows connection management to evolve without changing caller interface.
    """
    return create_connection()


def get_db() -> Generator[SnowflakeConnection, None, None]:
    """FastAPI dependency yielding a managed Snowflake connection object.

    Yields a SnowflakeConnection and guarantees connection teardown on request completion.
    """
    conn: SnowflakeConnection | None = None
    try:
        conn = get_connection()
        yield conn
    finally:
        if conn and not conn.is_closed():
            logger.info("Closing Snowflake connection for request.")
            conn.close()


def execute_query(
    conn: SnowflakeConnection,
    query: str,
    params: tuple[Any, ...] | dict[str, Any] | None = None,
    fetch_all: bool = True,
    cursor_factory: Any = DictCursor,
) -> list[dict[str, Any]] | dict[str, Any] | None:
    """Reusable query execution helper for repositories and Cortex integrations.

    Executes parameterized SQL queries using a dictionary cursor and returns results.
    Includes transaction commit for DML operations and rollback on execution errors.
    """
    query_type = (
        query.strip().split()[0].upper() if query and query.strip() else "UNKNOWN"
    )
    try:
        with conn.cursor(cursor_factory) as cursor:
            logger.debug("Executing SQL statement [type: %s]", query_type)
            cursor.execute(query, params)

            if cursor.description is None:
                # Non-SELECT DDL/DML query: commit if autocommit is disabled
                if not getattr(conn, "autocommit", True):
                    conn.commit()
                return None

            return cursor.fetchall() if fetch_all else cursor.fetchone()
    except SnowflakeError as exc:
        logger.error(
            "Database query execution failed [type: %s] | Error: %s",
            query_type,
            str(exc),
        )
        try:
            conn.rollback()
        except Exception as rb_exc:
            logger.warning("Transaction rollback attempt failed: %s", str(rb_exc))

        raise DatabaseQueryError(f"Query execution error: {exc}") from exc


def ping() -> bool:
    """Lightweight connectivity health check running 'SELECT 1;'.

    Returns True if Snowflake database is reachable, False on database connection or query error.
    """
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1;")
                res = cursor.fetchone()
                return res is not None and res[0] == 1
        finally:
            if not conn.is_closed():
                conn.close()
    except (DatabaseConnectionError, SnowflakeError) as exc:
        logger.warning("Snowflake ping health check failed: %s", str(exc))
        return False
