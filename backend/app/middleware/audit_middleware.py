# Audit Logging Middleware for State-Changing API Requests

import uuid
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.database import get_snowflake_connection

class AuditLogMiddleware(BaseHTTPMiddleware):
    """
    Intercepts state-changing HTTP requests (POST, PUT, PATCH, DELETE) and writes an audit log row to Snowflake.
    """
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Only audit state-changing actions
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            user_claims = getattr(request.state, "user", None)
            user_id = user_claims.get("sub") if user_claims else "ANONYMOUS"
            action = f"{request.method} {request.url.path}"
            resource = request.url.path
            ip_address = request.client.host if request.client else "0.0.0.0"

            self._log_audit_event(user_id=user_id, action=action, resource=resource, ip_address=ip_address)

        return response

    def _log_audit_event(self, user_id: str, action: str, resource: str, ip_address: str):
        log_id = f"aud_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        query = """
            INSERT INTO audit_logs (id, user_id, action, resource, ip_address, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            with get_snowflake_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (log_id, user_id, action, resource, ip_address, now))
        except Exception as exc:
            # Prevent audit persistence failures from interrupting primary HTTP response handling
            print(f"[WARNING] Audit logging failed: {str(exc)}")
