# TTKi-cli 🤖🖥️

**Terminal AI + Desktop Environment** - Kompletne środowisko deweloperskie z AI asystentem i graficznym desktopem dostępnym przez przeglądarkę.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-latest-green.svg)](https://flask.palletsprojects.com/)

## 🌟 Funkcje

- **🤖 AI Terminal** - Inteligentny terminal z Google Gemini AI
- **🖥️ VNC Desktop** - Pełen graficzny desktop w przeglądarce (noVNC)
- **🌐 Web Interface** - Nowoczesny interfejs dostępny przez przeglądarkę
- **🔧 Zarządzanie** - Automatyczne skrypty uruchamiania i monitorowania
- **📊 Monitoring** - Real-time status usług i portów
- **🔒 Bezpieczeństwo** - Zabezpieczone pliki konfiguracyjne

## 🚀 Szybki start

### Wymagania
- Python 3.8+
- TigerVNC Server
- Google Gemini API Key

### Instalacja

```bash
# Klonowanie repozytorium
git clone https://github.com/yourusername/ttki-cli.git
cd ttki-cli

# Instalacja zależności Python
pip install -r requirements.txt

# Instalacja TigerVNC (Ubuntu/Debian)
sudo apt update
sudo apt install tigervnc-standalone-server tigervnc-viewer

# Konfiguracja VNC hasła
vncpasswd

# Ustawienie Google Gemini API Key
export GEMINI_API_KEY="your_api_key_here"
```

### Uruchomienie

```bash
# Uruchomienie wszystkich usług
./ttki.sh start

# Sprawdzenie statusu
./ttki.sh status

# Zatrzymanie usług
./ttki.sh stop
```

## 🌐 Dostęp do usług

Po uruchomieniu dostępne są następujące adresy:

- **🏠 Główny portal**: http://localhost:4000
- **🤖 AI Terminal**: http://localhost:4001  
- **🖥️ VNC Desktop**: http://localhost:4051

## ⚙️ Konfiguracja

### Pliki konfiguracyjne

- `config/prompt.txt` - Systemowy prompt dla AI
- `config/functions.txt` - Definicje funkcji AI
- `config/ports.conf` - Konfiguracja portów

### Zmienne środowiskowe

```bash
# Google Gemini AI
export GEMINI_API_KEY="your_api_key_here"

# Flask (opcjonalne)
export FLASK_SECRET="your_secret_key"
```

## 🏗️ Architektura

### Porty i usługi

| Port | Usługa | Opis |
|------|--------|------|
| 4000 | Landing Page | Główna strona portalu |
| 4001 | AI Terminal | Flask app z AI asystentem |
| 4051 | noVNC Web | Web interface do VNC |
| 5950 | VNC Server | TigerVNC server (display :50) |

### Struktura projektu

```
ttki-cli/
├── src/           # Kod źródłowy aplikacji
├── scripts/       # Skrypty zarządzające
├── config/        # Pliki konfiguracyjne
├── tests/         # Testy automatyczne
├── docs/          # Dokumentacja
├── templates/     # Szablony HTML
├── logs/          # Pliki logów
└── backup/        # Kopie zapasowe
```

## 📋 Komendy zarządzania

```bash
# Podstawowe operacje
./ttki.sh start     # Uruchom wszystkie usługi
./ttki.sh stop      # Zatrzymaj wszystkie usługi
./ttki.sh restart   # Restart usług
./ttki.sh status    # Pokaż status usług

# Diagnostyka
./ttki.sh ports     # Sprawdź porty
./ttki.sh logs      # Pokaż logi aplikacji
./ttki.sh clean     # Wyczyść procesy

# Bezpieczeństwo
./scripts/secure_manus.sh  # Zabezpiecz pliki config
```

## 🧪 Testowanie

```bash
# Uruchomienie testów
python -m pytest tests/

# Testy konkretnego modułu
python -m pytest tests/test_flask.py

# Testy środowiska
python tests/test_environment.py
```

## 🛠️ Rozwój

### Struktura kodu

- **`src/app.py`** - Główna aplikacja Flask
- **`src/user.py`** - Zarządzanie użytkownikami  
- **`scripts/ttki.sh`** - Główny skrypt zarządzający
- **`scripts/status_ttki.sh`** - Monitoring statusu

### Dodawanie funkcji AI

1. Edytuj `config/functions.txt`
2. Dodaj implementację w `src/app.py`
3. Zaktualizuj `TOOL_FUNCTIONS` mapping
4. Przetestuj funkcjonalność

## 📚 Dokumentacja

- [📖 Przewodnik instalacji](docs/installation/ttki_quickstart_guide.md)
- [🏗️ Architektura systemu](docs/architecture/system_architecture_design.md)
- [🔧 Integracja Gemini](docs/installation/gemini_integration_guide.md)
- [🧪 Testowanie](docs/testing/TESTING_README.md)

## 🤝 Współpraca

Zapraszamy do współpracy! Aby dodać funkcjonalność:

1. Fork repozytorium
2. Utwórz branch funkcji (`git checkout -b feature/AmazingFeature`)
3. Commit zmian (`git commit -m 'Add some AmazingFeature'`)
4. Push do brancha (`git push origin feature/AmazingFeature`)
5. Otwórz Pull Request

## 🐛 Zgłaszanie problemów

Jeśli napotkasz problemy:

1. Sprawdź [Issues](https://github.com/yourusername/ttki-cli/issues)
2. Uruchom `./ttki.sh status` dla diagnostyki
3. Sprawdź logi: `./ttki.sh logs`
4. Utwórz nowy Issue z opisem problemu

## 📦 Zależności

### Python packages
```
flask>=2.0.0
flask-socketio>=5.0.0
google-generativeai>=0.3.0
```

### System packages
```
tigervnc-standalone-server
tigervnc-viewer
python3-websockify
```

## 🔄 Changelog

### v0.2.0 (2025-08-31)
- ✅ Reorganizacja struktury projektu na profesjonalną
- ✅ Zmiana nazw plików konfiguracyjnych (prompt.txt, functions.txt)
- ✅ Refaktoryzacja nazw funkcji AI
- ✅ Dodanie README.md i licencji MIT
- ✅ Utworzenie requirements.txt
- ✅ Usprawnienie skryptów zarządzających

### v0.1.0 (2025-08-31)
- ✅ Pierwsza wersja robocza
- ✅ AI Terminal z Google Gemini
- ✅ VNC Desktop integration
- ✅ Podstawowe skrypty zarządzające

## 📄 Licencja

Ten projekt jest licencjonowany na licencji MIT - szczegóły w pliku [LICENSE](LICENSE).

```
Copyright (c) 2025 TTKi-cli Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

## 👨‍💻 Autor

**TTKi** - *Initial work*

## 🙏 Podziękowania

- Google Gemini AI za potężne API
- noVNC team za excellent web VNC client
- TigerVNC za reliable VNC server
- Flask community za amazing web framework

## 📧 Kontakt

- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

---

⭐ **Jeśli projekt Ci się podoba, zostaw gwiazdkę!** ⭐
