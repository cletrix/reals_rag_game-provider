# Análise Arquitetural - RAG Game Provider

## Data: 2026-05-25

## Visão Geral

Este documento analisa a arquitetura atual do projeto e recomendações para refatoração.

## Estrutura Atual

```
reals_rag_game-provider/
├── web/                    # API FastAPI
│   ├── main.py           (1024 linhas) ❌ Muito grande
│   ├── db.py             (22KB)        ❌ Muitas responsabilidades
│   ├── schemas.py        (19KB)        ⚠️  Pode ser dividido
│   ├── auth.py           (1.5KB)       ✅ OK
│   ├── indexer.py        (10KB)        ✅ OK
│   ├── folder_scanner.py (4KB)         ✅ OK
│   └── templates/
├── app/                    # Aplicação RAG
├── rag/                    # Módulos RAG
├── db/                     # Scripts SQL
├── migrations/             # Migrations
├── tests/                  # Testes
└── scripts/                # Scripts utilitários
```

## Problemas Identificados

### 1. main.py - Monolito de Rotas (1024 linhas)

**Problema:**
- Contém todas as rotas em um único arquivo
- Mistura de responsabilidades: auth, chat, folders, documents, conversations, users, settings, health
- Difícil manutenção e testes
- Violação do princípio de responsabilidade única

**Rotas atuais em main.py:**
- `/api/auth/*` - Autenticação
- `/api/chat/*` - Chat
- `/api/folders/*` - Pastas
- `/api/documents/*` - Documentos
- `/api/conversations/*` - Conversas
- `/api/users/*` - Usuários
- `/api/settings/*` - Configurações
- `/liveness`, `/readiness` - Health checks
- `/login` - Página de login

### 2. db.py - Acesso ao Banco Monolítico (22KB)

**Problema:**
- Todas as funções de acesso ao banco em um arquivo
- Funções para usuários, pastas, documentos, conversas, queries misturadas
- Difícil localizar e manter funções específicas

**Funções atuais em db.py:**
- Usuários: `create_user`, `get_user_by_email`, `get_user_by_id`, `update_user`, `list_users`
- Pastas: `create_folder`, `get_folders`, `get_folder`, `update_folder`, `delete_folder`, `get_folder_by_path`, `get_auto_index_folders`
- Documentos: `create_document`, `get_documents`, `get_document`, `update_document_indexed`, `delete_document`, `get_document_by_path`
- Conversas: `get_conversations`, `get_conversation`, `get_conversation_messages`, `create_conversation`, `update_conversation_title`
- Queries: `get_history`, `get_query_by_id`, `save_query`, `get_stats`
- Pool: `get_pool`

### 3. schemas.py - Schemas Misturados (19KB)

**Problema:**
- Todos os schemas Pydantic em um arquivo
- Difícil localizar schemas específicos
- Pode ser dividido por domínio

## Recomendações

### 1. Manter como Monolito (Não Microserviços)

**Justificativa:**
- Projeto não é complexo o suficiente para microserviços
- Overhead de comunicação entre serviços não é justificado
- Equipe pequena, monolito mais fácil de manter
- Escalabilidade pode ser alcançada com horizontal scaling do container

**Quando considerar microserviços:**
- Quando o projeto tiver 50+ desenvolvedores
- Quando diferentes partes precisam escalar independentemente
- Quando diferentes equipes precisam trabalhar em diferentes domínios
- Quando tecnologias diferentes forem necessárias para diferentes partes

### 2. Refatorar main.py em Módulos de Rotas

**Estrutura proposta:**

```
web/
├── main.py                 (apenas inicialização e registro de rotas)
├── routes/
│   ├── __init__.py
│   ├── auth.py            (rotas de autenticação)
│   ├── chat.py            (rotas de chat)
│   ├── folders.py         (rotas de pastas)
│   ├── documents.py       (rotas de documentos)
│   ├── conversations.py   (rotas de conversas)
│   ├── users.py           (rotas de usuários)
│   ├── settings.py        (rotas de configurações)
│   └── health.py          (rotas de health check)
```

