# Conversation Management Service

from typing import Optional, List, Dict, Any
from app.repositories.conversation_repository import ConversationRepository
from app.utils.cortex_client import CortexClient

class ConversationService:
    """Manages session retrieval, chat history, Cortex intent detection, and prompt context building."""

    def __init__(self, repository: Optional[ConversationRepository] = None):
        self.repository = repository or ConversationRepository()

    def get_or_create_session(self, user_id: str, session_id: Optional[str] = None) -> str:
        return self.repository.get_or_create_session(user_id=user_id, session_id=session_id)

    def load_history(self, conversation_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        return self.repository.load_history(conversation_id=conversation_id, limit=limit)

    async def detect_intent(self, message: str, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        return await CortexClient.detect_intent(message=message, history=history)

    def needs_clarification(self, intent_result: Dict[str, Any]) -> bool:
        return intent_result.get("needs_clarification", False) or intent_result.get("confidence", 0.0) < 0.50

    def build_context(
        self,
        user: Dict[str, Any],
        history: List[Dict[str, Any]],
        workflow_state: Optional[Dict[str, Any]],
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assembles a structured prompt object for Cortex generation."""
        return {
            "user_id": user.get("sub"),
            "department_id": user.get("department_id"),
            "role": user.get("role"),
            "active_workflow_session": workflow_state,
            "conversation_history": history,
            "retrieved_chunks": retrieved_chunks
        }
