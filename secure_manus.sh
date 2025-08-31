#!/bin/bash

# Script zabezpieczający pliki Manus przed przypadkowym usunięciem
# Użycie: ./secure_manus.sh

echo "🔒 Zabezpieczanie plików Manus..."

# Sprawdzanie czy pliki istnieją
if [ ! -f "Manus_Prompt.txt" ] || [ ! -f "Manus_Functions.txt" ]; then
    echo "❌ Błąd: Pliki Manus nie istnieją!"
    echo "Sprawdź folder backup/ lub przywróć z Git"
    exit 1
fi

# Ustawianie uprawnień tylko do odczytu
chmod 444 Manus_Prompt.txt Manus_Functions.txt
echo "✅ Ustawiono uprawnienia tylko do odczytu"

# Tworzenie kopii zapasowych
if [ ! -d "backup" ]; then
    mkdir backup
fi

cp Manus_Prompt.txt Manus_Functions.txt backup/
chmod 444 backup/Manus_Prompt.txt backup/Manus_Functions.txt
echo "✅ Utworzono kopie zapasowe w folderze backup/"

# Commit do Git jeśli repozytorium istnieje
if [ -d ".git" ]; then
    git add Manus_Prompt.txt Manus_Functions.txt
    git commit -m "Aktualizacja zabezpieczonych plików Manus - $(date)"
    echo "✅ Zapisano w Git"
fi

echo "🎉 Pliki Manus zostały zabezpieczone!"
echo ""
echo "Sposoby przywracania w przypadku utraty:"
echo "1. Z folderu backup/: cp backup/Manus_*.txt ."
echo "2. Z Git: git checkout Manus_Prompt.txt Manus_Functions.txt"
echo "3. Ponownie uruchom: ./secure_manus.sh"
