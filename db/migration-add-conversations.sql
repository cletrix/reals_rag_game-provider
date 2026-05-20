-- Migração: Adicionar sistema de conversas ao banco existente
-- Execute este script no PostgreSQL para migrar de queries individuais para sistema de conversas

-- 1. Criar tabela de conversas
CREATE TABLE IF NOT EXISTS conversations (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title         VARCHAR(255),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations (updated_at DESC);

-- 2. Adicionar coluna conversation_id à tabela queries (se ainda não existir)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'queries' AND column_name = 'conversation_id'
    ) THEN
        ALTER TABLE queries ADD COLUMN conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE;
    END IF;
END $$;

-- 3. Criar índice para busca eficiente
CREATE INDEX IF NOT EXISTS idx_queries_conversation ON queries(conversation_id, created_at ASC);

-- 4. Migrar dados existentes: criar uma conversa para cada query existente
-- (Opcional - execute apenas se quiser preservar histórico existente como conversas individuais)
/*
DO $$
DECLARE
    query_rec RECORD;
    new_conv_id UUID;
BEGIN
    FOR query_rec IN SELECT id, question, created_at FROM queries WHERE conversation_id IS NULL
    LOOP
        -- Criar conversa para cada query existente
        INSERT INTO conversations (title, created_at, updated_at)
        VALUES (
            LEFT(query_rec.question, 50) || CASE WHEN LENGTH(query_rec.question) > 50 THEN '...' ELSE '' END,
            query_rec.created_at,
            query_rec.created_at
        )
        RETURNING id INTO new_conv_id;
        
        -- Atualizar query com o ID da conversa
        UPDATE queries SET conversation_id = new_conv_id WHERE id = query_rec.id;
    END LOOP;
END $$;
*/

-- Comando para aplicar migração:
-- docker compose exec postgres psql -U rag -d ragdb -f db/migration-add-conversations.sql
