-- =============================================================================
-- TTKi Advanced Systems Database Schema
-- PostgreSQL 17 + pgvector for Cross-Agent Learning & Analytics
-- =============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- =============================================================================
-- CORE SYSTEM TABLES
-- =============================================================================

-- System Configuration
CREATE TABLE system_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    config_type VARCHAR(20) DEFAULT 'string', -- string, json, number, boolean
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- AGENT MANAGEMENT TABLES
-- =============================================================================

-- Agent Registry
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(100) UNIQUE NOT NULL,
    agent_type VARCHAR(50) NOT NULL, -- desktop, vision, coding, etc.
    agent_name VARCHAR(100) NOT NULL,
    capabilities TEXT[], -- array of capabilities
    status VARCHAR(20) DEFAULT 'active', -- active, inactive, learning, upgrading
    version VARCHAR(20) DEFAULT '1.0.0',
    architecture_type VARCHAR(50) DEFAULT 'hybrid', -- hybrid, legacy, ddd
    performance_score DECIMAL(5,2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent Performance Metrics
CREATE TABLE agent_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    metric_type VARCHAR(50) NOT NULL, -- execution_time, success_rate, resource_usage
    metric_value DECIMAL(10,4) NOT NULL,
    measurement_unit VARCHAR(20), -- ms, percentage, mb, etc.
    context JSONB, -- additional context data
    measured_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent Relationships (for collaboration patterns)
CREATE TABLE agent_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    primary_agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    secondary_agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL, -- collaboration, delegation, learning_from
    strength DECIMAL(3,2) DEFAULT 0.0, -- 0.0 to 1.0
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_interaction TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(primary_agent_id, secondary_agent_id, relationship_type)
);

-- =============================================================================
-- TASK MANAGEMENT & EXECUTION
-- =============================================================================

-- Tasks
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id VARCHAR(100) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    priority INTEGER DEFAULT 5, -- 1 (highest) to 10 (lowest)
    status VARCHAR(20) DEFAULT 'pending', -- pending, running, completed, failed, cancelled
    assigned_agent_id UUID REFERENCES agents(id),
    parent_task_id UUID REFERENCES tasks(id),
    parameters JSONB,
    result JSONB,
    error_message TEXT,
    estimated_duration INTEGER, -- in seconds
    actual_duration INTEGER, -- in seconds
    complexity_score DECIMAL(3,2), -- 0.0 to 1.0
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Task Dependencies
CREATE TABLE task_dependencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    depends_on_task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    dependency_type VARCHAR(30) DEFAULT 'sequential', -- sequential, parallel, conditional
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(task_id, depends_on_task_id)
);

-- Task Execution Steps
CREATE TABLE task_execution_steps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES tasks(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    step_description TEXT NOT NULL,
    step_type VARCHAR(50) NOT NULL,
    agent_id UUID REFERENCES agents(id),
    status VARCHAR(20) DEFAULT 'pending',
    input_data JSONB,
    output_data JSONB,
    execution_time INTEGER, -- in milliseconds
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(task_id, step_number)
);

-- =============================================================================
-- CROSS-AGENT LEARNING SYSTEM
-- =============================================================================

-- Learning Events
CREATE TABLE learning_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(50) NOT NULL, -- success_pattern, failure_analysis, optimization
    source_agent_id UUID REFERENCES agents(id),
    target_agent_id UUID REFERENCES agents(id), -- who learned from this
    task_id UUID REFERENCES tasks(id),
    context JSONB NOT NULL, -- detailed context of the learning event
    learning_data JSONB NOT NULL, -- the actual learning content
    confidence_score DECIMAL(3,2) DEFAULT 0.0, -- how confident we are in this learning
    impact_score DECIMAL(3,2) DEFAULT 0.0, -- how much this improved performance
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    applied_at TIMESTAMP WITH TIME ZONE
);

-- Knowledge Base (vector embeddings for semantic search)
CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    knowledge_type VARCHAR(50) NOT NULL, -- pattern, solution, best_practice, failure_case
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536), -- OpenAI embedding dimensions
    source_agent_id UUID REFERENCES agents(id),
    related_task_ids UUID[],
    tags TEXT[],
    confidence_score DECIMAL(3,2) DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    effectiveness_score DECIMAL(3,2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Agent Learning Progress
CREATE TABLE agent_learning_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    learning_domain VARCHAR(100) NOT NULL, -- e.g., "desktop_operations", "error_handling"
    skill_level DECIMAL(3,2) DEFAULT 0.0, -- 0.0 to 1.0
    learning_events_count INTEGER DEFAULT 0,
    last_improvement_date TIMESTAMP WITH TIME ZONE,
    learning_velocity DECIMAL(5,4) DEFAULT 0.0, -- improvement rate
    plateau_indicator BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(agent_id, learning_domain)
);

