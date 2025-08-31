# Database Architecture Analysis for TTKi System

## Current Data Storage Requirements

### 1. **Agent State & Memory**
- `AgentState`: cursor_position, active_context, session_start, vision_enabled
- `ActionHistory`: timestamp, action_type, parameters, result, success, context_before/after
- `Memory`: key-value pairs dla patterns, context, successful actions
- **Current limitation**: In-memory only, lost on restart

### 2. **Vision System Data**
- `InteractiveElement`: type, coordinates, confidence, context_relevance
- Screenshot analysis results: elements_detected, recommended_actions
- Vision AI caching: reuse element detection między akcjami
- **Current limitation**: No persistence, re-analysis needed

### 3. **Performance Metrics**
- Vision processing times, action success rates
- Health checks: container connectivity, API availability
- Cursor movement efficiency, targeting accuracy
- **Current limitation**: No structured storage

## Database Options Analysis

### 🏆 **RECOMMENDATION: PostgreSQL + pgvector**

#### **Dlaczego PostgreSQL + pgvector jest optymalne:**

✅ **Vector Storage dla RAG**
- Native vector search z pgvector extension
- Efficient similarity search dla patterns i context
- Embedding storage dla vision analysis results

✅ **JSON Support**
- Native JSONB dla complex data structures (ActionHistory, InteractiveElement)
- Indexing na JSON fields dla fast queries
- Schema flexibility dla evolving data structures

✅ **ACID Compliance**
- Reliable persistence dla agent state
- Transaction safety dla critical operations
- Data integrity dla action history

✅ **Performance**
- Excellent query performance z proper indexing
- Connection pooling dla container architecture
- Efficient storage dla time-series data (metrics)

✅ **RAG-Ready Architecture**
- Vector similarity search dla context retrieval
- Hybrid search (traditional + vector)
- Scalable dla future microagent RAG modules

#### **Alternative Options Considered:**

🔸 **Redis + PostgreSQL Hybrid**
- Redis: Fast cache dla cursor position, recent actions
- PostgreSQL: Persistent storage dla history, patterns
- **Pros**: Ultra-fast access, good persistence
- **Cons**: Complexity, synchronization challenges

🔸 **Chroma/Pinecone + SQLite**
- Vector DB dla embeddings, SQLite dla structured data
- **Pros**: Specialized vector performance
- **Cons**: Multiple systems, container complexity

🔸 **SingleStore/MemSQL**
- Native vector + SQL in one system
- **Pros**: High performance, unified
- **Cons**: Licensing costs, overkill dla current scale

## Proposed Database Schema

### **Core Tables:**

```sql
-- Agent Sessions
CREATE TABLE agent_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    cursor_position JSONB,
    active_context VARCHAR(20),
    vision_enabled BOOLEAN DEFAULT TRUE
);

-- Action History
CREATE TABLE action_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES agent_sessions(id),
    timestamp TIMESTAMP DEFAULT NOW(),
    action_type VARCHAR(20),
    action_name TEXT,
    parameters JSONB,
    result JSONB,
    success BOOLEAN,
    context_before JSONB,
    context_after JSONB,
    processing_time_ms INTEGER
);

-- Agent Memory
CREATE TABLE agent_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES agent_sessions(id),
    key VARCHAR(255),
    value JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(session_id, key)
);

-- Vision Analysis Cache
CREATE TABLE vision_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    screenshot_hash VARCHAR(64),
    task_context TEXT,
    elements_detected JSONB,
    recommended_actions JSONB,
    analysis_metadata JSONB,
    processing_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Vector Embeddings (dla RAG)
CREATE TABLE embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_type VARCHAR(50), -- 'action_pattern', 'context', 'vision_result'
    content_id UUID,
    embedding vector(1536), -- OpenAI embedding dimension
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Performance Metrics
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES agent_sessions(id),
    metric_type VARCHAR(50),
    metric_name VARCHAR(100),
    value NUMERIC,
    metadata JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

### **Indexes dla Performance:**

```sql
-- Fast session lookup
CREATE INDEX idx_sessions_started ON agent_sessions(started_at DESC);

-- Action history queries
CREATE INDEX idx_actions_session_time ON action_history(session_id, timestamp DESC);
CREATE INDEX idx_actions_type ON action_history(action_type);
CREATE INDEX idx_actions_success ON action_history(success);

-- Memory lookup
CREATE INDEX idx_memory_session_key ON agent_memory(session_id, key);

-- Vision cache
CREATE INDEX idx_vision_hash ON vision_analysis(screenshot_hash);
CREATE INDEX idx_vision_context ON vision_analysis USING gin(to_tsvector('english', task_context));

-- Vector similarity search
CREATE INDEX idx_embeddings_vector ON embeddings USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_embeddings_type ON embeddings(content_type);

-- Metrics queries
CREATE INDEX idx_metrics_session_time ON performance_metrics(session_id, timestamp DESC);
CREATE INDEX idx_metrics_type ON performance_metrics(metric_type, metric_name);
```

## Implementation Strategy

### **Phase 1: Basic Persistence (Current Sprint)**
- Replace in-memory storage z PostgreSQL
- Migrate AgentState, ActionHistory, Memory
- Add database connection handling

### **Phase 2: Performance Optimization**
- Implement vision analysis caching
- Add performance metrics collection
- Optimize queries z proper indexing

### **Phase 3: RAG Preparation**
- Install pgvector extension
- Create embeddings infrastructure
- Implement similarity search functions

### **Phase 4: Advanced Features**
- Pattern recognition from action history
- Predictive context suggestions
- Automated performance analysis

## Container Integration

### **Docker Compose Addition:**
```yaml
services:
  ttki-postgres:
    image: pgvector/pgvector:pg16
    container_name: ttki-postgres
    environment:
      - POSTGRES_DB=ttki
      - POSTGRES_USER=ttki_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - ttki-db-data:/var/lib/postgresql/data
      - ./db/init:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    networks:
      - ttki-network
    restart: unless-stopped

volumes:
  ttki-db-data:
```

## Benefits dla TTKi System

### **Immediate Benefits:**
- ✅ Persistent agent memory across restarts
- ✅ Action history dla debugging i optimization
- ✅ Vision analysis caching → faster responses
- ✅ Performance monitoring i metrics

### **Future RAG Benefits:**
- 🚀 Context-aware suggestions z historical patterns
- 🚀 Intelligent action prediction
- 🚀 Automated knowledge base building
- 🚀 Cross-session learning i improvement

### **Operational Benefits:**
- 📊 Detailed analytics i performance tracking
- 🔍 Advanced debugging capabilities
- 🎯 Pattern recognition dla UI automation
- ⚡ Reduced redundant processing through caching

**PostgreSQL + pgvector provides the perfect foundation dla current needs while being fully prepared dla future RAG microagent integration.**
