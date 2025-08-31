# Wytyczne Bezpieczeństwa TTKi CLI

## 🔒 Ważne zagadnienia bezpieczeństwa

### Klucze API i dane uwierzytelniające

**NIGDY nie commituj kluczy API do repozytorium git!**

### Bezpieczne zarządzanie kluczami

1. **Użyj pliku .env**:
   ```bash
   cp .env.example .env
   nano .env  # Dodaj swoje prawdziwe klucze
   ```

2. **Plik .env jest w .gitignore** - nie zostanie przypadkowo scommitowany

3. **Alternatywnie ustaw zmienne środowiskowe**:
   ```bash
   export GEMINI_API_KEY="twój_prawdziwy_klucz"
   export FLASK_SECRET_KEY="bezpieczny_losowy_ciąg"
   ```

### Komponenty wymagające uwagi

- **Google Gemini API Key**: Wymagany do funkcjonowania AI
- **Flask Secret Key**: Potrzebny do bezpieczeństwa sesji
- **VNC hasło**: Ustawiane przez `vncpasswd`

### Jeśli przypadkowo scommitowałeś klucze

1. **Natychmiast odwołaj klucze API** w odpowiednich serwisach
2. **Wygeneruj nowe klucze**
3. **Użyj git filter-branch lub BFG** do usunięcia z historii
4. **Force push** do zdalnego repozytorium

### Zgłaszanie problemów bezpieczeństwa

Jeśli znajdziesz podatność bezpieczeństwa, proszę zgłoś ją prywatnie poprzez:
- Email: security@example.com
- GitHub Security Advisories

**Nie otwieraj publicznych issue dla problemów bezpieczeństwa!**

## 🛡️ Dobre praktyki

- Regularnie rotuj klucze API
- Używaj różnych kluczy dla środowisk dev/staging/production
- Monitoruj logi aplikacji pod kątem nieautoryzowanych dostępów
- Aktualizuj zależności regularnie (`pip audit`)
- Używaj HTTPS w środowisku produkcyjnym

## 📋 Lista kontrolna bezpieczeństwa

- [ ] Plik .env nie jest w git
- [ ] Klucze API są unikalne dla każdego środowiska
- [ ] VNC ma ustawione silne hasło
- [ ] Flask SECRET_KEY jest losowy i bezpieczny
- [ ] Aplikacja działa za proxy/firewall w produkcji
- [ ] Logi nie zawierają poufnych danych
