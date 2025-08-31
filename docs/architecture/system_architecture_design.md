# TTKi-cli - Projekt Architektury Systemu Terminal AI

## Wprowadzenie

Niniejszy dokument przedstawia projekt architektury systemu terminal AI TTKi-cli. Celem jest stworzenie elastycznego i skalowalnego rozwiązania, które umożliwi użytkownikom interakcję z terminalem za pomocą sztucznej inteligencji oraz dostęp do środowiska pulpitu przez VNC. Architektura uwzględnia kluczowe aspekty, takie jak przetwarzanie języka naturalnego, wykonywanie poleceń, zarządzanie sesjami oraz interfejs webowy.

## 1. Przegląd Architektury

System będzie składał się z kilku głównych komponentów, współpracujących ze sobą w celu zapewnienia kompleksowej funkcjonalności. Poniżej przedstawiono ogólny schemat architektury:

```mermaid
graph TD
    A[Użytkownik] --> B(Interfejs Użytkownika: Aplikacja Webowa/Terminalowa)
    B --> C{API Gateway}
    C --> D[Serwis LLM Proxy]
    D --> E[Model LLM (np. Gemini API)]
    C --> F[Serwis Zarządzania Projektem]
    F --> G[Baza Danych Projektów (np. NoSQL/SQL)]
    C --> H[Serwis Generowania Kodu]
    H --> I[Repozytorium Szablonów Kodu]
    C --> J[Serwis Wersjonowania i Historii]
    J --> G
    C --> K[Serwis Podglądu i Deployu]
    K --> L[Środowisko Sandbox/Hosting]
    K --> M[Serwis Monitorowania Tokenów]
    M --> G
```

## 2. Kluczowe Komponenty i Ich Funkcjonalności

### 2.1. Interfejs Użytkownika (UI)

Interfejs użytkownika będzie głównym punktem interakcji dla użytkowników. Będzie dostępny zarówno jako aplikacja webowa, jak i opcjonalnie jako aplikacja terminalowa (jak ta, którą stworzyliśmy wcześniej). Kluczowe funkcjonalności UI to:

*   **Chatbox**: Główny element do wprowadzania promptów tekstowych i wyświetlania odpowiedzi od AI.
*   **Podgląd Aplikacji**: Dynamiczny podgląd generowanej lub modyfikowanej aplikacji webowej w czasie rzeczywistym.
*   **Historia Czatu i Wersji**: Możliwość przeglądania poprzednich interakcji i przywracania wcześniejszych wersji projektu.
*   **Zarządzanie Projektem**: Interfejs do tworzenia, otwierania, zapisywania i usuwania projektów.
*   **Ustawienia**: Konfiguracja API kluczy, preferencji użytkownika, itp.

### 2.2. API Gateway

API Gateway będzie pojedynczym punktem wejścia dla wszystkich żądań z interfejsu użytkownika. Będzie odpowiedzialny za:

*   **Routing Żądań**: Przekierowywanie żądań do odpowiednich serwisów backendowych.
*   **Autoryzacja i Autentykacja**: Zapewnienie bezpieczeństwa poprzez weryfikację tożsamości użytkowników i ich uprawnień.
*   **Limitowanie Żądań (Rate Limiting)**: Ochrona przed nadmiernym obciążeniem serwisów.
*   **Transformacja Danych**: Konwersja formatów danych między UI a serwisami backendowymi.

### 2.3. Serwis LLM Proxy

Ten serwis będzie pośredniczył w komunikacji z zewnętrznym modelem LLM (np. Gemini API). Jego główne zadania to:

*   **Abstrakcja LLM**: Ukrycie szczegółów implementacyjnych konkretnego API LLM, umożliwiając łatwą zmianę dostawcy LLM w przyszłości.
*   **Zarządzanie Kluczami API**: Bezpieczne przechowywanie i używanie kluczy API LLM.
*   **Formatowanie Promptów**: Przygotowywanie promptów w formacie oczekiwanym przez model LLM.
*   **Parsowanie Odpowiedzi**: Przetwarzanie odpowiedzi z LLM i przekazywanie ich do innych serwisów.
*   **Zarządzanie Trybami (Build/Discussion)**: Implementacja logiki przełączania między trybami Build Mode i Discussion Mode, potencjalnie wykorzystując różne modele LLM lub różne konfiguracje promptów dla optymalizacji tokenów.

