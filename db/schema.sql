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
