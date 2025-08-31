# TTKi-cli - Konfiguracja Portów

## 🎯 Obecny stan portów (do uporządkowania)

### Aktywne porty aplikacji:
- **5003** - Flask App (AI Terminal) - na localhost
- **5903** - VNC Server (Xvnc :3) 
- **6080** - noVNC Web Interface (websockify)
- **8080** - Landing Page (nie uruchomiona)

## 🔧 Proponowany nowy schemat portów

### Logiczne grupowanie portów dla TTKi-cli:

```
TTKi-cli Port Scheme:
┌─────────────────────────────────────┐
│ 4000-4099: Core Services            │
├─────────────────────────────────────┤
│ 4000 - Landing Page (główny portal) │
│ 4001 - AI Terminal (Flask)          │
│ 4002 - Status API                   │
├─────────────────────────────────────┤
│ 4050-4059: VNC Services             │
├─────────────────────────────────────┤
│ 4050 - VNC Server                   │
│ 4051 - noVNC Web Client             │
├─────────────────────────────────────┤
│ 4090-4099: Development/Debug        │
├─────────────────────────────────────┤
│ 4090 - Test Environment             │
│ 4091 - Debug Server                 │
└─────────────────────────────────────┘
```

## 📋 Plan migracji portów

### Krok 1: Zatrzymaj obecne usługi
```bash
pkill -f websockify
pkill -f Xvnc
pkill -f flask
```

### Krok 2: Zaktualizuj konfiguracje
- app.py: port 5003 → 4001
- VNC: display :3 (port 5903) → display :50 (port 4050)
- websockify: 6080 → 4051
- index.html: 8080 → 4000

### Krok 3: Uruchom z nowymi portami

## 🌐 Mapowanie dostępu

Po migracji:
- **http://localhost:4000** - Główny portal TTKi-cli
- **http://localhost:4001** - AI Terminal
- **http://localhost:4051** - Desktop (noVNC)

## ✅ Korzyści z nowego schematu

1. **Logiczne grupowanie** - wszystkie porty w zakresie 4000-4099
2. **Łatwość zapamiętania** - sekwencyjne numerowanie
3. **Unikanie konfliktów** - unikalny zakres dla TTKi-cli
4. **Możliwość rozbudowy** - miejsce na nowe usługi
5. **Profesjonalny wygląd** - spójny system portów
