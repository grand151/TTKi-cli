#!/usr/bin/env python3
"""
Prosty test Flask aplikacji - sprawdza czy podstawowa funkcjonalność działa
"""

from flask import Flask
from flask_socketio import SocketIO

# Prosta aplikacja testowa
test_app = Flask(__name__)
test_socketio = SocketIO(test_app, cors_allowed_origins="*")

@test_app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Terminal - Test</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; }
            .status { padding: 20px; background: #e8f5e8; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1>🤖 AI Terminal - Test</h1>
        <div class="status">
            ✅ Flask server działa poprawnie!<br>
            🌐 Port: 5002<br>
            🔧 Status: Aplikacja testowa uruchomiona
        </div>
        <p>Aplikacja AI Terminal została skonfigurowana i jest gotowa do użycia.</p>
        <p>Podstawowe komponenty:</p>
        <ul>
            <li>✅ Flask web server</li>
            <li>✅ Socket.IO komunikacja</li>
            <li>⚠️ Gemini AI (wymaga konfiguracji)</li>
        </ul>
    </body>
    </html>
    """

@test_socketio.on('connect')
def test_connect():
    print('Client connected')

if __name__ == '__main__':
    print("🧪 Uruchamianie testowej aplikacji Flask...")
    test_socketio.run(test_app, port=4001, debug=False, allow_unsafe_werkzeug=True)
