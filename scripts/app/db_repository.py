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
        return None

    def _try_init_pg(self):
        try:
            with psycopg.connect(self.conn_str, connect_timeout=3) as conn:
                with conn.cursor() as cur:
                    if os.path.exists(SCHEMA_FILE):
                        with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
                            cur.execute(f.read())
                        cur.execute("ALTER TABLE needs ADD COLUMN IF NOT EXISTS description TEXT;")
                        conn.commit()
                self.use_pg = True
                print("[DatabaseManager] Conectado ao banco PostgreSQL independente.")
        except Exception as e:
            self.use_pg = False
            print(f"[DatabaseManager] PostgreSQL não ativo ({e}). Utilizando armazenamento local.")

    def healthy(self):
        if not self.use_pg or not HAS_PSYCOPG or not self.conn_str:
            return False
        try:
            with psycopg.connect(self.conn_str, connect_timeout=2) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    return cur.fetchone()[0] == 1
        except Exception:
            return False

    def get_integration_agreement(self):
        if not self.use_pg:
            return None
        with psycopg.connect(self.conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT json_build_object(
                        'agreement_id', agreement_id,
                        'counterparty_system_id', counterparty_system_id,
                        'protocol_version', protocol_version,
                        'profile', profile,
                        'revision', revision,
                        'agreement_status', agreement_status,
                        'local_processing_status', local_processing_status,
                        'digest', digest,
                        'proposal', proposal,
                        'counterproposal', counterproposal,
                        'negotiated_capabilities', negotiated_capabilities,
                        'acceptance_receipt', acceptance_receipt,
                        'activation_receipt', activation_receipt,
                        'proposed_by', proposed_by,
                        'accepted_by', accepted_by,
                        'proposed_at', proposed_at,
                        'accepted_at', accepted_at,
                        'activated_at', activated_at,
                        'suspended_at', suspended_at,
                        'revoked_at', revoked_at,
                        'updated_at', updated_at,
                        'events', coalesce((
                            SELECT json_agg(json_build_object(
                                'event_id', e.event_id,
                                'revision', e.revision,
                                'event_type', e.event_type,
                                'agreement_status', e.agreement_status,
                                'local_processing_status', e.local_processing_status,
                                'digest', e.digest,
                                'issued_by', e.issued_by,
                                'subject_id', e.subject_id,
                                'receipt', e.receipt,
                                'occurred_at', e.occurred_at
                            ) ORDER BY e.occurred_at DESC)
                            FROM integration_agreement_events e
                            WHERE e.agreement_id = integration_agreements.agreement_id
                        ), '[]'::json)
                    )
                    FROM integration_agreements
                    WHERE counterparty_system_id = 'sister_nexo'
                      AND profile = 'nexo-compras.profile/1.0.0'
                """)
                row = cur.fetchone()
                return row[0] if row else None

    def receive_integration_proposal(self, proposal, digest, subject_id):
        agreement_id = proposal["agreement_id"]
        revision = int(proposal["revision"])
        capabilities = proposal["capabilities"]
        with psycopg.connect(self.conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT agreement_id::text, revision, digest
                    FROM integration_agreements
                    WHERE counterparty_system_id = 'sister_nexo'
                      AND profile = 'nexo-compras.profile/1.0.0'
                    FOR UPDATE
                """)
                current = cur.fetchone()
                if current:
                    current_id, current_revision, current_digest = current
                    if revision < current_revision:
                        raise ValueError("proposta obsoleta")
                    if revision == current_revision:
                        if current_id != agreement_id or current_digest != digest:
                            raise ValueError("revisão conflitante com o acordo vigente")
                        return self.get_integration_agreement()
                    if current_id != agreement_id:
                        raise ValueError("nova revisão alterou o agreement_id")
                cur.execute("""
                    INSERT INTO integration_agreements (
                        agreement_id, counterparty_system_id, protocol_version,
                        profile, revision, agreement_status,
                        local_processing_status, digest, proposal,
                        negotiated_capabilities, proposed_by
                    ) VALUES (
                        %s::uuid, 'sister_nexo', %s, %s, %s, 'proposed',
                        'pending_validation', %s, %s::jsonb, %s::jsonb, %s
                    )
                    ON CONFLICT (counterparty_system_id, profile) DO UPDATE SET
                        agreement_id = excluded.agreement_id,
                        protocol_version = excluded.protocol_version,
                        revision = excluded.revision,
                        agreement_status = 'proposed',
                        local_processing_status = 'pending_validation',
                        digest = excluded.digest,
                        proposal = excluded.proposal,
                        counterproposal = null,
                        negotiated_capabilities = excluded.negotiated_capabilities,
                        acceptance_receipt = null,
                        activation_receipt = null,
                        proposed_by = excluded.proposed_by,
                        accepted_by = null,
                        proposed_at = now(),
                        accepted_at = null,
                        activated_at = null,
                        updated_at = now()
                    WHERE integration_agreements.revision < excluded.revision
                """, (
                    agreement_id, proposal["protocol_version"], proposal["profile"],
                    revision, digest, json.dumps(proposal),
                    json.dumps(capabilities), subject_id
                ))
                self._append_integration_event(
                    cur, agreement_id, revision, "proposal_received", "proposed",
                    "pending_validation", digest, "sister_nexo", subject_id, None
                )
            conn.commit()
        return self.get_integration_agreement()

    def accept_integration_proposal(self, receipt, capabilities, subject_id):
        with psycopg.connect(self.conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE integration_agreements SET
                        agreement_status = 'accepted',
                        local_processing_status = 'awaiting_receipt',
                        negotiated_capabilities = %s::jsonb,
                        acceptance_receipt = %s::jsonb,
                        accepted_by = %s,
                        accepted_at = now(),
                        updated_at = now()
                    WHERE agreement_id = %s::uuid
                      AND revision = %s
                      AND digest = %s
                      AND agreement_status = 'proposed'
                """, (
                    json.dumps(capabilities), json.dumps(receipt), subject_id,
                    receipt["agreement_id"], receipt["revision"], receipt["digest"]
                ))
                if cur.rowcount != 1:
                    raise ValueError("proposta inexistente, divergente ou já respondida")
                self._append_integration_event(
                    cur, receipt["agreement_id"], receipt["revision"],
                    "acceptance_issued", "accepted", "awaiting_receipt",
                    receipt["digest"], "sister_compras", subject_id, receipt
                )
            conn.commit()
        return self.get_integration_agreement()

    def counter_propose_integration(self, counterproposal, digest, subject_id):
        with psycopg.connect(self.conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE integration_agreements SET
                        agreement_status = 'counter_proposed',
                        local_processing_status = 'awaiting_receipt',
                        counterproposal = %s::jsonb,
                        negotiated_capabilities = %s::jsonb,
                        digest = %s,
                        revision = %s,
                        accepted_by = %s,
                        updated_at = now()
                    WHERE agreement_id = %s::uuid
                      AND agreement_status = 'proposed'
                """, (
                    json.dumps(counterproposal), json.dumps(counterproposal["capabilities"]),
                    digest, counterproposal["revision"], subject_id,
                    counterproposal["agreement_id"]
                ))
                if cur.rowcount != 1:
                    raise ValueError("proposta não está disponível para contraproposta")
                self._append_integration_event(
                    cur, counterproposal["agreement_id"], counterproposal["revision"],
                    "counterproposal_issued", "counter_proposed", "awaiting_receipt",
                    digest, "sister_compras", subject_id, counterproposal
                )
            conn.commit()
        return self.get_integration_agreement()

    def activate_integration_agreement(self, receipt, subject_id):
        with psycopg.connect(self.conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT activation_receipt
                    FROM integration_agreements
                    WHERE agreement_id = %s::uuid
                    FOR UPDATE
                """, (receipt["agreement_id"],))
                current = cur.fetchone()
                if current and current[0] is not None:
                    if current[0] != receipt:
                        raise ValueError("recibo de ativação conflita com o vigente")
                    return self.get_integration_agreement()
                cur.execute("""
                    UPDATE integration_agreements SET
                        agreement_status = 'active',
                        local_processing_status = 'ready',
                        activation_receipt = %s::jsonb,
                        activated_at = now(),
                        updated_at = now()
                    WHERE agreement_id = %s::uuid
                      AND revision = %s
                      AND digest = %s
                      AND acceptance_receipt IS NOT NULL
                """, (
                    json.dumps(receipt), receipt["agreement_id"],
                    receipt["revision"], receipt["digest"]
                ))
                if cur.rowcount != 1:
                    raise ValueError("recibo de ativação não corresponde ao acordo aceito")
                self._append_integration_event(
                    cur, receipt["agreement_id"], receipt["revision"],
                    "activation_received", "active", "ready", receipt["digest"],
                    "sister_nexo", subject_id, receipt
                )
            conn.commit()
        return self.get_integration_agreement()

    def transition_integration_agreement(self, status, receipt, subject_id, issued_by):
        if status not in {"suspended", "revoked"}:
            raise ValueError("transição não permitida")
        timestamp_column = "suspended_at" if status == "suspended" else "revoked_at"
        with psycopg.connect(self.conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute(f"""
                    UPDATE integration_agreements SET
                        agreement_status = %s,
                        local_processing_status = 'ready',
                        {timestamp_column} = now(),
                        updated_at = now()
                    WHERE agreement_id = %s::uuid
                      AND revision = %s
                      AND digest = %s
                """, (
                    status, receipt["agreement_id"],
                    receipt["revision"], receipt["digest"]
                ))
                if cur.rowcount != 1:
                    raise ValueError("recibo não corresponde ao acordo")
                self._append_integration_event(
                    cur, receipt["agreement_id"], receipt["revision"],
                    f"{status}_received", status, "ready", receipt["digest"],
                    issued_by, subject_id, receipt
                )
            conn.commit()
        return self.get_integration_agreement()

    @staticmethod
    def _append_integration_event(
        cursor, agreement_id, revision, event_type, agreement_status,
        local_processing_status, digest, issued_by, subject_id, receipt
    ):
        import uuid
        cursor.execute("""
            INSERT INTO integration_agreement_events (
                event_id, agreement_id, revision, event_type, agreement_status,
                local_processing_status, digest, issued_by, subject_id, receipt
            ) VALUES (%s::uuid, %s::uuid, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
        """, (
            str(uuid.uuid4()), agreement_id, revision, event_type,
            agreement_status, local_processing_status, digest, issued_by,
            subject_id, json.dumps(receipt) if receipt is not None else "null"
        ))

    def load_data(self):
        if self.use_pg:
            try:
                data = {
                    "version": "0.4.0",
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
                        cur.execute("SELECT id, project_id, title, category, quantity, priority, status, responsible, estimated_budget, description, research_activity_id, activity_id FROM needs ORDER BY id ASC")
                        needs_map = {}
                        for row in cur.fetchall():
                            need_item = {
                                "id": row[0], "project_id": row[1], "title": row[2],
                                "category": row[3], "quantity": row[4], "priority": row[5],
                                "status": row[6], "responsible": row[7],
                                "estimated_budget": float(row[8]) if row[8] is not None else 0.0,
                                "description": row[9] or "",
                                "research_activity_id": row[10],
                                "activity_id": row[11],
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
            "version": "0.4.0",
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
                                INSERT INTO needs (id, project_id, title, category, quantity, priority, status, responsible, estimated_budget, description, research_activity_id, activity_id)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (id) DO UPDATE SET
                                    title = EXCLUDED.title,
                                    category = EXCLUDED.category,
                                    quantity = EXCLUDED.quantity,
                                    priority = EXCLUDED.priority,
                                    status = EXCLUDED.status,
                                    responsible = EXCLUDED.responsible,
                                    estimated_budget = EXCLUDED.estimated_budget,
                                    description = EXCLUDED.description,
                                    research_activity_id = EXCLUDED.research_activity_id,
                                    activity_id = EXCLUDED.activity_id;
                            """, (
                                need.get("id"), need.get("project_id", "PROJ-PESQUISA-01"),
                                need.get("title"), need.get("category"), need.get("quantity", 1),
                                need.get("priority", "Essencial"), need.get("status", "Especificada"),
                                need.get("responsible", "Equipe de Pesquisa"), float(need.get("estimated_budget", 0.0)),
                                need.get("description", ""),
                                need.get("research_activity_id"),
                                need.get("activity_id")
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
