-- ============================================================================
-- SisTer-Compras — Esquema Relacional PostgreSQL
-- Arquitetura de Persistência para Gestão de Necessidades e Aquisições
-- ============================================================================

CREATE TABLE IF NOT EXISTS projects (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    lead_researcher VARCHAR(255) NOT NULL,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS needs (
    id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    priority VARCHAR(50) NOT NULL DEFAULT 'Essencial',
    status VARCHAR(50) NOT NULL DEFAULT 'Especificada',
    responsible VARCHAR(255) NOT NULL,
    estimated_budget NUMERIC(14, 2) DEFAULT 0.0,
    description TEXT,
    research_activity_id VARCHAR(64),
    activity_id VARCHAR(64),
    deadline DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS requirements (
    id VARCHAR(64) PRIMARY KEY,
    need_id VARCHAR(64) NOT NULL REFERENCES needs(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    constraint_value VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alternatives (
    id VARCHAR(64) PRIMARY KEY,
    need_id VARCHAR(64) NOT NULL REFERENCES needs(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'Produto Comercial',
    supplier_or_source VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS price_observations (
    id VARCHAR(64) PRIMARY KEY,
    alternative_id VARCHAR(64) NOT NULL REFERENCES alternatives(id) ON DELETE CASCADE,
    supplier VARCHAR(255) NOT NULL,
    unit_price NUMERIC(14, 2) NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'BRL',
    observed_date DATE DEFAULT CURRENT_DATE,
    source_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS evidences (
    id VARCHAR(64) PRIMARY KEY,
    alternative_id VARCHAR(64) NOT NULL REFERENCES alternatives(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    value TEXT NOT NULL,
    source_type VARCHAR(100) NOT NULL,
    source_description TEXT,
    consulted_at DATE DEFAULT CURRENT_DATE,
    verified_by VARCHAR(255),
    state VARCHAR(50) NOT NULL DEFAULT 'Verified',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS decisions (
    id VARCHAR(64) PRIMARY KEY,
    need_id VARCHAR(64) UNIQUE NOT NULL REFERENCES needs(id) ON DELETE CASCADE,
    selected_alternative_id VARCHAR(64) NOT NULL REFERENCES alternatives(id) ON DELETE CASCADE,
    technical_justification TEXT NOT NULL,
    decided_by VARCHAR(255) NOT NULL,
    decision_date DATE DEFAULT CURRENT_DATE,
    is_human_decision BOOLEAN NOT NULL DEFAULT TRUE,
    ai_assistant_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices de Performance
CREATE INDEX IF NOT EXISTS idx_needs_project ON needs(project_id);
CREATE INDEX IF NOT EXISTS idx_requirements_need ON requirements(need_id);
CREATE INDEX IF NOT EXISTS idx_alternatives_need ON alternatives(need_id);
CREATE INDEX IF NOT EXISTS idx_price_observations_alt ON price_observations(alternative_id);
CREATE INDEX IF NOT EXISTS idx_evidences_alt ON evidences(alternative_id);

ALTER TABLE needs ADD COLUMN IF NOT EXISTS research_activity_id VARCHAR(64);
ALTER TABLE needs ADD COLUMN IF NOT EXISTS activity_id VARCHAR(64);
CREATE INDEX IF NOT EXISTS idx_needs_research_activity
    ON needs(research_activity_id);
CREATE INDEX IF NOT EXISTS idx_needs_activity
    ON needs(activity_id);

CREATE TABLE IF NOT EXISTS integration_agreements (
    agreement_id UUID PRIMARY KEY,
    counterparty_system_id TEXT NOT NULL,
    protocol_version TEXT NOT NULL,
    profile TEXT NOT NULL,
    revision INTEGER NOT NULL CHECK (revision > 0),
    agreement_status TEXT NOT NULL CHECK (agreement_status IN (
        'draft', 'proposed', 'counter_proposed', 'accepted', 'active',
        'suspended', 'revoked', 'rejected', 'expired', 'incompatible'
    )),
    local_processing_status TEXT NOT NULL CHECK (local_processing_status IN (
        'pending_validation', 'validating', 'awaiting_receipt',
        'installing_credentials', 'ready', 'failed'
    )),
    digest TEXT NOT NULL,
    proposal JSONB NOT NULL,
    counterproposal JSONB,
    negotiated_capabilities JSONB NOT NULL DEFAULT '[]'::jsonb,
    acceptance_receipt JSONB,
    activation_receipt JSONB,
    proposed_by TEXT NOT NULL,
    accepted_by TEXT,
    proposed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    accepted_at TIMESTAMPTZ,
    activated_at TIMESTAMPTZ,
    suspended_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (counterparty_system_id, profile)
);

CREATE TABLE IF NOT EXISTS integration_agreement_events (
    event_id UUID PRIMARY KEY,
    agreement_id UUID NOT NULL REFERENCES integration_agreements(agreement_id),
    revision INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    agreement_status TEXT NOT NULL,
    local_processing_status TEXT NOT NULL,
    digest TEXT NOT NULL,
    issued_by TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    receipt JSONB,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS integration_agreement_events_agreement_idx
    ON integration_agreement_events(agreement_id, occurred_at);

CREATE TABLE IF NOT EXISTS compras_schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

DO $migration$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM compras_schema_migrations
        WHERE version='002_canonical_nexo_project_reference'
    ) THEN
        INSERT INTO projects(
            id,name,description,lead_researcher,start_date,end_date)
        SELECT
            'PROJ-RESILIENCIA',
            'Projeto Resiliência',
            coalesce(description,
                'Referência de projeto sob autoridade do SisTer Nexo.'),
            lead_researcher,
            start_date,
            end_date
        FROM projects
        WHERE id='PROJ-PESQUISA-01'
        ON CONFLICT(id) DO NOTHING;

        UPDATE needs
        SET project_id='PROJ-RESILIENCIA'
        WHERE project_id='PROJ-PESQUISA-01';

        INSERT INTO compras_schema_migrations(version)
        VALUES('002_canonical_nexo_project_reference');
    END IF;
END
$migration$;
