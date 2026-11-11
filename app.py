#!/usr/bin/env python3
"""
app.py
Serveur web applicatif pour la Parole du Jour (Paroisse Saint Michel de Houéto) :
- Sert l'interface web studio (index.html, assets, output)
- Expose l'API de synchronisation et génération (/api/generate)
"""
import os
import json
from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse
from scripts.generate_daily import run_pipeline

PORT = int(os.getenv("PORT", 8080))

class ParoleHandler(SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/check":
            query = urllib.parse.parse_qs(parsed.query)
            date_str = query.get("date", [""])[0]
            data_file = f"output/data-{date_str}.json"
            if date_str and os.path.exists(data_file):
                try:
                    with open(data_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    resp = {"exists": True, "data": data}
                except Exception:
                    resp = {"exists": False}
            else:
                resp = {"exists": False}

            resp_bytes = json.dumps(resp, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(resp_bytes)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(resp_bytes)
            return

        super().do_GET()

    def do_POST(self):
        if self.path == "/api/generate":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                params = json.loads(post_data) if post_data else {}
            except Exception:
                params = {}

            date_str = params.get("date")
            try:
                # Vérifier si l'affiche existe déjà pour éviter toute duplication
                data_file = f"output/data-{date_str}.json"
                if date_str and os.path.exists(data_file):
                    with open(data_file, "r", encoding="utf-8") as f:
                        result = json.load(f)
                else:
                    result = run_pipeline(date_str)

                resp_bytes = json.dumps(result, ensure_ascii=False).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(resp_bytes)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(resp_bytes)
            except Exception as e:
                err_dict = {"status": "error", "message": str(e)}
                err_bytes = json.dumps(err_dict, ensure_ascii=False).encode('utf-8')
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Length', str(len(err_bytes)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(err_bytes)
        else:
            self.send_error(404, "Chemin inconnu")

def run():
    print(f"[*] Serveur Parole du Jour prêt sur http://localhost:{PORT}")
    server = HTTPServer(('0.0.0.0', PORT), ParoleHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Arrêt du serveur.")
        server.server_close()

if __name__ == "__main__":
    run()