-- =============================================================================
-- SHARED MEMORY SYSTEM
-- =============================================================================

-- Shared Memory Banks
CREATE TABLE memory_banks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bank_name VARCHAR(100) UNIQUE NOT NULL,
    bank_type VARCHAR(50) NOT NULL, -- global, agent_group, temporary, persistent
    access_level VARCHAR(20) DEFAULT 'public', -- public, private, restricted
    retention_policy VARCHAR(50) DEFAULT 'permanent', -- permanent, time_based, usage_based
    max_size_mb INTEGER DEFAULT 1024,
    current_size_mb DECIMAL(10,2) DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Memory Entries
CREATE TABLE memory_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    memory_bank_id UUID REFERENCES memory_banks(id) ON DELETE CASCADE,
    entry_key VARCHAR(200) NOT NULL,
    entry_type VARCHAR(50) NOT NULL, -- experience, pattern, solution, cache
    content JSONB NOT NULL,
    embedding vector(1536), -- for semantic similarity search
    created_by_agent_id UUID REFERENCES agents(id),
    access_count INTEGER DEFAULT 0,
    relevance_score DECIMAL(3,2) DEFAULT 0.0,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(memory_bank_id, entry_key)
);

-- Memory Access Log
CREATE TABLE memory_access_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    memory_entry_id UUID REFERENCES memory_entries(id) ON DELETE CASCADE,
    accessing_agent_id UUID REFERENCES agents(id),
    access_type VARCHAR(20) NOT NULL, -- read, write, update, delete
    context JSONB,
    access_duration INTEGER, -- in milliseconds
    accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- ADVANCED ANALYTICS TABLES
-- =============================================================================

-- System Performance Analytics
CREATE TABLE system_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_category VARCHAR(50) NOT NULL, -- performance, resource_usage, error_rates
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,4) NOT NULL,
    measurement_unit VARCHAR(20),
    time_window VARCHAR(20), -- minute, hour, day, week
    aggregation_type VARCHAR(20), -- avg, sum, min, max, count
    metadata JSONB,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Optimization Recommendations
CREATE TABLE optimization_recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recommendation_type VARCHAR(50) NOT NULL, -- performance, resource, learning
    target_component VARCHAR(100) NOT NULL, -- specific agent, system, memory_bank
    recommendation_text TEXT NOT NULL,
    technical_details JSONB,
    priority_level INTEGER DEFAULT 5, -- 1 (critical) to 5 (nice-to-have)
    estimated_impact DECIMAL(3,2), -- expected improvement 0.0 to 1.0
    implementation_effort VARCHAR(20), -- low, medium, high
    status VARCHAR(20) DEFAULT 'pending', -- pending, in_progress, implemented, rejected
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    implemented_at TIMESTAMP WITH TIME ZONE
);

-- Resource Usage Tracking
CREATE TABLE resource_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resource_type VARCHAR(50) NOT NULL, -- cpu, memory, disk, network, db_connections
    component_id VARCHAR(100), -- agent_id, system_component name
    component_type VARCHAR(50), -- agent, system, database
    usage_value DECIMAL(15,4) NOT NULL,
    max_capacity DECIMAL(15,4),
    usage_percentage DECIMAL(5,2),
    measurement_unit VARCHAR(20),
    measured_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- FEEDBACK LOOPS & SELF-IMPROVEMENT
-- =============================================================================

-- Feedback Events
CREATE TABLE feedback_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feedback_type VARCHAR(50) NOT NULL, -- user_feedback, performance_feedback, automated_feedback
    source_type VARCHAR(50) NOT NULL, -- user, agent, system, external
    source_id VARCHAR(100), -- identifier of the feedback source
    target_component VARCHAR(100) NOT NULL, -- what the feedback is about
    feedback_content JSONB NOT NULL,
    sentiment_score DECIMAL(3,2), -- -1.0 (negative) to 1.0 (positive)
    actionable BOOLEAN DEFAULT TRUE,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Self-Improvement Actions
CREATE TABLE improvement_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action_type VARCHAR(50) NOT NULL, -- parameter_adjustment, algorithm_update, training_data_update
    target_component VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    implementation_details JSONB,
    triggered_by_feedback_id UUID REFERENCES feedback_events(id),
    expected_improvement DECIMAL(3,2),
    actual_improvement DECIMAL(3,2),
    status VARCHAR(20) DEFAULT 'planned', -- planned, implementing, completed, reverted
    risk_level VARCHAR(20) DEFAULT 'low', -- low, medium, high
    rollback_plan JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    implemented_at TIMESTAMP WITH TIME ZONE,
    measured_at TIMESTAMP WITH TIME ZONE
);

