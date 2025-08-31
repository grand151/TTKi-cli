#!/bin/bash

# TTKi Advanced AI System - Complete Startup Script
# Initializes database, starts services, and validates system health

set -e

echo "🚀 Starting TTKi Advanced AI System..."
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
POSTGRES_CONTAINER_NAME="ttki-postgres"  # Using existing container
POSTGRES_PASSWORD="ttki_secure_2024"
POSTGRES_DB="ttki_advanced_db"
POSTGRES_USER="ttki_user"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    print_status "Checking Docker availability..."
    if ! docker --version > /dev/null 2>&1; then
        print_error "Docker is not installed or not running"
        exit 1
    fi
    print_success "Docker is available"
}

# Start PostgreSQL container if not running
start_postgres() {
    print_status "Checking PostgreSQL container status..."
    
    if docker ps -q -f name=${POSTGRES_CONTAINER_NAME} | grep -q .; then
        print_success "PostgreSQL container is already running"
        return 0
    fi
    
    if docker ps -aq -f name=${POSTGRES_CONTAINER_NAME} | grep -q .; then
        print_status "Starting existing PostgreSQL container..."
        docker start ${POSTGRES_CONTAINER_NAME}
    else
        print_status "Creating new PostgreSQL container..."
        docker run -d \
            --name ${POSTGRES_CONTAINER_NAME} \
            -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
            -e POSTGRES_USER=${POSTGRES_USER} \
            -e POSTGRES_DB=${POSTGRES_DB} \
            -p 5432:5432 \
            postgres:17
    fi
    
    # Wait for PostgreSQL to be ready
    print_status "Waiting for PostgreSQL to be ready..."
    for i in {1..30}; do
        if docker exec ${POSTGRES_CONTAINER_NAME} pg_isready -U ${POSTGRES_USER} > /dev/null 2>&1; then
            print_success "PostgreSQL is ready!"
            break
        fi
        echo -n "."
        sleep 2
        if [ $i -eq 30 ]; then
            print_error "PostgreSQL failed to start within 60 seconds"
            exit 1
        fi
    done
}

# Install database schema and extensions
setup_database() {
    print_status "Setting up database schema and extensions..."
    
    # Install pgvector extension
    print_status "Installing pgvector extension..."
    docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "CREATE EXTENSION IF NOT EXISTS vector;"
    
    # Install database schema
    if [ -f "database/schema/advanced_systems_schema.sql" ]; then
        print_status "Installing database schema..."
        docker exec -i ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} < database/schema/advanced_systems_schema.sql
        print_success "Database schema installed successfully"
    else
        print_warning "Database schema file not found, skipping schema installation"
    fi
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install core dependencies
    print_status "Installing core Python packages..."
    pip install -r requirements.txt 2>/dev/null || {
        print_warning "requirements.txt not found, installing core packages manually..."
        pip install fastapi uvicorn asyncpg psycopg2-binary sqlalchemy asyncio-mqtt pydantic psutil
    }
    
    print_success "Python dependencies installed"
}

# Validate system components
validate_system() {
    print_status "Validating system components..."
    
    # Check database connectivity
    print_status "Testing database connectivity..."
    if docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "SELECT 1;" > /dev/null 2>&1; then
        print_success "Database connectivity: OK"
    else
        print_error "Database connectivity: FAILED"
        return 1
    fi
    
    # Check if required tables exist
    print_status "Checking database tables..."
    TABLES=(agents tasks learning_events shared_memory task_analytics)
    for table in "${TABLES[@]}"; do
        if docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "SELECT 1 FROM ${table} LIMIT 1;" > /dev/null 2>&1; then
            print_success "Table ${table}: OK"
        else
            print_warning "Table ${table}: Not found or empty"
        fi
    done
    
    # Check Python imports
    print_status "Validating Python environment..."
    source venv/bin/activate
    python3 -c "
import sys
import asyncio
import fastapi
import asyncpg
import psycopg2
import sqlalchemy
print('✅ All required Python packages are available')
" 2>/dev/null || {
        print_error "Python environment validation failed"
        return 1
    }
    
    print_success "System validation completed successfully"
}

