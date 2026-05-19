# RAG Híbrido — Interface Web + Embeddings Locais + Groq

Sistema de consulta a documentos privados em linguagem natural, com **interface web estilo ChatGPT**, histórico de conversas persistido em banco de dados e alternância entre Groq e Ollama sem reiniciar nada.

> Faça perguntas em português sobre documentos em inglês — o modelo multilingual `bge-m3` resolve o mismatch de idioma.

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
| Runtime Python | Python 3.12 | Docker |
| Package manager | `uv` | Docker |

---

## Requisitos

### Obrigatórios

| Ferramenta | Versão mínima | Para que serve |
|---|---|---|
| **Docker Desktop** | 4.x | Roda Qdrant, PostgreSQL e o app web |
| **Ollama** | 0.3+ | Gera os embeddings localmente (Metal GPU no Mac) |
| **Groq API key** | — | LLM padrão (gratuito com limites) |

### Como instalar

```bash
# Docker Desktop
# https://www.docker.com/products/docker-desktop/

# Ollama (Mac)
brew install ollama
# ou baixar em https://ollama.com

# Verificar se Ollama está rodando
ollama list
```

### Groq API key

1. Criar conta em [console.groq.com](https://console.groq.com)
2. Gerar uma API key em **API Keys**
3. Copiar para o `.env` (ver Setup abaixo)

> Sem `GROQ_API_KEY`, o sistema usa Ollama local como LLM — mais lento, mas 100% offline.

---

## Setup (primeira vez)

```bash
# 1. Baixar o modelo de embedding
ollama pull bge-m3

# 2. Configurar variáveis de ambiente
cp .env.example .env
# editar .env e inserir sua GROQ_API_KEY

# 3. Colocar seus documentos (PDF, MD, TXT)
cp seus-docs/* data/raw/

# 4. Build completo: imagens + indexação
make build

# 5. Subir a interface web
make web-bg

# 6. Abrir no browser
open http://localhost:2468
```

---

## Uso diário

```bash
# Subir a interface web (com logs)
make web

# Subir em background
make web-bg
open http://localhost:2468

# Indexar novos documentos adicionados em data/raw/
make index

# Chat via linha de comando (modo legado)
make chat

# Acessar o banco PostgreSQL
make psql

# Reconstruir imagens Docker
make rebuild

# Zerar Qdrant e reindexar do zero
make reset
```

---

## Interface web (`http://localhost:2468`)

### Chat

- **Sidebar esquerda** — histórico de todas as conversas, clique para reabrir
- **Área central** — mensagens em bolhas (usuário à direita, assistente à esquerda)
- **Streaming** — a resposta aparece token a token enquanto o LLM processa
- **Fontes** — cada resposta mostra os documentos usados (clique para expandir)
- **Tempo** — duração de cada resposta exibida abaixo da bolha

### Configurações (ícone ⚙ no sidebar)

- **Provider LLM** — alternar entre Groq e Ollama sem reiniciar nada
- **Modelo Groq** — escolher entre llama-3.3-70b-versatile, llama-3.1-8b-instant, mixtral, gemma2
- **Modelo Ollama** — escolher entre llama3.1:8b, qwen2.5:7b, mistral:7b, qwen2.5:14b
- **Chunks recuperados** — quantos trechos do Qdrant são passados ao LLM (padrão: 2)
- **Uso Groq** — contagem de queries e tokens acumulados no banco local

As configurações são salvas no PostgreSQL e persistem entre reinicializações.

---

## Variáveis de ambiente (`.env`)

| Variável | Padrão | Descrição |
|---|---|---|
| `GROQ_API_KEY` | — | Chave da API Groq (**obrigatória** para usar Groq) |
| `EMBED_MODEL` | `bge-m3` | Modelo de embedding (Ollama) |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Modelo LLM padrão |
| `OLLAMA_BASE_URL` | `http://host.docker.internal:11434` | Endereço do Ollama nativo |
| `QDRANT_URL` | `http://qdrant:6333` | Endereço do Qdrant (interno Docker) |
| `QDRANT_COLLECTION` | `landf_docs` | Nome da collection |
| `CHUNK_SIZE` | `1024` | Tokens por chunk na indexação |
| `CHUNK_OVERLAP` | `200` | Sobreposição entre chunks |
| `SIMILARITY_TOP_K` | `2` | Chunks recuperados por query |
| `EMBED_BATCH_SIZE` | `50` | Chunks por batch no embedding |

> `DATABASE_URL` é definido automaticamente pelo Docker Compose para o container web — não precisa configurar no `.env`.

---

## Arquitetura dos containers

```
Host (Mac)
├── Ollama  [nativo, Metal GPU]  ← porta 11434
│
└── Docker Compose
    ├── landf_qdrant    [qdrant:latest]     ← portas 6333, 6334
    ├── landf_postgres  [postgres:16-alpine] ← porta 5432
    └── landf_web       [python:3.12-slim]  ← porta 2468
            │
            ├── monta ./rag/          (módulo RAG compartilhado)
            ├── monta ./web/          (hot-reload em dev)
            ├── acessa qdrant via rede Docker
            ├── acessa postgres via rede Docker
            └── acessa ollama via host.docker.internal:11434
```

**Por que Ollama roda fora do Docker?**
Containerizar o Ollama desperdiça a aceleração Metal (Apple Silicon). Rodando nativo, o `bge-m3` processa ~3.6 chunks/s com GPU. Dentro de Docker seria significativamente mais lento.

---

## Schema do banco (PostgreSQL)

```sql
-- Histórico de todas as consultas
queries (
  id            UUID PRIMARY KEY,
  question      TEXT,
  answer        TEXT,
  sources       JSONB,        -- [{file, page, score}]
  elapsed_ms    INTEGER,
  llm_provider  VARCHAR(20),  -- "groq" ou "ollama"
  llm_model     VARCHAR(100),
  tokens_total  INTEGER,      -- null para Ollama
  created_at    TIMESTAMPTZ
)

-- Configurações persistentes
settings (
  key        VARCHAR(100) PRIMARY KEY,  -- ex: "llm_provider"
  value      TEXT,
  updated_at TIMESTAMPTZ
)
```

---

## Documentação adicional

| Arquivo | Conteúdo |
|---|---|
| [`docs/rag-local-groq.skill`](docs/rag-local-groq.skill) | Skill completa — setup, código, decisões, troubleshooting |
| [`docs/alternativas-comerciais.md`](docs/alternativas-comerciais.md) | Comparativo de opções: hardware local vs Groq vs cloud |
| [`docs/alternativas-llm-cloud.md`](docs/alternativas-llm-cloud.md) | Como trocar Groq por Cerebras, Together AI, OpenRouter |
| [`docs/rag-pesquisa-arquitetura.skill`](docs/rag-pesquisa-arquitetura.skill) | Pesquisa inicial de arquitetura e decisões técnicas |

---

## Autores

**Cleyton Pedroza** — ideação, requisitos e validação  
**Claude Sonnet 4.6** (Anthropic) — implementação e documentação
