CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS queries (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question      TEXT NOT NULL,
    answer        TEXT NOT NULL,
    sources       JSONB NOT NULL DEFAULT '[]',
    elapsed_ms    INTEGER,
    llm_provider  VARCHAR(20) NOT NULL DEFAULT 'groq',
    llm_model     VARCHAR(100),
    tokens_total  INTEGER,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_queries_created_at ON queries (created_at DESC);

CREATE TABLE IF NOT EXISTS settings (
    key        VARCHAR(100) PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO settings (key, value) VALUES
    ('llm_provider',     'groq'),
    ('groq_model',       'llama-3.3-70b-versatile'),
    ('ollama_model',     'llama3.1:8b'),
    ('similarity_top_k', '2')
ON CONFLICT (key) DO NOTHING;
