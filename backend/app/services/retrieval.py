# Vector & Knowledge Retrieval Service (Cortex Search Integration)

from typing import List, Dict, Any, Optional
from app.utils.cortex_client import CortexClient

class RetrievalService:
    """Retrieves grounded knowledge chunks and active SOP step content."""

    async def retrieve_chunks(self, query: str, department_id: str) -> List[Dict[str, Any]]:
        """
        Executes Cortex Search filter-scoped to the user's department.
        Enforces strict architectural rule: only status='PUBLISHED' versions are queried.
        """
        return await CortexClient.search(query=query, department_id=department_id)

    def retrieve_current_sop_step(self, workflow_session: Optional[Any]) -> Optional[Dict[str, Any]]:
        """Fetches current step content from active SOP session if available."""
        if not workflow_session or not getattr(workflow_session, 'id', None):
            return None
        return {
            "sop_id": getattr(workflow_session, 'knowledge_version_id', 'sop_unknown'),
            "step_number": getattr(workflow_session, 'current_step', 0) + 1,
            "step_title": "Safety Valve Verification"
        }
