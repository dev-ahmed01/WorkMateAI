# FastAPI Router for Copilot Session State Operations

from fastapi import APIRouter, Depends, HTTPException, status
from app.models.workflow_session import WorkflowSession, AbandonSessionRequest
from app.services.workflow_state import WorkflowStateService
from app.middleware.rbac import require_role

router = APIRouter(prefix="/copilot/session", tags=["Copilot Session"])

@router.post(
    "/{id}/resume",
    response_model=WorkflowSession,
    summary="Resume a paused workflow session",
    dependencies=[Depends(require_role(["employee", "admin"]))]
)
async def resume_session_endpoint(
    id: str,
    service: WorkflowStateService = Depends()
):
    """Resumes a paused workflow session back to active status."""
    return service.resume_session(session_id=id)

@router.post(
    "/{id}/pause",
    response_model=WorkflowSession,
    summary="Pause an active workflow session",
    dependencies=[Depends(require_role(["employee", "admin"]))]
)
async def pause_session_endpoint(
    id: str,
    service: WorkflowStateService = Depends()
):
    """Pauses an active workflow session."""
    return service.pause_session(session_id=id)

@router.post(
    "/{id}/abandon",
    response_model=WorkflowSession,
    summary="Abandon an active workflow session",
    dependencies=[Depends(require_role(["employee", "admin"]))]
)
async def abandon_session_endpoint(
    id: str,
    payload: AbandonSessionRequest,
    service: WorkflowStateService = Depends()
):
    """Abandons a session with an logged audit reason."""
    return service.abandon_session(session_id=id, reason=payload.reason)
