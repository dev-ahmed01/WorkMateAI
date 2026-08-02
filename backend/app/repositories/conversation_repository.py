# Snowflake SQL Persistence Layer for Conversations & Conversation Messages

import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.core.database import get_snowflake_connection
from app.exceptions.custom_exceptions import DatabaseException

class ConversationRepository:
    """Manages CRUD operations for 'conversations' and 'conversation_messages' tables in Snowflake."""

    @staticmethod
    def get_or_create_session(user_id: str, session_id: Optional[str] = None) -> str:
        now = datetime.utcnow()
        if session_id:
            query = "SELECT id FROM conversations WHERE id = %s AND user_id = %s"
            try:
                with get_snowflake_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(query, (session_id, user_id))
                        row = cur.fetchone()
                        if row:
                            return row[0]
            except Exception as e:
                raise DatabaseException(message=f"Failed to fetch conversation session: {str(e)}")

        new_id = f"conv_{uuid.uuid4().hex[:12]}"
        insert_query = "INSERT INTO conversations (id, user_id, created_at, updated_at) VALUES (%s, %s, %s, %s)"
        try:
            with get_snowflake_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(insert_query, (new_id, user_id, now, now))
            return new_id
        except Exception as e:
            raise DatabaseException(message=f"Failed to create conversation session: {str(e)}")

    @staticmethod
    def load_history(conversation_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        query = """
            SELECT id, sender, content, confidence_score, created_at
            FROM conversation_messages
            WHERE conversation_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        try:
            with get_snowflake_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (conversation_id, limit))
                    rows = cur.fetchall()
                    columns = [col[0].lower() for col in cur.description]
                    messages = [dict(zip(columns, row)) for row in rows]
                    return list(reversed(messages))
        except Exception as e:
            raise DatabaseException(message=f"Failed to load conversation history: {str(e)}")

    @staticmethod
    def persist_message(
        conversation_id: str,
        sender: str,
        content: str,
        confidence_score: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        msg_id = f"msg_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        query = """
            INSERT INTO conversation_messages (
                id, conversation_id, sender, content, confidence_score, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            with get_snowflake_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (msg_id, conversation_id, sender, content, confidence_score, now))
            return msg_id
        except Exception as e:
            raise DatabaseException(message=f"Failed to persist conversation message: {str(e)}")
