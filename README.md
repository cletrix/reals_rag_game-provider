# RAG Híbrido — Interface Web + Embeddings Locais + Groq

Sistema de consulta a documentos privados em linguagem natural, com interface web estilo ChatGPT, histórico de conversas, upload de documentos e alternância entre Groq e Ollama.

---

## Subindo o sistema

### Pré-requisitos

| Ferramenta | Como instalar |
|---|---|
| **Docker Desktop** | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/) |
| **Ollama** (nativo, não no Docker) | `brew install ollama` ou [ollama.com](https://ollama.com) |
| **Groq API key** | Criar conta em [console.groq.com](https://console.groq.com) → API Keys |

### Primeira vez

```bash
# 1. Baixar o modelo de embedding
ollama pull bge-m3

# 2. Configurar variáveis de ambiente
cp .env.example .env
# abrir .env e inserir GROQ_API_KEY=gsk_...

# 3. Colocar seus documentos (PDF, MD ou TXT)
cp seus-docs/* data/raw/

# 4. Build das imagens + indexação inicial
make build

# 5. Subir a interface web
make web-bg
open http://localhost:2468
```

### Uso diário

```bash
make web-bg            # sobe tudo em background → http://localhost:2468
make index             # indexa novos documentos adicionados em data/raw/
make chat              # chat via linha de comando (modo legado)
make psql              # abre o PostgreSQL interativo
make rebuild           # reconstrói as imagens Docker
make reset             # zera Qdrant e reindexação (mantém banco de histórico)
```

> **Dica:** pelo painel "Documentos" na interface web você pode fazer upload e indexar arquivos diretamente, sem precisar do terminal.

---

## Como funciona

```
Pergunta (pt-BR ou en)
        │
        ▼
  bge-m3 [Ollama, local, Metal GPU]
        │  embedding da query
        ▼
  Qdrant [Docker] ──► chunks mais relevantes
        │
        ▼
  Groq API [nuvem] ou Ollama [local]  ← configurável na UI
        │
        ▼
  Resposta em streaming + Fontes + Tempo
        │
        ▼
  PostgreSQL [Docker] ← histórico salvo automaticamente
```

Documentos ficam locais. Embeddings são gerados na sua máquina (Metal GPU). Apenas a pergunta + chunks vão ao Groq (se configurado assim).

---

## Interface web (`http://localhost:2468`)

### Chat
- **Sidebar** — histórico de todas as conversas; clique para reabrir qualquer uma
- **Streaming** — a resposta aparece token a token enquanto o LLM processa
- **Fontes** — cada resposta mostra os documentos usados (clique para expandir)

### Documentos (ícone no sidebar)
- Lista todos os arquivos em `data/raw/` com status **indexado** ou **pendente**
- Upload por **drag & drop** ou clique — aceita PDF, MD, TXT
- Botão "Indexar pendentes" roda a indexação em background
- **Barra de progresso flutuante** mostra chunks processados em tempo real — você pode voltar ao chat enquanto isso
- Bolinha amarela pulsante no sidebar indica indexação em andamento

### Configurações (ícone ⚙ no sidebar)
- Toggle **Groq / Ollama** sem reiniciar containers
- Seleção de modelo para cada provider
- Ajuste de chunks recuperados por query
- Estatísticas de uso: queries e tokens acumulados

---

## Stack

| Componente | Tecnologia | Onde roda |
|---|---|---|
| Interface web | FastAPI + Tailwind + Alpine.js | Docker (porta **2468**) |
| Embedding | `bge-m3` via Ollama | **Nativo** (Metal GPU) |
| Vector store | Qdrant | Docker (porta 6333) |
| Banco de histórico | PostgreSQL 16 | Docker (porta 5432) |
| LLM padrão | `llama-3.3-70b-versatile` via Groq | Nuvem |
| LLM alternativo | Qualquer modelo Ollama | **Nativo** |
| Orquestração RAG | LlamaIndex 0.11+ | Docker |

**Por que Ollama fora do Docker?** Containerizar desperdiça a aceleração Metal. Rodando nativo, o `bge-m3` processa ~3.6 chunks/s com GPU.

---

## Variáveis de ambiente (`.env`)

| Variável | Padrão | Descrição |
|---|---|---|
| `GROQ_API_KEY` | — | Chave da API Groq (**obrigatória** para usar Groq) |
| `EMBED_MODEL` | `bge-m3` | Modelo de embedding (Ollama) |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Modelo LLM padrão |
| `OLLAMA_BASE_URL` | `http://host.docker.internal:11434` | Endereço do Ollama nativo |
| `QDRANT_COLLECTION` | `landf_docs` | Nome da collection no Qdrant |
| `CHUNK_SIZE` | `1024` | Tokens por chunk na indexação |
| `SIMILARITY_TOP_K` | `2` | Chunks recuperados por query |

---

## Arquitetura dos containers

```
Host (Mac)
├── Ollama  [nativo, Metal GPU]  ← porta 11434
│
└── Docker Compose
    ├── landf_qdrant    [qdrant:latest]      ← portas 6333, 6334
    ├── landf_postgres  [postgres:16-alpine] ← porta 5432
    └── landf_web       [python:3.12-slim]   ← porta 2468
```

---

## Documentação adicional

| Arquivo | Conteúdo |
|---|---|
| [`docs/alternativas-comerciais.md`](docs/alternativas-comerciais.md) | Hardware local vs Groq vs cloud |
| [`docs/alternativas-llm-cloud.md`](docs/alternativas-llm-cloud.md) | Como trocar Groq por Cerebras, Together AI, OpenRouter |
| [`docs/rag-local-groq.skill`](docs/rag-local-groq.skill) | Skill com decisões técnicas e troubleshooting |
| [`docs/TODO.md`](docs/TODO.md) | Plano de implementação enterprise |
| [`docs/api-documentation.md`](docs/api-documentation.md) | Documentação completa da API |
| [`docs/guia-auditoria.md`](docs/guia-auditoria.md) | Guia de consultas de auditoria LGPD |
| [`docs/analise-mudancas-training_lb.md`](docs/analise-mudancas-training_lb.md) | Análise de mudanças da branch training_lb |

---

## Melhorias Implementadas (Branch training_lb)

### Funcionalidades Enterprise
- ✅ **Sistema de Conversas** - Agrupamento de mensagens em conversas com contexto
- ✅ **Documentação de API** - FastAPI com OpenAPI/Swagger, Pydantic schemas, docs/api-documentation.md
- ✅ **Health Checks** - Endpoints /health, /readiness, /liveness com verificação de dependências
- ✅ **Rate Limiting** - Proteção contra abuso (30 requests/60 segundos por IP)
- ✅ **Logging Estruturado** - Logs JSON com structlog, Request ID para rastreabilidade
- ✅ **Error Handlers Globais** - Tratamento consistente de erros HTTP, Validation e Generic
- ✅ **Grafana** - Dashboard de monitoramento configurado (porta 3001)
- ✅ **Deploy Automatizado** - Script deploy.sh e migrações automáticas via docker-compose
- ✅ **Auditoria Enterprise** - Schema opcional para compliance LGPD/ISO 27001

### Acesso à API
- Swagger UI: http://localhost:2468/docs
- ReDoc: http://localhost:2468/redoc
- OpenAPI JSON: http://localhost:2468/openapi.json
- Grafana: http://localhost:3001 (admin/admin)

---

## Plano Futuro (TODO.md)

### Melhorias Pendentes
- ⚠️ **Testes Automatizados** - Pytest com testes unitários, integração e E2E
- ⚠️ **CI/CD** - GitHub Actions para pipeline test → build → deploy
- ⚠️ **Autenticação e Autorização** - OAuth2/LDAP, JWT tokens, RBAC por departamento
- ⚠️ **Configuração por Ambiente** - .env.dev, .env.staging, .env.prod
- ⚠️ **Backup Automatizado** - Scripts de backup/restore, cron job

### Status Atual
- ✅ Funcional
- 🟡 Parcialmente Enterprise-ready (5 de 10 falhas críticas resolvidas)

**Para Enterprise-ready:** Implementar as melhorias pendentes listadas em docs/TODO.md

---

## Autores

**Cleyton Pedroza** — ideação, requisitos e validação  
**Claude Sonnet 4.6** (Anthropic) — implementação e documentação
