# Changelog

---

## [v1.2.0] — 2026-05-21

### Melhorias Técnicas e Infraestrutura

#### Rate Limiting (web/main.py)
- Rate limiting in-memory por IP: 30 requisições / 60 segundos (padrão)
- Configurável via variáveis de ambiente: `RATE_LIMIT_REQUESTS`, `RATE_LIMIT_WINDOW`
- Aplica apenas em rotas `/api/*` e `/chat/*`
- Retorna HTTP 429 com mensagem clara ao exceder o limite

#### Logging Estruturado JSON (web/logger.py)
- Novo módulo `logger.py` com `JSONFormatter`
- Cada log emitido como linha JSON: `ts`, `level`, `logger`, `msg` + campos extras
- Campos extras por contexto: `request_id`, `path`, `method`, `status_code`, `duration_ms`, `conversation_id`, `query_id`, `user_ip`
- Compatível com Loki, ELK Stack, Datadog, CloudWatch

#### Middleware de Requests (web/main.py)
- `logging_middleware`: loga método, path, status, duração e IP de cada request
- Adiciona header `X-Request-ID` em todas as respostas (útil para rastreamento)

#### Error Handlers Globais (web/main.py)
- `StarletteHTTPException` → JSON `{"error": "HTTPException", "message": "..."}`
- `RequestValidationError` → JSON `{"error": "ValidationError", "detail": [...]}`
- `Exception` genérica → JSON `{"error": "InternalServerError"}` + log do traceback

#### Validação de Input (web/main.py)
- `/chat/stream` agora valida o body via Pydantic `ChatRequest`
- Retorna 422 com mensagem clara se `question` estiver ausente ou vazia
- Limites: `min_length=1`, `max_length=10000`

#### Health / Readiness / Liveness (web/main.py)
- `GET /health` — verifica PostgreSQL, Qdrant e Ollama; retorna `207` quando degradado
- `GET /readiness` — probe de readiness: verifica conexão com PostgreSQL; retorna `503` se indisponível
- `GET /liveness` — probe de liveness: sempre `200` se o processo estiver vivo

#### Health Check no docker-compose (docker-compose.yml)
- Serviço `web` agora tem `healthcheck` via `/liveness`
- `start_period: 20s` para aguardar inicialização do FastAPI

#### Grafana (docker-compose.yml + grafana/)
- Serviço `grafana:10.4.2` adicionado na porta `3001`
- Volume nomeado `grafana_data` (criado automaticamente pelo Docker, sem `mkdir` manual)
- Senha configurável via `GRAFANA_PASSWORD` no `.env` (padrão: `admin`)
- **Provisioning automático** — datasource e dashboards configurados sem interação manual

#### Dashboards Grafana (grafana/provisioning/dashboards/)

**RAG — Visão Geral** (`rag-overview.json`)
- Total de queries, conversas, tokens e latência média nas últimas 24h (stats cards)
- Gráfico de queries por hora (timeseries)
- Gráfico de latência média por hora
- Pizza de queries por LLM provider
- Pizza de queries por modelo
- Tabela com as últimas 20 queries

**RAG — Conversas e Sessões** (`rag-conversations.json`)
- Conversas ativas nos últimos 7 dias
- Média e máximo de mensagens por conversa
- Queries sem conversa associada
- Gráfico de novas conversas por dia
- Histograma de distribuição de mensagens por conversa
- Top 10 conversas mais longas
- Tabela de conversas recentes

---

## [v1.1.0] — 2026-05-20

### Sistema de Conversas/Sessões

#### Banco de Dados (db/init.sql, db/migration-add-conversations.sql)
- Nova tabela `conversations` (`id`, `title`, `created_at`, `updated_at`)
- Coluna `conversation_id` (FK) adicionada em `queries`
- Índices para busca eficiente por conversa
- Script de migração para bancos existentes

#### Backend (web/db.py)
- `create_conversation(title)` — cria nova conversa
- `get_conversation(id)` — busca dados da conversa
- `get_conversations(limit)` — lista conversas com `message_count` e `preview`
- `get_conversation_messages(id)` — retorna thread completa ordenada
- `update_conversation_timestamp(id)` — atualiza `updated_at`
- `update_conversation_title(id, title)` — atualiza título
- `save_query(...)` — agora aceita `conversation_id` e retorna `(query_id, conv_id)`

#### API (web/main.py)
- `GET  /api/conversations` — lista conversas
- `POST /api/conversations` — cria nova conversa
- `GET  /api/conversations/{id}` — dados da conversa
- `GET  /api/conversations/{id}/messages` — thread completa
- `PATCH /api/conversations/{id}` — atualiza título
- `POST /chat/stream` — agora aceita e retorna `conversation_id`

#### Frontend (web/templates/index.html)
- Estados: `conversations[]`, `currentConversationId`
- `loadConversations()` — carrega lista para sidebar
- `loadConversation(id)` — carrega thread completa ao clicar no histórico
- `newChat()` — reseta `currentConversationId` para criar nova sessão
- `sendMessage()` — envia `conversation_id` no payload
- Sidebar exibe conversas agrupadas com contagem de mensagens

---

## [v1.0.0] — 2026-05-19

### Documentação de API (web/main.py, web/schemas.py)
- FastAPI docs automático em `/docs` e `/redoc`
- Todos os endpoints documentados com docstrings e tags
- Schemas Pydantic com exemplos em `web/schemas.py`
- `GET /health` inicial adicionado

### Schema de Auditoria Enterprise (db/schema-auditoria-enterprise.sql)
- Tabelas: `users`, `audit_log`, `documents`, `document_access_log`, `settings_history`
- Views: `user_activity_summary`, `department_activity_summary`
- Função `detect_anomalous_access()`
- Função `anonymize_old_data()` (LGPD)
