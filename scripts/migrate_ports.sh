#!/bin/bash

# TTKi-cli Port Migration Script
# Migrates all services to the new 4000-4099 port range

echo "🔄 TTKi-cli - Migracja Portów"
echo "=============================="

# Step 1: Stop existing services
echo "🛑 Zatrzymywanie obecnych usług..."
pkill -f websockify 2>/dev/null
pkill -f "Xvnc :3" 2>/dev/null
pkill -f "test_flask.py" 2>/dev/null
pkill -f "python.*app.py" 2>/dev/null

sleep 2

# Step 2: Check if new ports are available
echo "🔍 Sprawdzanie dostępności nowych portów..."

check_port() {
    if ss -tuln | grep -q ":$1 "; then
        echo "❌ Port $1 jest zajęty"
        return 1
    else
        echo "✅ Port $1 jest dostępny"
        return 0
    fi
}

ports_ok=true
for port in 4000 4001 4050 4051; do
    if ! check_port $port; then
        ports_ok=false
    fi
done

if [ "$ports_ok" = false ]; then
    echo "⚠️  Niektóre porty są zajęte. Kontynuować? (y/n)"
    read -r response
    if [ "$response" != "y" ]; then
        echo "❌ Migracja anulowana"
        exit 1
    fi
fi

# Step 3: Update configurations
echo "📝 Aktualizowanie konfiguracji..."

# Create backup of configs
echo "Tworzę kopie zapasowe konfiguracji..."
cp app.py app.py.backup 2>/dev/null || true
cp test_flask.py test_flask.py.backup 2>/dev/null || true
cp index.html index.html.backup 2>/dev/null || true
cp main.py main.py.backup 2>/dev/null || true

# Update all Python files with port configurations
echo "Aktualizuję porty w plikach Python..."
for file in app.py test_flask.py main.py test_*.py; do
    if [ -f "$file" ]; then
        echo "  → $file"
        # Main Flask app: 5002 → 4001
        sed -i 's/port=5002/port=4001/g' "$file"
        sed -i 's/port=5003/port=4001/g' "$file" 
        sed -i 's/port=5000/port=4001/g' "$file"
        # VNC URLs: 5903 → 4050, 6080 → 4051
        sed -i 's/:5903/:4050/g' "$file"
        sed -i 's/:6080/:4051/g' "$file"
        # Update base URLs in tests
        sed -i 's/localhost:5002/localhost:4001/g' "$file"
        sed -i 's/localhost:5000/localhost:4001/g' "$file"
    fi
done

# Update HTML files
echo "Aktualizuję porty w plikach HTML..."
for file in index.html templates/*.html; do
    if [ -f "$file" ]; then
        echo "  → $file"
        # AI Terminal: 5002/5003 → 4001
        sed -i 's/:5002/:4001/g' "$file"
        sed -i 's/:5003/:4001/g' "$file"
        sed -i 's/:5000/:4001/g' "$file"
        # VNC: 5903 → 4050, noVNC: 6080 → 4051
        sed -i 's/:5903/:4050/g' "$file"
        sed -i 's/:6080/:4051/g' "$file"
        # Landing page: 8080 → 4000
        sed -i 's/:8080/:4000/g' "$file"
    fi
done

# Step 4: Start services with new ports
echo "🚀 Uruchamianie usług z nowymi portami..."

# Start VNC with new display number
echo "Uruchamianie VNC na porcie 4050 (display :50)..."
Xvnc :50 -desktop "TTKi-cli Desktop" -geometry 1280x800 -depth 24 -SecurityTypes VncAuth -PasswordFile ~/.vnc/passwd &
sleep 2

# Start window manager
echo "Uruchamianie Openbox..."
DISPLAY=:50 openbox &
sleep 1

# Start websockify with new ports
echo "Uruchamianie noVNC na porcie 4051..."
websockify --web novnc/noVNC-1.4.0 4051 localhost:4050 &
sleep 2

# Start Flask app
echo "Uruchamianie AI Terminal na porcie 4001..."
if [ -f "app.py" ]; then
    python app.py &
else
    python test_flask.py &
fi
sleep 2

# Step 5: Start landing page on port 4000
echo "Uruchamianie Landing Page na porcie 4000..."
if command -v python3 >/dev/null 2>&1; then
    python3 -m http.server 4000 &
else
    python -m http.server 4000 &
fi

echo ""
echo "🎉 Migracja portów zakończona!"
echo ""
echo "📍 Nowe adresy TTKi-cli:"
echo "• Główny portal:  http://localhost:4000"
echo "• AI Terminal:    http://localhost:4001" 
echo "• Desktop (VNC):  http://localhost:4051"
echo ""
echo "🔍 Sprawdź status: ss -tuln | grep -E ':(4000|4001|4050|4051)'"
