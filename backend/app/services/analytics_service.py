"""Analytics Service layer executing optimized read-only queries against Snowflake materialized views."""

from typing import Any, Dict, List, Optional
from app.core.database import get_db_cursor


class AnalyticsService:
    """Service handling Manager Intelligence Hub data retrievals."""

    @staticmethod
    def get_sop_usage(department_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = "SELECT SOP_ID, SOP_TITLE, DEPARTMENT_ID, TOTAL_EXECUTIONS, UNIQUE_USERS, AVG_COMPLETION_MINUTES, LAST_USED_AT FROM V_ANALYTICS_SOP_USAGE"
        params = []
        if department_id:
            query += " WHERE DEPARTMENT_ID = %s"
            params.append(department_id)
        query += " ORDER BY TOTAL_EXECUTIONS DESC"

        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def get_faqs(department_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        query = "SELECT QUERY_TOPIC, DEPARTMENT_ID, QUERY_COUNT, AVG_CONFIDENCE, LAST_QUERIED_AT FROM V_ANALYTICS_FAQS"
        params = []
        if department_id:
            query += " WHERE DEPARTMENT_ID = %s"
            params.append(department_id)
        query += " ORDER BY QUERY_COUNT DESC LIMIT %s"
        params.append(limit)

        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def get_confusing_procedures(department_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = "SELECT SOP_ID, SOP_TITLE, DEPARTMENT_ID, TOTAL_SESSIONS, CONFUSING_SESSIONS, CONFUSION_RATE_PCT, AVG_CLARIFICATION_REQUESTS FROM V_ANALYTICS_CONFUSING_PROCEDURES"
        params = []
        if department_id:
            query += " WHERE DEPARTMENT_ID = %s"
            params.append(department_id)
        query += " ORDER BY CONFUSION_RATE_PCT DESC"

        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def get_escalations(department_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = "SELECT ESCALATION_ID, SESSION_ID, USER_ID, DEPARTMENT_ID, SOP_ID, SOP_TITLE, ESCALATION_REASON, ESCALATION_STATUS, CREATED_AT FROM V_ANALYTICS_ESCALATIONS"
        params = []
        if department_id:
            query += " WHERE DEPARTMENT_ID = %s"
            params.append(department_id)
        query += " ORDER BY CREATED_AT DESC"

        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def get_department_adoption() -> List[Dict[str, Any]]:
        query = "SELECT DEPARTMENT_ID, TOTAL_ENROLLED_USERS, ACTIVE_COPILOT_USERS, TOTAL_INTERACTIONS, ADOPTION_RATE_PCT FROM V_ANALYTICS_DEPARTMENT_ADOPTION ORDER BY ADOPTION_RATE_PCT DESC"
        with get_db_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    @staticmethod
    def get_confidence_trends(department_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query = "SELECT METRIC_DATE, DEPARTMENT_ID, TOTAL_RESPONSES, AVG_CONFIDENCE_SCORE, MIN_CONFIDENCE_SCORE, MAX_CONFIDENCE_SCORE FROM V_ANALYTICS_CONFIDENCE_TRENDS"
        params = []
        if department_id:
            query += " WHERE DEPARTMENT_ID = %s"
            params.append(department_id)
        query += " ORDER BY METRIC_DATE ASC"

        with get_db_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
