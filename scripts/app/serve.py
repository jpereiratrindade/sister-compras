#!/usr/bin/env python3
import http.server
import socketserver
import urllib.request
import urllib.parse
import urllib.error
import sys
import os
import json
import re
from db_repository import db_manager

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8002
WEB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../web'))
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")

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

def generate_ollama_intent(model_name, user_message, history, current_context_data):
    system_prompt = """Você é o Assistente RAG de Inteligência do SisTer-Compras com ACESSO AO HISTÓRICO COMPLETO DA CONVERSA e ao Banco de Dados.
Sua missão é extrair E MANTER acumulados todos os dados informados pelo usuário ao longo de TODAS AS MENSAGENS da conversa (Multi-Turn Chat).

REGRAS RAG, EDIÇÃO E EXCLUSÃO DE REGISTROS:
1. EXCLUSÃO DE REGISTROS: Se o usuário pedir para excluir, remover ou apagar um registro que existe no banco (ex: "Excluir NED-002", "Apagar necessidade do Power Bank"), RESPONDA COM "action": "delete_need" E O "need_id" DO ITEM.
2. EDIÇÃO DE REGISTROS: Se a instrução se referir a um registro existente (ex: "NED-002" ou "cooler do RPi 5") e o usuário quiser alterar dados ou incluir valor estimado/descrição, RESPONDA COM "action": "update_need" E O "need_id".
3. Se o usuário quiser cadastrar UMA NOVA NECESSIDADE que não existe no banco, responda com "action": "create_need".
4. Ao cadastrar nova necessidade, peça proativamente o Orçamento Estimado (R$) se não for informado, utilizando "action": "ask_clarification".
5. Se o usuário informar um valor monetário em português (ex: "80,00", "R$ 80", "80 reais"), CONVERTA AUTOMATICAMENTE PARA FLOAT (ex: 80.0) na chave "estimated_budget" ou "price".

RETORNE EXATAMENTE UM JSON NO SEGUINTE FORMATO SEM TEXTO ADICIONAL:
{
  "action": "create_need" | "update_need" | "delete_need" | "add_quote" | "make_decision" | "update_status" | "ask_clarification",
  "explanation": "Descrição clara para o usuário sobre a ação ou esclarecimento",
  "options": ["Opção 1", "Opção 2"],
  "params": {
    "need_id": "NED-002",
    "title": "...",
    "category": "Energia & Infraestrutura" | "Equipamentos Científicos" | "Componentes Eletrônicos" | "Consumo & Reativos" | "Serviços & Licenças",
    "quantity": 1,
    "priority": "Essencial" | "Alta" | "Média" | "Baixa",
    "responsible": "Equipe de Pesquisa",
    "estimated_budget": 80.0,
    "description": "...",
    "supplier": "...",
    "price": 0.0,
    "selected_alternative_id": "ALT-01",
    "technical_justification": "..."
  }
}
"""

    history_text = ""
    if history and len(history) > 0:
        history_text = "\n--- HISTÓRICO DAS MENSAGENS ANTERIORES ---\n"
        for item in history:
            role = "Usuário" if item.get('role') == 'user' else "Assistente"
            history_text += f"{role}: {item.get('content')}\n"
        history_text += "--- FIM DO HISTÓRICO ---\n"

    prompt = f"{history_text}\nMensagem Atual do Usuário: '{user_message}'\nEstado Atual do Banco de Dados (RAG): {json.dumps(current_context_data, ensure_ascii=False)}"
    payload = {
        "model": model_name,
        "system": system_prompt,
        "prompt": prompt,
        "stream": False,
        "format": "json"
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
            raw_text = res_data.get('response', '{}')
            return json.loads(raw_text)
    except Exception as e:
        print(f"[Ollama Intent Error] {e}")
        return {
            "action": "create_need",
            "explanation": f"Não foi possível processar via {model_name}. Proposta gerada por fallback.",
            "params": {
                "title": user_message,
                "category": "Equipamentos Científicos",
                "quantity": 1,
                "priority": "Essencial",
                "responsible": "Equipe de Pesquisa",
                "estimated_budget": 0.0,
                "description": ""
            }
        }

def generate_ollama_analysis(model_name, need_item, mode="analyze"):
    if mode == "specify":
        prompt_text = f"""Você é o Assistente de Engenharia e Especificação do SisTer-Compras.
O pesquisador cadastrou o seguinte recurso de pesquisa:
Título: {need_item.get('title')}
Categoria: {need_item.get('category')}
Quantidade: {need_item.get('quantity')}

Sugira uma lista de 3 a 5 requisitos técnicos fundamentais (obrigatorios, de segurança e normativos) para este item em formato JSON ou lista estruturada.
Resposta curta e objetiva."""
    else:
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
2. Identificação de lacunas ou pontos de atenção.
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

def generate_print_html(data, filter_ids=None):
    project = data.get('projects', [{}])[0]
    needs = data.get('needs', [])
    
    if filter_ids:
        needs = [n for n in needs if n.get('id') in filter_ids]

    decisions = {d['need_id']: d for d in data.get('decisions', [])}
    
    total_budget = 0.0
    items_rows = ""
    
    for need in needs:
        dec = decisions.get(need['id'])
        alt_title = "Aguardando Parecer"
        price_str = "R$ 0,00"
        subtotal_str = "R$ 0,00"
        
        has_decision = False
        if dec and need.get('alternatives'):
            for alt in need['alternatives']:
                if alt['id'] == dec.get('selected_alternative_id'):
                    alt_title = alt.get('title', 'Alternativa Aprovada')
                    if alt.get('prices') and len(alt['prices']) > 0:
                        unit_p = alt['prices'][0].get('unit_price', 0.0)
                        subtotal = unit_p * need.get('quantity', 1)
                        total_budget += subtotal
                        price_str = f"R$ {unit_p:,.2f}"
                        subtotal_str = f"R$ {subtotal:,.2f}"
                        has_decision = True
                    break

        if not has_decision and need.get('estimated_budget', 0.0) > 0:
            est_p = float(need.get('estimated_budget', 0.0))
            subtotal = est_p * need.get('quantity', 1)
            total_budget += subtotal
            price_str = f"R$ {est_p:,.2f} <small style='color:#777'>(Estimado)</small>"
            subtotal_str = f"R$ {subtotal:,.2f} <small style='color:#777'>(Estimado)</small>"

        items_rows += f"""
        <tr>
            <td><strong>{need.get('id')}</strong></td>
            <td>{need.get('title')}<br><small style="color:#666">{alt_title}</small></td>
            <td>{need.get('category')}</td>
            <td>{need.get('quantity')}</td>
            <td>{price_str}</td>
            <td><strong>{subtotal_str}</strong></td>
            <td><span class="status-tag">{need.get('status', 'Especificada')}</span></td>
        </tr>
        """

    if not items_rows:
        items_rows = "<tr><td colspan='7' style='text-align:center; padding:20px;'>*Nenhum item selecionado.*</td></tr>"

    db_type = "PostgreSQL" if db_manager.use_pg else "Armazenamento Local"

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <title>Lista de Compras Oficial — {project.get('id')}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 40px; color: #09254b; background: #fff; }}
        .header {{ border-bottom: 2px solid #062d55; padding-bottom: 16px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: flex-end; }}
        .header h1 {{ margin: 0; font-size: 24px; color: #062d55; }}
        .meta {{ font-size: 14px; margin-bottom: 24px; background: #f4f8fb; padding: 16px; border-radius: 8px; border: 1px solid #dce7ef; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 16px; font-size: 14px; }}
        th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #dce7ef; }}
        th {{ background: #062d55; color: #fff; text-transform: uppercase; font-size: 12px; }}
        .total-box {{ margin-top: 24px; text-align: right; font-size: 18px; font-weight: bold; color: #062d55; border-top: 2px solid #062d55; padding-top: 12px; }}
        .signatures {{ margin-top: 60px; display: grid; grid-template-columns: 1fr 1fr; gap: 40px; text-align: center; font-size: 13px; }}
        .sig-line {{ border-top: 1px solid #09254b; padding-top: 8px; font-weight: bold; }}
        .status-tag {{ background: #edf2f8; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
        @media print {{ body {{ padding: 0; }} button {{ display: none; }} }}
    </style>
</head>
<body>
    <button onclick="window.print()" style="float:right; padding:10px 20px; background:#062d55; color:#fff; border:none; border-radius:6px; cursor:pointer; font-weight:bold;">🖨️ Imprimir / Salvar PDF</button>
    <div class="header">
        <div>
            <span style="font-size:12px; font-weight:bold; color:#1c9b98;">SISTER-COMPRAS · MANIFESTO DE AQUISIÇÃO</span>
            <h1>Lista Oficial de Compras do Projeto {'(Lote Selecionado)' if filter_ids else ''}</h1>
        </div>
        <div style="text-align:right;">
            <strong>Data: 2026-07-29</strong>
        </div>
    </div>
    
    <div class="meta">
        <strong>Projeto:</strong> {project.get('name')} ({project.get('id')})<br>
        <strong>Pesquisador Responsável:</strong> {project.get('lead_researcher')}<br>
        <strong>Itens no Lote:</strong> {len(needs)} item(ns)<br>
        <strong>Fonte de Persistência:</strong> {db_type}<br>
        <strong>Formato de Integração:</strong> Manifesto por Contrato (v0.3.0)
    </div>

    <table>
        <thead>
            <tr>
                <th>Código</th>
                <th>Item / Especificação</th>
                <th>Categoria</th>
                <th>Qtd</th>
                <th>Vl. Unitário</th>
                <th>Subtotal</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {items_rows}
        </tbody>
    </table>

    <div class="total-box">
        ORÇAMENTO TOTAL DO LOTE: R$ {total_budget:,.2f}
    </div>

    <div class="signatures">
        <div>
            <div class="sig-line">{project.get('lead_researcher')}</div>
            Pesquisador Responsável (Aprovação Técnica)
        </div>
        <div>
            <div class="sig-line">Gestão de Suprimentos / Aquisições</div>
            Departamento de Compras e Licitações
        </div>
    </div>
</body>
</html>"""

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            data = db_manager.load_data()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            return
        elif path == '/api/ollama/models':
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
        elif path == '/api/reports/shopping-list':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            data = db_manager.load_data()
            filter_ids = None
            if 'ids' in query and query['ids']:
                filter_ids = [i.strip() for i in query['ids'][0].split(',') if i.strip()]
            html = generate_print_html(data, filter_ids=filter_ids)
            self.wfile.write(html.encode('utf-8'))
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

        data = db_manager.load_data()

        if self.path == '/api/needs':
            existing_nums = []
            for n in data.get('needs', []):
                nid = n.get('id', '')
                match = re.search(r'NED-(\d+)', nid)
                if match:
                    existing_nums.append(int(match.group(1)))
            next_num = (max(existing_nums) + 1) if existing_nums else 1
            new_id = f"NED-{next_num:03d}"

            payload['id'] = new_id
            payload['project_id'] = data['projects'][0]['id'] if data.get('projects') else 'PROJ-PESQUISA-01'
            payload['status'] = 'Especificada'
            if 'estimated_budget' not in payload:
                payload['estimated_budget'] = 0.0
            if 'description' not in payload:
                payload['description'] = ''
            if 'requirements' not in payload:
                payload['requirements'] = []
            if 'alternatives' not in payload:
                payload['alternatives'] = []
            data.setdefault('needs', []).append(payload)
            db_manager.save_data(data)

            self.send_response(201)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "need": payload}, ensure_ascii=False).encode('utf-8'))
            return

        elif self.path == '/api/needs/update':
            need_id = payload.get('need_id')
            found = False
            for need in data.get('needs', []):
                if need['id'] == need_id:
                    if 'title' in payload and payload['title']: need['title'] = payload['title']
                    if 'category' in payload and payload['category']: need['category'] = payload['category']
                    if 'quantity' in payload and payload['quantity']: need['quantity'] = int(payload['quantity'])
                    if 'priority' in payload and payload['priority']: need['priority'] = payload['priority']
                    if 'responsible' in payload and payload['responsible']: need['responsible'] = payload['responsible']
                    if 'estimated_budget' in payload and payload['estimated_budget'] is not None: need['estimated_budget'] = float(payload['estimated_budget'])
                    if 'description' in payload and payload['description'] is not None: need['description'] = payload['description']
                    found = True
                    break
            if found:
                db_manager.save_data(data)
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}, ensure_ascii=False).encode('utf-8'))
            else:
                self.send_error(404, "Necessidade nao encontrada para atualizacao")
            return

        elif self.path == '/api/needs/delete':
            need_id = payload.get('need_id')
            data['needs'] = [n for n in data.get('needs', []) if n.get('id') != need_id]
            data['decisions'] = [d for d in data.get('decisions', []) if d.get('need_id') != need_id]
            
            if db_manager.use_pg:
                try:
                    import psycopg
                    with psycopg.connect(db_manager.conn_str) as conn:
                        with conn.cursor() as cur:
                            cur.execute("DELETE FROM needs WHERE id = %s;", (need_id,))
                            conn.commit()
                except Exception as e:
                    print(f"[DatabaseManager] Erro ao deletar no PostgreSQL: {e}")

            db_manager.save_data(data)
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "deleted_id": need_id}, ensure_ascii=False).encode('utf-8'))
            return

        elif self.path == '/api/needs/status':
            need_id = payload.get('need_id')
            new_status = payload.get('status', 'Adquirida')
            found = False
            for need in data.get('needs', []):
                if need['id'] == need_id:
                    need['status'] = new_status
                    found = True
                    break
            if found:
                db_manager.save_data(data)
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}, ensure_ascii=False).encode('utf-8'))
            else:
                self.send_error(404, "Necessidade nao encontrada")
            return

        elif self.path == '/api/alternatives':
            need_id = payload.get('need_id')
            need_found = False
            
            existing_nums = []
            for n in data.get('needs', []):
                for a in n.get('alternatives', []):
                    aid = a.get('id', '')
                    match = re.search(r'ALT-(\d+)', aid)
                    if match:
                        existing_nums.append(int(match.group(1)))
            next_num = (max(existing_nums) + 1) if existing_nums else 1
            alt_id = f"ALT-{next_num:02d}"

            for need in data.get('needs', []):
                if need['id'] == need_id:
                    need_found = True
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
                db_manager.save_data(data)
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
            existing_nums = []
            for d in data.get('decisions', []):
                did = d.get('id', '')
                match = re.search(r'DEC-(\d+)', did)
                if match:
                    existing_nums.append(int(match.group(1)))
            next_num = (max(existing_nums) + 1) if existing_nums else 1
            dec_id = f"DEC-{next_num:03d}"

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
            db_manager.save_data(data)

            self.send_response(201)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "decision": dec_item}, ensure_ascii=False).encode('utf-8'))
            return

        elif self.path == '/api/project/update':
            lead_researcher = payload.get('lead_researcher', '').strip()
            project_name = payload.get('name', '').strip()
            
            if not data.get('projects'):
                data['projects'] = [{
                    "id": "PROJ-PESQUISA-01",
                    "name": project_name or "Projeto de Pesquisa e Desenvolvimento Tecnológico",
                    "lead_researcher": lead_researcher or "Pesquisador Responsável"
                }]
            else:
                if lead_researcher:
                    data['projects'][0]['lead_researcher'] = lead_researcher
                if project_name:
                    data['projects'][0]['name'] = project_name
            
            # Sincronizar PostgreSQL e storage JSON
            db_manager.save_data(data)

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "project": data['projects'][0]}, ensure_ascii=False).encode('utf-8'))
            return

        elif self.path == '/api/ollama/intent':
            user_message = payload.get('message', '')
            history = payload.get('history', [])
            model_name = payload.get('model', 'qwen2.5:14b')
            proposal = generate_ollama_intent(model_name, user_message, history, data)

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success", "proposal": proposal}, ensure_ascii=False).encode('utf-8'))
            return

        elif self.path == '/api/ollama/analyze':
            need_id = payload.get('need_id')
            model_name = payload.get('model', 'qwen2.5:14b')
            mode = payload.get('mode', 'analyze')
            target_need = None
            for need in data.get('needs', []):
                if need['id'] == need_id:
                    target_need = need
                    break

            if not target_need and mode != 'specify':
                self.send_error(404, "Necessidade nao encontrada para analise")
                return

            if mode == 'specify' and not target_need:
                target_need = {"title": "Recurso de Pesquisa", "category": "Geral", "quantity": 1}

            analysis_text = generate_ollama_analysis(model_name, target_need, mode=mode)

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            res = {
                "need_id": need_id,
                "model": model_name,
                "mode": mode,
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
