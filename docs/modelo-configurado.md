# Modelo LLM Configurado

## Modelo Atual: qwen2.5:7b-instruct

**Data de configuração:** 19/05/2026  
**Hardware:** Mac Mini M1, 16GB RAM  
**Uso:** RAG + Programação (Python) + Conhecimentos Gerais

## Especificações

- **Parâmetros:** 7B
- **Tamanho:** 4.7GB
- **Uso de RAM:** ~5-6GB
- **Contexto:** 32K tokens
- **Aceleração:** Metal GPU (Apple Silicon)

## Por que este modelo?

### Critérios de Seleção
1. **Hardware M1 16GB:** Precisava de modelo que coupa confortavelmente sem travar
2. **Programação (Python):** Forte capacidade de geração e análise de código
3. **RAG:** Excelente para consulta de documentos
4. **Conhecimentos Gerais:** Bom para perguntas gerais além de código

### Comparação Completa de Modelos

#### Modelos Leves (8-16GB RAM)

| Modelo | Código | Geral | RAM | Tamanho | Contexto | Veredito |
|--------|--------|-------|-----|---------|----------|----------|
| phi3:mini (3.8B) | ⭐⭐⭐ | ⭐⭐⭐⭐ | 4-5GB | 2.2GB | 4K | Ultra leve, bom para M1 8GB |
| llama3.2:3b | ⭐⭐⭐ | ⭐⭐⭐⭐ | 4-5GB | 2.0GB | 4K | Muito leve, bom geral |
| gemma2:2b | ⭐⭐ | ⭐⭐⭐ | 3-4GB | 1.6GB | 8K | Extremamente leve |
| qwen2.5:3b | ⭐⭐⭐ | ⭐⭐⭐ | 4-5GB | ~2GB | 32K | Leve, bom contexto |

#### Modelos Médios (16GB RAM - Recomendado para M1 16GB)

| Modelo | Código | Geral | RAM | Tamanho | Contexto | Veredito |
|--------|--------|-------|-----|---------|----------|----------|
| qwen2.5:7b-instruct | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 5-6GB | 4.7GB | 32K | **Equilíbrio ideal (atual)** |
| deepseek-coder:6.7b | ⭐⭐⭐⭐⭐ | ⭐⭐ | 6-7GB | ~4GB | 16K | Excelente para código |
| mistral:7b | ⭐⭐⭐ | ⭐⭐⭐⭐ | 5-6GB | ~4GB | 32K | Bom geral |
| llama3.1:8b | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 6-7GB | 4.7GB | 128K | Excelente contexto |
| qwen2.5-coder:7b | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 6-7GB | ~4.5GB | 32K | Ótimo para código |
| phi3:medium (14B) | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 8-10GB | ~7GB | 4K | Bom, mas pesado |

#### Modelos Pesados (32GB+ RAM - Para upgrade futuro)

| Modelo | Código | Geral | RAM | Tamanho | Contexto | Veredito |
|--------|--------|-------|-----|---------|----------|----------|
| qwen2.5:14b | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 10-12GB | ~9GB | 32K | Excelente qualidade |
| qwen2.5-coder:14b | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 10-12GB | ~9GB | 32K | Top em código |
| deepseek-coder:33b | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 16-20GB | ~20GB | 16K | SOTA código, pesado |
| qwen2.5-coder:32b | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 18-22GB | ~19GB | 32K | 92.7% HumanEval |
| llama3.1:70b | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 35-40GB | ~40GB | 128K | SOTA geral, muito pesado |

#### Modelos Especializados em Código

| Modelo | Código | Geral | RAM | Tamanho | Especialidade |
|--------|--------|-------|-----|---------|---------------|
| deepseek-coder:6.7b | ⭐⭐⭐⭐⭐ | ⭐⭐ | 6-7GB | ~4GB | Código geral |
| qwen2.5-coder:7b | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 6-7GB | ~4.5GB | Código + RAG |
| codestral:22b | ⭐⭐⭐⭐⭐ | ⭐⭐ | 14-16GB | ~14GB | Código avançado |
| deepseek-coder:33b | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 16-20GB | ~20GB | SOTA código |

