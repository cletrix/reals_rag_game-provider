# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## O que é este repositório

Este repositório é um **asset de skills** para Claude Code — não é um projeto de software executável. Contém arquivos `.skill` (ZIP archives) que empacotam conhecimento especializado para ser instalado e invocado via Claude Code em outros projetos.

## Estrutura de um arquivo `.skill`

Cada `.skill` é um ZIP com a estrutura:
```
nome-da-skill/
└── SKILL.md    ← frontmatter YAML + conteúdo Markdown
```

O `SKILL.md` tem obrigatoriamente um frontmatter com:
```yaml
---
name: nome-da-skill
description: Descrição detalhada de quando usar este skill (palavras-chave, contextos).
---
```

## Criar ou atualizar uma skill

```bash
# 1. Editar o conteúdo
mkdir -p skill-dir && vi skill-dir/SKILL.md

# 2. Empacotar
zip -r nova-skill.skill skill-dir/

# 3. Verificar
unzip -l nova-skill.skill
```

## Skill atual: `rag-ollama-docker.skill`

Documenta um sistema RAG 100% local para consulta de documentos privados:

- **Stack**: LlamaIndex 0.11+ · Qdrant (Docker) · Python 3.12 · Ollama (nativo/Metal)
- **Projeto alvo**: `/Users/cleyton/Dev/LandF/landf_rag/`
- **Collection Qdrant**: `landf_docs`
- **Modelos**: `nomic-embed-text` (embedding) + `llama3.1:8b` ou `qwen2.5:7b` (LLM)

### Decisão arquitetural principal

Ollama roda **fora do Docker** (nativo, Metal GPU). Os containers acessam via `host.docker.internal:11434`. Containerizar o Ollama desperdiçaria aceleração de hardware.

### Comandos de operação (quando o projeto estiver implantado)

```bash
# Setup inicial
ollama pull nomic-embed-text && ollama pull llama3.1:8b
docker compose up -d qdrant
docker compose run --rm rag python ingest.py   # indexar data/raw/

# Uso normal
docker compose up -d qdrant
docker compose run --rm -it rag                # query interativo

# Re-indexar após adicionar docs
docker compose run --rm rag python ingest.py

# Dashboard Qdrant
open http://localhost:6333/dashboard
```

### Variáveis de ambiente (`.env`)

| Variável | Padrão | Descrição |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://host.docker.internal:11434` | Ollama nativo |
| `QDRANT_URL` | `http://qdrant:6333` | Vector store |
| `QDRANT_COLLECTION` | `landf_docs` | Nome da collection |
| `EMBED_MODEL` | `nomic-embed-text` | Modelo de embedding |
| `LLM_MODEL` | `llama3.1:8b` | Modelo de inferência |
| `CHUNK_SIZE` | `1024` | Tamanho do chunk |
| `SIMILARITY_TOP_K` | `4` | Chunks recuperados por query |
