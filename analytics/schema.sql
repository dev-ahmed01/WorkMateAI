-- ============================================================================
-- WorkMate AI — Enterprise Operational Intelligence Platform Schema (Snowflake)
-- ============================================================================

-- 1. Departments: Scopes users, knowledge items, and RBAC visibility boundaries.
CREATE TABLE IF NOT EXISTS departments (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP_NTZ NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

-- 2. Roles: Defines platform operational roles and JSON-formatted permission sets.
CREATE TABLE IF NOT EXISTS roles (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    permission_set VARIANT NOT NULL,
    created_at TIMESTAMP_NTZ NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

-- 3. Users: Enterprise employees and administrators bound to a specific department.
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(64) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    department_id VARCHAR(64) NOT NULL REFERENCES departments(id),
    created_at TIMESTAMP_NTZ NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

-- 4. User Roles: Junction table mapping enterprise users to assigned system roles.
CREATE TABLE IF NOT EXISTS user_roles (
    user_id VARCHAR(64) NOT NULL REFERENCES users(id),
    role_id VARCHAR(64) NOT NULL REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id)
);

-- 5. Knowledge Items: Core operational knowledge entities (SOPs, policies, manuals).
CREATE TABLE IF NOT EXISTS knowledge_items (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(512) NOT NULL,
    department_id VARCHAR(64) NOT NULL REFERENCES departments(id),
    created_by VARCHAR(64) NOT NULL REFERENCES users(id),
    created_at TIMESTAMP_NTZ NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

-- 6. Knowledge Versions: Lifecycle tracking for uploaded document revisions.
CREATE TABLE IF NOT EXISTS knowledge_versions (
    id VARCHAR(64) PRIMARY KEY,
    knowledge_item_id VARCHAR(64) NOT NULL REFERENCES knowledge_items(id),
    version_number INT NOT NULL,
    stage_file_uri VARCHAR(1024) NOT NULL,
    status VARCHAR(32) NOT NULL CHECK (status IN ('staged', 'processed', 'pending_approval', 'published', 'superseded', 'failed')),
    created_at TIMESTAMP_NTZ NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    published_at TIMESTAMP_NTZ NULL
);

-- 7. Knowledge Chunks: Parsed document chunks linked to Cortex Search vector indices.
CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id VARCHAR(64) PRIMARY KEY,
    knowledge_version_id VARCHAR(64) NOT NULL REFERENCES knowledge_versions(id),
    chunk_text TEXT NOT NULL,
    chunk_index INT NOT NULL,
    embedding_ref VARCHAR(255) NOT NULL
);

-- 8. Conversations: Copilot interaction threads associated with employees.
CREATE TABLE IF NOT EXISTS conversations (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL REFERENCES users(id),
    started_at TIMESTAMP_NTZ NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    ended_at TIMESTAMP_NTZ NULL
);

-- 9. Conversation Messages: Turn-by-turn chat history with intent, grounding, and confidence scores.
CREATE TABLE IF NOT EXISTS conversation_messages (
    id VARCHAR(64) PRIMARY KEY,
    conversation_id VARCHAR(64) NOT NULL REFERENCES conversations(id),
    sender VARCHAR(16) NOT NULL CHECK (sender IN ('employee', 'ai')),
    message_text TEXT NOT NULL,
    intent VARCHAR(128) NULL,
    retrieved_chunk_ids ARRAY NULL,
    citations VARIANT NULL,
    confidence_score FLOAT NOT NULL DEFAULT 0.0,
    escalated BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP_NTZ NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

-- 10. Workflow Sessions: Deterministic state-machine tracking active SOP steps.
CREATE TABLE IF NOT EXISTS workflow_sessions (
    id VARCHAR(64) PRIMARY KEY,
    conversation_id VARCHAR(64) NOT NULL REFERENCES conversations(id),
    knowledge_version_id VARCHAR(64) NOT NULL REFERENCES knowledge_versions(id),
    current_step INT NOT NULL DEFAULT 0,
    status VARCHAR(16) NOT NULL CHECK (status IN ('active', 'paused', 'complete', 'abandoned')),
    abandon_reason VARCHAR(512) NULL,
    updated_at TIMESTAMP_NTZ NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    created_at TIMESTAMP_NTZ NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

-- 11. Escalations: Human-in-the-loop escalation records for low-confidence Copilot responses.
CREATE TABLE IF NOT EXISTS escalations (
    id VARCHAR(64) PRIMARY KEY,
    conversation_message_id VARCHAR(64) NOT NULL REFERENCES conversation_messages(id),
    reason VARCHAR(255) NOT NULL,
    status VARCHAR(16) NOT NULL CHECK (status IN ('open', 'notified', 'resolved')),
    notified_at TIMESTAMP_NTZ NULL,
    resolution_note TEXT NULL,
    external_ticket_ref VARCHAR(255) NULL,
    created_at TIMESTAMP_NTZ NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    resolved_at TIMESTAMP_NTZ NULL,
    updated_at TIMESTAMP_NTZ NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

-- 12. Analytics Events: Raw telemetry stream for Intelligence Hub BI views.
CREATE TABLE IF NOT EXISTS analytics_events (
    id VARCHAR(64) PRIMARY KEY,
    event_type VARCHAR(128) NOT NULL,
    conversation_message_id VARCHAR(64) NULL REFERENCES conversation_messages(id),
    knowledge_version_id VARCHAR(64) NULL REFERENCES knowledge_versions(id),
    payload VARIANT NULL,
    created_at TIMESTAMP_NTZ NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

-- 13. Audit Log: Compliance record of state-changing operations across the platform.
CREATE TABLE IF NOT EXISTS audit_logs (
    id VARCHAR(64) PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    action VARCHAR(255) NOT NULL,
    resource VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    created_at TIMESTAMP_NTZ NOT NULL DEFAULT CURRENT_TIMESTAMP()
);

-- ============================================================================
-- Indexes & Clustering Keys
-- ============================================================================

-- Fast lookup for Copilot search queries restricted strictly to published document versions
ALTER TABLE knowledge_versions CLUSTER BY (status);

-- Time-windowed BI analytics queries filtering by event type and timeframe
ALTER TABLE analytics_events CLUSTER BY (event_type, created_at);
