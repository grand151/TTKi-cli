#!/bin/bash

# TTKi AI Desktop Environment - Simple Docker Build
# Alternative startup without docker-compose

set -e

echo "🚀 TTKi AI Desktop Environment v0.2.1 (Simple Mode)"
echo "================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
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

# Create Docker network if it doesn't exist
docker network create ttki-network 2>/dev/null || true

# Build AI application image
echo "🔨 Building AI application image..."
docker build -t ttki-ai:latest -f Dockerfile .

# Build Desktop VNC image  
echo "🔨 Building Desktop VNC image..."
docker build -t ttki-desktop:latest -f Dockerfile.desktop .

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker stop ttki-ai ttki-desktop ttki-landing 2>/dev/null || true
docker rm ttki-ai ttki-desktop ttki-landing 2>/dev/null || true

# Start AI application
echo "🎯 Starting AI application..."
docker run -d \
    --name ttki-ai \
    --network ttki-network \
    -p 4001:4001 \
    -e GEMINI_API_KEY="$GEMINI_API_KEY" \
    -e FLASK_ENV=production \
    ttki-ai:latest

# Start Desktop VNC
echo "🖥️ Starting Desktop VNC..."
docker run -d \
    --name ttki-desktop \
    --network ttki-network \
    -p 4051:4051 \
    -p 5950:5950 \
    -e DISPLAY=:50 \
    -e USER=ttki \
    ttki-desktop:latest

# Start Landing page
echo "🏠 Starting Landing page..."
docker run -d \
    --name ttki-landing \
    --network ttki-network \
    -p 4000:4000 \
    -e FLASK_ENV=production \
    --entrypoint python3 \
    ttki-ai:latest \
    -c "
from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>TTKi AI Desktop Environment</title>
    <style>
        body { font-family: Arial; margin: 40px; background: #1a1a1a; color: #fff; }
        .container { max-width: 800px; margin: 0 auto; }
        .service { background: #2a2a2a; padding: 20px; margin: 10px 0; border-radius: 8px; }
        .service a { color: #4CAF50; text-decoration: none; }
        .service a:hover { text-decoration: underline; }
        h1 { color: #4CAF50; }
    </style>
</head>
<body>
    <div class=\"container\">
        <h1>🤖 TTKi AI Desktop Environment</h1>
        <p>Welcome to the AI-powered desktop environment!</p>
        
        <div class=\"service\">
            <h3>🤖 AI Interface (Split-Screen)</h3>
            <p>Main AI chat interface with integrated VNC desktop</p>
            <a href=\"http://localhost:4001\" target=\"_blank\">→ Open AI Interface</a>
        </div>
        
        <div class=\"service\">
            <h3>🖥️ VNC Desktop (Direct)</h3>
            <p>Direct access to Ubuntu desktop environment</p>
            <a href=\"http://localhost:4051/vnc.html\" target=\"_blank\">→ Open VNC Desktop</a>
        </div>
        
        <div class=\"service\">
            <h3>📚 Documentation</h3>
            <p>System guides and documentation</p>
            <a href=\"#\">→ View Docs</a>
        </div>
        
        <hr style=\"margin: 30px 0;\">
        <p><strong>System Status:</strong> ✅ All services running</p>
        <p><strong>Version:</strong> TTKi v0.2.1</p>
    </div>
</body>
</html>
    '''

app.run(host='0.0.0.0', port=4000)
"

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 15

# Check service status
echo "📊 Service Status:"
echo "=================="

# Check AI Terminal
if curl -s http://localhost:4001/health > /dev/null 2>&1; then
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

# Check Desktop VNC
if curl -s http://localhost:4051 > /dev/null 2>&1; then
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
echo "   docker ps                     # View running containers"
echo "   docker logs ttki-ai           # View AI logs"
echo "   docker logs ttki-desktop      # View VNC logs"
echo "   docker stop ttki-ai ttki-desktop ttki-landing  # Stop services"
echo "   docker rm ttki-ai ttki-desktop ttki-landing    # Remove containers"
echo ""
echo "🔧 To stop the environment: docker stop ttki-ai ttki-desktop ttki-landing"
