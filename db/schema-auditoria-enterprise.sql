-- Schema Melhorado para Auditoria Enterprise
-- Compliance: LGPD, ISO 27001
-- Adiciona rastreabilidade completa de acessos e ações

-- =================================================================
-- TABELA DE USUÁRIOS (para autenticação e autorização)
-- =================================================================

CREATE TABLE IF NOT EXISTS users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         VARCHAR(255) UNIQUE NOT NULL,
    name          VARCHAR(255) NOT NULL,
    department    VARCHAR(100) NOT NULL,
    role          VARCHAR(50) NOT NULL DEFAULT 'user', -- admin, user, viewer
    is_active     BOOLEAN NOT NULL DEFAULT true,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_department ON users (department);
CREATE INDEX IF NOT EXISTS idx_users_role ON users (role);

-- =================================================================
-- TABELA DE AUDITORIA DE ACESSOS (logs de todas as ações)
-- =================================================================

CREATE TABLE IF NOT EXISTS audit_log (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID REFERENCES users(id) ON DELETE SET NULL,
    user_email    VARCHAR(255), -- redundante para quando user é deletado
    action_type   VARCHAR(50) NOT NULL, -- query, document_view, document_index, document_delete, settings_change, login, logout
    resource_type VARCHAR(50), -- query, document, settings, user
    resource_id   VARCHAR(255), -- ID do recurso acessado
    details       JSONB DEFAULT '{}',
    ip_address    INET,
    user_agent    TEXT,
    success       BOOLEAN NOT NULL DEFAULT true,
    error_message TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log (user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_action_type ON audit_log (action_type);
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at ON audit_log (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_log_resource ON audit_log (resource_type, resource_id);

-- =================================================================
-- ALTERAÇÃO NA TABELA QUERIES (adicionar user_id para rastreabilidade)
-- =================================================================

ALTER TABLE queries ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id) ON DELETE SET NULL;
ALTER TABLE queries ADD COLUMN IF NOT EXISTS user_email VARCHAR(255); -- redundante para auditoria
ALTER TABLE queries ADD COLUMN IF NOT EXISTS user_department VARCHAR(100);
ALTER TABLE queries ADD COLUMN IF NOT EXISTS ip_address INET;

CREATE INDEX IF NOT EXISTS idx_queries_user_id ON queries (user_id);
CREATE INDEX IF NOT EXISTS idx_queries_user_department ON queries (user_department);

-- =================================================================
-- TABELA DE DOCUMENTOS (rastrear documentos indexados)
-- =================================================================

CREATE TABLE IF NOT EXISTS documents (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_name     VARCHAR(512) NOT NULL,
    file_path     TEXT NOT NULL,
    file_size_kb  INTEGER,
    file_type     VARCHAR(50), -- pdf, md, txt
    department    VARCHAR(100),
    sensitivity_level VARCHAR(20) DEFAULT 'public', -- public, restricted, confidential
    indexed_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_accessed_at TIMESTAMPTZ,
    access_count  INTEGER DEFAULT 0,
    is_active     BOOLEAN NOT NULL DEFAULT true,
    metadata      JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_documents_file_name ON documents (file_name);
CREATE INDEX IF NOT EXISTS idx_documents_department ON documents (department);
CREATE INDEX IF NOT EXISTS idx_documents_sensitivity ON documents (sensitivity_level);
CREATE INDEX IF NOT EXISTS idx_documents_indexed_at ON documents (indexed_at DESC);

-- =================================================================
-- TABELA DE ACESSOS A DOCUMENTOS (auditoria específica de documentos)
-- =================================================================

CREATE TABLE IF NOT EXISTS document_access_log (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id   UUID REFERENCES documents(id) ON DELETE CASCADE,
    user_id       UUID REFERENCES users(id) ON DELETE SET NULL,
    user_email    VARCHAR(255),
    user_department VARCHAR(100),
    access_type   VARCHAR(50) NOT NULL, -- view, download, source_in_query
    query_id      UUID REFERENCES queries(id) ON DELETE SET NULL, -- se acesso via query
    ip_address    INET,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_doc_access_document_id ON document_access_log (document_id);
CREATE INDEX IF NOT EXISTS idx_doc_access_user_id ON document_access_log (user_id);
CREATE INDEX IF NOT EXISTS idx_doc_access_created_at ON document_access_log (created_at DESC);

-- =================================================================
-- TABELA DE CONFIGURAÇÕES (já existe, mas vamos adicionar auditoria)
-- =================================================================

-- Criar tabela de histórico de mudanças nas configurações
CREATE TABLE IF NOT EXISTS settings_history (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    setting_key   VARCHAR(100) NOT NULL,
    old_value     TEXT,
    new_value     TEXT NOT NULL,
    changed_by    UUID REFERENCES users(id) ON DELETE SET NULL,
    changed_by_email VARCHAR(255),
    changed_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reason        TEXT
);

CREATE INDEX IF NOT EXISTS idx_settings_history_key ON settings_history (setting_key);
CREATE INDEX IF NOT EXISTS idx_settings_history_changed_at ON settings_history (changed_at DESC);

-- =================================================================
-- TRIGGER PARA LOGAR MUDANÇAS NAS CONFIGURAÇÕES
-- =================================================================

CREATE OR REPLACE FUNCTION log_settings_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.value IS DISTINCT FROM NEW.value THEN
        INSERT INTO settings_history (setting_key, old_value, new_value, changed_by, changed_by_email, reason)
        VALUES (NEW.key, OLD.value, NEW.value, NULL, NULL, 'Configuration change');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_settings_change
    AFTER UPDATE ON settings
    FOR EACH ROW
    EXECUTE FUNCTION log_settings_change();

-- =================================================================
-- FUNÇÕES DE AUDITORIA (helpers para queries)
-- =================================================================

-- Função para obter estatísticas de uso por usuário
CREATE OR REPLACE FUNCTION get_user_stats(p_user_id UUID)
RETURNS TABLE (
    total_queries INTEGER,
    total_tokens INTEGER,
    avg_elapsed_ms NUMERIC,
    first_query TIMESTAMPTZ,
    last_query TIMESTAMPTZ,
    documents_accessed INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(q.id),
        COALESCE(SUM(q.tokens_total), 0),
        ROUND(AVG(q.elapsed_ms)::NUMERIC, 2),
        MIN(q.created_at),
        MAX(q.created_at),
        (SELECT COUNT(DISTINCT document_id) FROM document_access_log WHERE user_id = p_user_id)
    FROM queries q
    WHERE q.user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- Função para obter estatísticas por departamento
CREATE OR REPLACE FUNCTION get_department_stats(p_department VARCHAR)
RETURNS TABLE (
    total_queries INTEGER,
    total_users INTEGER,
    total_tokens INTEGER,
    avg_elapsed_ms NUMERIC,
    most_active_user VARCHAR,
    most_active_user_queries INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(q.id),
        COUNT(DISTINCT q.user_id),
        COALESCE(SUM(q.tokens_total), 0),
        ROUND(AVG(q.elapsed_ms)::NUMERIC, 2),
        (SELECT u.email FROM users u JOIN queries q2 ON u.id = q2.user_id WHERE q2.user_department = p_department GROUP BY u.email ORDER BY COUNT(q2.id) DESC LIMIT 1),
        (SELECT COUNT(q3.id) FROM queries q3 JOIN users u2 ON q3.user_id = u2.id WHERE u2.department = p_department GROUP BY u2.email ORDER BY COUNT(q3.id) DESC LIMIT 1)
    FROM queries q
    WHERE q.user_department = p_department;
END;
$$ LANGUAGE plpgsql;

-- Função para obter documentos mais acessados
CREATE OR REPLACE FUNCTION get_most_accessed_documents(p_limit INTEGER DEFAULT 10, p_days INTEGER DEFAULT 30)
RETURNS TABLE (
    document_id UUID,
    file_name VARCHAR,
    department VARCHAR,
    access_count INTEGER,
    unique_users INTEGER,
    last_accessed TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.id,
        d.file_name,
        d.department,
        COUNT(dal.id),
        COUNT(DISTINCT dal.user_id),
        MAX(dal.created_at)
    FROM documents d
    JOIN document_access_log dal ON d.id = dal.document_id
    WHERE dal.created_at >= NOW() - (p_days || ' days')::INTERVAL
    GROUP BY d.id, d.file_name, d.department
    ORDER BY COUNT(dal.id) DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Função para detectar acessos anômalos (muitos acessos em pouco tempo)
CREATE OR REPLACE FUNCTION detect_anomalous_access(p_threshold INTEGER DEFAULT 100, p_minutes INTEGER DEFAULT 60)
RETURNS TABLE (
    user_id UUID,
    user_email VARCHAR,
    access_count INTEGER,
    time_window INTERVAL,
    detected_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        al.user_id,
        al.user_email,
        COUNT(al.id),
        NOW() - MIN(al.created_at),
        NOW()
    FROM audit_log al
    WHERE al.created_at >= NOW() - (p_minutes || ' minutes')::INTERVAL
    GROUP BY al.user_id, al.user_email
    HAVING COUNT(al.id) > p_threshold
    ORDER BY COUNT(al.id) DESC;
END;
$$ LANGUAGE plpgsql;

-- =================================================================
-- VIEWS PARA RELATÓRIOS DE AUDITORIA
-- =================================================================

-- View: Resumo de atividade por usuário
CREATE OR REPLACE VIEW user_activity_summary AS
SELECT 
    u.id,
    u.email,
    u.name,
    u.department,
    u.role,
    COUNT(q.id) as total_queries,
    COALESCE(SUM(q.tokens_total), 0) as total_tokens,
    ROUND(AVG(q.elapsed_ms)::NUMERIC, 2) as avg_elapsed_ms,
    MIN(q.created_at) as first_query,
    MAX(q.created_at) as last_query,
    COUNT(DISTINCT dal.document_id) as unique_documents_accessed
FROM users u
LEFT JOIN queries q ON u.id = q.user_id
LEFT JOIN document_access_log dal ON u.id = dal.user_id
GROUP BY u.id, u.email, u.name, u.department, u.role;

-- View: Resumo de atividade por departamento
CREATE OR REPLACE VIEW department_activity_summary AS
SELECT 
    q.user_department,
    COUNT(DISTINCT q.user_id) as active_users,
    COUNT(q.id) as total_queries,
    COALESCE(SUM(q.tokens_total), 0) as total_tokens,
    ROUND(AVG(q.elapsed_ms)::NUMERIC, 2) as avg_elapsed_ms,
    MIN(q.created_at) as first_query,
    MAX(q.created_at) as last_query
FROM queries q
WHERE q.user_department IS NOT NULL
GROUP BY q.user_department;

-- View: Log de auditoria consolidado
CREATE OR REPLACE VIEW audit_consolidated AS
SELECT 
    al.id,
    al.action_type,
    al.resource_type,
    al.resource_id,
    al.user_email,
    u.department,
    al.ip_address,
    al.success,
    al.error_message,
    al.created_at,
    CASE 
        WHEN al.action_type = 'query' THEN (SELECT question FROM queries WHERE id = al.resource_id::UUID)
        WHEN al.action_type = 'document_view' THEN (SELECT file_name FROM documents WHERE id = al.resource_id::UUID)
        ELSE NULL
    END as context
FROM audit_log al
LEFT JOIN users u ON al.user_id = u.id;

-- =================================================================
-- POLÍTICA DE RETENÇÃO (LGPD)
-- =================================================================

-- Função para anonimizar dados pessoais antigos (conforme política de retenção)
CREATE OR REPLACE FUNCTION anonymize_old_data(p_retention_days INTEGER DEFAULT 1825) -- 5 anos por padrão
RETURNS INTEGER AS $$
DECLARE
    anonymized_count INTEGER;
BEGIN
    -- Anonimizar emails em queries antigas
    UPDATE queries 
    SET user_email = 'user_' || id::text,
        ip_address = NULL
    WHERE created_at < NOW() - (p_retention_days || ' days')::INTERVAL
    AND user_email IS NOT NULL;
    
    GET DIAGNOSTICS anonymized_count = ROW_COUNT;
    
    -- Anonimizar emails em audit_log antigas
    UPDATE audit_log 
    SET user_email = 'user_' || id::text,
        ip_address = NULL
    WHERE created_at < NOW() - (p_retention_days || ' days')::INTERVAL
    AND user_email IS NOT NULL;
    
    RETURN anonymized_count;
END;
$$ LANGUAGE plpgsql;

-- =================================================================
-- COMENTÁRIOS DE DOCUMENTAÇÃO
-- =================================================================

COMMENT ON TABLE users IS 'Tabela de usuários para autenticação e autorização';
COMMENT ON TABLE audit_log IS 'Tabela de auditoria de todos os acessos e ações no sistema';
COMMENT ON TABLE documents IS 'Tabela de documentos indexados no sistema RAG';
COMMENT ON TABLE document_access_log IS 'Tabela de auditoria específica de acessos a documentos';
COMMENT ON TABLE settings_history IS 'Histórico de mudanças nas configurações do sistema';

COMMENT ON COLUMN queries.user_id IS 'ID do usuário que fez a query (para rastreabilidade)';
COMMENT ON COLUMN queries.user_email IS 'Email do usuário (redundante para auditoria quando user é deletado)';
COMMENT ON COLUMN queries.user_department IS 'Departamento do usuário (para análises por departamento)';
COMMENT ON COLUMN queries.ip_address IS 'Endereço IP de onde a query foi feita (para auditoria de segurança)';

COMMENT ON COLUMN documents.sensitivity_level IS 'Nível de sensibilidade: public, restricted, confidential';
COMMENT ON COLUMN documents.access_count IS 'Contador de acessos ao documento (para métricas de uso)';

COMMENT ON COLUMN audit_log.action_type IS 'Tipo de ação: query, document_view, document_index, document_delete, settings_change, login, logout';
COMMENT ON COLUMN audit_log.resource_type IS 'Tipo de recurso: query, document, settings, user';
COMMENT ON COLUMN audit_log.resource_id IS 'ID do recurso acessado';

-- =================================================================
-- DADOS DE EXEMPLO (para teste)
-- =================================================================

-- Inserir usuário administrador padrão (senha deve ser hash no sistema real)
INSERT INTO users (email, name, department, role) VALUES
    ('admin@empresa.com', 'Administrador', 'TI', 'admin')
ON CONFLICT (email) DO NOTHING;

-- Inserir usuários de exemplo por departamento
INSERT INTO users (email, name, department, role) VALUES
    ('dev1@empresa.com', 'Desenvolvedor 1', 'Game Development', 'user'),
    ('dev2@empresa.com', 'Desenvolvedor 2', 'Game Development', 'user'),
    ('bets1@empresa.com', 'Analista Bets 1', 'Bets', 'user'),
    ('rh1@empresa.com', 'RH 1', 'RH', 'user')
ON CONFLICT (email) DO NOTHING;

-- =================================================================
-- NOTAS DE IMPLEMENTAÇÃO
-- =================================================================

-- 1. Para implementar autenticação:
--    - Adicionar sistema de login (OAuth2/LDAP)
--    - Criar middleware para identificar usuário em cada request
--    - Atualizar API para incluir user_id em todas as operações

-- 2. Para implementar auditoria automática:
--    - Criar triggers ou middleware para logar todas as ações
--    - Logar: queries, visualizações de documentos, mudanças de configuração
--    - Implementar alertas para acessos anômalos

-- 3. Para compliance LGPD:
--    - Configurar job periódico para anonimizar dados antigos
--    - Implementar endpoint para solicitação de exclusão de dados (direito ao esquecimento)
--    - Documentar base legal para processamento de dados

-- 4. Para monitoramento:
--    - Configurar dashboard para visualizar métricas de uso
--    - Configurar alertas para acessos não autorizados
--    - Monitorar usuários inativos para revogação de acesso

-- 5. Para performance:
--    - Considerar particionamento da tabela audit_log por data
--    - Configurar índices adicionais conforme necessário
--    - Arquivar logs antigos em storage separado
