# TTKi-cli QuickStart Guide

## Wprowadzenie

Przewodnik po szybkim uruchomieniu TTKi-cli - systemu terminal AI z interfejsem VNC.

TTKi-cli to inteligentny system terminala, który łączy tradycyjne polecenia z możliwościami sztucznej inteligencji oraz dostępem do środowiska graficznego przez VNC.

## Co będziesz potrzebować

* Przeglądarkę internetową (Chrome, Firefox, Edge, etc.)
* 10–15 minut czasu
* Terminal Linux/Unix
* Python 3.x

## Część 1: Uruchomienie TTKi-cli

Oto jak uruchomić swój pierwszy system TTKi-cli:

1. W terminalu przejdź do folderu TTKi-cli
2. Uruchom system: `./ttki.sh start`
3. Otwórz przeglądarkę i przejdź do http://localhost:4000
4. Kliknij "Otwórz AI Terminal" lub przejdź bezpośrednio do http://localhost:4001
5. Kliknij "Otwórz Pulpit" lub przejdź do http://localhost:4051 dla środowiska VNC
6. Zacznij korzystać z AI terminala!

Gratulacje! Właśnie uruchomiłeś swój pierwszy TTKi-cli!

## Jak działają tokeny w AI

TTKi-cli wykorzystuje technologię dużych modeli językowych (LLM) do przetwarzania poleceń i budowania inteligentnych odpowiedzi terminala. System używa tokenów gdy:

* Czyta polecenia użytkownika
* Analizuje kontekst
* Generuje odpowiedzi

## Część 2: Korzystanie z AI Terminal

Teraz gdy TTKi-cli jest uruchomiony, spróbuj następujących funkcji:

1. W AI Terminal (http://localhost:4001) wpisz polecenie
2. Obserwuj jak AI interpretuje twoje polecenia
3. Sprawdź dostęp do pulpitu VNC przez http://localhost:4051
4. Eksperymentuj z różnymi poleceniami i interakcjami

### Przykłady poleceń do wypróbowania:

* `ls -la` - listowanie plików
* `pwd` - aktualna ścieżka
* `ps aux` - procesy systemowe
* Dowolne polecenia systemowe

## Część 3: Zarządzanie systemem

TTKi-cli oferuje wygodne polecenia zarządzania:

```bash
./ttki.sh start    # Uruchom wszystkie usługi
./ttki.sh stop     # Zatrzymaj wszystkie usługi  
./ttki.sh restart  # Restart systemu
./ttki.sh status   # Sprawdź status usług
./ttki.sh clean    # Wyczyść procesy
```

## Część 4: Konfiguracja

System TTKi-cli można dostosować:

* Porty usług w pliku `ports.conf`
* Konfiguracja AI w plikach Manus
* Ustawienia VNC w skryptach systemowych

## Rozwiązywanie problemów

Jeśli napotkasz problemy:

1. Sprawdź status: `./ttki.sh status`
2. Sprawdź logi: `./ttki.sh logs`
3. Restart systemu: `./ttki.sh restart`
4. Wyczyść procesy: `./ttki.sh clean`

## Następne kroki

Gratulacje! Teraz jesteś częścią społeczności TTKi-cli! Możesz:

* Eksplorować różne funkcje AI terminala
* Dostosować konfigurację w plikach systemu
* Rozwijać własne rozszerzenia i funkcjonalności
* Korzystać z środowiska VNC do pracy graficznej
* Zabezpieczyć swoje pliki konfiguracyjne

## Funkcje bezpieczeństwa

TTKi-cli zawiera zabezpieczenia:

* Ochrona plików Manus przed przypadkowym usunięciem
* Automatyczne kopie zapasowe
* Kontrola wersji przez Git
* Bezpieczne zarządzanie sesjami

## Wsparcie

Jeśli potrzebujesz pomocy:

* Sprawdź dokumentację w folderze `docs/`
* Użyj polecenia `./ttki.sh help`
* Sprawdź logi systemu
* Uruchom diagnostykę statusu

Miłego korzystania z TTKi-cli! 🚀