#### Modelos Especializados em RAG/Long Context

| Modelo | Código | Geral | RAM | Tamanho | Contexto | Especialidade |
|--------|--------|-------|-----|---------|----------|---------------|
| llama3.1:8b | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 6-7GB | 4.7GB | 128K | Longo contexto |
| qwen2.5:7b-instruct | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 5-6GB | 4.7GB | 32K | RAG + código |
| qwen2.5:14b | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 10-12GB | ~9GB | 32K | Alta qualidade RAG |
| command-r:35b | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 18-22GB | ~20GB | 128K | SOTA RAG |

### Vantagens do qwen2.5:7b-instruct

1. **Excelente em Código:** 
   - Alta performance em benchmarks de programação
   - Treinado em大量 código Python
   - Boa capacidade de debugging e explicação

2. **Fortíssimo em RAG:**
   - Excelente compreensão de contexto
   - Boa capacidade de síntese de múltiplas fontes
   - 32K contexto permite documentos longos

3. **Conhecimentos Gerais:**
   - Amplo conhecimento geral além de código
   - Boa capacidade de raciocínio
   - Multilíngue (inclui português)

4. **Otimizado para M1:**
   - Aceleração via Metal GPU
   - Quantização eficiente via Ollama
   - Não trava em 16GB RAM

## Configuração Atual

```bash
# .env
EMBED_MODEL=bge-m3
LLM_MODEL=qwen2.5:7b-instruct
OLLAMA_BASE_URL=http://host.docker.internal:11434
QDRANT_COLLECTION=landf_docs
CHUNK_SIZE=1024
SIMILARITY_TOP_K=2
```

## Modelos Disponíveis (Ollama)

```bash
ollama list
# bge-m3:latest (embeddings)
# phi3:mini (alternativa leve)
# qwen2.5:7b-instruct (atual)
# llama3.2:latest (alternativa geral)
```

## Alternativas se Necessário

### Para Hardware M1 8GB (Modelos Leves)

#### Ultra leve (3-4GB RAM):
```bash
ollama pull gemma2:2b
# Atualizar .env: LLM_MODEL=gemma2:2b
```

#### Leve com bom contexto (4-5GB RAM):
```bash
ollama pull phi3:mini
# Atualizar .env: LLM_MODEL=phi3:mini
```

#### Leve geral (4-5GB RAM):
```bash
ollama pull llama3.2:3b
# Atualizar .env: LLM_MODEL=llama3.2:3b
```

### Para M1 16GB (Modelos Médios)

#### Foco 100% em código:
```bash
ollama pull deepseek-coder:6.7b
# Atualizar .env: LLM_MODEL=deepseek-coder:6.7b
```

#### Código + RAG (melhor que atual):
```bash
ollama pull qwen2.5-coder:7b
# Atualizar .env: LLM_MODEL=qwen2.5-coder:7b
```

#### Longo contexto (128K tokens):
```bash
ollama pull llama3.1:8b
# Atualizar .env: LLM_MODEL=llama3.1:8b
```

#### Geral equilibrado:
```bash
ollama pull mistral:7b
# Atualizar .env: LLM_MODEL=mistral:7b
```

### Para Upgrade 32GB+ RAM (Modelos Pesados)

#### Alta qualidade geral:
```bash
ollama pull qwen2.5:14b
# Atualizar .env: LLM_MODEL=qwen2.5:14b
```

#### SOTA em código (92.7% HumanEval):
```bash
ollama pull qwen2.5-coder:32b
# Atualizar .env: LLM_MODEL=qwen2.5-coder:32b
```

#### SOTA código (DeepSeek):
```bash
ollama pull deepseek-coder:33b
# Atualizar .env: LLM_MODEL=deepseek-coder:33b
```

#### SOTA geral (GPT-4 level):
```bash
ollama pull llama3.1:70b
# Atualizar .env: LLM_MODEL=llama3.1:70b
```

### Para Especialistas

