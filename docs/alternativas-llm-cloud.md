# Alternativas ao Groq para LLM na Nuvem

Serviços equivalentes ao Groq para uso como LLM no pipeline RAG. A troca é apenas uma linha no `.env` — a arquitetura já suporta qualquer provedor via LlamaIndex.

---

## Comparativo

| Serviço | Modelos disponíveis | Free tier | Latência típica | Destaque |
|---|---|---|---|---|
| [Groq](https://console.groq.com) | Llama 3.x, Mixtral, Gemma | Sim, generoso | ~2s | LPU dedicado — mais rápido do mercado |
| [Cerebras](https://cloud.cerebras.ai) | Llama 3.x | Sim | < 1s | Chip proprietário — supera Groq em velocidade |
| [Together AI](https://api.together.xyz) | Llama, Qwen, Mistral, Gemma | Créditos iniciais | ~3s | Maior variedade de modelos open source |
| [OpenRouter](https://openrouter.ai) | 100+ modelos | Alguns gratuitos | ~3-5s | Agrega Groq, Together, OpenAI, Anthropic etc. |
| [Hugging Face Inference](https://huggingface.co/inference-api) | Open source variado | Sim, limitado | ~5-10s | Lento no free tier; bom para testes |

---

## Como trocar o provedor

### Groq (atual)
```env
LLM_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=sua_chave
```

### Cerebras
```bash
pip install llama-index-llms-cerebras
```
```env
LLM_MODEL=llama3.1-70b
CEREBRAS_API_KEY=sua_chave
```

### Together AI
```bash
pip install llama-index-llms-together
```
```env
LLM_MODEL=meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo
TOGETHER_API_KEY=sua_chave
```

### OpenRouter
```bash
pip install llama-index-llms-openrouter
```
```env
LLM_MODEL=meta-llama/llama-3.3-70b-instruct
OPENROUTER_API_KEY=sua_chave
```

---

## Recomendação

- **Velocidade máxima:** Cerebras → Groq
- **Maior variedade de modelos:** OpenRouter ou Together AI
- **Orçamento zero para testes:** Groq free tier ou Cerebras free tier
