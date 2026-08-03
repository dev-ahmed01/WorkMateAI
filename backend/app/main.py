"""WorkMate AI FastAPI Application entry point."""

import logging
import time
from typing import Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import ping

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format=settings.LOG_FORMAT,
)
logger = logging.getLogger("workmate.main")


def create_app() -> FastAPI:
    """Application factory for WorkMate AI FastAPI backend."""
    app = FastAPI(
        title=settings.APP_NAME,
        description="WorkMate AI — Enterprise Operational Intelligence Platform API",
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Startup & Shutdown Lifecycle Event Logging
    @app.on_event("startup")
    async def startup_event() -> None:
        logger.info(
            "Starting %s v%s [Environment: %s]",
            settings.APP_NAME,
            settings.APP_VERSION,
            settings.APP_ENV,
        )
        logger.info("Allowed CORS Origins: %s", settings.ALLOWED_ORIGINS)

    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        logger.info("Shutting down %s...", settings.APP_NAME)

    # Register CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request Logging & Process Time Middleware
    @app.middleware("http")
    async def log_request_time(request: Request, call_next: Any) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time_ms = (time.perf_counter() - start_time) * 1000.0
        response.headers["X-Process-Time"] = f"{process_time_ms:.2f}ms"

        logger.info(
            "%s %s - %d (%.2fms)",
            request.method,
            request.url.path,
            response.status_code,
            process_time_ms,
        )
        return response

    # API v1 Router Registration Placeholder
    try:
        from app.api.v1 import api_v1_router  # type: ignore

        app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)
        logger.info("Mounted API v1 router at %s", settings.API_V1_PREFIX)
    except (ImportError, AttributeError):
        logger.info(
            "API v1 router aggregator not ready yet. Skipping router inclusion."
        )

    # Root Endpoint
    @app.get("/", tags=["System"])
    async def root() -> dict[str, str]:
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.APP_ENV,
            "status": "running",
            "api_prefix": settings.API_V1_PREFIX,
            "docs_url": "/docs",
        }

    # Health Endpoint
    @app.get("/health", tags=["System"])
    async def health() -> dict[str, str]:
        db_healthy = ping()
        return {
            "status": "ok" if db_healthy else "degraded",
            "database": "connected" if db_healthy else "unreachable",
            "environment": settings.APP_ENV,
        }

    return app


app = create_app()
