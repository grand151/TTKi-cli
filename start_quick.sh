#!/bin/bash

# TTKi AI Desktop Environment - Quick Start (Use existing images)
# This script uses already built images if available

set -e

echo "🚀 TTKi AI Desktop Environment v0.2.1 (Quick Start)"
echo "================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check for .env file and API key
if [ ! -f .env ]; then
    echo "❌ No .env file found. Please create .env with GEMINI_API_KEY"
    exit 1
fi

source .env

if [ "$GEMINI_API_KEY" = "your_gemini_api_key_here" ] || [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Please set your GEMINI_API_KEY in .env file"
    exit 1
fi

echo "✅ Environment configured"

# Create Docker network if it doesn't exist
docker network create ttki-network 2>/dev/null || true

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker stop ttki-ai ttki-desktop ttki-landing 2>/dev/null || true
docker rm ttki-ai ttki-desktop ttki-landing 2>/dev/null || true

# Check if we have AI image
AI_IMAGE=$(docker images -q ttki/ai-terminal:latest)
if [ -z "$AI_IMAGE" ]; then
    # Try old name as fallback
    AI_IMAGE=$(docker images -q jakstworzyaplikacjterminalaaiwstylubolt-ttki-ai:latest)
    if [ -z "$AI_IMAGE" ]; then
        echo "❌ No TTKi AI image found. Please run docker compose build first."
        exit 1
    else
        IMAGE_NAME="jakstworzyaplikacjterminalaaiwstylubolt-ttki-ai:latest"
    fi
else
    IMAGE_NAME="ttki/ai-terminal:latest"
fi

# Start AI application
echo "🎯 Starting AI application..."
docker run -d \
    --name ttki-ai \
    --network ttki-network \
    -p 4001:4001 \
    -e GEMINI_API_KEY="$GEMINI_API_KEY" \
    -e FLASK_ENV=production \
    -v "$(pwd)/templates:/app/templates" \
    -v "$(pwd)/static:/app/static" \
    $IMAGE_NAME

# Try to start basic VNC container (Ubuntu with VNC)
echo "🖥️ Starting basic VNC container..."
docker run -d \
    --name ttki-vnc \
    --network ttki-network \
    -p 4051:6080 \
    -p 5950:5900 \
    -e VNC_PW=password \
    dorowu/ubuntu-desktop-lxde-vnc

# Start simple landing page
echo "🏠 Starting Landing page..."
docker run -d \
    --name ttki-landing \
    --network ttki-network \
    -p 4000:8000 \
    -v "$(pwd):/app" \
    python:3.11-slim \
    python3 -c "
import http.server
import socketserver
import os
os.chdir('/app')

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = '''
<!DOCTYPE html>
<html>
<head>
    <title>TTKi AI Desktop Environment</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #1a1a1a; color: #fff; }
        .container { max-width: 800px; margin: 0 auto; }
        .service { background: #2a2a2a; padding: 20px; margin: 10px 0; border-radius: 8px; }
        .service a { color: #4CAF50; text-decoration: none; font-size: 18px; }
        .service a:hover { text-decoration: underline; }
        h1 { color: #4CAF50; text-align: center; }
        .status { background: #0f3f0f; padding: 15px; border-radius: 8px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class=\"container\">
        <h1>🤖 TTKi AI Desktop Environment</h1>
        <p style=\"text-align: center; font-size: 18px;\">AI-Powered Development Environment</p>
        
        <div class=\"service\">
            <h3>🤖 AI Interface (Split-Screen)</h3>
            <p>Main AI chat interface with integrated VNC desktop</p>
            <a href=\"http://localhost:4001\" target=\"_blank\">→ Open AI Interface</a>
        </div>
        
        <div class=\"service\">
            <h3>🖥️ VNC Desktop</h3>
            <p>Ubuntu desktop environment with development tools</p>
            <a href=\"http://localhost:4051\" target=\"_blank\">→ Open VNC Desktop</a>
        </div>
        
        <div class=\"status\">
            <h3>📊 System Status</h3>
            <p>✅ AI Terminal: Port 4001</p>
            <p>✅ VNC Desktop: Port 4051</p>
            <p>✅ Landing Page: Port 4000</p>
            <p><strong>Version:</strong> TTKi v0.2.1</p>
        </div>
    </div>
</body>
</html>
            '''
            self.wfile.write(html.encode())
        else:
            super().do_GET()

with socketserver.TCPServer(('', 8000), MyHTTPRequestHandler) as httpd:
    httpd.serve_forever()
"

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check service status
echo "📊 Service Status:"
echo "=================="

# Check AI Terminal
if curl -s http://localhost:4001 > /dev/null 2>&1; then
    echo "✅ AI Terminal: http://localhost:4001"
else
    echo "❌ AI Terminal: Not responding"
fi

# Check Landing Page
if curl -s http://localhost:4000 > /dev/null 2>&1; then
    echo "✅ Landing Page: http://localhost:4000"
else
    echo "❌ Landing Page: Not responding"
fi

# Check VNC Desktop
if curl -s http://localhost:4051 > /dev/null 2>&1; then
    echo "✅ VNC Desktop: http://localhost:4051"
else
    echo "❌ VNC Desktop: Not responding"
fi

echo ""
echo "🌟 TTKi AI Desktop Environment is ready!"
echo "========================================="
echo "🖥️  AI Interface: http://localhost:4001"
echo "🏠 Landing Page: http://localhost:4000"
echo "🖥️  VNC Desktop: http://localhost:4051"
echo ""
echo "📋 Container Management:"
echo "   docker ps                     # View running containers"
echo "   docker logs ttki-ai           # View AI logs"
echo "   docker logs ttki-vnc          # View VNC logs"
echo "   docker stop ttki-ai ttki-vnc ttki-landing  # Stop all"
echo ""
echo "🔧 To stop: docker stop ttki-ai ttki-vnc ttki-landing"
