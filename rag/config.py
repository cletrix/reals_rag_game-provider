import os
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.embeddings.ollama import OllamaEmbedding

load_dotenv()

def configure():
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        from llama_index.llms.groq import Groq
        Settings.llm = Groq(
            model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
            api_key=groq_key,
        )
    else:
        from llama_index.llms.ollama import Ollama
        Settings.llm = Ollama(
            model=os.getenv("LLM_MODEL", "llama3.1:8b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"),
            request_timeout=120.0,
        )

    Settings.embed_model = OllamaEmbedding(
        model_name=os.getenv("EMBED_MODEL", "nomic-embed-text"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"),
        embed_batch_size=int(os.getenv("EMBED_BATCH_SIZE", "50")),
    )
    Settings.chunk_size = int(os.getenv("CHUNK_SIZE", "1024"))
    Settings.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
