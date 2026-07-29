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
import hashlib
import uuid
from datetime import datetime, timezone
from db_repository import db_manager

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8016
HOST = os.environ.get("NEXO_COMPRAS_HOST", "127.0.0.1")
WEB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../web'))
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")

def canonical_digest(payload):
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')
    ).encode('utf-8')
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"

def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def integration_receipt(agreement, event, issued_by, subject_id):
    previous = agreement.get("acceptance_receipt")
    return {
        "receipt_id": str(uuid.uuid4()),
        "agreement_id": str(agreement["agreement_id"]),
        "revision": int(agreement["revision"]),
        "digest": agreement["digest"],
        "event": event,
        "issued_by": issued_by,
        "issued_at": utc_now(),
        "subject_id": subject_id,
        "previous_receipt_digest": (
            canonical_digest(previous) if previous and event != "accepted" else None
        ),
        "signature": None,
    }

def agreement_allows(agreement, capability_id):
    if not agreement or agreement.get("agreement_status") != "active":
        return False
    return any(
        capability.get("capability_id") == capability_id
        and capability.get("decision") in {"accepted", "accepted_with_constraints"}
        for capability in agreement.get("negotiated_capabilities", [])
    )

def post_nexo(path, payload, identity):
    request = urllib.request.Request(
        f"http://127.0.0.1:8015{path}",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Sister-Subject": identity["subject"],
            "X-Sister-Name": identity["name"],
            "X-Sister-Email": identity["email"],
            "X-Sister-Role": identity["role"],
            "X-Sister-System": "sister_compras",
            "User-Agent": "Nexo-Compras/0.4.0",
        },
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))

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
            <span style="font-size:12px; font-weight:bold; color:#1c9b98;">NEXO-COMPRAS · MANIFESTO DE AQUISIÇÃO</span>
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

    def end_headers(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/" or path.endswith((".html", ".js", ".css")):
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def identity(self):
        subject = self.headers.get("X-Sister-Subject", "").strip()
        if not subject:
            return None
        return {
            "subject": subject,
            "name": self.headers.get("X-Sister-Name", subject).strip() or subject,
            "email": self.headers.get("X-Sister-Email", "").strip(),
            "role": self.headers.get("X-Sister-Role", "user").strip() or "user",
        }

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        self.end_headers()
        self.wfile.write(body)

    def require_identity(self):
        identity = self.identity()
        if identity is None:
            self.send_json(401, {
                "status": "error",
                "detail": "Acesso autenticado pelo SisTer é obrigatório."
            })
        return identity

    def require_nexo_permission(
        self, identity, permission, source_project_id
    ):
        if not source_project_id:
            self.send_json(422, {
                "status": "error",
                "detail": "Selecione um projeto cadastrado no Nexo.",
            })
            return False
        try:
            decision = post_nexo(
                "/api/v1/access/authorize",
                {
                    "source_project_id": source_project_id,
                    "permission": permission,
                },
                identity,
            )
        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            TimeoutError,
            json.JSONDecodeError,
        ) as error:
            self.send_json(503, {
                "status": "error",
                "detail": (
                    "A autoridade de acesso do Nexo está indisponível; "
                    f"o acesso foi negado por segurança: {error}"
                ),
            })
            return False
        if not decision.get("allowed", False):
            self.send_json(403, {
                "status": "error",
                "detail": (
                    "A identidade não possui atribuição local no projeto "
                    "do Nexo para esta operação."
                ),
                "authorization": decision,
            })
            return False
        return True

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/api/health":
            database_ok = db_manager.healthy()
            self.send_json(200 if database_ok else 503, {
                "status": "ok" if database_ok else "degraded",
                "service": "nexo-compras",
                "system_id": "sister_compras",
                "version": "0.4.0",
                "database": "ok" if database_ok else "unavailable",
            })
            return
        if path == "/api/integration/manifest":
            self.send_json(200, {
                "contract_version": "1.0.0",
                "system_id": "sister_compras",
                "parent_system_id": "sister_nexo",
                "product_name": "Nexo-Compras",
                "access_url": "/integrations/nexo/compras/",
                "access_mode": "nexo_authenticated_reverse_proxy",
                "database_ownership": "exclusive",
                "capabilities": [
                    "needs", "requirements", "quotes", "decisions", "fulfillment"
                ],
            })
            return

        identity = self.require_identity()
        if identity is None:
            return

        if path == '/api/me':
            self.send_json(200, identity)
            return
        if path == '/api/integration-agreements/nexo':
            self.send_json(200, {
                "agreement": db_manager.get_integration_agreement(),
                "participant": "sister_compras",
                "counterparty": "sister_nexo",
            })
            return
        trusted_nexo_projection = (
            path == '/api/integration/data/need-summaries'
            and self.headers.get("X-Sister-System", "").strip()
            == "sister_nexo"
        )
        if not trusted_nexo_projection and path in {
            '/api/integration/data/need-summaries',
            '/api/data',
            '/api/reports/shopping-list',
        } and not self.require_nexo_permission(
            identity, "procurement.view",
            query.get("project_id", [None])[0],
        ):
            return
        if path == '/api/integration/data/need-summaries':
            agreement = db_manager.get_integration_agreement()
            if not agreement_allows(agreement, "compras.need-summary.read"):
                self.send_json(403, {
                    "status": "error",
                    "detail": (
                        "A capacidade compras.need-summary.read não está "
                        "ativa no acordo Nexo–Compras."
                    )
                })
                return
            project_id = query.get("project_id", [None])[0]
            data = db_manager.load_data()
            summaries = [{
                "need_id": need["id"],
                "project_id": need.get("project_id"),
                "research_activity_id": need.get("research_activity_id"),
                "activity_id": need.get("activity_id"),
                "title": need.get("title"),
                "status": need.get("status"),
                "priority": need.get("priority"),
            } for need in data.get("needs", [])
              if project_id is None or need.get("project_id") == project_id]
            self.send_json(200, {
                "schema": "compras-need-summary/1.0.0",
                "agreement_id": str(agreement["agreement_id"]),
                "items": summaries,
            })
            return
        if path == '/api/nexo/context':
            agreement = db_manager.get_integration_agreement()
            if not agreement_allows(agreement, "nexo.project-context.read"):
                self.send_json(403, {
                    "status": "error",
                    "detail": (
                        "A capacidade nexo.project-context.read não está "
                        "ativa no acordo Nexo–Compras."
                    )
                })
                return
            request = urllib.request.Request(
                "http://127.0.0.1:8015/api/v1/integrations/compras/context",
                headers={
                    "X-Sister-Subject": identity["subject"],
                    "X-Sister-Name": identity["name"],
                    "X-Sister-Email": identity["email"],
                    "X-Sister-Role": identity["role"],
                    "X-Sister-System": "sister_compras",
                    "User-Agent": "Nexo-Compras/0.4.0",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=3) as response:
                    context = json.loads(response.read().decode("utf-8"))
                if (
                    context.get("schema") != "nexo-project-context/1.0.0"
                    or context.get("system_id") != "sister_nexo"
                    or str(context.get("agreement", {}).get("agreement_id"))
                    != str(agreement["agreement_id"])
                    or context.get("agreement", {}).get("revision")
                    != agreement["revision"]
                    or context.get("agreement", {}).get("digest")
                    != agreement["digest"]
                ):
                    raise ValueError(
                        "metadados do projeto não correspondem ao acordo ativo"
                    )
                self.send_json(200, context)
            except urllib.error.HTTPError as error:
                try:
                    detail = json.loads(
                        error.read().decode("utf-8")
                    ).get("error", str(error))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    detail = str(error)
                self.send_json(error.code, {
                    "status": "error",
                    "detail": detail,
                })
            except (
                urllib.error.URLError, TimeoutError,
                json.JSONDecodeError, ValueError
            ) as error:
                self.send_json(502, {
                    "status": "error",
                    "detail": f"Contexto de projetos do Nexo indisponível: {error}",
                })
            return
        if path == '/api/data':
            project_id = query.get("project_id", [None])[0]
            data = db_manager.load_data()
            visible_need_ids = {
                need["id"] for need in data.get("needs", [])
                if need.get("project_id") == project_id
            }
            data["projects"] = [
                project for project in data.get("projects", [])
                if project.get("id") == project_id
            ]
            data["needs"] = [
                need for need in data.get("needs", [])
                if need.get("id") in visible_need_ids
            ]
            data["decisions"] = [
                decision for decision in data.get("decisions", [])
                if decision.get("need_id") in visible_need_ids
            ]
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
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
            project_id = query.get("project_id", [None])[0]
            data["projects"] = [
                project for project in data.get("projects", [])
                if project.get("id") == project_id
            ]
            visible_need_ids = {
                need["id"] for need in data.get("needs", [])
                if need.get("project_id") == project_id
            }
            data["needs"] = [
                need for need in data.get("needs", [])
                if need.get("id") in visible_need_ids
            ]
            data["decisions"] = [
                decision for decision in data.get("decisions", [])
                if decision.get("need_id") in visible_need_ids
            ]
            filter_ids = None
            if 'ids' in query and query['ids']:
                filter_ids = [i.strip() for i in query['ids'][0].split(',') if i.strip()]
            html = generate_print_html(data, filter_ids=filter_ids)
            self.wfile.write(html.encode('utf-8'))
            return
        return super().do_GET()

    def do_POST(self):
        identity = self.require_identity()
        if identity is None:
            return
        if identity["role"] != "admin" and self.path.startswith(
            "/api/integration-agreements/"
        ):
            self.send_json(403, {
                "status": "error",
                "detail": "A governança de acordos exige papel administrativo."
            })
            return
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            payload = json.loads(post_data.decode('utf-8'))
        except Exception:
            self.send_error(400, "JSON invalido")
            return

        path = urllib.parse.urlparse(self.path).path
        if path == '/api/integration-agreements/proposals':
            try:
                proposal = payload["proposal"]
                digest = payload["digest"]
                if canonical_digest(proposal) != digest:
                    raise ValueError("digest da proposta é inválido")
                if (
                    proposal.get("protocol_version")
                    != "sister.integration-agreement/1.0.0"
                    or proposal.get("profile") != "nexo-compras.profile/1.0.0"
                    or proposal.get("proposer_system_id") != "sister_nexo"
                    or proposal.get("counterparty_system_id") != "sister_compras"
                ):
                    raise ValueError("proposta incompatível com o perfil Nexo-Compras")
                result = db_manager.receive_integration_proposal(
                    proposal, digest, identity["subject"]
                )
                self.send_json(201, {"status": "proposed", "agreement": result})
            except (KeyError, TypeError, ValueError) as error:
                self.send_json(422, {"status": "error", "detail": str(error)})
            return

        if path == '/api/integration-agreements/nexo/accept':
            try:
                agreement = db_manager.get_integration_agreement()
                if not agreement:
                    raise ValueError("nenhuma proposta recebida")
                if agreement["agreement_status"] == "accepted":
                    receipt = agreement["acceptance_receipt"]
                else:
                    if agreement["agreement_status"] != "proposed":
                        raise ValueError("o acordo não está aguardando aceite")
                    capabilities = agreement["proposal"]["capabilities"]
                    negotiated = [{
                        **capability,
                        "decision": (
                            "declined"
                            if capability.get("decision") == "declined"
                            else "accepted"
                        ),
                        "accepted_constraints": (
                            {}
                            if capability.get("decision") == "declined"
                            else capability["requested_constraints"]
                        ),
                        "decision_reason": (
                            capability.get("decision_reason")
                            if capability.get("decision") == "declined"
                            else "Aceita integralmente pelo Nexo-Compras."
                        )
                    } for capability in capabilities]
                    receipt = integration_receipt(
                        agreement, "accepted", "sister_compras", identity["subject"]
                    )
                    agreement = db_manager.accept_integration_proposal(
                        receipt, negotiated, identity["subject"]
                    )
                post_nexo(
                    "/api/v1/integration-agreements/compras/receipts/acceptance",
                    {"receipt": receipt,
                     "capabilities": agreement["negotiated_capabilities"]},
                    identity
                )
                self.send_json(200, {"status": "accepted", "agreement": agreement})
            except (ValueError, urllib.error.URLError, TimeoutError) as error:
                self.send_json(502, {"status": "error", "detail": str(error)})
            return

        if path == '/api/integration-agreements/nexo/counter-propose':
            try:
                agreement = db_manager.get_integration_agreement()
                if not agreement or agreement["agreement_status"] != "proposed":
                    raise ValueError("nenhuma proposta está aguardando negociação")
                decisions = payload.get("decisions", {})
                capabilities = []
                for capability in agreement["proposal"]["capabilities"]:
                    decision = decisions.get(
                        capability["capability_id"], "accepted"
                    )
                    if decision not in {
                        "accepted", "accepted_with_constraints", "declined"
                    }:
                        raise ValueError(
                            f"decisão inválida para "
                            f"{capability['capability_id']}: {decision}"
                        )
                    if capability["requirement"] == "required" and decision == "declined":
                        raise ValueError(
                            f"capacidade obrigatória não pode ser recusada: "
                            f"{capability['capability_id']}"
                        )
                    capabilities.append({
                        **capability,
                        "decision": decision,
                        "accepted_constraints": (
                            capability["requested_constraints"]
                            if decision != "declined" else {}
                        ),
                        "decision_reason": (
                            "Contraproposta do Nexo-Compras."
                            if decision != "accepted"
                            else "Aceita na contraproposta."
                        )
                    })
                counterproposal = {
                    **agreement["proposal"],
                    "revision": int(agreement["revision"]) + 1,
                    "proposer_system_id": "sister_compras",
                    "counterparty_system_id": "sister_nexo",
                    "capabilities": capabilities,
                }
                digest = canonical_digest(counterproposal)
                agreement = db_manager.counter_propose_integration(
                    counterproposal, digest, identity["subject"]
                )
                post_nexo(
                    "/api/v1/integration-agreements/compras/counterproposal",
                    {"counterproposal": counterproposal, "digest": digest},
                    identity
                )
                self.send_json(200, {
                    "status": "counter_proposed", "agreement": agreement
                })
            except (ValueError, urllib.error.URLError, TimeoutError) as error:
                self.send_json(502, {"status": "error", "detail": str(error)})
            return

        if path == '/api/integration-agreements/receipts/activation':
            try:
                receipt = payload["receipt"]
                if (
                    receipt.get("event") != "activated"
                    or receipt.get("issued_by") != "sister_nexo"
                ):
                    raise ValueError("recibo de ativação possui emissor ou evento inválido")
                agreement = db_manager.activate_integration_agreement(
                    receipt, identity["subject"]
                )
                self.send_json(200, {"status": "active", "agreement": agreement})
            except (KeyError, ValueError) as error:
                self.send_json(422, {"status": "error", "detail": str(error)})
            return

        if path == '/api/integration-agreements/receipts/status':
            try:
                receipt = payload["receipt"]
                if receipt.get("issued_by") != "sister_nexo":
                    raise ValueError("emissor do recibo de estado é inválido")
                agreement = db_manager.transition_integration_agreement(
                    receipt["event"], receipt, identity["subject"],
                    receipt["issued_by"]
                )
                self.send_json(200, {
                    "status": receipt["event"], "agreement": agreement
                })
            except (KeyError, ValueError) as error:
                self.send_json(422, {"status": "error", "detail": str(error)})
            return

        if path in {
            '/api/integration-agreements/nexo/suspend',
            '/api/integration-agreements/nexo/revoke'
        }:
            try:
                status = "suspended" if path.endswith("/suspend") else "revoked"
                agreement = db_manager.get_integration_agreement()
                if not agreement:
                    raise ValueError("acordo inexistente")
                receipt = integration_receipt(
                    agreement, status, "sister_compras", identity["subject"]
                )
                agreement = db_manager.transition_integration_agreement(
                    status, receipt, identity["subject"], "sister_compras"
                )
                post_nexo(
                    "/api/v1/integration-agreements/compras/receipts/status",
                    {"receipt": receipt}, identity
                )
                self.send_json(200, {"status": status, "agreement": agreement})
            except (ValueError, urllib.error.URLError, TimeoutError) as error:
                self.send_json(502, {"status": "error", "detail": str(error)})
            return

        data = db_manager.load_data()
        if path == '/api/project/update':
            self.send_json(403, {
                "status": "error",
                "detail": (
                    "Projetos são cadastrados e alterados exclusivamente no Nexo."
                ),
            })
            return

        source_project_id = payload.get("project_id")
        if not source_project_id:
            need_id = payload.get("need_id")
            source_project_id = next((
                need.get("project_id")
                for need in data.get("needs", [])
                if need.get("id") == need_id
            ), None)
        if not self.require_nexo_permission(
            identity, "procurement.manage", source_project_id
        ):
            return

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
            payload['project_id'] = source_project_id
            if not any(
                project.get("id") == source_project_id
                for project in data.get("projects", [])
            ):
                data.setdefault("projects", []).append({
                    "id": source_project_id,
                    "name": payload.pop(
                        "project_name", source_project_id
                    ),
                    "description": (
                        "Referência de projeto sob autoridade do SisTer Nexo."
                    ),
                    "lead_researcher": identity["name"],
                    "start_date": "2026-01-01",
                    "end_date": "2026-12-31",
                })
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
    with ReuseTCPServer((HOST, PORT), CustomHandler) as httpd:
        print(f"[Nexo-Compras Web Server] Executando em http://{HOST}:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[Nexo-Compras Web Server] Encerrado.")
