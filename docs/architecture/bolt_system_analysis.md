# Analiza systemu budowania Bolt.new

System Bolt.new to platforma do tworzenia stron internetowych i aplikacji oparta na sztucznej inteligencji, która wykorzystuje duże modele językowe (LLM) do generowania kodu i struktury aplikacji na podstawie promptów tekstowych. Kluczowe cechy i mechanizmy działania, które należy wziąć pod uwagę przy klonowaniu tego systemu, to:

## 1. Interfejs oparty na czacie i promptach

Użytkownicy wchodzą w interakcję z systemem poprzez interfejs czatu, wprowadzając prompt opisujący pożądaną aplikację lub zmianę. System interpretuje ten prompt i generuje odpowiednie elementy aplikacji. To wymaga solidnego silnika przetwarzania języka naturalnego (NLP) i integracji z modelem LLM.

## 2. Tryby działania: Build Mode i Discussion Mode

*   **Build Mode**: Główny tryb, w którym system generuje lub modyfikuje kod aplikacji na podstawie promptów. Jest to tryb intensywnie wykorzystujący tokeny, ponieważ wiąże się z faktycznym tworzeniem lub przebudową aplikacji.
*   **Discussion Mode**: Tryb do burzy mózgów i uzyskiwania porad, który zużywa znacznie mniej tokenów (około 90% mniej). Jest to tryb konwersacyjny, służący do planowania, zadawania pytań i uzyskiwania sugestii bez faktycznego generowania kodu. Wskazuje to na wykorzystanie lżejszych lub bardziej zoptymalizowanych interakcji z LLM w tym trybie.

## 3. Zarządzanie tokenami

System śledzi zużycie tokenów, co jest kluczowe dla planów darmowych i płatnych. Tokeny są zużywane podczas czytania promptów, 


myślenia (przetwarzania promptów przez LLM) i budowania (generowania kodu). Kluczowe jest zrozumienie, jak Bolt optymalizuje zużycie tokenów i jak to wpływa na koszt i wydajność.

## 4. Generowanie i modyfikacja aplikacji

Bolt jest w stanie generować całe aplikacje od podstaw na podstawie promptów, a także modyfikować istniejące aplikacje (np. zmieniać schematy kolorów). To sugeruje, że system ma zdolność do interpretowania promptów na poziomie wysokopoziomowym i przekształcania ich w konkretne zmiany w kodzie lub konfiguracji aplikacji.

## 5. Podgląd i wersjonowanie

System oferuje podgląd tworzonej aplikacji w czasie rzeczywistym. Posiada również funkcję historii wersji, która pozwala na przywracanie poprzednich stanów aplikacji bez zużycia dodatkowych tokenów. To wskazuje na istnienie systemu kontroli wersji, który przechowuje migawki projektu.

## 6. Publikacja i hosting

Bolt umożliwia publikację stworzonych aplikacji za pomocą wbudowanego hostingu. To oznacza, że system integruje się z procesem wdrażania i udostępniania aplikacji online.

## 7. Integracje

Bolt integruje się z narzędziami takimi jak Figma i GitHub, co sugeruje możliwość importowania projektów lub synchronizacji kodu z zewnętrznymi repozytoriami.

## 8. Technologie bazowe

Chociaż dokumentacja nie wchodzi w szczegóły techniczne, jasno wynika, że Bolt opiera się na dużych modelach językowych (LLM) do generowania kodu. Prawdopodobnie wykorzystuje również frameworki webowe (np. React, Vue, Angular) do budowania frontendu i odpowiednie technologie backendowe do obsługi logiki i bazy danych.

## Wnioski do klonowania systemu:

Aby sklonować system podobny do Bolt.new, będziemy potrzebować:

*   **Silnika LLM**: Do przetwarzania promptów i generowania kodu. Możemy wykorzystać Gemini API, tak jak zaktualizowałem aplikację terminala.
*   **Interfejsu czatu**: Do interakcji z użytkownikiem.
*   **Systemu zarządzania projektem**: Do przechowywania i wersjonowania kodu aplikacji.
*   **Mechanizmu generowania kodu**: Który będzie tłumaczył instrukcje LLM na konkretny kod (np. HTML, CSS, JavaScript, Python, itp.).
*   **Środowiska podglądu**: Do wyświetlania tworzonej aplikacji.
*   **Systemu wdrażania/hostingu**: Do publikacji aplikacji.
*   **Systemu zarządzania tokenami**: Do śledzenia zużycia zasobów LLM.

Następnym krokiem będzie zaprojektowanie architektury naszego systemu budowania, uwzględniając te elementy.