#### Código avançado (22B):
```bash
ollama pull codestral:22b
# Atualizar .env: LLM_MODEL=codestral:22b
```

#### SOTA RAG (128K contexto):
```bash
ollama pull command-r:35b
# Atualizar .env: LLM_MODEL=command-r:35b
```

## Quando Considerar Upgrade

### Sinais que modelo atual (qwen2.5:7b-instruct) é suficiente:
- Respostas satisfatórias para tarefas de programação
- RAG retorna informações relevantes
- Sistema não trava nem fica excessivamente lento
- RAM disponível > 8GB durante uso

### Sinais que precisa de modelo melhor:
- Respostas de código frequentemente incorretas ou incompletas
- RAG não consegue sintetizar informações complexas
- Precisa de contexto muito longo (> 32K tokens)
- Tarefas de raciocínio complexo falham frequentemente

### Sinais que precisa de mais RAM/hardware:
- Sistema trava frequentemente
- Outras aplicações fecham por falta de RAM
- Ollama usa swap constante
- Performance degradada significativamente

### Recomendações de Upgrade por Cenário

#### Para programador profissional (código 90% do tempo):
- **Atual (16GB):** qwen2.5-coder:7b ou deepseek-coder:6.7b
- **Upgrade (32GB):** qwen2.5-coder:32b (92.7% HumanEval)
- **Upgrade (64GB):** deepseek-coder:33b + qwen2.5-coder:32b

#### Para RAG extensivo (documentos longos):
- **Atual (16GB):** llama3.1:8b (128K contexto)
- **Upgrade (32GB):** qwen2.5:14b (32K, alta qualidade)
- **Upgrade (64GB):** command-r:35b (128K SOTA RAG)

#### Para uso geral equilibrado:
- **Atual (16GB):** qwen2.5:7b-instruct (atual)
- **Upgrade (32GB):** qwen2.5:14b
- **Upgrade (64GB):** llama3.1:70b (GPT-4 level)

#### Para pesquisa/experimentação:
- **Atual (16GB):** Testar vários modelos 7B
- **Upgrade (32GB):** Testar modelos 14B-22B
- **Upgrade (64GB):** Testar modelos 32B-70B

## Performance Esperada

- **Velocidade:** ~15-20 tokens/s com Metal GPU
- **RAM:** ~5-6GB durante uso
- **Startup:** ~2-3 segundos para primeira resposta
- **Qualidade Código:** Comparável a GPT-3.5 para tarefas comuns
- **Qualidade RAG:** Excelente para síntese e consulta de documentos

### Performance Comparativa por Categoria

| Categoria | Velocidade | RAM | Qualidade |
|-----------|-----------|-----|-----------|
| Leves (3-4B) | 25-35 t/s | 3-5GB | ⭐⭐⭐ |
| Médios (7-8B) | 15-20 t/s | 5-7GB | ⭐⭐⭐⭐ |
| Pesados (14B) | 8-12 t/s | 10-12GB | ⭐⭐⭐⭐⭐ |
| SOTA (32B+) | 4-8 t/s | 18-40GB | ⭐⭐⭐⭐⭐ |

## Casos de Uso Ideais

1. **Programação Python:**
   - Geração de código
   - Debugging e explicação
   - Code review
   - Refatoração

2. **RAG Documental:**
   - Consulta a documentos técnicos
   - Síntese de múltiplas fontes
   - Perguntas sobre documentação

3. **Conhecimentos Gerais:**
   - Explicações técnicas
   - Conceitos de programação
   - Boas práticas

## Limitações

- Não é tão especializado em código quanto deepseek-coder
- Pode ser mais lento que phi3:mini em hardware mais limitado
- 32K contexto pode ser insuficiente para documentos muito longos

## Referências

- [Qwen2.5 Coder](https://ollama.com/library/qwen2.5-coder)
- [Ollama Models Guide](https://localaimaster.com/blog/mac-local-ai-setup)
- [Best Ollama Models for Coding](https://www.codegpt.co/blog/choosing-best-ollama-model)