**Benefícios:**
- Separação clara de responsabilidades
- Mais fácil testar cada módulo
- Mais fácil manter e evoluir
- Permite diferentes desenvolvedores trabalharem em diferentes módulos

### 3. Refatorar db.py em Módulos de Acesso ao Banco

**Estrutura proposta:**

```
web/
├── db/
│   ├── __init__.py
│   ├── pool.py            (get_pool)
│   ├── users.py           (operações com usuários)
│   ├── folders.py         (operações com pastas)
│   ├── documents.py       (operações com documentos)
│   ├── conversations.py   (operações com conversas)
│   └── queries.py         (operações com queries)
```

**Benefícios:**
- Separação por domínio
- Mais fácil localizar funções
- Mais fácil testar cada módulo
- Permite otimizações específicas por domínio

### 4. Refatorar schemas.py em Módulos de Schemas

**Estrutura proposta:**

```
web/
├── schemas/
│   ├── __init__.py
│   ├── auth.py            (UserCreate, UserLogin, UserResponse, TokenResponse)
│   ├── chat.py            (ChatRequest, QueryResponse, QueryDetail)
│   ├── folders.py         (FolderResponse, FolderCreate, FolderUpdate)
│   ├── documents.py       (DocumentResponse, FolderUploadResponse)
│   ├── conversations.py  (ConversationResponse, ConversationDetail, ConversationUpdate, MessageResponse)
│   ├── settings.py        (SettingsResponse, SettingsUpdate)
│   └── common.py          (HealthResponse, ErrorResponse, StatsResponse)
```

**Benefícios:**
- Separação por domínio
- Mais fácil localizar schemas
- Mais fácil manter consistência

## Plano de Refatoração

### Fase 1: Preparação
1. Criar estrutura de diretórios
2. Criar arquivos `__init__.py`
3. Mover imports e exports

### Fase 2: Refatorar db.py
1. Criar `db/pool.py` com `get_pool`
2. Criar `db/users.py` com funções de usuários
3. Criar `db/folders.py` com funções de pastas
4. Criar `db/documents.py` com funções de documentos
5. Criar `db/conversations.py` com funções de conversas
6. Criar `db/queries.py` com funções de queries
7. Atualizar imports em `main.py`
8. Rodar testes para garantir que nada quebrou

### Fase 3: Refatorar schemas.py
1. Criar `schemas/auth.py` com schemas de autenticação
2. Criar `schemas/chat.py` com schemas de chat
3. Criar `schemas/folders.py` com schemas de pastas
4. Criar `schemas/documents.py` com schemas de documentos
5. Criar `schemas/conversations.py` com schemas de conversas
6. Criar `schemas/settings.py` com schemas de configurações
7. Criar `schemas/common.py` com schemas comuns
8. Atualizar imports em `main.py` e `db/`
9. Rodar testes para garantir que nada quebrou

### Fase 4: Refatorar main.py
1. Criar `routes/auth.py` com rotas de autenticação
2. Criar `routes/chat.py` com rotas de chat
3. Criar `routes/folders.py` com rotas de pastas
4. Criar `routes/documents.py` com rotas de documentos
5. Criar `routes/conversations.py` com rotas de conversas
6. Criar `routes/users.py` com rotas de usuários
7. Criar `routes/settings.py` com rotas de configurações
8. Criar `routes/health.py` com rotas de health check
9. Atualizar `main.py` para apenas registrar as rotas
10. Rodar testes para garantir que nada quebrou

### Fase 5: Validação
1. Rodar todos os testes
2. Testar manualmente todos os endpoints
3. Verificar performance
4. Documentar novas estruturas

## Conclusão

**Recomendação:** Manter como monolito, mas refatorar para melhor organização de código.

**Não recomendado:** Microserviços (projeto não tem complexidade suficiente).

**Prioridade:** Alta - Refatoração deve ser feita para facilitar manutenção futura.

**Tempo estimado:** 2-3 dias para refatoração completa com testes.
