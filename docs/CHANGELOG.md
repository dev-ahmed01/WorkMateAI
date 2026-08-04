# WorkMate AI Changelog

## Sprint 10 — Authentication API Endpoints
**Date:** 2026-08-04

### Added
- Implemented `backend/app/api/v1/auth.py`
- Added REST API endpoints:
  - `POST /api/v1/auth/login` (Credential validation and JWT token issuance)
  - `POST /api/v1/auth/refresh` (Refresh token rotation and access token renewal)
  - `GET /api/v1/auth/me` (Authenticated identity profile lookup)
- Registered `auth_router` inside `backend/app/api/v1/__init__.py`
- Pydantic request & response models (`LoginRequest`, `TokenRefreshRequest`, `UserResponse`, `TokenResponse`)
- Standardized HTTP error mapping (`AUTH_INVALID`, `AUTH_INACTIVE`, `USER_NOT_FOUND`, `INTERNAL_ERROR`)
- Request-scoped dependency factory `get_auth_service(conn = Depends(get_db))`

### Verification
- Project compiled successfully using `.venv/bin/python -m compileall app`
- OpenAPI / Swagger `/docs` endpoint rendering and schema validation

---

## Sprint 9 — Authentication Service
**Date:** 2026-08-04

### Added
- Implemented `backend/app/services/authentication_service.py`
- Domain workflows: `login()`, `refresh_token()`, `get_current_user_profile()`
- Sanitization helper `_sanitize_user()` stripping sensitive fields
- Shared token response helper `_build_token_response()`
- Domain exceptions (`UserNotFoundError`, `InvalidCredentialsError`, `InactiveUserError`, `InvalidRefreshTokenError`)

---

## Sprint 8 — User Repository
**Date:** 2026-08-04

### Added
- Implemented `backend/app/repositories/user_repository.py`
- Pure Snowflake data access layer for user lookups and insertions (`get_user_by_email`, `get_user_by_id`, `create_user`, `update_last_login`)

---

## Sprint 7 — RBAC Middleware

### Added
- Implemented `backend/app/middleware/rbac_middleware.py`
- Role-Based Access Control (`require_role`, `has_role`) and department scope authorization (`require_own_department`)