### 2.4. Model LLM (np. Gemini API)

Zewnętrzny duży model językowy, który będzie sercem systemu. Będzie odpowiedzialny za:

*   **Generowanie Kodu**: Tworzenie fragmentów kodu, całych komponentów lub nawet kompletnych aplikacji na podstawie promptów.
*   **Generowanie Treści**: Tworzenie tekstów, opisów, komentarzy do kodu, itp.
*   **Analiza i Sugestie**: Zapewnianie porad, rozwiązań problemów i sugestii dotyczących projektu.

### 2.5. Serwis Zarządzania Projektem

Ten serwis będzie odpowiedzialny za zarządzanie cyklem życia projektów użytkowników. Funkcjonalności obejmują:

*   **Tworzenie/Usuwanie Projektów**: Inicjowanie nowych projektów i usuwanie istniejących.
*   **Zapisywanie/Ładowanie Projektów**: Trwałe przechowywanie stanu projektu w bazie danych.
*   **Zarządzanie Plikami Projektu**: Przechowywanie i organizowanie plików kodu, zasobów i konfiguracji dla każdego projektu.

### 2.6. Baza Danych Projektów

Baza danych będzie przechowywać wszystkie dane związane z projektami, w tym:

*   **Metadane Projektu**: Nazwa, właściciel, data utworzenia, itp.
*   **Pliki Projektu**: Kod źródłowy, zasoby, konfiguracje (prawdopodobnie przechowywane jako BLOBy lub ścieżki do systemu plików/obiektowego magazynu).
*   **Historia Wersji**: Migawki projektu w różnych punktach czasowych.
*   **Dane Użytkowników**: Informacje o użytkownikach i ich subskrypcjach.
*   **Dane o Zużyciu Tokenów**: Logi zużycia tokenów dla każdego użytkownika i projektu.

Można rozważyć użycie bazy danych NoSQL (np. MongoDB, Cassandra) dla elastyczności w przechowywaniu struktury projektu lub relacyjnej bazy danych (np. PostgreSQL) dla bardziej ustrukturyzowanych danych.

### 2.7. Serwis Generowania Kodu

Ten serwis będzie odpowiedzialny za interpretację instrukcji z LLM i przekształcanie ich w rzeczywisty kod. Będzie działał jako warstwa abstrakcji między ogólnymi instrukcjami LLM a konkretnymi frameworkami i językami programowania. Funkcjonalności to:

*   **Parsowanie Instrukcji LLM**: Analiza odpowiedzi z LLM w celu wyodrębnienia instrukcji dotyczących generowania lub modyfikacji kodu.
*   **Generowanie Szablonów**: Wykorzystanie predefiniowanych szablonów kodu (np. dla React, Vue, HTML/CSS) do szybkiego tworzenia struktury aplikacji.
*   **Modyfikacja Kodu**: Inteligentne wstawianie, usuwanie lub modyfikowanie fragmentów kodu w istniejących plikach projektu.
*   **Walidacja Kodu**: Podstawowa walidacja składniowa generowanego kodu.

### 2.8. Repozytorium Szablonów Kodu

Będzie to zbiór predefiniowanych szablonów kodu, komponentów i fragmentów, które Serwis Generowania Kodu będzie wykorzystywał do budowania aplikacji. Szablony mogą być zorganizowane według technologii (np. React, Vue, Flask) i typu komponentu (np. przyciski, formularze, nawigacja).

### 2.9. Serwis Wersjonowania i Historii

Ten serwis będzie odpowiedzialny za zarządzanie historią zmian w projektach. Kluczowe funkcjonalności to:

