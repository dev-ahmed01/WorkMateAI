# WorkMate AI — Changelog

## Sprint 1 — Configuration
### Added
- Centralized configuration module (`app/core/config.py`)
- Environment management using Pydantic Settings
- Snowflake configuration
- JWT configuration
- Logging configuration
- CORS configuration
- n8n configuration
- Cached settings singleton

### Verified
- Configuration loading
- Environment validation
- Project compilation

---

## Sprint 2 — Database Layer
### Added
- Snowflake database connection manager
- Connection helper
- Query execution helper
- FastAPI database dependency
- Database health check
- Graceful connection handling
- Foundation for Cortex SQL integration

### Verified
- Import tests
- Configuration loading
- Project compilation

---

## Sprint 3 — FastAPI Application
### Added
- FastAPI application factory
- Startup & shutdown lifecycle
- Logging initialization
- Request timing middleware
- CORS middleware
- Root endpoint
- Health endpoint
- Swagger & ReDoc
- API router registration

### Verified
- Uvicorn startup
- Root endpoint
- Health endpoint
- Swagger
- ReDoc
- Project compilation

---

## Sprint 4 — API Router Aggregation
### Added
- API v1 router aggregator
- Safe router registration
- Scalable API versioning foundation

### Verified
- Router imports
- FastAPI startup
- Project compilation

---

## Sprint 5 — Security Foundation
### Added
- Password hashing (bcrypt)
- Password verification
- JWT access token generation
- JWT refresh token generation
- JWT decoding
- Token validation
- Custom token exceptions

### Verified
- Password hashing
- Password verification
- JWT creation
- JWT decoding
- Project compilation

---

## Sprint 6 — Authentication Middleware
### Added
- Bearer token authentication dependency
- Optional authentication dependency
- JWT validation integration
- Request user context attachment
- Standardized HTTP 401 authentication responses
- Authentication logging

### Improved
- Optional authentication now logs invalid or expired tokens at DEBUG level.

### Verified
- Middleware compilation
- FastAPI dependency validation
- Git review
- Commit & Push