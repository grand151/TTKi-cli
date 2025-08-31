#!/bin/bash

# TTKi-cli Status Checker
# Sprawdza status wszystkich usług w nowym schemacie portów

echo "🔍 TTKi-cli - Status usług"
echo "=========================="

# Source port configuration
if [ -f "../config/ports.conf" ]; then
    source ../config/ports.conf
fi

# Function to check if port is listening
check_port() {
    local port=$1
    local service=$2
    if ss -tuln | grep -q ":$port "; then
        echo "✅ $service (port $port) - AKTYWNY"
        return 0
    else
        echo "❌ $service (port $port) - NIEAKTYWNY"
        return 1
    fi
}

# Function to check URL response
check_url() {
    local url=$1
    local service=$2
    if curl -s --connect-timeout 3 --max-time 5 "$url" >/dev/null 2>&1; then
        echo "🌐 $service - ODPOWIADA"
        return 0
    else
        echo "🔴 $service - BRAK ODPOWIEDZI"
        return 1
    fi
}

echo ""
echo "📋 Status portów:"
check_port 4000 "Landing Page"
check_port 4001 "AI Terminal"
check_port 4051 "noVNC Web"
check_port 5950 "VNC Server (display :50)"

echo ""
echo "🌐 Status usług HTTP:"
check_url "http://localhost:4000" "Landing Page"
check_url "http://localhost:4001" "AI Terminal"
check_url "http://localhost:4051" "noVNC Web"

echo ""
echo "🔧 Procesy TTKi-cli:"
ps aux | grep -E "(Xvnc.*:50|websockify.*4051|python.*src/app.py|http.server.*4000)" | grep -v grep | while read line; do
    echo "  → $line" | cut -d' ' -f11-
done

echo ""
echo "📍 Adresy dostępu:"
echo "• Główny portal:  http://localhost:4000"
echo "• AI Terminal:    http://localhost:4001"  
echo "• Desktop (VNC):  http://localhost:4051"
echo ""
echo "🔧 Zarządzanie:"
echo "• Start:    ./ttki.sh start"
echo "• Stop:     ./ttki.sh stop"
echo "• Restart:  ./ttki.sh restart"
