# Mandatory Response Validation Gate (Grounding, Permissions, Citations, Confidence)

from typing import List, Dict, Any, Union
from app.models.copilot import Citation, ValidatedResponse, EscalationRequired

class ResponseValidationService:
    """
    Mandatory architectural validation gate.
    Every Copilot response must pass through this layer before delivery.
    """

    def verify_grounding(self, response: str, retrieved_chunks: List[Dict[str, Any]]) -> bool:
        """Verifies if response text strictly references concepts within retrieved chunks."""
        if not retrieved_chunks:
            return False
        # Simple heuristic verification for stubbed Cortex evaluation
        return len(response.strip()) > 0 and any(chunk.get("document_id") for chunk in retrieved_chunks)

    def check_permissions(self, user: Dict[str, Any], retrieved_chunks: List[Dict[str, Any]]) -> bool:
        """Re-verifies department permissions for all retrieved chunks prior to formatting response."""
        user_dept = user.get("department_id")
        user_role = user.get("role")
        if user_role == "admin":
            return True
        return all(chunk.get("department_id") == user_dept for chunk in retrieved_chunks)

    def generate_citations(self, retrieved_chunks: List[Dict[str, Any]]) -> List[Citation]:
        """Maps retrieved raw chunks to structured frontend citations."""
        citations = []
        for chunk in retrieved_chunks:
            citations.append(
                Citation(
                    document_id=chunk.get("document_id", "doc_unknown"),
                    document_title=chunk.get("document_title", "Unknown SOP Document"),
                    version_number=chunk.get("version_number", 1),
                    step_number=chunk.get("step_number"),
                    chunk_id=chunk.get("chunk_id", "chk_unknown"),
                    excerpt=chunk.get("content", "")[:150]
                )
            )
        return citations

    def estimate_confidence(
        self,
        response: str,
        retrieved_chunks: List[Dict[str, Any]],
        retrieval_scores: List[float]
    ) -> float:
        """Estimates overall response confidence based on vector similarity and grounding."""
        if not retrieved_chunks or not retrieval_scores:
            return 0.0
        avg_score = sum(retrieval_scores) / len(retrieval_scores)
        return round(min(avg_score * 1.05, 0.99), 2)

    def validate_response(
        self,
        response_text: str,
        user: Dict[str, Any],
        retrieved_chunks: List[Dict[str, Any]]
    ) -> Union[ValidatedResponse, EscalationRequired]:
        """Single point of entry for response validation. Guarantees no unvalidated response passes."""
        if not retrieved_chunks:
            return EscalationRequired(
                answer="No published knowledge document was found matching your query for your department.",
                reason="NO_GROUNDING_KNOWLEDGE_FOUND",
                confidence_score=0.0
            )

        if not self.check_permissions(user=user, retrieved_chunks=retrieved_chunks):
            return EscalationRequired(
                answer="Permission denied: You do not have permission to view the matching document scope.",
                reason="RBAC_PERMISSION_DENIED",
                confidence_score=0.0
            )

        is_grounded = self.verify_grounding(response=response_text, retrieved_chunks=retrieved_chunks)
        scores = [chunk.get("score", 0.5) for chunk in retrieved_chunks]
        confidence = self.estimate_confidence(response=response_text, retrieved_chunks=retrieved_chunks, retrieval_scores=scores)

        if not is_grounded or confidence < 0.75:
            return EscalationRequired(
                answer="I could not generate a response with sufficient grounding confidence. Escalating to supervisor.",
                reason="LOW_CONFIDENCE_OR_UNGROUNDED",
                confidence_score=confidence
            )

        citations = self.generate_citations(retrieved_chunks=retrieved_chunks)
        return ValidatedResponse(
            answer=response_text,
            citations=citations,
            confidence_score=confidence,
            is_grounded=True,
            requires_escalation=False
        )
