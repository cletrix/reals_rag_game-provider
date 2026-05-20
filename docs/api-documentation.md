# Documentação da API - RAG Game Provider

## Visão Geral

A API do RAG Game Provider fornece endpoints para:
- Consulta de documentos com RAG (Retrieval Augmented Generation)
- Gerenciamento de conversas e histórico
- Upload e indexação de documentos
- Configurações do sistema
- Estatísticas e health checks

**Base URL:** `http://localhost:2468`

**Documentação Interativa:**
- Swagger UI: http://localhost:2468/docs
- ReDoc: http://localhost:2468/redoc
- OpenAPI JSON: http://localhost:2468/openapi.json

---

## Autenticação

**Status:** Não implementado (ver TODO.md - Falha #3)

Atualmente a API não requer autenticação. Para produção, implementar:
- OAuth2/LDAP
- JWT tokens
- RBAC por departamento

---

## Rate Limiting

**Status:** Não implementado (ver TODO.md - Falha #4)

Atualmente não há rate limiting. Para produção, implementar:
- Rate limiting por IP
- Rate limiting por usuário
- Rate limiting por endpoint

---

## Endpoints

### Health Check

#### GET /health

Verifica saúde dos serviços dependentes.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-05-20T18:45:06.239791+00:00",
  "services": {
    "postgres": "healthy",
    "qdrant": "healthy",
    "ollama": "healthy"
  }
}
```

**Status Codes:**
- 200: OK
- 503: Service Unhealthy

**Exemplo:**
```bash
curl http://localhost:2468/health
```

---

### History

#### GET /api/history

Retorna histórico de queries com preview da resposta.

**Query Parameters:**
- (Nenhum - retorna últimas 50 queries)

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "question": "Como funciona o sistema?",
    "answer_preview": "O sistema utiliza RAG para responder perguntas...",
    "elapsed_ms": 1500,
    "llm_provider": "ollama",
    "llm_model": "qwen2.5:7b-instruct",
    "created_at": "2026-05-20T18:00:00+00:00",
    "conversation_id": "550e8400-e29b-41d4-a716-446655440001"
  }
]
```

**Exemplo:**
```bash
curl http://localhost:2468/api/history
```

#### GET /api/query/{query_id}

Retorna detalhes completos de uma query específica.

**Path Parameters:**
- `query_id` (string, required): ID da query

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "question": "Como funciona o sistema?",
  "answer": "O sistema utiliza RAG para responder perguntas baseadas em documentos indexados...",
  "sources": [
    {
      "file": "documento.md",
      "page": "1",
      "score": 0.85
    }
  ],
  "elapsed_ms": 1500,
  "llm_provider": "ollama",
  "llm_model": "qwen2.5:7b-instruct",
  "tokens_total": 500,
  "created_at": "2026-05-20T18:00:00+00:00"
}
```

**Status Codes:**
- 200: OK
- 404: Query não encontrada

**Exemplo:**
```bash
curl http://localhost:2468/api/query/550e8400-e29b-41d4-a716-446655440000
```

---

### Conversations

#### GET /api/conversations

Retorna lista de conversas com contagem de mensagens e preview.

**Query Parameters:**
- (Nenhum - retorna últimas 50 conversas)

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Como funciona o sistema?",
    "created_at": "2026-05-20T18:00:00+00:00",
    "updated_at": "2026-05-20T18:05:00+00:00",
    "message_count": 3,
    "preview": "Qual o seu nome?"
  }
]
```

**Exemplo:**
```bash
curl http://localhost:2468/api/conversations
```

#### POST /api/conversations

Cria uma nova conversa.

**Request Body:**
```json
{
  "title": "Minha nova conversa"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Minha nova conversa"
}
```

**Exemplo:**
```bash
curl -X POST http://localhost:2468/api/conversations \
  -H "Content-Type: application/json" \
  -d '{"title": "Minha nova conversa"}'
```

#### GET /api/conversations/{conversation_id}

Retorna dados de uma conversa específica.

