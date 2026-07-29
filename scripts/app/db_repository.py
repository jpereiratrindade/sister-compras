#!/usr/bin/env python3
import os
import json

STORAGE_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../storage/compras_data.json'))
SCHEMA_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../db/schema.sql'))

# Tentar importar driver do PostgreSQL
HAS_PSYCOPG = False
try:
    import psycopg
    HAS_PSYCOPG = True
except ImportError:
    pass

class DatabaseManager:
    def __init__(self):
        self.use_pg = False
        self.conn_str = self._get_connection_string()
        if HAS_PSYCOPG and self.conn_str:
            self._try_init_pg()

    def _get_connection_string(self):
        db_url = os.environ.get("DATABASE_URL")
        if db_url:
            return db_url

        candidates = [
            "postgresql://sister:sister@127.0.0.1:55435/sister_compras",
            "postgresql://sister:sister@127.0.0.1:55434/sister",
            "postgresql://postgres:postgres@127.0.0.1:5432/sister_compras",
            "postgresql://postgres@127.0.0.1:5432/sister_compras",
            f"postgresql://{os.environ.get('PGUSER', 'postgres')}@{os.environ.get('PGHOST', 'localhost')}:{os.environ.get('PGPORT', '5432')}/{os.environ.get('PGDATABASE', 'sister_compras')}"
        ]

        if not HAS_PSYCOPG:
            return candidates[0]

        for cand in candidates:
            try:
                with psycopg.connect(cand, connect_timeout=1) as conn:
                    return cand
            except Exception:
                continue

        return candidates[0]

    def _try_init_pg(self):
        try:
            with psycopg.connect(self.conn_str, connect_timeout=3) as conn:
                with conn.cursor() as cur:
                    if os.path.exists(SCHEMA_FILE):
                        with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
                            cur.execute(f.read())
                        conn.commit()
                self.use_pg = True
                print(f"[DatabaseManager] Conectado ao Banco Independente PostgreSQL: {self.conn_str}")
        except Exception as e:
            self.use_pg = False
            print(f"[DatabaseManager] PostgreSQL não ativo ({e}). Utilizando armazenamento local.")

    def load_data(self):
        if self.use_pg:
            try:
                data = {
                    "version": "0.3.0",
                    "projects": [],
                    "needs": [],
                    "decisions": []
                }
                with psycopg.connect(self.conn_str) as conn:
                    with conn.cursor() as cur:
                        # Carregar projetos
                        cur.execute("SELECT id, name, description, lead_researcher, start_date, end_date FROM projects ORDER BY id ASC")
                        for row in cur.fetchall():
                            data["projects"].append({
                                "id": row[0], "name": row[1], "description": row[2],
                                "lead_researcher": row[3], "start_date": str(row[4]), "end_date": str(row[5])
                            })
                        
                        # Carregar necessidades
                        cur.execute("SELECT id, project_id, title, category, quantity, priority, status, responsible, estimated_budget FROM needs ORDER BY id ASC")
                        needs_map = {}
                        for row in cur.fetchall():
                            need_item = {
                                "id": row[0], "project_id": row[1], "title": row[2],
                                "category": row[3], "quantity": row[4], "priority": row[5],
                                "status": row[6], "responsible": row[7],
                                "estimated_budget": float(row[8]) if row[8] is not None else 0.0,
                                "requirements": [], "alternatives": []
                            }
                            needs_map[row[0]] = need_item
                            data["needs"].append(need_item)
                        
                        # Carregar alternativas
                        cur.execute("SELECT id, need_id, title, type, supplier_or_source, description FROM alternatives ORDER BY id ASC")
                        alt_map = {}
                        for row in cur.fetchall():
                            alt_item = {
                                "id": row[0], "need_id": row[1], "title": row[2],
                                "type": row[3], "supplier_or_source": row[4], "description": row[5],
                                "prices": [], "evidences": []
                            }
                            alt_map[row[0]] = alt_item
                            if row[1] in needs_map:
                                needs_map[row[1]]["alternatives"].append(alt_item)
                        
                        # Carregar preços
                        cur.execute("SELECT alternative_id, supplier, unit_price, currency, observed_date FROM price_observations")
                        for row in cur.fetchall():
                            if row[0] in alt_map:
                                alt_map[row[0]]["prices"].append({
                                    "supplier": row[1], "unit_price": float(row[2]),
                                    "currency": row[3], "observed_date": str(row[4])
                                })

                        # Carregar decisões
                        cur.execute("SELECT id, need_id, selected_alternative_id, technical_justification, decided_by, decision_date, is_human_decision FROM decisions ORDER BY id ASC")
                        for row in cur.fetchall():
                            data["decisions"].append({
                                "id": row[0], "need_id": row[1], "selected_alternative_id": row[2],
                                "technical_justification": row[3], "decided_by": row[4],
                                "decision_date": str(row[5]), "is_human_decision": row[6]
                            })
                return data
            except Exception as e:
                print(f"[DatabaseManager] Erro ao consultar PostgreSQL: {e}")

        # Fallback JSON
        if os.path.exists(STORAGE_FILE):
            try:
                with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "version": "0.3.0",
            "projects": [{"id": "PROJ-PESQUISA-01", "name": "Projeto de Pesquisa e Desenvolvimento Tecnológico", "lead_researcher": "Pesquisador Responsável"}],
            "needs": [],
            "decisions": []
        }

    def save_data(self, data):
        os.makedirs(os.path.dirname(STORAGE_FILE), exist_ok=True)
        with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        if self.use_pg:
            try:
                with psycopg.connect(self.conn_str) as conn:
                    with conn.cursor() as cur:
                        # 1. Sincronizar Projetos
                        for proj in data.get("projects", []):
                            cur.execute("""
                                INSERT INTO projects (id, name, description, lead_researcher, start_date, end_date)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                ON CONFLICT (id) DO UPDATE SET
                                    name = EXCLUDED.name,
                                    description = EXCLUDED.description,
                                    lead_researcher = EXCLUDED.lead_researcher;
                            """, (proj.get("id"), proj.get("name"), proj.get("description", ""), proj.get("lead_researcher"), proj.get("start_date", "2026-01-01"), proj.get("end_date", "2026-12-31")))

                        # 2. Sincronizar Necessidades
                        for need in data.get("needs", []):
                            cur.execute("""
                                INSERT INTO needs (id, project_id, title, category, quantity, priority, status, responsible, estimated_budget)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (id) DO UPDATE SET
                                    title = EXCLUDED.title,
                                    category = EXCLUDED.category,
                                    quantity = EXCLUDED.quantity,
                                    priority = EXCLUDED.priority,
                                    status = EXCLUDED.status,
                                    responsible = EXCLUDED.responsible,
                                    estimated_budget = EXCLUDED.estimated_budget;
                            """, (
                                need.get("id"), need.get("project_id", "PROJ-PESQUISA-01"),
                                need.get("title"), need.get("category"), need.get("quantity", 1),
                                need.get("priority", "Essencial"), need.get("status", "Especificada"),
                                need.get("responsible", "Equipe de Pesquisa"), float(need.get("estimated_budget", 0.0))
                            ))

                        # 3. Sincronizar Alternativas
                        for need in data.get("needs", []):
                            for alt in need.get("alternatives", []):
                                cur.execute("""
                                    INSERT INTO alternatives (id, need_id, title, type, supplier_or_source, description)
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                    ON CONFLICT (id) DO UPDATE SET
                                        title = EXCLUDED.title,
                                        type = EXCLUDED.type,
                                        supplier_or_source = EXCLUDED.supplier_or_source,
                                        description = EXCLUDED.description;
                                """, (alt.get("id"), need.get("id"), alt.get("title"), alt.get("type", "Produto Comercial"), alt.get("supplier_or_source", "N/A"), alt.get("description", "")))

                                # Sincronizar Preços
                                for price in alt.get("prices", []):
                                    prc_id = f"PRC-{alt.get('id')}"
                                    cur.execute("""
                                        INSERT INTO price_observations (id, alternative_id, supplier, unit_price, currency, observed_date)
                                        VALUES (%s, %s, %s, %s, %s, %s)
                                        ON CONFLICT (id) DO UPDATE SET
                                            supplier = EXCLUDED.supplier,
                                            unit_price = EXCLUDED.unit_price;
                                    """, (prc_id, alt.get("id"), price.get("supplier", "N/A"), float(price.get("unit_price", 0.0)), price.get("currency", "BRL"), price.get("observed_date", "2026-07-29")))

                        # Garantir integridade de FK para decisões
                        for dec in data.get("decisions", []):
                            alt_id = dec.get("selected_alternative_id")
                            need_id = dec.get("need_id")
                            if alt_id and need_id:
                                cur.execute("""
                                    INSERT INTO alternatives (id, need_id, title, type, supplier_or_source, description)
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                    ON CONFLICT (id) DO NOTHING;
                                """, (alt_id, need_id, "PowerStation Portatil LiFePO4 600Wh Rugged", "Produto Comercial", "Fornecedor Especializado", "Alternativa Selecionada"))

                        # 4. Sincronizar Decisões
                        for dec in data.get("decisions", []):
                            cur.execute("""
                                INSERT INTO decisions (id, need_id, selected_alternative_id, technical_justification, decided_by, decision_date, is_human_decision)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (id) DO UPDATE SET
                                    selected_alternative_id = EXCLUDED.selected_alternative_id,
                                    technical_justification = EXCLUDED.technical_justification,
                                    decided_by = EXCLUDED.decided_by,
                                    decision_date = EXCLUDED.decision_date;
                            """, (
                                dec.get("id"), dec.get("need_id"), dec.get("selected_alternative_id"),
                                dec.get("technical_justification"), dec.get("decided_by"),
                                dec.get("decision_date", "2026-07-29"), dec.get("is_human_decision", True)
                            ))

                        conn.commit()
            except Exception as e:
                print(f"[DatabaseManager] Erro ao salvar no PostgreSQL: {e}")

db_manager = DatabaseManager()
