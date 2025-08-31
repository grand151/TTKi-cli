# TTKi AI Desktop Environment - Docker Setup

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Google Gemini API key

### Setup

1. **Clone/Download the project**
   ```bash
   git clone <repository> # or download files
   cd ttki-ai-desktop
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   nano .env  # Add your GEMINI_API_KEY
   ```

3. **Start the environment**
   ```bash
   ./start_ttki.sh
   ```

## 🌟 Services

The environment consists of 3 Docker containers:

### 1. TTKi AI Terminal (Port 4001)
- **URL**: http://localhost:4001
- **Description**: Main AI interface with split-screen design
- **Features**: 
  - AI chat with Google Gemini
  - VNC desktop integration
  - Resizable panels
  - Modern dark theme

### 2. TTKi Landing Page (Port 4000)
- **URL**: http://localhost:4000
- **Description**: Project landing page and documentation
- **Features**: Project overview, links to services

### 3. TTKi Desktop VNC (Port 4051)
- **URL**: http://localhost:4051/vnc.html
- **Description**: Ubuntu desktop environment in browser
- **Features**:
  - Full Ubuntu 22.04 desktop
  - Pre-installed: VS Code, Firefox, Konsole
  - Development tools: Python, Node.js, Git
  - Window manager: Openbox with tint2 panel

## 📁 Architecture

```
ttki-ai-desktop/
├── Dockerfile              # AI Terminal application
├── Dockerfile.desktop      # Ubuntu VNC desktop
├── docker-compose.yml      # Service orchestration
├── start_ttki.sh          # Quick start script
├── app.py                 # Main AI application
├── templates/
│   ├── ai_interface.html  # Split-screen AI interface
│   └── index.html         # Landing page
├── static/               # CSS, JS, images
└── requirements.txt      # Python dependencies
```

## 🔧 Management Commands

```bash
# Start environment
./start_ttki.sh

# View logs
docker-compose logs -f

# Stop services
docker-compose stop

# Restart services
docker-compose restart

# Stop and remove containers
docker-compose down

# Rebuild containers
docker-compose build --no-cache

# Check service status
docker-compose ps
```

## 🛡️ Security

- All API keys stored in environment variables
- No hardcoded credentials in code
- Non-root user in containers
- Health checks for all services
- Secure VNC setup with password protection

## 🔍 Troubleshooting

### Service not responding
```bash
# Check if containers are running
docker-compose ps

# View specific service logs
docker-compose logs ttki-ai
docker-compose logs ttki-desktop
docker-compose logs ttki-landing
```

### VNC connection issues
```bash
# Restart desktop service
docker-compose restart ttki-desktop

# Check VNC port accessibility
curl http://localhost:4051
curl http://localhost:5950
```

### AI Terminal not working
```bash
# Check API key configuration
docker-compose exec ttki-ai env | grep GEMINI

# Check health endpoint
curl http://localhost:4001/health
```

## 📊 Port Reference

| Service | Port | Protocol | Description |
|---------|------|----------|-------------|
| AI Terminal | 4001 | HTTP | Main AI interface |
| Landing Page | 4000 | HTTP | Project homepage |
| VNC Web | 4051 | HTTP | noVNC web client |
| VNC Direct | 5950 | VNC | Direct VNC connection |

## 🔄 Updates

To update the environment:

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
./start_ttki.sh
```

## 📝 Development

For development mode:

```bash
# Start in development mode
FLASK_ENV=development docker-compose up

# Mount local code for live editing
# (modify docker-compose.yml volumes section)
```

## 🆘 Support

- Check logs: `docker-compose logs -f`
- Restart services: `docker-compose restart`
- Clean reset: `docker-compose down && docker-compose up --build`
- Report issues: Include logs and error messages
