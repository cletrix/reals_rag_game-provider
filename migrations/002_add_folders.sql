-- Migration 002: Add folders and documents tables
-- Adiciona sistema de organização por pastas para documentos

-- Tabela de pastas/folders
CREATE TABLE IF NOT EXISTS folders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    path VARCHAR(1024) NOT NULL UNIQUE,
    size_bytes BIGINT DEFAULT 0,
    file_count INT DEFAULT 0,
    indexed_at TIMESTAMP,
    auto_index BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_folders_path ON folders(path);
CREATE INDEX IF NOT EXISTS idx_folders_auto_index ON folders(auto_index);

-- Tabela de documentos (rastreia arquivos no sistema de arquivos)
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    folder_id UUID REFERENCES folders(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    path VARCHAR(1024) NOT NULL UNIQUE,
    size_bytes BIGINT NOT NULL,
    indexed BOOLEAN DEFAULT FALSE,
    indexed_at TIMESTAMP,
    mtime TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_documents_folder ON documents(folder_id);
CREATE INDEX IF NOT EXISTS idx_documents_indexed ON documents(indexed);
CREATE INDEX IF NOT EXISTS idx_documents_path ON documents(path);

-- Trigger para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_folders_updated_at BEFORE UPDATE ON folders
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Função para atualizar estatísticas da pasta
CREATE OR REPLACE FUNCTION update_folder_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE folders 
        SET size_bytes = size_bytes + NEW.size_bytes,
            file_count = file_count + 1,
            updated_at = NOW()
        WHERE id = NEW.folder_id;
    ELSIF TG_OP = 'UPDATE' THEN
        -- Se mudou de pasta ou tamanho
        IF OLD.folder_id != NEW.folder_id THEN
            UPDATE folders 
            SET size_bytes = size_bytes - OLD.size_bytes,
                file_count = file_count - 1,
                updated_at = NOW()
            WHERE id = OLD.folder_id;
            
            UPDATE folders 
            SET size_bytes = size_bytes + NEW.size_bytes,
                file_count = file_count + 1,
                updated_at = NOW()
            WHERE id = NEW.folder_id;
        ELSIF OLD.size_bytes != NEW.size_bytes THEN
            UPDATE folders 
            SET size_bytes = size_bytes - OLD.size_bytes + NEW.size_bytes,
                updated_at = NOW()
            WHERE id = NEW.folder_id;
        END IF;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE folders 
        SET size_bytes = size_bytes - OLD.size_bytes,
            file_count = file_count - 1,
            updated_at = NOW()
        WHERE id = OLD.folder_id;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_update_folder_stats
    AFTER INSERT OR UPDATE OR DELETE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_folder_stats();
