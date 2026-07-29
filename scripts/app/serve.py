#!/usr/bin/env python3
import http.server
import socketserver
import urllib.request
import urllib.error
import sys
import os
import json

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8002
WEB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../web'))
STORAGE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../storage/compras_data.json'))
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")

def load_data():
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "version": "0.2.0",
        "projects": [{"id": "PROJ-PESQUISA-01", "name": "Projeto de Pesquisa e Desenvolvimento Tecnológico", "lead_researcher": "Pesquisador Responsável"}],
        "needs": [],
        "decisions": []
    }

def save_data(data):
    os.makedirs(os.path.dirname(STORAGE_FILE), exist_ok=True)
    with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def fetch_ollama_models():
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            models = [m['name'] for m in data.get('models', [])]
            return models
    except Exception as e:
        print(f"[Ollama] Erro ao consultar modelos locais: {e}")
        return ["qwen2.5:14b", "qwen2.5:7b", "llama3:8b"]

def generate_ollama_analysis(model_name, need_item):
    prompt_text = f"""Você é o Assistente de Compras e Aquisições do SisTer-Compras.
Análise da Necessidade de Pesquisa:
ID: {need_item.get('id')}
Título: {need_item.get('title')}
Categoria: {need_item.get('category')}
Quantidade: {need_item.get('quantity')} | Prioridade: {need_item.get('priority')}
Responsável: {need_item.get('responsible')}

Requisitos Registrados: {json.dumps(need_item.get('requirements', []), ensure_ascii=False)}
Alternativas e Cotações: {json.dumps(need_item.get('alternatives', []), ensure_ascii=False)}

Por favor, elabore:
1. Avaliação de conformidade das cotações em relação aos requisitos.
2. Identificação de lacunas ou pontos de ateno.
3. Minuta de Justificativa Técnica recomendada para a decisão do pesquisador.
Importante: Sua resposta é uma sugestão de IA. A decisão final é exclusivamente humana."""

    payload = {
        "model": model_name,
        "prompt": prompt_text,
        "stream": False
    }

    try:
        req_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/generate",
            data=req_data,
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=90) as resp:
            res_data = json.loads(resp.read().decode('utf-8'))
            return res_data.get('response', 'Nenhuma resposta gerada pelo modelo.')
    except Exception as e:
        return f"[Erro Ollama] Falha ao comunicar com {model_name} em {OLLAMA_URL}: {e}"

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        if self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            data = load_data()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            return
        elif self.path == '/api/ollama/models':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            models = fetch_ollama_models()
            res = {
                "models": models,
                "default": "qwen2.5:14b" if "qwen2.5:14b" in models else (models[0] if models else "qwen2.5:14b")
            }
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode('utf-8'))
            return
        return super().do_GET()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            payload = json.loads(post_data.decode('utf-8'))
        except Exception:
            self.send_error(400, "JSON invalido")
            return

        data = load_data()

        if self.path == '/api/needs':
            new_id = f"NED-00{len(data.get('needs', [])) + 1}"
            payload['id'] = new_id
            payload['project_id'] = data['projects'][0]['id'] if data.get('projects') else 'PROJ-PESQUISA-01'
            payload['status'] = 'Especificada'
            if 'requirements' not in payload:
                payload['requirements'] = []
            if 'alternatives' not in payload:
                payload['alternatives'] = []
            data.setdefault('needs', []).append(payload)
            save_data(data)

            self.send_response(201)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "need": payload}, ensure_ascii=False).encode('utf-8'))
            return

        elif self.path == '/api/alternatives':
            need_id = payload.get('need_id')
            need_found = False
            for need in data.get('needs', []):
                if need['id'] == need_id:
                    need_found = True
                    alt_id = f"ALT-0{len(need.get('alternatives', [])) + 1}"
                    alt_item = {
                        "id": alt_id,
                        "need_id": need_id,
                        "title": payload.get('title', 'Alternativa sem titulo'),
                        "type": payload.get('type', 'Produto Comercial'),
                        "supplier_or_source": payload.get('supplier', 'Fornecedor N/A'),
                        "description": payload.get('description', ''),
                        "prices": [{
                            "supplier": payload.get('supplier', 'Fornecedor N/A'),
                            "unit_price": float(payload.get('price', 0.0)),
                            "currency": "BRL",
                            "observed_date": payload.get('observed_date', '2026-07-29')
                        }],
                        "evidences": [{
                            "field_name": "conformidade_tecnica",
                            "value": payload.get('evidence_value', 'Verificado'),
                            "source_type": "cotacao",
                            "state": "Verified"
                        }]
                    }
                    need.setdefault('alternatives', []).append(alt_item)
                    break

            if need_found:
                save_data(data)
                self.send_response(201)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}, ensure_ascii=False).encode('utf-8'))
            else:
                self.send_error(404, "Necessidade nao encontrada")
            return

        elif self.path == '/api/decisions':
            need_id = payload.get('need_id')
            dec_id = f"DEC-00{len(data.get('decisions', [])) + 1}"
            dec_item = {
                "id": dec_id,
                "need_id": need_id,
                "selected_alternative_id": payload.get('selected_alternative_id', 'ALT-01'),
                "technical_justification": payload.get('technical_justification', 'Justificativa técnica padrão.'),
                "decided_by": payload.get('decided_by', 'Pesquisador Responsável'),
                "decision_date": payload.get('decision_date', '2026-07-29'),
                "is_human_decision": True
            }
            
            for need in data.get('needs', []):
                if need['id'] == need_id:
                    need['status'] = 'Decidida'

            data.setdefault('decisions', []).append(dec_item)
            save_data(data)

            self.send_response(201)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "decision": dec_item}, ensure_ascii=False).encode('utf-8'))
            return

        elif self.path == '/api/ollama/analyze':
            need_id = payload.get('need_id')
            model_name = payload.get('model', 'qwen2.5:14b')
            target_need = None
            for need in data.get('needs', []):
                if need['id'] == need_id:
                    target_need = need
                    break

            if not target_need:
                self.send_error(404, "Necessidade nao encontrada para analise")
                return

            analysis_text = generate_ollama_analysis(model_name, target_need)

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            res = {
                "need_id": need_id,
                "model": model_name,
                "analysis": analysis_text
            }
            self.wfile.write(json.dumps(res, ensure_ascii=False).encode('utf-8'))
            return

        self.send_error(404, "Endpoint nao encontrado")

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
