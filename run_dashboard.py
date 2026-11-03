"""
Project Agere - Dashboard Server Launcher
Starts a local web server and opens the interactive dashboard in your default browser.
"""

import sys
import os
import webbrowser
import socket
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

DASHBOARD_DIR = Path(__file__).resolve().parent / "dashboard"

def find_available_port(start_port=8000, max_attempts=50):
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
    return start_port

class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASHBOARD_DIR), **kwargs)

    def end_headers(self):
        # Enable CORS and disable aggressive caching for local development
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

def main():
    if not DASHBOARD_DIR.exists():
        print(f"Error: Dashboard directory {DASHBOARD_DIR} not found.")
        sys.exit(1)

    data_dir = DASHBOARD_DIR / "data"
    if not (data_dir / "derived_aggregates.json").exists():
        print("Data not prepared yet. Running data pipeline first...")
        import subprocess
        subprocess.run([sys.executable, "scripts/prepare_dashboard_data.py"])

    port = find_available_port(8000)
    server_address = ('localhost', port)
    url = f"http://localhost:{port}/"

    print("\n" + "=" * 70)
    print("  PROJECT AGERE - RESEARCH & HARDWARE ANALYTICS DASHBOARD")
    print(f"  Server running at: {url}")
    print("  Press Ctrl+C to stop the server.")
    print("=" * 70 + "\n")

    # Open browser automatically
    try:
        webbrowser.open(url)
    except Exception:
        pass

    httpd = HTTPServer(server_address, CustomHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server. Goodbye!")
        httpd.server_close()

if __name__ == "__main__":
    main()

