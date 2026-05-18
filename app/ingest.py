import os
import sys
import json
import time
sys.path.insert(0, "/app")

from pathlib import Path
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from rag.config import configure

configure()

DATA_DIR    = Path("/app/data/raw")
INDEX_FILE  = Path("/app/data/indexed.json")
SPEED_FILE  = Path("/app/data/embed_speed.json")
COLLECTION  = os.getenv("QDRANT_COLLECTION", "landf_docs")
QDRANT_URL  = os.getenv("QDRANT_URL", "http://qdrant:6333")
CHUNK_SIZE  = int(os.getenv("CHUNK_SIZE", "1024"))
CHUNK_OV    = int(os.getenv("CHUNK_OVERLAP", "200"))

if not DATA_DIR.exists() or not any(DATA_DIR.iterdir()):
    print(f"ERRO: Nenhum documento encontrado em {DATA_DIR}")
    sys.exit(1)

indexed = json.loads(INDEX_FILE.read_text()) if INDEX_FILE.exists() else {}

all_files = [
    f for f in DATA_DIR.rglob("*")
    if f.suffix in {".pdf", ".md", ".txt"} and f.is_file()
]

new_files = [
    f for f in all_files
    if str(f) not in indexed or indexed[str(f)] != f.stat().st_mtime
]

if not new_files:
    print("Nenhum documento novo. Nada a indexar.")
    sys.exit(0)

print(f"{len(new_files)} documento(s) para indexar:")
for f in new_files:
    print(f"  + {f.name}  ({f.stat().st_size / 1024 / 1024:.1f} MB)")

# Carregar documentos e contar chunks reais antes de indexar
print("\nAnalisando documentos...")
documents = SimpleDirectoryReader(
    input_files=[str(f) for f in new_files],
).load_data()

splitter   = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OV)
nodes      = splitter.get_nodes_from_documents(documents)
est_chunks = len(nodes)

# Velocidade: usa medição anterior se disponível
embed_speed = json.loads(SPEED_FILE.read_text()) if SPEED_FILE.exists() else {}
model       = os.getenv("EMBED_MODEL", "nomic-embed-text")
speed       = embed_speed.get(model, 12)  # padrão conservador
est_seconds = est_chunks / speed
est_min     = int(est_seconds // 60)
est_sec     = int(est_seconds % 60)

print(f"Chunks reais:  {est_chunks:,}")
print(f"Estimativa:    ~{est_min}m{est_sec:02d}s  ({speed:.0f} chunks/s com {model})\n")

client = QdrantClient(url=QDRANT_URL)

before = 0
if client.collection_exists(COLLECTION):
    before = client.get_collection(COLLECTION).points_count or 0

vector_store = QdrantVectorStore(client=client, collection_name=COLLECTION)
storage_ctx  = StorageContext.from_defaults(vector_store=vector_store)

t0 = time.time()
VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_ctx,
    show_progress=True,
)
elapsed = time.time() - t0

after = client.get_collection(COLLECTION).points_count or 0
added = after - before
real_speed = added / elapsed if elapsed > 0 else 0

# Salvar velocidade real medida para próxima estimativa
embed_speed[model] = real_speed
SPEED_FILE.write_text(json.dumps(embed_speed, indent=2))

for f in new_files:
    indexed[str(f)] = f.stat().st_mtime
INDEX_FILE.write_text(json.dumps(indexed, indent=2))

print(f"\nIndexação concluída em {int(elapsed // 60)}m{int(elapsed % 60):02d}s")
print(f"Vetores adicionados: {added:,}  |  total: {after:,}  |  velocidade real: {real_speed:.0f} chunks/s")