*   **Tworzenie Migawki (Snapshot)**: Zapisywanie stanu projektu w określonym momencie (np. po każdej znaczącej zmianie wygenerowanej przez AI).
*   **Przywracanie Wersji**: Umożliwienie użytkownikom powrotu do wcześniejszych wersji projektu.
*   **Porównywanie Wersji**: Opcjonalnie, wizualne porównywanie zmian między wersjami.

### 2.10. Serwis Podglądu i Deployu

Ten serwis będzie odpowiedzialny za kompilację, podgląd i wdrażanie aplikacji. Funkcjonalności obejmują:

*   **Kompilacja/Bundling**: Przygotowanie kodu aplikacji do uruchomienia (np. za pomocą Webpack, Parcel).
*   **Środowisko Sandbox**: Izolowane środowisko do uruchamiania i podglądu generowanych aplikacji w bezpieczny sposób.
*   **Hosting**: Wdrażanie skompilowanych aplikacji na serwerach publicznych, udostępniając je pod unikalnymi adresami URL.
*   **Zarządzanie Domenami**: Opcjonalnie, wsparcie dla niestandardowych domen.

### 2.11. Serwis Monitorowania Tokenów

Ten serwis będzie śledził i zarządzał zużyciem tokenów przez użytkowników. Funkcjonalności to:

*   **Logowanie Zużycia**: Rejestrowanie każdego żądania do LLM i przypisywanie mu zużycia tokenów.
*   **Limitowanie Zużycia**: Egzekwowanie limitów tokenów dla różnych planów subskrypcji (np. darmowy, płatny).
*   **Raportowanie**: Generowanie raportów o zużyciu tokenów dla użytkowników i administratorów.

## 3. Przepływ Danych (Przykład: Generowanie Nowej Aplikacji)

1.  Użytkownik wprowadza prompt (np. 


"`Build a simple to-do list app with add, edit, and delete functionality.`") do interfejsu użytkownika.
2.  Interfejs użytkownika wysyła żądanie do API Gateway.
3.  API Gateway uwierzytelnia użytkownika i przekazuje żądanie do Serwisu LLM Proxy.
4.  Serwis LLM Proxy formatuje prompt i wysyła go do Modelu LLM (Gemini API).
5.  Model LLM generuje kod źródłowy aplikacji (np. HTML, CSS, JavaScript) na podstawie promptu.
6.  Serwis LLM Proxy odbiera wygenerowany kod i przekazuje go z powrotem do API Gateway.
7.  API Gateway przekazuje kod do Serwisu Generowania Kodu.
8.  Serwis Generowania Kodu zapisuje wygenerowany kod w systemie plików projektu, zarządzanym przez Serwis Zarządzania Projektem, który z kolei przechowuje dane w Bazie Danych Projektów.
9.  Serwis Wersjonowania i Historii tworzy nową migawkę projektu, rejestrując wygenerowany kod jako nową wersję.
10. Serwis Podglądu i Deployu kompiluje i wdraża aplikację w środowisku sandbox. 
11. Interfejs użytkownika wyświetla podgląd nowo wygenerowanej aplikacji.
12. Serwis Monitorowania Tokenów rejestruje zużycie tokenów przez Model LLM dla tej operacji.

## 4. Przepływ Danych (Przykład: Modyfikacja Istniejącej Aplikacji)

1.  Użytkownik wprowadza prompt (np. "`Change the color scheme to dark mode.`") do interfejsu użytkownika.
2.  Interfejs użytkownika wysyła żądanie do API Gateway.
3.  API Gateway uwierzytelnia użytkownika i przekazuje żądanie do Serwisu LLM Proxy.
4.  Serwis LLM Proxy formatuje prompt i wysyła go do Modelu LLM (Gemini API).
5.  Model LLM generuje instrukcje modyfikacji kodu (np. zmiany w plikach CSS lub JavaScript) na podstawie promptu.
6.  Serwis LLM Proxy odbiera instrukcje i przekazuje je z powrotem do API Gateway.
7.  API Gateway przekazuje instrukcje do Serwisu Generowania Kodu.
8.  Serwis Generowania Kodu modyfikuje istniejące pliki projektu zgodnie z instrukcjami, zarządzanymi przez Serwis Zarządzania Projektem i przechowywanymi w Bazie Danych Projektów.
9.  Serwis Wersjonowania i Historii tworzy nową migawkę projektu, rejestrując zmodyfikowany kod jako nową wersję.
10. Serwis Podglądu i Deployu ponownie kompiluje i wdraża zaktualizowaną aplikację w środowisku sandbox.
11. Interfejs użytkownika odświeża podgląd zaktualizowanej aplikacji.
12. Serwis Monitorowania Tokenów rejestruje zużycie tokenów przez Model LLM dla tej operacji.

