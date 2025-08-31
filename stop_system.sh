#!/bin/bash

# TTKi Advanced AI System - Stop Script
# Gracefully shuts down all system components

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
POSTGRES_CONTAINER_NAME="ttki-postgres"  # Using existing container

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

echo "🛑 Stopping TTKi Advanced AI System..."
echo "====================================="

# Stop FastAPI server
stop_server() {
    print_status "Stopping FastAPI server..."
    
    if [ -f "ttki_server.pid" ]; then
        PID=$(cat ttki_server.pid)
        if kill -0 $PID 2>/dev/null; then
            print_status "Terminating server process (PID: $PID)..."
            kill $PID
            
            # Wait for graceful shutdown
            sleep 3
            
            # Force kill if still running
            if kill -0 $PID 2>/dev/null; then
                print_warning "Forcing server termination..."
                kill -9 $PID
            fi
            
            print_success "Server stopped successfully"
        else
            print_warning "Server process not running"
        fi
        
        rm -f ttki_server.pid
    else
        print_warning "Server PID file not found"
    fi
}

# Stop PostgreSQL container (optional)
stop_postgres() {
    print_status "Checking PostgreSQL container..."
    
    if docker ps -q -f name=${POSTGRES_CONTAINER_NAME} | grep -q .; then
        echo -n "Stop PostgreSQL container? [y/N]: "
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            print_status "Stopping PostgreSQL container..."
            docker stop ${POSTGRES_CONTAINER_NAME}
            print_success "PostgreSQL container stopped"
        else
            print_status "Keeping PostgreSQL container running"
        fi
    else
        print_status "PostgreSQL container is not running"
    fi
}

# Clean up temporary files
cleanup() {
    print_status "Cleaning up temporary files..."
    
    # Remove PID files
    rm -f ttki_server.pid
    
    # Clean up log files if requested
    if [ "$1" = "--clean-logs" ]; then
        print_status "Removing log files..."
        rm -f app.log
        rm -f system_status_report.txt
        print_success "Log files removed"
    fi
    
    print_success "Cleanup completed"
}

# Generate shutdown report
generate_shutdown_report() {
    print_status "Generating shutdown report..."
    
    cat > shutdown_report.txt << EOF
TTKi Advanced AI System - Shutdown Report
Generated: $(date)
=======================================

SYSTEM STATUS BEFORE SHUTDOWN:
- Server PID: $(cat ttki_server.pid 2>/dev/null || echo "Not found")
- PostgreSQL Container: $(docker ps --format "table {{.Names}}\t{{.Status}}" | grep ${POSTGRES_CONTAINER_NAME} || echo "Not running")

SHUTDOWN ACTIONS:
- FastAPI server: Stopped
- Temporary files: Cleaned
- PostgreSQL: $(if docker ps -q -f name=${POSTGRES_CONTAINER_NAME} | grep -q .; then echo "Kept running"; else echo "Stopped"; fi)

PRESERVED DATA:
✅ Database data (in PostgreSQL container)
✅ Source code and configuration
✅ Virtual environment
$(if [ "$1" != "--clean-logs" ]; then echo "✅ Log files"; else echo "❌ Log files (removed)"; fi)

TO RESTART SYSTEM:
./start_system.sh

DIRECT ACCESS:
- Database: docker exec -it ${POSTGRES_CONTAINER_NAME} psql -U ttki_user -d ttki_advanced_db
- Container logs: docker logs ${POSTGRES_CONTAINER_NAME}

EOF

    print_success "Shutdown report saved to: shutdown_report.txt"
}

# Main execution
main() {
    echo
    print_status "TTKi Advanced AI System Shutdown"
    print_status "Shutdown started at: $(date)"
    echo

    # Execute shutdown sequence
    stop_server
    cleanup "$1"
    stop_postgres
    generate_shutdown_report "$1"
    
    echo
    print_success "🏁 TTKi Advanced AI System shutdown completed!"
    echo
    print_status "System Status:"
    echo "  🛑 FastAPI server: Stopped"
    echo "  🐘 PostgreSQL: $(if docker ps -q -f name=${POSTGRES_CONTAINER_NAME} | grep -q .; then echo "Running (data preserved)"; else echo "Stopped"; fi)"
    echo "  💾 Data: Preserved"
    echo "  📄 Logs: $(if [ "$1" = "--clean-logs" ]; then echo "Removed"; else echo "Preserved"; fi)"
    echo
    print_status "To restart: ./start_system.sh"
    print_status "Shutdown report: cat shutdown_report.txt"
    echo
}

# Show usage if help requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  --clean-logs    Remove log files during shutdown"
    echo "  --help, -h      Show this help message"
    echo
    echo "Examples:"
    echo "  $0                 # Normal shutdown (preserve logs)"
    echo "  $0 --clean-logs   # Shutdown and remove logs"
    exit 0
fi

# Execute main function
main "$@"
