#!/bin/bash

# TTKi-cli Startup Script with Environment Variables
# This script loads environment variables from .env file and starts containers

echo "🚀 Starting TTKi-cli AI Desktop Environment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with your API keys."
    echo "See .env.example for template."
    exit 1
fi

# Load environment variables from .env file
source .env

# Validate required environment variables
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ Error: GEMINI_API_KEY not found in .env file!"
    echo "Please add your Google Gemini API key to .env file."
    exit 1
fi

echo "✅ Environment variables loaded from .env"

# Stop and remove existing containers if they exist
echo "🧹 Cleaning up existing containers..."
docker stop ttki-ai ttki-vnc ttki-landing ttki-desktop 2>/dev/null || true
docker rm ttki-ai ttki-vnc ttki-landing ttki-desktop 2>/dev/null || true

# Create shared volume for bridge communication
echo "🔗 Creating shared bridge volume..."
docker volume create ttki-bridge 2>/dev/null || true

# Start VNC container (using simpler consol image for now)
echo "🖥️  Starting VNC Desktop container..."
docker run -d \
    --name ttki-vnc \
    -p 4051:6901 \
    -p 5950:5901 \
    -e VNC_PW=ttki123 \
    -v ttki-bridge:/shared \
    consol/ubuntu-xfce-vnc

# Start AI container
echo "🤖 Starting AI Terminal container..."
docker run -d \
    --name ttki-ai \
    -p 4001:4001 \
    -e GEMINI_API_KEY="$GEMINI_API_KEY" \
    -e FLASK_SECRET_KEY="$FLASK_SECRET_KEY" \
    -v ttki-bridge:/shared \
    -v /var/run/docker.sock:/var/run/docker.sock \
    --user root \
    ttki/ai-terminal:latest

# Start Landing Page container
echo "🏠 Starting Landing Page container..."
docker run -d \
    --name ttki-landing \
    -p 4000:4000 \
    -e FLASK_ENV=production \
    -e FLASK_SECRET_KEY="$FLASK_SECRET_KEY" \
    ttki/ai-terminal:latest python landing.py

# Wait a moment for containers to start
echo "⏳ Waiting for containers to initialize..."
sleep 5

# Check container status
echo "📊 Container Status:"
docker ps | grep ttki

# Test health endpoints
echo "🏥 Testing health endpoints..."
echo "AI Health:"
curl -s http://localhost:4001/health | jq '.' 2>/dev/null || curl -s http://localhost:4001/health

echo -e "\n\nVNC Health:"
curl -s -I http://localhost:4051 | head -n 1

echo -e "\n\n✅ TTKi-cli started successfully!"
echo "🌐 Open http://localhost:4001 in your browser"
echo "🖥️  VNC Desktop: http://localhost:4051 (password: ttki123)"
echo "📊 AI Health: http://localhost:4001/health"
