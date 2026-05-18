import os
import sys
import time
sys.path.insert(0, "/app")

from qdrant_client import QdrantClient
from rag.config import configure
from rag.pipeline import get_query_engine

configure()

COLLECTION = os.getenv("QDRANT_COLLECTION", "landf_docs")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
LLM_MODEL  = os.getenv("LLM_MODEL", "?")
EMBED_MODEL = os.getenv("EMBED_MODEL", "?")

print("Conectando ao Qdrant e carregando índice...")
try:
    engine = get_query_engine()
except Exception as e:
    print(f"ERRO ao conectar: {e}")
    print("Certifique-se de rodar 'ingest.py' antes.")
    sys.exit(1)

client = QdrantClient(url=QDRANT_URL)
vectors = client.get_collection(COLLECTION).points_count or 0

print(f"\n  LLM:       {LLM_MODEL}")
print(f"  Embedding: {EMBED_MODEL}")
print(f"  Chunks:    {vectors:,}")
print(f"\nRAG pronto. Digite sua pergunta (Ctrl+C para sair).\n")

while True:
    try:
        q = input("Pergunta: ").strip()
        if not q:
            continue

        t0 = time.time()
        response = engine.query(q)
        elapsed = time.time() - t0

        print(f"\nResposta:\n{response}\n")

        if response.source_nodes:
            seen = {}
            for node in response.source_nodes:
                src  = node.metadata.get("file_name", "?")
                page = node.metadata.get("page_label", "")
                key  = (src, page)
                if key not in seen or (node.score or 0) > seen[key]:
                    seen[key] = node.score or 0
            print("Fontes:")
            for i, (src, page) in enumerate(seen, 1):
                score = seen[(src, page)]
                print(f"  [{i}] {src} {f'p.{page}' if page else ''} (score: {score:.3f})")

        print(f"  tempo: {elapsed:.1f}s\n")

    except KeyboardInterrupt:
        print("\nSaindo.")
        break
    except Exception as e:
        print(f"Erro na query: {e}\n")
