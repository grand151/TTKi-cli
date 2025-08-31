#!/bin/bash

# TTKi AI Desktop Environment Startup Script
# This script starts the complete AI desktop environment using Docker

set -e

echo "🚀 TTKi AI Desktop Environment v0.2.1"
echo "========================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null 2>&1 && ! docker compose version > /dev/null 2>&1; then
    echo "❌ docker-compose or 'docker compose' not found. Please install docker-compose."
    exit 1
fi

# Set compose command
if command -v docker-compose > /dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
else
    COMPOSE_CMD="docker compose"
fi

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating template..."
    cat > .env << EOF
# TTKi AI Environment Variables
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_ENV=production
EOF
    echo "📝 Please edit .env file and add your GEMINI_API_KEY"
    echo "   Then run this script again."
    exit 1
fi

# Source environment variables
source .env

# Check if API key is set
if [ "$GEMINI_API_KEY" = "your_gemini_api_key_here" ] || [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Please set your GEMINI_API_KEY in .env file"
    exit 1
fi

echo "✅ Environment configured"

# Build and start services
echo "🔨 Building Docker images..."
$COMPOSE_CMD build

echo "🎯 Starting services..."
$COMPOSE_CMD up -d

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check service status
echo "📊 Service Status:"
echo "=================="

# Check AI Terminal
if curl -s http://localhost:4001/health > /dev/null; then
    echo "✅ AI Terminal: http://localhost:4001"
else
    echo "❌ AI Terminal: Not responding"
fi

# Check Landing Page
if curl -s http://localhost:4000 > /dev/null; then
    echo "✅ Landing Page: http://localhost:4000"
else
    echo "❌ Landing Page: Not responding"
fi

# Check Desktop VNC
if curl -s http://localhost:4051 > /dev/null; then
    echo "✅ Desktop VNC: http://localhost:4051/vnc.html"
else
    echo "❌ Desktop VNC: Not responding"
fi

echo ""
echo "🌟 TTKi AI Desktop Environment is ready!"
echo "========================================="
echo "🖥️  AI Interface: http://localhost:4001"
echo "🏠 Landing Page: http://localhost:4000"
echo "🖥️  Desktop VNC: http://localhost:4051/vnc.html"
echo ""
echo "📋 Useful commands:"
echo "   $COMPOSE_CMD logs -f    # View logs"
echo "   $COMPOSE_CMD stop       # Stop services"
echo "   $COMPOSE_CMD down       # Stop and remove containers"
echo "   $COMPOSE_CMD restart    # Restart services"
echo ""
echo "🔧 To stop the environment: $COMPOSE_CMD down"
