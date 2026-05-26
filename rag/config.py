import os
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.embeddings.ollama import OllamaEmbedding

load_dotenv()


def configure(
    llm_provider: str | None = None,
    llm_model: str | None = None,
) -> None:
    """
    Configura o LLM global do LlamaIndex.

    llm_provider: "groq" | "ollama" | None (detecta via GROQ_API_KEY)
    llm_model:    nome do modelo; None usa o padrão do provider
    """
    groq_key = os.getenv("GROQ_API_KEY")

    if llm_provider is None:
        llm_provider = "groq" if groq_key and groq_key.strip() else "ollama"

    if llm_provider == "groq":
        from llama_index.llms.groq import Groq
        model = llm_model or os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        Settings.llm = Groq(model=model, api_key=groq_key)
    else:
        from llama_index.llms.ollama import Ollama
        model = llm_model or os.getenv("LLM_MODEL", "llama3.1:8b")
        Settings.llm = Ollama(
            model=model,
            base_url=os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"),
            request_timeout=120.0,
        )

    Settings.embed_model = OllamaEmbedding(
        model_name=os.getenv("EMBED_MODEL", "bge-m3"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"),
        embed_batch_size=int(os.getenv("EMBED_BATCH_SIZE", "50")),
    )
    Settings.chunk_size = int(os.getenv("CHUNK_SIZE", "1024"))
    Settings.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
