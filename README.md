# RAG Híbrido — Embeddings Locais + Groq

Sistema de consulta a documentos privados em linguagem natural. Embeddings gerados localmente via Ollama, respostas via API do Groq (llama-3.3-70b-versatile).

> Faça perguntas em português sobre documentos em inglês — o modelo multilingual `bge-m3` resolve o mismatch de idioma.

---

## Como funciona

```
Sua pergunta (pt-BR ou en)
        │
        ▼
  bge-m3 [local, Ollama/Metal]
        │  embedding da query
        ▼
  Qdrant [Docker] ──► chunks mais relevantes
        │
        ▼
  Groq API [nuvem, llama-3.3-70b]
        │
        ▼
  Resposta + Fontes + Tempo de resposta
```

Os documentos ficam locais. As perguntas e os chunks recuperados são enviados ao Groq para geração de resposta.

---

## Stack

| Componente | Tecnologia |
|---|---|
| Embedding | `bge-m3` via Ollama (local, Metal GPU) |
| Vector store | Qdrant (Docker) |
| LLM | `llama-3.3-70b-versatile` via Groq API |
| Orquestração RAG | LlamaIndex 0.11+ |
| Runtime | Python 3.12 (Docker) |
| Instalador | `uv` |

---

## Requisitos

- Docker Desktop
- Ollama instalado nativamente
- Conta gratuita no [Groq](https://console.groq.com) para obter a API key

---

## Setup

```bash
# 1. Baixar modelo de embedding
ollama pull bge-m3

# 2. Configurar variáveis
cp .env.example .env
# editar .env: inserir GROQ_API_KEY

# 3. Colocar documentos (PDF, MD, TXT)
cp seus-docs/* data/raw/

# 4. Build + indexação + chat
make build
make chat
```

---

## Comandos

```bash
make chat      # uso normal — sobe Qdrant e abre o chat
make index     # indexa apenas documentos novos ou modificados
make rebuild   # reconstrói a imagem Docker
make reset     # apaga Qdrant e registro de indexação
make build     # setup completo do zero
```

---

## Variáveis de ambiente (`.env`)

| Variável | Descrição |
|---|---|
| `GROQ_API_KEY` | Chave da API Groq |
| `EMBED_MODEL` | Modelo de embedding (padrão: `bge-m3`) |
| `LLM_MODEL` | Modelo LLM (padrão: `llama-3.3-70b-versatile`) |
| `QDRANT_COLLECTION` | Nome da collection (padrão: `landf_docs`) |
| `CHUNK_SIZE` | Tokens por chunk (padrão: `1024`) |
| `SIMILARITY_TOP_K` | Chunks recuperados por query (padrão: `2`) |

Sem `GROQ_API_KEY`, o sistema usa Ollama local como fallback.

---

## Documentação

| Arquivo | Conteúdo |
|---|---|
| [`docs/rag-local-groq.skill`](docs/rag-local-groq.skill) | Skill completa — setup, código, decisões, troubleshooting |
| [`docs/alternativas-comerciais.md`](docs/alternativas-comerciais.md) | Comparativo de opções locais, cloud e hardware |
| [`docs/rag-pesquisa-arquitetura.skill`](docs/rag-pesquisa-arquitetura.skill) | Pesquisa inicial de arquitetura |

---

## Autores

**Cleyton Pedroza** — ideação, requisitos e validação  
**Claude Sonnet 4.6** (Anthropic) — implementação e documentação
