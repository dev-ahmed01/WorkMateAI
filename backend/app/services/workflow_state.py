# Deterministic State Machine for Step-Aware Copilot SOP Guidance

from typing import Optional, Dict, Any, List
from app.models.workflow_session import WorkflowSession, NextActionResponse
from app.repositories.workflow_session_repository import WorkflowSessionRepository
from app.exceptions.custom_exceptions import NotFoundException, ValidationException

class WorkflowStateService:
    """
    Manages operational SOP session progression.
    Guarantees deterministic execution indexing into verified sop_structure without LLM generation.
    """

    def __init__(self, repository: Optional[WorkflowSessionRepository] = None):
        self.repository = repository or WorkflowSessionRepository()

    def get_active_session(self, conversation_id: str) -> Optional[WorkflowSession]:
        """Returns the active workflow_session for a given conversation, or None."""
        data = self.repository.get_active_by_conversation(conversation_id)
        if not data:
            return None
        return WorkflowSession(**data)

    def start_session(self, conversation_id: str, knowledge_version_id: str) -> str:
        """Begins tracking a new SOP session with current_step=0 and status='active'."""
        existing = self.get_active_session(conversation_id)
        if existing:
            # Pause previous active session prior to initiating new SOP
            self.pause_session(existing.id)

        return self.repository.create(
            conversation_id=conversation_id,
            knowledge_version_id=knowledge_version_id
        )

    def mark_step_complete(self, session_id: str, total_steps: int) -> WorkflowSession:
        """
        Advances current_step by 1.
        If it reaches or exceeds the last step index, marks status='complete'.
        """
        session_data = self.repository.get_by_id(session_id)
        if not session_data:
            raise NotFoundException(message=f"Workflow session {session_id} not found.")

        current_step = session_data['current_step'] + 1
        new_status = 'active'

        if current_step >= total_steps:
            current_step = max(total_steps - 1, 0)
            new_status = 'complete'

        self.repository.update_step_and_status(
            session_id=session_id,
            current_step=current_step,
            status=new_status
        )

        updated_data = self.repository.get_by_id(session_id)
        return WorkflowSession(**updated_data)

    def pause_session(self, session_id: str) -> WorkflowSession:
        """Pauses an active workflow session."""
        success = self.repository.update_status(session_id=session_id, status='paused')
        if not success:
            raise NotFoundException(message=f"Workflow session {session_id} not found.")
        return WorkflowSession(**self.repository.get_by_id(session_id))

    def resume_session(self, session_id: str) -> WorkflowSession:
        """Resumes a paused workflow session back to status='active'."""
        success = self.repository.update_status(session_id=session_id, status='active')
        if not success:
            raise NotFoundException(message=f"Workflow session {session_id} not found.")
        return WorkflowSession(**self.repository.get_by_id(session_id))

    def abandon_session(self, session_id: str, reason: str) -> WorkflowSession:
        """Marks a workflow session as abandoned with an audit reason."""
        success = self.repository.update_status(
            session_id=session_id,
            status='abandoned',
            abandon_reason=reason
        )
        if not success:
            raise NotFoundException(message=f"Workflow session {session_id} not found.")
        return WorkflowSession(**self.repository.get_by_id(session_id))

    def get_next_action(
        self,
        session_id: str,
        sop_structure: List[Dict[str, Any]]
    ) -> NextActionResponse:
        """
        Deterministic state machine decision logic.
        Validates current session state strictly against retrieved SOP step boundaries.
        Never calls LLM logic or fabricates unverified steps.
        """
        session_data = self.repository.get_by_id(session_id)
        if not session_data:
            raise NotFoundException(message=f"Workflow session {session_id} not found.")

        total_steps = len(sop_structure)
        if total_steps == 0:
            return NextActionResponse(
                action='needs_document',
                total_steps=0
            )

        current_step_idx = session_data['current_step']

        if session_data['status'] == 'complete' or current_step_idx >= total_steps:
            return NextActionResponse(
                action='workflow_complete',
                total_steps=total_steps
            )

        step_data = sop_structure[current_step_idx]

        # Deterministic boundary evaluation
        return NextActionResponse(
            action='proceed_to_step',
            target_step=current_step_idx,
            step_title=step_data.get('title', f"Step {current_step_idx + 1}"),
            total_steps=total_steps
        )
