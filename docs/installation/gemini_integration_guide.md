# Instrukcje integracji z Gemini API

Ten przewodnik wyjaśnia, jak zintegrować Gemini API z aplikacją TTKi Computer w celu korzystania z modelu `gemini-2.5-flash` z własnym promptem.

## Krok 1: Instalacja biblioteki Gemini API

Najpierw należy zainstalować oficjalną bibliotekę Pythona od Google dla Gemini API. Uruchom następującą komendę w terminalu, upewniając się, że używasz pip z wirtualnego środowiska:

```bash
venv/bin/pip install google-generativeai
```

## Krok 2: Konfiguracja klucza API

1.  Zdobądź klucz API z [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Ustaw klucz API jako zmienną środowiskową. W terminalu, w którym uruchamiasz aplikację, wykonaj następującą komendę, zastępując "TWOJ_KLUCZ_API" swoim kluczem:

    ```bash
    export GEMINI_API_KEY="TWOJ_KLUCZ_API"
    ```

    **Ważne:** Nie umieszczaj klucza API bezpośrednio w kodzie źródłowym.

## Krok 3: Modyfikacja pliku `app.py`

Zastąp zawartość pliku `app.py` poniższym kodem. Wprowadza on następujące zmiany:

*   Importuje niezbędne biblioteki: `os` i `google.generativeai`.
*   Konfiguruje klienta Gemini API przy użyciu klucza API ze zmiennej środowiskowej.
*   Definiuje zmienną `GEMINI_PROMPT`, w której możesz umieścić swój własny prompt.
*   Modyfikuje funkcję `handle_message`, aby wysyłała zapytanie do Gemini API z promptem i wiadomością od użytkownika.
*   Odpowiedź z Gemini API jest traktowana jako komenda do wykonania w piaskownicy.

```python
import os
import subprocess
import google.generativeai as genai
from flask import Flask, render_template
from flask_socketio import SocketIO

# Konfiguracja Gemini API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

# --- MODYFIKUJ TEN PROMPT ---
GEMINI_PROMPT = """
Jesteś asystentem programistycznym AI działającym wewnątrz bezpiecznej piaskownicy Ubuntu. 
Twoim zadaniem jest odpowiadanie na polecenia użytkownika, generując wyłącznie komendy powłoki bash, które zostaną wykonane w tej piaskownicy. 
Nie dodawaj żadnych wyjaśnień, opisów ani formatowania markdown. Odpowiadaj tylko i wyłącznie komendą.

Przykład:
Użytkownik: "Pokaż mi listę plików w bieżącym katalogu."
Twoja odpowiedź: ls -l

Użytkownik: {user_message}
Twoja odpowiedź:
"""

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

def execute_in_sandbox(command):
    try:
        result = subprocess.run(
            ['docker', 'exec', 'ttki-computer-container', 'bash', '-c', command],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)

@socketio.on('connect')
def handle_connect():
    print('client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('client disconnected')

@socketio.on('message')
def handle_message(message):
    print(f'received message: {message}')

    # Wygeneruj komendę za pomocą Gemini API
    try:
        prompt = GEMINI_PROMPT.format(user_message=message)
        response = model.generate_content(prompt)
        command_to_execute = response.text.strip()
    except Exception as e:
        socketio.emit('message', f"Błąd podczas komunikacji z Gemini API: {e}")
        return

    print(f'executing command: {command_to_execute}')
    output = execute_in_sandbox(command_to_execute)
    socketio.emit('message', f"> {command_to_execute}\n{output}")

if __name__ == '__main__':
    socketio.run(app, debug=True)

```

## Krok 4: Uruchomienie aplikacji

1.  Upewnij się, że ustawiłeś zmienną środowiskową `GEMINI_API_KEY` (Krok 2).
2.  Zatrzymaj poprzednią instancję aplikacji, jeśli jest uruchomiona.
3.  Uruchom aplikację ponownie:

    ```bash
    venv/bin/python app.py &
    ```

Teraz możesz otworzyć interfejs webowy pod adresem `http://127.0.0.1:5000` i zacząć wydawać polecenia w języku naturalnym. Aplikacja będzie używać Gemini API do tłumaczenia Twoich poleceń na komendy powłoki i wykonywania ich w piaskownicy.