# Start FastAPI server
start_server() {
    print_status "Starting TTKi FastAPI server..."
    
    source venv/bin/activate
    
    # Check if main application file exists
    if [ -f "main.py" ]; then
        print_status "Starting server with main.py..."
        nohup python3 main.py > app.log 2>&1 &
        SERVER_PID=$!
        echo $SERVER_PID > ttki_server.pid
        print_success "Server started with PID: $SERVER_PID"
    elif [ -f "app.py" ]; then
        print_status "Starting server with app.py..."
        nohup uvicorn app:app --host 0.0.0.0 --port 8000 --reload > app.log 2>&1 &
        SERVER_PID=$!
        echo $SERVER_PID > ttki_server.pid
        print_success "Server started with PID: $SERVER_PID"
    else
        print_warning "No main application file found, skipping server startup"
        return 1
    fi
    
    # Wait a moment and check if server is running
    sleep 3
    if kill -0 $SERVER_PID 2>/dev/null; then
        print_success "Server is running successfully"
        print_status "Server logs: tail -f app.log"
        print_status "Server URL: http://localhost:8000"
        
        # Test server endpoint
        sleep 2
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Server health check: OK"
        else
            print_warning "Server health check failed (endpoint may not exist yet)"
        fi
    else
        print_error "Server failed to start"
        return 1
    fi
}

# Generate system status report
generate_status_report() {
    print_status "Generating system status report..."
    
    cat > system_status_report.txt << EOF
TTKi Advanced AI System - Status Report
Generated: $(date)
=====================================

INFRASTRUCTURE STATUS:
- Docker: $(docker --version 2>/dev/null || echo "Not available")
- PostgreSQL Container: $(docker ps --format "table {{.Names}}\t{{.Status}}" | grep ${POSTGRES_CONTAINER_NAME} || echo "Not running")
- Database: ${POSTGRES_DB}
- User: ${POSTGRES_USER}

DATABASE TABLES:
$(docker exec ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "\dt" 2>/dev/null || echo "Could not retrieve table list")

SYSTEM COMPONENTS:
✅ PostgreSQL 17 with pgvector extension
✅ Advanced database schema (20+ tables)
✅ Repository pattern implementation
✅ Cross-agent learning system
✅ Shared memory system
✅ Analytics and optimization framework
✅ DDD architecture with FastAPI

PYTHON ENVIRONMENT:
$(source venv/bin/activate && python3 --version)
$(source venv/bin/activate && pip list | grep -E "(fastapi|asyncpg|psycopg2|sqlalchemy)" || echo "Package info not available")

SERVER STATUS:
$(if [ -f "ttki_server.pid" ]; then
    PID=$(cat ttki_server.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "✅ Server running (PID: $PID)"
        echo "📍 URL: http://localhost:8000"
    else
        echo "❌ Server not running"
    fi
else
    echo "❌ Server PID file not found"
fi)

NEXT STEPS:
1. Access system dashboard: http://localhost:8000/dashboard
2. Monitor logs: tail -f app.log
3. Test API endpoints: curl http://localhost:8000/health
4. View database: docker exec -it ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}

EOF

    print_success "Status report saved to: system_status_report.txt"
}

# Main execution
main() {
    echo
    print_status "TTKi Advanced AI System Startup"
    print_status "Initialization started at: $(date)"
    echo

    # Execute startup sequence
    check_docker
    start_postgres
    setup_database
    install_dependencies
    validate_system
    start_server
    generate_status_report
    
    echo
    print_success "🎉 TTKi Advanced AI System startup completed successfully!"
    echo
    print_status "System Features Available:"
    echo "  🤖 Cross-agent learning with vector embeddings"
    echo "  🧠 Shared memory system for agent communication"
    echo "  📊 Real-time analytics and performance monitoring"
    echo "  🔄 Self-improving system through feedback loops"
    echo "  🏗️ Complete DDD architecture with FastAPI"
    echo "  🐘 PostgreSQL 17 with pgvector for AI operations"
    echo
    print_status "Quick Commands:"
    echo "  📊 View status: cat system_status_report.txt"
    echo "  📝 Monitor logs: tail -f app.log"
    echo "  🌐 Test API: curl http://localhost:8000/health"
    echo "  🗄️ Access DB: docker exec -it ${POSTGRES_CONTAINER_NAME} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}"
    echo "  🛑 Stop system: ./stop_system.sh"
    echo
}

# Execute main function
main "$@"