## 5. Wybór Technologii (Propozycje)

### 5.1. Frontend (Interfejs Użytkownika)

*   **Framework**: React.js lub Vue.js (dla aplikacji webowej) – zapewniają komponentową strukturę i bogate ekosystemy.
*   **Stylizacja**: Tailwind CSS lub Styled Components – dla szybkiego i elastycznego tworzenia interfejsu.

### 5.2. Backend (Serwisy)

*   **Język Programowania**: Python (ze względu na łatwość integracji z LLM i bogactwo bibliotek AI) lub Node.js (dla asynchronicznych operacji I/O).
*   **Framework**: Flask (Python) lub Express.js (Node.js) – dla budowy lekkich i skalowalnych mikroserwisów.
*   **API Gateway**: Nginx lub Kong – dla routingu, autoryzacji i zarządzania ruchem.

### 5.3. Baza Danych

*   **Projekty i Wersje**: MongoDB (NoSQL) – dla elastycznego przechowywania struktury projektu i migawek. Alternatywnie PostgreSQL z rozszerzeniem JSONB.
*   **Użytkownicy i Tokeny**: PostgreSQL (SQL) – dla ustrukturyzowanych danych użytkowników i logów tokenów.

### 5.4. Środowisko Uruchomieniowe i Hosting

*   **Konteneryzacja**: Docker – dla izolacji i łatwego wdrażania poszczególnych serwisów.
*   **Orkiestracja**: Kubernetes (dla skalowalności i zarządzania klastrem) – opcjonalnie, w zależności od skali projektu.
*   **Hosting**: Chmura publiczna (np. Google Cloud Platform, AWS, Azure) – dla skalowalności i dostępności.

## 6. Aspekty Bezpieczeństwa

*   **Uwierzytelnianie i Autoryzacja**: Implementacja standardowych protokołów OAuth2/JWT dla bezpiecznego dostępu do API.
*   **Zarządzanie Kluczami API**: Bezpieczne przechowywanie kluczy API LLM (np. w zmiennych środowiskowych, systemach zarządzania sekretami).
*   **Walidacja Danych Wejściowych**: Dokładna walidacja wszystkich danych wejściowych od użytkownika, aby zapobiec atakom typu injection.
*   **Izolacja Środowiska Sandbox**: Zapewnienie, że kod generowany przez AI jest uruchamiany w bezpiecznym, izolowanym środowisku, aby zapobiec potencjalnym zagrożeniom bezpieczeństwa.

## 7. Skalowalność i Wydajność

*   **Mikroserwisy**: Architektura oparta na mikroserwisach ułatwia skalowanie poszczególnych komponentów niezależnie.
*   **Cache'owanie**: Wykorzystanie mechanizmów cache'owania (np. Redis) dla często odczytywanych danych.
*   **Asynchroniczne Przetwarzanie**: Wykorzystanie kolejek wiadomości (np. RabbitMQ, Kafka) dla operacji generowania kodu i deployu, aby nie blokować interfejsu użytkownika.

## 8. Podsumowanie

Przedstawiona architektura stanowi solidną podstawę do rozwoju systemu TTKi-cli. Kluczowe jest skupienie się na modułowości, skalowalności i bezpieczeństwie, a także na efektywnym wykorzystaniu modeli LLM. Następnym etapem będzie dalsze rozwijanie poszczególnych komponentów i funkcjonalności.

