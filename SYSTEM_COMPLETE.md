# 🚀 TTKi AI Desktop Environment - Kompletny System Docker

## 📋 Przegląd Systemu

TTKi AI Desktop Environment to kompleksowe rozwiązanie łączące:
- **Interfejs AI Chat** - Nowoczesny interfejs z split-screen
- **Ubuntu Desktop VNC** - Pełne środowisko programistyczne 
- **Landing Page** - Strona główna projektu
- **Wszystko w kontenerach Docker** - Łatwe wdrożenie i skalowanie

## 🏗️ Architektura

```
┌─────────────────────────────────────────────────────────────┐
│                TTKi AI Desktop Environment                 │
├─────────────────────────────────────────────────────────────┤
│  🌐 Frontend (Port 4001)     │  🖥️  VNC Desktop (4051)     │
│  ├─ Split-screen Interface   │  ├─ Ubuntu 22.04            │
│  ├─ AI Chat Panel           │  ├─ VS Code + Firefox        │
│  ├─ VNC Desktop Panel       │  ├─ Konsole Terminal         │
│  └─ Resize Handles          │  └─ Development Tools        │
├─────────────────────────────────────────────────────────────┤
│  🏠 Landing Page (Port 4000) │  🔧 Backend Services        │
│  ├─ Project Documentation   │  ├─ Flask + Socket.IO       │
│  ├─ Service Links           │  ├─ Google Gemini AI        │
│  └─ System Status           │  └─ noVNC + websockify      │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Komponenty

### 1. AI Terminal Application (`ttki-ai`)
- **Technologie**: Flask, Socket.IO, Google Gemini AI
- **Port**: 4001
- **Funkcje**:
  - Chat z AI w czasie rzeczywistym
  - Split-screen interface (VNC + Chat)
  - Resizable panels
  - Dark theme UI
  - Health check endpoint

### 2. Ubuntu VNC Desktop (`ttki-desktop`)
- **Technologie**: Ubuntu 22.04, TigerVNC, noVNC, Openbox
- **Porty**: 4051 (web), 5950 (direct VNC)
- **Aplikacje**:
  - VS Code (edytor kodu)
  - Firefox (przeglądarka)
  - Konsole (terminal)
  - Python, Node.js, Git
- **Interface**: Tint2 panel, PCManFM file manager

### 3. Landing Page (`ttki-landing`)
- **Technologie**: Flask (minimal)
- **Port**: 4000
- **Funkcje**:
  - Strona główna projektu
  - Linki do wszystkich serwisów
  - Dokumentacja

## 🚦 Schemat Portów

| Serwis | Port | Protokół | Opis |
|--------|------|----------|------|
| AI Interface | `4001` | HTTP | Główny interfejs AI |
| Landing Page | `4000` | HTTP | Strona główna |
| VNC Web | `4051` | HTTP/WebSocket | noVNC web client |
| VNC Direct | `5950` | VNC | Bezpośrednie połączenie VNC |

## 🔧 Instalacja i Uruchomienie

### Wymagania
- Docker
- Docker Compose (lub `docker compose`)
- Klucz API Google Gemini

### Kroki

1. **Sklonuj/Pobierz projekt**
```bash
git clone <repository>
cd ttki-ai-desktop
```

2. **Skonfiguruj środowisko**
```bash
cp .env.example .env
nano .env  # Dodaj swój GEMINI_API_KEY
```

3. **Uruchom system**
```bash
./start_ttki.sh
```

**LUB ręcznie:**
```bash
docker compose build
docker compose up -d
```

## 📁 Struktura Plików

```
ttki-ai-desktop/
├── 🐳 Docker Configuration
│   ├── Dockerfile                 # AI Application
│   ├── Dockerfile.desktop         # Ubuntu VNC Desktop
│   ├── docker-compose.yml         # Services orchestration
│   └── start_ttki.sh              # Quick start script
│
├── 🖥️ AI Application
│   ├── app.py                     # Main Flask app
│   ├── requirements.txt           # Python dependencies
│   └── templates/
│       ├── ai_interface.html      # Split-screen interface
│       └── index.html             # Landing page
│
├── 🎨 Static Resources
│   ├── static/                    # CSS, JS, images
│   └── templates/                 # HTML templates
│
├── 📚 Documentation
│   ├── DOCKER_README.md           # Docker guide
│   ├── TESTING_README.md          # Testing guide
│   └── .rules                     # Project rules
│
└── ⚙️ Configuration
    ├── .env.example               # Environment template
    ├── .gitignore                 # Git ignore rules
    └── SECURITY.md                # Security guidelines
