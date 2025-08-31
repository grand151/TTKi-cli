#!/usr/bin/env python3
"""
TTKi-cli Landing Page
Simple landing page for TTKi AI Terminal environment
"""

from flask import Flask, render_template_string
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key')

# Simple landing page template
LANDING_TEMPLATE = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TTKi-cli - AI Desktop Environment</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .container {
            text-align: center;
            max-width: 800px;
            padding: 40px 20px;
        }

        .logo {
            font-size: 4rem;
            font-weight: bold;
            margin-bottom: 1rem;
            background: linear-gradient(45deg, #00f5ff, #ff00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .subtitle {
            font-size: 1.5rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }

        .description {
            font-size: 1.1rem;
            margin-bottom: 3rem;
            line-height: 1.6;
            opacity: 0.8;
        }

        .services {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }

        .service-card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 2rem;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .service-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }

        .service-card h3 {
            font-size: 1.3rem;
            margin-bottom: 1rem;
            color: #00f5ff;
        }

        .service-card p {
            opacity: 0.8;
            margin-bottom: 1rem;
        }

        .service-btn {
            display: inline-block;
            padding: 12px 24px;
            background: linear-gradient(45deg, #00f5ff, #ff00ff);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            transition: all 0.3s ease;
        }

        .service-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(0, 245, 255, 0.4);
        }

        .footer {
            margin-top: 3rem;
            opacity: 0.6;
            font-size: 0.9rem;
        }

        @media (max-width: 768px) {
            .logo {
                font-size: 2.5rem;
            }
            
            .subtitle {
                font-size: 1.2rem;
            }
            
            .services {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">TTKi-cli</div>
        <div class="subtitle">AI Desktop Environment</div>
        <div class="description">
            Nowoczesne środowisko pracy łączące sztuczną inteligencję z pełnoprawnym systemem desktop. 
            Pracuj z AI asystentem i Ubuntu desktop w jednym interfejsie.
        </div>

        <div class="services">
            <div class="service-card">
                <h3>🤖 AI Terminal + Desktop</h3>
                <p>Kompletny interfejs łączący AI chat z Ubuntu desktop w jednym oknie (split-screen)</p>
                <a href="http://localhost:4001" class="service-btn">Otwórz Pełny Interface</a>
            </div>

            <div class="service-card">
                <h3>🖥️ Tylko Desktop VNC</h3>
                <p>Samodzielny Ubuntu desktop z VS Code, Firefox, narzędziami deweloperskimi</p>
                <a href="http://localhost:4051" class="service-btn">Otwórz Tylko Desktop</a>
            </div>

            <div class="service-card">
                <h3>� Status Systemu</h3>
                <p>Sprawdź status wszystkich serwisów, porty, zdrowie aplikacji</p>
                <a href="http://localhost:4001/health" class="service-btn">Sprawdź Status</a>
            </div>
        </div>

        <div class="footer">
            <p>TTKi-cli v0.2.1 | Powered by Google Gemini AI & Docker</p>
            <p>🔗 VNC Direct: localhost:5950 | 🏥 Health: <a href="http://localhost:4001/health">localhost:4001/health</a></p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def landing():
    return render_template_string(LANDING_TEMPLATE)

@app.route('/health')
def health():
    return {
        "service": "ttki-landing",
        "status": "healthy",
        "version": "0.2.1",
        "services": {
            "ai_terminal": "http://localhost:4001",
            "vnc_desktop": "http://localhost:4051", 
            "vnc_direct": "localhost:5950"
        }
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 4000))
    app.run(host='0.0.0.0', port=port, debug=False)
