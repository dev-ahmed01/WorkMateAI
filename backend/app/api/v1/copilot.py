# FastAPI Router for WorkMate Copilot Message Endpoint

from fastapi import APIRouter, Depends, HTTPException, status
from app.models.copilot import CopilotMessageRequest, CopilotResponse, ValidatedResponse, EscalationRequired
from app.services.conversation import ConversationService
from app.services.retrieval import RetrievalService
from app.services.validation import ResponseValidationService
from app.services.workflow_state import WorkflowStateService
from app.services.escalation import EscalationService
from app.utils.cortex_client import CortexClient
from app.middleware.rbac import require_role, get_current_user

router = APIRouter(prefix="/copilot", tags=["Copilot"])

# Assumption: Endpoint allows 'employee' or 'admin' roles to interact with Copilot
@router.post(
    "/message",
    response_model=CopilotResponse,
    summary="Send message to WorkMate Copilot",
    dependencies=[Depends(require_role(["employee", "admin"]))]
)
async def copilot_message(
    payload: CopilotMessageRequest,
    current_user: dict = Depends(get_current_user),
    conv_service: ConversationService = Depends(),
    retrieval_service: RetrievalService = Depends(),
    validation_service: ResponseValidationService = Depends(),
    workflow_service: WorkflowStateService = Depends(),
    escalation_service: EscalationService = Depends()
):
    """
    Core Copilot Orchestration Pipeline:
    Detect Intent -> Clarification Check -> Chunk Retrieval -> Context Assembly ->
    Cortex Response Generation -> Response Validation -> Persist & Return (or Escalate).
    """
    user_id = current_user.get("sub")
    department_id = current_user.get("department_id", "GENERAL")

    # 1. Session Management & History Loading
    conversation_id = conv_service.get_or_create_session(user_id=user_id, session_id=payload.conversation_id)
    conv_service.repository.persist_message(conversation_id=conversation_id, sender="user", content=payload.message)
    history = conv_service.load_history(conversation_id=conversation_id)

    # 2. Intent Detection
    intent_result = await conv_service.detect_intent(message=payload.message, history=history)

    # Short-circuit on clarification requirement
    if conv_service.needs_clarification(intent_result):
        clarification_text = "Could you please specify which SOP or equipment section you are referring to?"
        msg_id = conv_service.repository.persist_message(
            conversation_id=conversation_id,
            sender="assistant",
            content=clarification_text,
            confidence_score=0.40
        )
        return CopilotResponse(
            conversation_id=conversation_id,
            message_id=msg_id,
            answer=clarification_text,
            citations=[],
            confidence_score=0.40,
            is_grounded=True,
            requires_escalation=False
        )

    # 3. Active Workflow Session State & Retrieval
    active_session = workflow_service.get_active_session(conversation_id=conversation_id)
    retrieved_chunks = await retrieval_service.retrieve_chunks(query=payload.message, department_id=department_id)
    sop_step_info = retrieval_service.retrieve_current_sop_step(workflow_session=active_session)

    # 4. Context Assembly & Cortex Complete Generation
    prompt_context = conv_service.build_context(
        user=current_user,
        history=history,
        workflow_state=active_session.dict() if active_session else None,
        retrieved_chunks=retrieved_chunks
    )
    raw_response = await CortexClient.generate_response(prompt_context)

    # 5. Mandatory Response Validation Layer Execution
    validated_result = validation_service.validate_response(
        response_text=raw_response,
        user=current_user,
        retrieved_chunks=retrieved_chunks
    )

    requires_escalation = False
    if isinstance(validated_result, EscalationRequired):
        requires_escalation = True
        answer_text = validated_result.answer
        citations = []
        confidence_score = validated_result.confidence_score

        # Persist escalation attempt message
        msg_id = conv_service.repository.persist_message(
            conversation_id=conversation_id,
            sender="assistant",
            content=answer_text,
            confidence_score=confidence_score
        )
        # Trigger internal escalation lifecycle (n8n notification)
        await escalation_service.escalate(
            conversation_message_id=msg_id,
            reason=validated_result.reason
        )
    else:
        answer_text = validated_result.answer
        citations = validated_result.citations
        confidence_score = validated_result.confidence_score
        msg_id = conv_service.repository.persist_message(
            conversation_id=conversation_id,
            sender="assistant",
            content=answer_text,
            confidence_score=confidence_score
        )

    return CopilotResponse(
        conversation_id=conversation_id,
        message_id=msg_id,
        answer=answer_text,
        citations=citations,
        confidence_score=confidence_score,
        is_grounded=not requires_escalation,
        requires_escalation=requires_escalation,
        active_sop_id=sop_step_info.get("sop_id") if sop_step_info else None,
        active_step_number=sop_step_info.get("step_number") if sop_step_info else None,
        active_step_title=sop_step_info.get("step_title") if sop_step_info else None
    )