```

## 🎮 Korzystanie z Systemu

### 1. Główny Interfejs AI (Port 4001)
- **URL**: http://localhost:4001
- **Funkcje**:
  - Panel czatu AI po prawej stronie
  - Panel VNC desktop po lewej stronie  
  - Przeciąganie separatora do zmiany rozmiaru
  - Przycisk "Uruchom Desktop" do inicjalizacji VNC

### 2. Desktop VNC (Port 4051)
- **URL**: http://localhost:4051/vnc.html
- **Logowanie**: automatyczne (hasło: `password`)
- **Aplikacje dostępne**:
  - VS Code: `code`
  - Firefox: `firefox`
  - Terminal: `konsole`
  - File Manager: `pcmanfm`

### 3. Landing Page (Port 4000)
- **URL**: http://localhost:4000
- **Zawiera**: Dokumentację, linki, status systemu

## 🔍 Debugowanie

### Sprawdzenie statusu kontenerów
```bash
docker compose ps
```

### Logi serwisów
```bash
# Wszystkie logi
docker compose logs -f

# Konkretny serwis
docker compose logs -f ttki-ai
docker compose logs -f ttki-desktop
docker compose logs -f ttki-landing
```

### Health Check
```bash
# AI Application
curl http://localhost:4001/health

# VNC Desktop
curl http://localhost:4051

# Landing Page  
curl http://localhost:4000
```

### Restart serwisów
```bash
# Restart wszystkich
docker compose restart

# Restart konkretnego
docker compose restart ttki-ai
docker compose restart ttki-desktop
```

## 🛡️ Bezpieczeństwo

- ✅ Wszystkie klucze API w zmiennych środowiskowych
- ✅ Brak hardkodowanych haseł w kodzie
- ✅ Non-root user w kontenerach
- ✅ Health checks dla wszystkich serwisów
- ✅ Bezpieczna konfiguracja VNC z hasłem

## 🔄 Aktualizacje

```bash
# Zatrzymaj system
docker compose down

# Pobierz najnowsze zmiany
git pull

# Przebuduj i uruchom
docker compose build --no-cache
./start_ttki.sh
```

## 🎯 Rozwój

### Development Mode
```bash
# Uruchom z montowanym kodem
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Modyfikacja interfejsu
- Edytuj `templates/ai_interface.html`
- Restart kontenera: `docker compose restart ttki-ai`

### Dodawanie aplikacji do VNC
- Modyfikuj `Dockerfile.desktop`
- Przebuduj: `docker compose build ttki-desktop`

## 🆘 Rozwiązywanie Problemów

### "Connection refused" dla VNC
```bash
# Sprawdź czy kontener działa
docker compose ps ttki-desktop

# Sprawdź logi VNC
docker compose logs ttki-desktop

# Restart VNC service
docker compose restart ttki-desktop
```

### AI nie odpowiada
```bash
# Sprawdź klucz API
docker compose exec ttki-ai env | grep GEMINI

# Sprawdź health
curl http://localhost:4001/health

# Sprawdź logi
docker compose logs ttki-ai
```

### Brak miejsca na dysku
```bash
# Wyczyść stare obrazy
docker system prune -a

# Wyczyść volumes
docker volume prune
```

## 📊 Monitoring

### Status wszystkich serwisów
```bash
./start_ttki.sh  # Pokazuje status po uruchomieniu
```

### Wykorzystanie zasobów
```bash
docker stats
```

### Logi w czasie rzeczywistym
```bash
docker compose logs -f --tail=100
```

---

**🎉 TTKi AI Desktop Environment** - Kompletne rozwiązanie AI + VNC w Docker!

🌟 **Dostęp do systemu**:
- 🤖 **AI Interface**: http://localhost:4001
- 🏠 **Landing Page**: http://localhost:4000  
- 🖥️ **VNC Desktop**: http://localhost:4051/vnc.html
