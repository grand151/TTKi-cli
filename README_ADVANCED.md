# TTKi Advanced AI Terminal Application

**Aplikacja terminala AI w stylu Bolt z zaawansowanymi funkcjami uczenia maszynowego**

[![System Status](https://img.shields.io/badge/Status-Production%20Ready-green)](.)
[![Architecture](https://img.shields.io/badge/Architecture-DDD%2BFastAPI-blue)](.)
[![Database](https://img.shields.io/badge/Database-PostgreSQL%2017%2Bpgvector-blue)](.)
[![AI Features](https://img.shields.io/badge/AI-Cross%20Agent%20Learning-orange)](.)

## 🚀 Przegląd Systemu

TTKi to zaawansowana aplikacja terminala AI zbudowana w oparciu o architekturę Domain-Driven Design (DDD) z funkcjami **cross-agent learning**, **shared memory**, **advanced analytics** i **self-improving system** przez feedback loops.

### ✨ Kluczowe Funkcje

- 🤖 **Cross-Agent Learning** - Agenci uczą się od siebie nawzajem
- 🧠 **Shared Memory System** - Wspólna pamięć dla komunikacji między agentami
- 📊 **Advanced Analytics** - Zaawansowane analizy wydajności i optymalizacji
- 🔄 **Self-Improving System** - System samodoskonalący się przez feedback loops
- 🏗️ **DDD Architecture** - Czysta architektura Enterprise z FastAPI
- 🔍 **Vector Search** - Wyszukiwanie podobieństw z pgvector
- 📈 **Real-time Dashboard** - Dashboard w czasie rzeczywistym
- 🐘 **PostgreSQL 17** - Zaawansowana baza danych z rozszerzeniami AI

## 🏗️ Architektura Systemu

```
TTKi Advanced AI System
├── 🎯 Application Layer (Orchestration)
│   ├── TTKi Application Service
│   ├── System Dashboard Service
│   └── Cross-Agent Learning Coordinator
├── 🏛️ Domain Layer (Business Logic)
│   ├── Entities (Agent, Task, Learning Event)
│   ├── Value Objects (Task Result, Learning Score)
│   └── Domain Services (Orchestration, Analytics)
├── 🔧 Infrastructure Layer
│   ├── Database (PostgreSQL 17 + pgvector)
│   ├── Repositories (Agent, Task, Learning, Memory, Analytics)
│   ├── Hybrid Bridge (Legacy Integration)
│   └── Agent Registry
└── 🌐 Presentation Layer
    ├── FastAPI REST API
    ├── Real-time Dashboard
    └── WebSocket Connections
```

## 🗄️ Schema Bazy Danych

### Główne Tabele

1. **agents** - Rejestry agentów z capabilities i metadata
2. **tasks** - Historia zadań z wynikami i metrykami
3. **learning_events** - Wydarzenia uczenia z vector embeddings
4. **shared_memory** - Wspólna pamięć z kluczami i typami
5. **task_analytics** - Analityka wydajności zadań
6. **cross_agent_insights** - Insights między agentami
7. **system_optimization** - Rekomendacje optymalizacji

### Zaawansowane Funkcje

- **Vector Embeddings** dla similarity search
- **JSONB** dla flexible metadata
- **Temporal Data** dla historical analysis
- **Indexing Strategy** dla high performance

## 🚀 Szybki Start

### 1. Uruchom System

```bash
# Uruchom cały system (baza danych + aplikacja)
./start_system.sh
```

### 2. Sprawdź Status

```bash
# Sprawdź status systemu
cat system_status_report.txt

# Monitoruj logi
tail -f app.log
```

### 3. Testuj API

```bash
# Health check
curl http://localhost:8000/health

# Dashboard
curl http://localhost:8000/dashboard

# Wykonaj zadanie
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"description": "Analyze data", "agent_type": "analysis_agent"}'
```

### 4. Zatrzymaj System

```bash
# Graceful shutdown
./stop_system.sh

# Z czyszczeniem logów
./stop_system.sh --clean-logs
```

## 🧪 Testowanie Systemu

### Comprehensive Integration Test

```bash
# Uruchom pełny test integracyjny
python3 test_system_integration.py
```

Test sprawdza:
- ✅ Database connectivity
- ✅ Repository operations (CRUD)
- ✅ Cross-agent learning
- ✅ System dashboard
- ✅ Application service

### Unit Tests

```bash
# Uruchom testy jednostkowe
python3 -m pytest test_scenarios_simple.py -v
```

## 📊 Monitoring i Analytics

### Real-time Dashboard

Dostęp do dashboardu: `http://localhost:8000/dashboard`

Funkcje dashboardu:
- 📈 System health metrics
- 🤖 Agent performance comparison
- 🧠 Learning insights i trends
- 💾 Memory usage statistics
- 🔧 Optimization recommendations

### Database Analytics

```bash
# Połącz się z bazą danych
docker exec -it ttki_postgres psql -U ttki_user -d ttki_advanced_db

# Przykładowe zapytania
SELECT COUNT(*) FROM learning_events;
SELECT agent_type, COUNT(*) FROM tasks GROUP BY agent_type;
SELECT * FROM system_optimization ORDER BY created_at DESC LIMIT 5;
```

## 🤖 Cross-Agent Learning

### Jak Działa

1. **Learning Events** - Agenci zapisują swoje doświadczenia
2. **Vector Embeddings** - Konwersja doświadczeń na embeddings
3. **Similarity Search** - Znajdowanie podobnych zadań
4. **Knowledge Sharing** - Dzielenie się successful patterns
5. **Adaptive Improvement** - Ciągłe doskonalenie

### Przykład Usage

```python
# Agent zapisuje learning event
await learning_repo.record_learning_event(
    agent_id="file_agent_001",
    event_type="file_processing",
    input_data={"file_type": "csv", "size": "large"},
    output_data={"processed_rows": 10000, "time": 5.2},
    feedback_score=0.95
)

# Znajdź podobne zadania
similar_tasks = await learning_repo.find_similar_tasks(
    "process large CSV file", limit=5, threshold=0.7
)

# Pobierz insights od innych agentów
insights = await application_service.get_cross_agent_insights(
    "data processing task"
)
```

## 🧠 Shared Memory System

### Memory Banks

- **global_patterns** - Globalne wzorce sukcesu
- **successful_patterns** - Udane strategie
- **cross_agent_learning** - Współdzielone uczenie
- **optimization_cache** - Cache optymalizacji

### API Usage

```python
# Zapisz w shared memory
await memory_repo.store_memory(
    bank_name="successful_patterns",
    entry_key="csv_processing_pattern",
    entry_type="success_pattern",
    content={
        "strategy": "chunk_processing",
        "optimal_chunk_size": 1000,
        "success_rate": 0.98
    }
)

# Pobierz z shared memory
pattern = await memory_repo.retrieve_memory(
    "successful_patterns", 
    "csv_processing_pattern"
)
```

## 📈 Self-Improving System

### Feedback Loops

1. **Task Execution** → Analytics Recording
2. **Performance Analysis** → Optimization Recommendations
3. **Pattern Recognition** → Agent Strategy Updates
4. **Cross-Agent Learning** → Knowledge Distribution
5. **Continuous Monitoring** → System Adaptation

### Optimization Features

- **Automatic Agent Selection** - Na podstawie historical performance
- **Dynamic Resource Allocation** - Intelligent load balancing
- **Predictive Analytics** - Przewidywanie execution time
- **Adaptive Strategies** - Automatically improving approaches

## 🔧 Konfiguracja i Deployment

### Environment Variables

```bash
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ttki_advanced_db
POSTGRES_USER=ttki_user
POSTGRES_PASSWORD=ttki_secure_2024

# Application Configuration
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
LOG_LEVEL=INFO
```

### Docker Deployment

```bash
# Build system image
docker build -t ttki-advanced-ai .

# Run with docker-compose
docker-compose up -d
```

### Production Setup

1. **Load Balancer** - Nginx/HAProxy
2. **Database Clustering** - PostgreSQL HA
3. **Monitoring** - Prometheus + Grafana
4. **Logging** - ELK Stack
5. **Security** - SSL/TLS + Authentication

## 📚 API Reference

### Core Endpoints

```http
GET    /health                 # System health check
GET    /dashboard              # Real-time dashboard
POST   /tasks                  # Execute task
GET    /tasks/{task_id}        # Get task status
GET    /agents                 # List agents
GET    /analytics              # System analytics
GET    /insights               # Cross-agent insights
```

### Dashboard Endpoints

```http
GET    /dashboard/metrics      # Performance metrics
GET    /dashboard/agents       # Agent performance
GET    /dashboard/learning     # Learning insights
GET    /dashboard/memory       # Memory status
GET    /dashboard/export       # Export data
```

### Learning Endpoints

```http
POST   /learning/events        # Record learning event
GET    /learning/similar       # Find similar tasks
GET    /learning/insights      # Get insights
POST   /learning/feedback      # Provide feedback
```

## 🔒 Security Features

- **Input Validation** - Comprehensive data validation
- **SQL Injection Protection** - Parameterized queries
- **Authentication** - JWT token-based auth
- **Authorization** - Role-based access control
- **Audit Logging** - Comprehensive audit trail
- **Data Encryption** - At-rest and in-transit

## 🛠️ Development

### Setup Development Environment

```bash
# Clone repository
git clone <repository-url>
cd ttki-advanced-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start development server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Code Structure

```
src/
├── application/           # Application services
├── domain/               # Domain entities and services  
├── infrastructure/       # Infrastructure layer
│   ├── database/        # Database and repositories
│   ├── hybrid_bridge/   # Legacy integration
│   └── agent_registry/  # Agent management
└── presentation/        # FastAPI endpoints
```

### Adding New Features

1. **Domain First** - Define entities and value objects
2. **Repository Pattern** - Implement data access
3. **Application Service** - Orchestrate business logic
4. **API Endpoints** - Expose functionality
5. **Tests** - Comprehensive test coverage

## 📋 Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check container status
docker ps | grep ttki_postgres

# Check logs
docker logs ttki_postgres

# Restart container
docker restart ttki_postgres
```

#### Import Errors
```bash
# Check Python path
echo $PYTHONPATH

# Install missing packages
pip install -r requirements.txt

# Check virtual environment
which python3
```

#### Performance Issues
```bash
# Check system resources
docker stats ttki_postgres

# Analyze database performance
docker exec -it ttki_postgres psql -U ttki_user -d ttki_advanced_db -c "
SELECT query, calls, total_time, total_time/calls as avg_time 
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;
"
```

### Support

- 📧 **Email**: support@ttki.ai
- 💬 **Discord**: TTKi Community
- 📖 **Docs**: https://docs.ttki.ai
- 🐛 **Issues**: GitHub Issues

## 🎯 Roadmap

### Version 2.0
- [ ] Multi-model AI integration (GPT, Claude, Gemini)
- [ ] Advanced workflow automation
- [ ] Natural language task description
- [ ] Visual workflow designer

### Version 2.5
- [ ] Kubernetes deployment
- [ ] Multi-tenant architecture
- [ ] Advanced security features
- [ ] Real-time collaboration

### Version 3.0
- [ ] AI-generated code execution
- [ ] Autonomous agent creation
- [ ] Cross-platform desktop app
- [ ] Enterprise features

## 📜 License

MIT License - Zobacz [LICENSE](LICENSE) dla szczegółów.

## 🤝 Contributing

Contributions are welcome! Zobacz [CONTRIBUTING.md](CONTRIBUTING.md) dla guidelines.

---

**TTKi Advanced AI System** - Zbudowane z ❤️ dla przyszłości AI automation.

*🚀 "Where AI Agents Learn, Share, and Evolve Together"*
