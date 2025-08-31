#!/bin/bash

# Script zabezpieczający pliki Manus przed przypadkowym usunięciem
# Użycie: ./secure_manus.sh

echo "🔒 Zabezpieczanie plików konfiguracyjnych..."

# Sprawdzanie czy pliki istnieją
if [ ! -f "config/prompt.txt" ] || [ ! -f "config/functions.txt" ]; then
    echo "❌ Błąd: Pliki konfiguracyjne nie istnieją!"
    echo "Sprawdź folder config/backup/ lub przywróć z Git"
    exit 1
fi

# Ustawianie uprawnień tylko do odczytu
chmod 444 config/prompt.txt config/functions.txt
echo "✅ Ustawiono uprawnienia tylko do odczytu"

# Tworzenie kopii zapasowych
if [ ! -d "config/backup" ]; then
    mkdir config/backup
fi

cp config/prompt.txt config/functions.txt config/backup/
chmod 444 config/backup/prompt.txt config/backup/functions.txt
echo "✅ Utworzono kopie zapasowe w folderze config/backup/"

# Commit do Git jeśli repozytorium istnieje
if [ -d ".git" ]; then
    git add config/prompt.txt config/functions.txt
    git commit -m "Aktualizacja zabezpieczonych plików konfiguracyjnych - $(date)"
    echo "✅ Zapisano w Git"
fi

echo "🎉 Pliki konfiguracyjne zostały zabezpieczone!"
echo ""
echo "Sposoby przywracania w przypadku utraty:"
echo "1. Z folderu config/backup/: cp config/backup/*.txt config/"
echo "2. Z Git: git checkout config/prompt.txt config/functions.txt"
echo "3. Ponownie uruchom: ./scripts/secure_manus.sh"
