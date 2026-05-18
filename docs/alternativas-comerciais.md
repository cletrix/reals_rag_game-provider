# Alternativas Comerciais e de Performance para RAG

Documento gerado a partir da sessão de implementação do RAG híbrido local + Groq.

---

## Situação atual do projeto

O sistema usa uma arquitetura **híbrida**:

| Componente | Onde roda | Privacidade |
|---|---|---|
| Embeddings (`bge-m3`) | Local — Ollama no Mac | Documentos nunca saem da máquina |
| Vector store (Qdrant) | Local — Docker | Dados locais |
| **LLM (`llama-3.3-70b-versatile`)** | **Nuvem — API do Groq** | **Queries e chunks recuperados vão para o Groq** |

> **Atenção:** as perguntas que você digita no chat e os trechos de documentos recuperados pelo Qdrant são enviados para os servidores do Groq para geração de resposta. Os documentos originais em `data/raw/` ficam locais, mas o conteúdo dos chunks relevantes trafega pela internet.

---

## Por que não ficamos 100% local

Durante a sessão, testamos modelos locais via Ollama no M4 Pro (48GB):

| Modelo | Resultado | Problema |
|---|---|---|
| `llama3.1:8b` | Rápido (~5s) | Respostas fracas, sem profundidade |
| `qwen2.5:14b` | Qualidade ok | 32s por resposta — lento demais |
| `llama3.1:70b` | Travou | Precisa ~45GB só para o modelo, sem sobra para o sistema |

**Solução adotada:** Groq na nuvem — respostas em 2-3s com modelo 70B de qualidade.

---

## Opções se precisar de 2s e 100% local

### Hardware de GPU (Linux ou Windows)

| Hardware | VRAM | Tempo 70B | Custo aproximado |
|---|---|---|---|
| RTX 4090 | 24GB | não roda 70B inteiro | ~R$ 9.000 |
| 2× RTX 4090 | 48GB | ~2-3s | ~R$ 18.000 |
| NVIDIA H100 PCIe | 80GB | < 1s | ~R$ 150.000+ |

- ROCm (AMD) funciona no Linux mas suporte é inferior ao CUDA da NVIDIA
- Para modelos até 14B, uma RTX 4090 sozinha resolve (~1-2s)

### Apple Silicon (mesma stack, hardware maior)

| Máquina | RAM unificada | Tempo 70B | Custo aproximado |
|---|---|---|---|
| Mac M4 Pro 48GB (atual) | 48GB | trava | — |
| Mac M4 Max 64GB | 64GB | ~8-10s | ~R$ 25.000 |
| **Mac Studio M4 Ultra 192GB** | **192GB** | **~2s** | **~R$ 50.000** |

O Mac Studio M4 Ultra é a opção mais simples para 100% local + 2s: mesmo sistema operacional, mesmo Ollama, sem Linux/CUDA.

### Software para melhorar performance no Mac atual

Não existe. O Ollama já usa Metal (GPU Apple) nativamente. O gargalo é hardware.

---

## Opções de nuvem

### Groq (atual)
- **Cadastro:** gratuito em `console.groq.com`, sem cartão
- **Free tier:** generoso para uso pessoal e testes
- **Plano pago:** ~$0.59/1M tokens (llama-3.3-70b) — para uso moderado empresarial, menos de $50/mês
- **Latência:** 2-3s para respostas completas
- **Limitação:** dados trafegam pela internet; não serve para compliance estrito

### Outras opções cloud

| Serviço | Modelos | Privacidade | Custo |
|---|---|---|---|
| **AWS Bedrock** | Llama, Claude, Titan | VPC privada, dados na sua região | Médio |
| **Azure OpenAI** | GPT-4, Llama | Compliance enterprise, LGPD | Alto |
| **Google Vertex AI** | Gemini, Llama | Dados na sua região | Médio |
| **Together AI** | Open source variado | Compartilhado | Baixo |
| **Hugging Face Inference** | Open source variado | Compartilhado | Gratuito/Baixo |

AWS Bedrock e Azure OpenAI são os mais indicados para empresas com compliance: dados ficam em região específica, SLA garantido, contratos enterprise.

---

## Recomendação por cenário

| Cenário | Recomendação |
|---|---|
| Teste / uso pessoal | Groq free tier (situação atual) |
| Empresa pequena, baixo volume | Groq pago (~$20-50/mês) |
| Empresa com compliance leve | AWS Bedrock ou Azure OpenAI |
| Compliance estrito (dados não podem sair) | Mac Studio M4 Ultra 192GB ou 2× RTX 4090 |
| Alta escala + baixa latência | H100 on-premise ou cluster GPU cloud |

---

## Próximo passo natural

Validar o produto com Groq. Quando o uso justificar (volume alto ou compliance obrigatório), migrar para hardware próprio ou nuvem privada. A troca é só uma linha no `.env` — a arquitetura já está preparada para ambos os casos.
