#!/usr/bin/env python3
"""
Simple HTTP server for TTKi-cli landing page
Serves index.html on port 4000
"""
import http.server
import socketserver
import os
import sys

class LandingPageHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '':
            self.path = '/index.html'
        return super().do_GET()

def main():
    PORT = 4000
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)  # Parent directory
    os.chdir(project_dir)
    
    # Check if index.html exists
    if not os.path.exists('index.html'):
        print("❌ Error: index.html not found in project directory")
        sys.exit(1)
    
    try:
        with socketserver.TCPServer(("", PORT), LandingPageHandler) as httpd:
            print(f"🏠 Landing Page server started on port {PORT}")
            print(f"📁 Serving from: {os.getcwd()}")
            print(f"🌐 Access at: http://localhost:{PORT}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Landing Page server stopped")
    except OSError as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
