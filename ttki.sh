#!/bin/bash

# TTKi-cli Complete Management Script
# Zarządzanie wszystkimi usługami TTKi-cli

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Source port configuration
source ports.conf 2>/dev/null || {
    echo -e "${YELLOW}Ostrzeżenie: ports.conf nie został znaleziony, używam domyślnych portów${NC}"
    LANDING_PAGE_PORT=4000
    AI_TERMINAL_PORT=4001
    VNC_DISPLAY=:50
    NOVNC_WEB_PORT=4051
}

print_banner() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════╗"
    echo "║            TTKi-cli Manager            ║"
    echo "║   Terminal AI w stylu Bolt + Desktop   ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"
}

show_help() {
    echo "Użycie: $0 [KOMENDA]"
    echo ""
    echo "Dostępne komendy:"
    echo "  start     - Uruchom wszystkie usługi TTKi-cli"
    echo "  stop      - Zatrzymaj wszystkie usługi TTKi-cli"
    echo "  restart   - Restart wszystkich usług"
    echo "  status    - Pokaż status usług"
    echo "  ports     - Sprawdź porty"
    echo "  logs      - Pokaż logi aplikacji"
    echo "  clean     - Wyczyść procesy i porty"
    echo "  help      - Pokaż tę pomoc"
    echo ""
    echo "Przykłady:"
    echo "  $0 start"
    echo "  $0 status"
    echo "  $0 clean && $0 start"
}

check_dependencies() {
    local missing=0
    
    for cmd in python3 vncserver websockify; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            echo -e "${RED}❌ Brak: $cmd${NC}"
            missing=1
        fi
    done
    
    if [ $missing -eq 1 ]; then
        echo -e "${RED}Błąd: Brakuje wymaganych zależności${NC}"
        exit 1
    fi
}

clean_processes() {
    echo -e "${YELLOW}🧹 Czyszczenie procesów...${NC}"
    
    # Kill specific processes with force
    pkill -9 -f "python.*app.py" 2>/dev/null || true
    pkill -9 -f "websockify.*$NOVNC_WEB_PORT" 2>/dev/null || true
    pkill -9 -f "Xvnc.*$VNC_DISPLAY" 2>/dev/null || true
    pkill -9 -f "http.server.*$LANDING_PAGE_PORT" 2>/dev/null || true
    pkill -9 -f "openbox" 2>/dev/null || true
    
    # Also kill by port
    local pids=$(ss -tulpn | grep ":$AI_TERMINAL_PORT " | grep -o "pid=[0-9]*" | cut -d= -f2 | sort -u)
    for pid in $pids; do
        kill -9 "$pid" 2>/dev/null || true
    done
    
    sleep 3
    echo -e "${GREEN}✅ Procesy wyczyszczone${NC}"
}

start_vnc() {
    echo -e "${BLUE}🖥️  Uruchamianie VNC Server...${NC}"
    
    # Ensure VNC directory exists
    mkdir -p ~/.vnc
    
    # Start VNC server
    Xvnc $VNC_DISPLAY -desktop "TTKi-cli Desktop" -geometry 1280x800 -depth 24 \
        -SecurityTypes VncAuth -PasswordFile ~/.vnc/passwd \
        >/dev/null 2>&1 &
    
    sleep 2
    
    # Start window manager
    DISPLAY=$VNC_DISPLAY openbox >/dev/null 2>&1 &
    
    echo -e "${GREEN}✅ VNC Server uruchomiony na display $VNC_DISPLAY${NC}"
}

start_novnc() {
    echo -e "${BLUE}🌐 Uruchamianie noVNC...${NC}"
    
    # Calculate VNC port (display + 5900)
    local vnc_port=$((${VNC_DISPLAY#:} + 5900))
    
    websockify --web novnc/noVNC-1.4.0 $NOVNC_WEB_PORT localhost:$vnc_port \
        >/dev/null 2>&1 &
    
    echo -e "${GREEN}✅ noVNC uruchomiony na porcie $NOVNC_WEB_PORT${NC}"
}

start_ai_terminal() {
    echo -e "${BLUE}🤖 Uruchamianie AI Terminal...${NC}"
    
    if [ ! -f "app.py" ]; then
        echo -e "${RED}❌ Plik app.py nie został znaleziony${NC}"
        return 1
    fi
    
    python3 app.py >app.log 2>&1 &
    sleep 3
    
    if ss -tuln | grep -q ":$AI_TERMINAL_PORT "; then
        echo -e "${GREEN}✅ AI Terminal uruchomiony na porcie $AI_TERMINAL_PORT${NC}"
    else
        echo -e "${RED}❌ Błąd uruchamiania AI Terminal${NC}"
        tail -5 app.log
        return 1
    fi
}

start_landing_page() {
    echo -e "${BLUE}🏠 Uruchamianie Landing Page...${NC}"
    
    python3 -m http.server $LANDING_PAGE_PORT >/dev/null 2>&1 &
    
    echo -e "${GREEN}✅ Landing Page uruchomiona na porcie $LANDING_PAGE_PORT${NC}"
}

start_all() {
    print_banner
    echo -e "${BLUE}🚀 Uruchamianie wszystkich usług TTKi-cli...${NC}"
    echo ""
    
    check_dependencies
    clean_processes
    
    start_vnc
    start_novnc
    start_ai_terminal
    start_landing_page
    
    echo ""
    echo -e "${GREEN}🎉 Wszystkie usługi TTKi-cli zostały uruchomione!${NC}"
    echo ""
    show_urls
}

stop_all() {
    print_banner
    echo -e "${YELLOW}🛑 Zatrzymywanie wszystkich usług TTKi-cli...${NC}"
    
    clean_processes
    
    echo -e "${GREEN}✅ Wszystkie usługi zostały zatrzymane${NC}"
}

show_status() {
    ./status_ttki.sh
}

show_ports() {
    echo -e "${BLUE}🔌 TTKi-cli - Porty w użyciu:${NC}"
    echo ""
    ss -tuln | grep -E ":(4000|4001|4050|4051|5950)" | sort || true
}

show_logs() {
    echo -e "${BLUE}📋 Ostatnie logi aplikacji:${NC}"
    echo ""
    if [ -f "app.log" ]; then
        tail -20 app.log
    else
        echo "Brak pliku logów app.log"
    fi
}

show_urls() {
    echo -e "${BLUE}📍 Adresy dostępu TTKi-cli:${NC}"
    echo -e "• ${GREEN}Główny portal:${NC}  http://localhost:$LANDING_PAGE_PORT"
    echo -e "• ${GREEN}AI Terminal:${NC}    http://localhost:$AI_TERMINAL_PORT"
    echo -e "• ${GREEN}Desktop (VNC):${NC}  http://localhost:$NOVNC_WEB_PORT"
    echo ""
}

# Main script logic
case "${1:-help}" in
    start)
        start_all
        ;;
    stop)
        stop_all
        ;;
    restart)
        stop_all
        sleep 2
        start_all
        ;;
    status)
        show_status
        ;;
    ports)
        show_ports
        ;;
    logs)
        show_logs
        ;;
    clean)
        clean_processes
        ;;
    help|--help|-h)
        print_banner
        show_help
        ;;
    *)
        echo -e "${RED}❌ Nieznana komenda: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