-- System Evolution Tracking
CREATE TABLE system_evolution (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    evolution_type VARCHAR(50) NOT NULL, -- capability_addition, performance_improvement, bug_fix
    description TEXT NOT NULL,
    version_before VARCHAR(20),
    version_after VARCHAR(20),
    components_affected TEXT[],
    improvement_metrics JSONB,
    rollback_available BOOLEAN DEFAULT TRUE,
    rollback_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- SECURITY & AUDIT TABLES
-- =============================================================================

-- Security Events
CREATE TABLE security_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(50) NOT NULL, -- authentication, authorization, data_access, suspicious_activity
    severity VARCHAR(20) NOT NULL, -- low, medium, high, critical
    source_ip INET,
    user_agent TEXT,
    agent_id UUID REFERENCES agents(id),
    event_details JSONB NOT NULL,
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Audit Log
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    operation VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    record_id UUID NOT NULL,
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(100), -- agent_id or system
    change_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- INDEXES FOR PERFORMANCE
-- =============================================================================

-- Core indexes
CREATE INDEX idx_agents_type_status ON agents(agent_type, status);
CREATE INDEX idx_agents_last_activity ON agents(last_activity);
CREATE INDEX idx_tasks_status_priority ON tasks(status, priority);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
CREATE INDEX idx_tasks_assigned_agent ON tasks(assigned_agent_id);

-- Learning system indexes
CREATE INDEX idx_learning_events_source_agent ON learning_events(source_agent_id);
CREATE INDEX idx_learning_events_created_at ON learning_events(created_at);
CREATE INDEX idx_knowledge_base_type_tags ON knowledge_base(knowledge_type, tags);
CREATE INDEX idx_knowledge_base_embedding ON knowledge_base USING ivfflat (embedding vector_cosine_ops);

-- Memory system indexes
CREATE INDEX idx_memory_entries_bank_type ON memory_entries(memory_bank_id, entry_type);
CREATE INDEX idx_memory_entries_embedding ON memory_entries USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_memory_access_log_agent ON memory_access_log(accessing_agent_id);

-- Analytics indexes
CREATE INDEX idx_system_analytics_category_time ON system_analytics(metric_category, recorded_at);
CREATE INDEX idx_resource_usage_component_time ON resource_usage(component_type, measured_at);

-- Security indexes
CREATE INDEX idx_security_events_severity_time ON security_events(severity, created_at);
CREATE INDEX idx_audit_log_table_time ON audit_log(table_name, created_at);

-- =============================================================================
-- VIEWS FOR COMMON QUERIES
-- =============================================================================

-- Agent Performance Summary
CREATE VIEW agent_performance_summary AS
SELECT 
    a.id,
    a.agent_id,
    a.agent_type,
    a.performance_score,
    COUNT(t.id) as total_tasks,
    COUNT(CASE WHEN t.status = 'completed' THEN 1 END) as completed_tasks,
    AVG(t.actual_duration) as avg_execution_time,
    MAX(a.last_activity) as last_activity
FROM agents a
LEFT JOIN tasks t ON a.id = t.assigned_agent_id
WHERE a.status = 'active'
GROUP BY a.id, a.agent_id, a.agent_type, a.performance_score;

-- Learning Progress Overview
CREATE VIEW learning_progress_overview AS
SELECT 
    a.agent_id,
    a.agent_type,
    alp.learning_domain,
    alp.skill_level,
    alp.learning_velocity,
    COUNT(le.id) as learning_events_count
FROM agents a
JOIN agent_learning_progress alp ON a.id = alp.agent_id
LEFT JOIN learning_events le ON a.id = le.source_agent_id
GROUP BY a.agent_id, a.agent_type, alp.learning_domain, alp.skill_level, alp.learning_velocity;

-- System Health Dashboard
CREATE VIEW system_health_dashboard AS
SELECT 
    'agents' as component,
    COUNT(*) as total_count,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_count,
    AVG(performance_score) as avg_performance
FROM agents
UNION ALL
SELECT 
    'tasks' as component,
    COUNT(*) as total_count,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as active_count,
    AVG(CASE WHEN actual_duration > 0 THEN actual_duration ELSE NULL END) as avg_performance
FROM tasks
WHERE created_at > NOW() - INTERVAL '24 hours';

-- =============================================================================
-- FUNCTIONS FOR ADVANCED OPERATIONS
-- =============================================================================

-- Function to find similar knowledge entries
CREATE OR REPLACE FUNCTION find_similar_knowledge(
    query_embedding vector(1536),
    similarity_threshold float DEFAULT 0.8,
    limit_count integer DEFAULT 10
)
RETURNS TABLE(
    id UUID,
    title VARCHAR,
    content TEXT,
    similarity_score float
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        kb.id,
        kb.title,
        kb.content,
        1 - (kb.embedding <=> query_embedding) as similarity_score
    FROM knowledge_base kb
    WHERE 1 - (kb.embedding <=> query_embedding) > similarity_threshold
    ORDER BY similarity_score DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate agent collaboration strength
CREATE OR REPLACE FUNCTION calculate_collaboration_strength(
    agent1_id UUID,
    agent2_id UUID
)
RETURNS DECIMAL(3,2) AS $$
DECLARE
    collaboration_count INTEGER;
    success_rate DECIMAL(3,2);
    strength DECIMAL(3,2);
BEGIN
    -- Count successful collaborations in the last 30 days
    SELECT COUNT(*)
    INTO collaboration_count
    FROM tasks t1
    JOIN task_execution_steps tes1 ON t1.id = tes1.task_id
    JOIN task_execution_steps tes2 ON t1.id = tes2.task_id
    WHERE tes1.agent_id = agent1_id 
    AND tes2.agent_id = agent2_id
    AND t1.status = 'completed'
    AND t1.created_at > NOW() - INTERVAL '30 days';
    
    -- Calculate success rate
    IF collaboration_count > 0 THEN
        SELECT 
            COUNT(CASE WHEN t.status = 'completed' THEN 1 END)::DECIMAL / COUNT(*)
        INTO success_rate
        FROM tasks t
        JOIN task_execution_steps tes1 ON t.id = tes1.task_id
        JOIN task_execution_steps tes2 ON t.id = tes2.task_id
        WHERE tes1.agent_id = agent1_id 
        AND tes2.agent_id = agent2_id
        AND t.created_at > NOW() - INTERVAL '30 days';
        
        strength := LEAST(1.0, (collaboration_count::DECIMAL / 10.0) * success_rate);
    ELSE
        strength := 0.0;
    END IF;
    
    RETURN strength;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- TRIGGERS FOR AUTOMATED UPDATES
-- =============================================================================

-- Update agent last_activity when tasks are assigned
CREATE OR REPLACE FUNCTION update_agent_activity() 
RETURNS TRIGGER AS $$
BEGIN
    UPDATE agents 
    SET last_activity = NOW() 
    WHERE id = NEW.assigned_agent_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_agent_activity
    AFTER INSERT OR UPDATE ON tasks
    FOR EACH ROW
    WHEN (NEW.assigned_agent_id IS NOT NULL)
    EXECUTE FUNCTION update_agent_activity();

-- Auto-update timestamps
CREATE OR REPLACE FUNCTION update_timestamp() 
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to relevant tables
CREATE TRIGGER trigger_agents_updated_at BEFORE UPDATE ON agents FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER trigger_knowledge_base_updated_at BEFORE UPDATE ON knowledge_base FOR EACH ROW EXECUTE FUNCTION update_timestamp();
CREATE TRIGGER trigger_memory_banks_updated_at BEFORE UPDATE ON memory_banks FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- =============================================================================
-- INITIAL DATA
-- =============================================================================

-- System configuration defaults
INSERT INTO system_config (config_key, config_value, config_type, description) VALUES
('system_version', '1.0.0', 'string', 'Current system version'),
('max_concurrent_tasks', '50', 'number', 'Maximum number of concurrent tasks'),
('learning_enabled', 'true', 'boolean', 'Enable cross-agent learning'),
('analytics_retention_days', '90', 'number', 'Days to retain analytics data'),
('vector_similarity_threshold', '0.8', 'number', 'Default similarity threshold for vector searches'),
('auto_optimization_enabled', 'true', 'boolean', 'Enable automatic system optimization');

-- Create default memory banks
INSERT INTO memory_banks (bank_name, bank_type, access_level, retention_policy, max_size_mb) VALUES
('global_patterns', 'global', 'public', 'permanent', 2048),
('agent_experiences', 'global', 'public', 'time_based', 1024),
('optimization_cache', 'temporary', 'public', 'usage_based', 512),
('security_context', 'global', 'restricted', 'permanent', 256);

-- Performance optimization settings
SET work_mem = '256MB';
SET shared_buffers = '512MB';
SET effective_cache_size = '2GB';
SET random_page_cost = 1.1;

-- Enable query plan caching
SELECT pg_stat_statements_reset();

COMMENT ON DATABASE ttki_advanced IS 'TTKi Advanced Systems Database - Cross-Agent Learning, Analytics & Self-Improvement';