**Path Parameters:**
- `conversation_id` (string, required): ID da conversa

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Como funciona o sistema?",
  "created_at": "2026-05-20T18:00:00+00:00",
  "updated_at": "2026-05-20T18:05:00+00:00"
}
```

**Status Codes:**
- 200: OK
- 404: Conversa não encontrada

**Exemplo:**
```bash
curl http://localhost:2468/api/conversations/550e8400-e29b-41d4-a716-446655440000
```

#### GET /api/conversations/{conversation_id}/messages

Retorna todas as mensagens de uma conversa.

**Path Parameters:**
- `conversation_id` (string, required): ID da conversa

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "question": "Como funciona o sistema?",
    "answer": "O sistema utiliza RAG para responder perguntas...",
    "sources": [
      {
        "file": "documento.md",
        "page": "1",
        "score": 0.85
      }
    ],
    "elapsed_ms": 1500,
    "llm_provider": "ollama",
    "llm_model": "qwen2.5:7b-instruct",
    "tokens_total": 500,
    "created_at": "2026-05-20T18:00:00+00:00"
  }
]
```

**Status Codes:**
- 200: OK
- 404: Conversa não encontrada

**Exemplo:**
```bash
curl http://localhost:2468/api/conversations/550e8400-e29b-41d4-a716-446655440000/messages
```

#### PATCH /api/conversations/{conversation_id}

Atualiza dados de uma conversa (título).

**Path Parameters:**
- `conversation_id` (string, required): ID da conversa

**Request Body:**
```json
{
  "title": "Novo título"
}
```

**Response:**
```json
{
  "ok": true
}
```

**Exemplo:**
```bash
curl -X PATCH http://localhost:2468/api/conversations/550e8400-e29b-41d4-a716-446655440000 \
  -H "Content-Type: application/json" \
  -d '{"title": "Novo título"}'
```

---

### Settings

#### GET /api/settings

Retorna todas as configurações do sistema.

**Response:**
```json
{
  "llm_provider": "ollama",
  "groq_model": null,
  "ollama_model": "qwen2.5:7b-instruct",
  "similarity_top_k": "2"
}
```

**Exemplo:**
```bash
curl http://localhost:2468/api/settings
```

#### POST /api/settings

Atualiza configurações do sistema.

**Request Body:**
```json
{
  "llm_provider": "ollama",
  "ollama_model": "qwen2.5:7b-instruct",
  "similarity_top_k": "3"
}
```

**Response:**
```json
{
  "ok": true
}
```

**Exemplo:**
```bash
curl -X POST http://localhost:2468/api/settings \
  -H "Content-Type: application/json" \
  -d '{"llm_provider": "ollama", "ollama_model": "qwen2.5:7b-instruct", "similarity_top_k": "3"}'
```

---

### Stats

#### GET /api/stats

Retorna estatísticas do sistema.

**Response:**
```json
{
  "total_queries": 150,
  "total_tokens": 75000,
  "groq_api_usage": null
}
```

**Exemplo:**
```bash
curl http://localhost:2468/api/stats
```

---

### Chat

#### POST /chat/stream

Endpoint de chat streaming com Server-Sent Events (SSE).

**Request Body:**
```json
{
  "question": "Como funciona o sistema?",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:** Server-Sent Events (SSE)

**Eventos:**
```json
// Token streaming
{"type": "token", "content": "O"}

// Sources
{"type": "sources", "sources": [{"file": "documento.md", "page": "1", "score": 0.85}]}

// Done
{"type": "done", "elapsed_ms": 1500, "query_id": "...", "conversation_id": "..."}

// Error
{"type": "error", "message": "Erro message"}
```

**Exemplo:**
```bash
curl -X POST http://localhost:2468/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "Como funciona o sistema?", "conversation_id": "..."}'
```

**Nota:** Se `conversation_id` não for fornecido, uma nova conversa é criada automaticamente.

---

### Documents

#### GET /api/files

Retorna lista de arquivos indexados.

**Response:**
```json
[
  {
    "filename": "documento.md",
    "size": 1024,
    "indexed": true
  }
]
```

**Exemplo:**
```bash
curl http://localhost:2468/api/files
```

#### POST /api/files/upload

Faz upload de arquivos para indexação.

**Request:** multipart/form-data

**Response:**
```json
{
  "saved": ["documento.md", "outro.pdf"]
}
```

**Exemplo:**
```bash
curl -X POST http://localhost:2468/api/files/upload \
  -F "files=@documento.md" \
  -F "files=@outro.pdf"
