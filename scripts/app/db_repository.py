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
        
        host = os.environ.get("PGHOST", "localhost")
        port = os.environ.get("PGPORT", "5432")
        user = os.environ.get("PGUSER", "postgres")
        password = os.environ.get("PGPASSWORD", "")
        dbname = os.environ.get("PGDATABASE", "sister_compras")
        
        if password:
            return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        return f"postgresql://{user}@{host}:{port}/{dbname}"

    def _try_init_pg(self):
        try:
            with psycopg.connect(self.conn_str, connect_timeout=3) as conn:
                with conn.cursor() as cur:
                    if os.path.exists(SCHEMA_FILE):
                        with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
                            cur.execute(f.read())
                        conn.commit()
                self.use_pg = True
                print(f"[DatabaseManager] Conectado ao PostgreSQL com sucesso: {self.conn_str}")
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
                        cur.execute("SELECT id, name, description, lead_researcher, start_date, end_date FROM projects")
                        for row in cur.fetchall():
                            data["projects"].append({
                                "id": row[0], "name": row[1], "description": row[2],
                                "lead_researcher": row[3], "start_date": str(row[4]), "end_date": str(row[5])
                            })
                        
                        # Carregar necessidades
                        cur.execute("SELECT id, project_id, title, category, quantity, priority, status, responsible FROM needs")
                        needs_map = {}
                        for row in cur.fetchall():
                            need_item = {
                                "id": row[0], "project_id": row[1], "title": row[2],
                                "category": row[3], "quantity": row[4], "priority": row[5],
                                "status": row[6], "responsible": row[7],
                                "requirements": [], "alternatives": []
                            }
                            needs_map[row[0]] = need_item
                            data["needs"].append(need_item)
                        
                        # Carregar alternativas
                        cur.execute("SELECT id, need_id, title, type, supplier_or_source, description FROM alternatives")
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
                        cur.execute("SELECT id, need_id, selected_alternative_id, technical_justification, decided_by, decision_date, is_human_decision FROM decisions")
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

db_manager = DatabaseManager()
