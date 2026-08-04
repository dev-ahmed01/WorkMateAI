"""API v1 router initialization and routing registry."""

from fastapi import APIRouter

# Primary API v1 router aggregator
api_v1_router = APIRouter()

# Explicit sub-router registrations will be added as feature modules are completed:
# from app.api.v1.auth import router as auth_router
# api_v1_router.include_router(auth_router)

__all__ = ["api_v1_router"]