```

#### POST /api/index

Inicia indexação de documentos.

**Response:**
```json
{
  "ok": true,
  "message": "Indexação iniciada"
}
```

**Ou se já estiver indexando:**
```json
{
  "ok": false,
  "message": "Indexação já em andamento"
}
```

**Exemplo:**
```bash
curl -X POST http://localhost:2468/api/index
```

#### GET /api/index/status

Retorna status atual da indexação.

**Response:**
```json
{
  "status": "running",
  "message": "Indexando...",
  "progress_pct": 50,
  "total_chunks": 100,
  "done_chunks": 50
}
```

**Exemplo:**
```bash
curl http://localhost:2468/api/index/status
```

---

## Erros

### Formato de Erro

```json
{
  "error": "ValidationError",
  "message": "Invalid input",
  "detail": "question field is required"
}
```

### Status Codes Comuns

- 200: OK
- 400: Bad Request (input inválido)
- 404: Not Found (recurso não encontrado)
- 500: Internal Server Error (erro no servidor)

---

## Exemplos de Uso

### Exemplo 1: Nova Conversa com Pergunta

```bash
# 1. Criar nova conversa
curl -X POST http://localhost:2468/api/conversations \
  -H "Content-Type: application/json" \
  -d '{"title": "Sobre o sistema"}'

# Response: {"id": "...", "title": "Sobre o sistema"}

# 2. Fazer pergunta na conversa
curl -X POST http://localhost:2468/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "Como funciona o sistema?", "conversation_id": "..."}'
```

### Exemplo 2: Consultar Histórico

```bash
# Listar conversas
curl http://localhost:2468/api/conversations

# Listar histórico de queries
curl http://localhost:2468/api/history

# Detalhes de uma query específica
curl http://localhost:2468/api/query/{query_id}
```

### Exemplo 3: Upload e Indexação

```bash
# Upload de arquivos
curl -X POST http://localhost:2468/api/files/upload \
  -F "files=@documento.md"

# Iniciar indexação
curl -X POST http://localhost:2468/api/index

# Verificar status
curl http://localhost:2468/api/index/status
```

---

## SDKs e Clientes

### Python

```python
import httpx

# Exemplo: Fazer pergunta
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:2468/chat/stream",
        json={"question": "Como funciona o sistema?"}
    )
    # Processar SSE response
```

### JavaScript/TypeScript

```javascript
// Exemplo: Fazer pergunta
fetch('http://localhost:2468/chat/stream', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    question: 'Como funciona o sistema?'
  })
})
.then(response => {
  // Processar SSE response
  const reader = response.body.getReader();
  // ...
});
```

### cURL

```bash
# Exemplo: Fazer pergunta
curl -X POST http://localhost:2468/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"question": "Como funciona o sistema?"}'
```

---

## Limitações

- **Sem autenticação:** Qualquer pessoa pode acessar (ver TODO.md - Falha #3)
- **Sem rate limiting:** Possível abuso (ver TODO.md - Falha #4)
- **Sem validação robusta:** Inputs podem não ser validados completamente (ver TODO.md - Falha #4)
- **Sem tratamento de erros robusto:** Erros podem não ser tratados adequadamente (ver TODO.md - Falha #9)

---

## Próximos Passos

Para Enterprise-ready, implementar:

1. **Autenticação** (Falha #3)
   - OAuth2/LDAP
   - JWT tokens
   - RBAC por departamento

2. **Rate Limiting** (Falha #4)
   - Por IP
   - Por usuário
   - Por endpoint

3. **Validação Robusta** (Falha #4)
   - Pydantic models (já implementado parcialmente)
   - Sanitização de inputs
   - Validação de tamanho

4. **Tratamento de Erros** (Falha #9)
   - Logging estruturado
   - Retry com exponential backoff
   - Exceções customizadas

---

## Referências

- FastAPI Documentation: https://fastapi.tiangolo.com/
- OpenAPI Specification: https://swagger.io/specification/
- TODO.md: Plano de implementação enterprise
- guia-auditoria.md: Guia de auditoria
