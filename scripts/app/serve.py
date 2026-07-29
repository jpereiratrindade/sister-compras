#!/usr/bin/env python3
import http.server
import socketserver
import sys
import os
import json

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8002
WEB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../web'))
STORAGE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../storage/compras_data.json'))

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        if self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            if os.path.exists(STORAGE_FILE):
                with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            else:
                fallback = {
                    "version": "0.2.0",
                    "projects": [{"id": "PROJ-PESQUISA-01", "name": "Projeto de Pesquisa e Desenvolvimento Tecnológico", "lead_researcher": "Pesquisador Responsável"}],
                    "needs": [],
                    "decisions": []
                }
                self.wfile.write(json.dumps(fallback, ensure_ascii=False).encode('utf-8'))
            return
        return super().do_GET()

class ReuseTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == '__main__':
    os.chdir(WEB_DIR)
    socketserver.TCPServer.allow_reuse_address = True
    with ReuseTCPServer(("", PORT), CustomHandler) as httpd:
        print(f"[SisTer-Compras Web Server] Executando em http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[SisTer-Compras Web Server] Encerrado.")
