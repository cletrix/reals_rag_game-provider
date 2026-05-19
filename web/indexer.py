"""
Indexador de documentos com tracking de progresso em memória.

Estratégia de progresso:
  1. Conta chunks via SentenceSplitter antes de indexar  → sabe o total
  2. Roda VectorStoreIndex.from_documents() numa thread  → não bloqueia
  3. A cada 2s, lê o pointcount do Qdrant               → progresso real
  4. Atualiza _state que é lido pelos endpoints SSE
"""
import asyncio
import json
import os
import time
from pathlib import Path

from qdrant_client import QdrantClient

DATA_DIR   = Path("/app/data/raw")
INDEX_FILE = Path("/app/data/indexed.json")
SPEED_FILE = Path("/app/data/embed_speed.json")
COLLECTION = os.getenv("QDRANT_COLLECTION", "landf_docs")
QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1024"))
CHUNK_OV   = int(os.getenv("CHUNK_OVERLAP", "200"))

_state: dict = {
    "running":      False,
    "status":       "idle",   # idle | running | done | error
    "message":      "",
    "progress_pct": 0,
    "total_chunks": 0,
    "done_chunks":  0,
    "files":        [],
    "elapsed_s":    0,
    "error":        None,
}


def get_state() -> dict:
    return dict(_state)


def get_files() -> list[dict]:
    """Lista todos os arquivos em data/raw/ com status de indexação."""
    indexed = _load_indexed()
    files = []
    if not DATA_DIR.exists():
        return files
    for f in sorted(DATA_DIR.rglob("*")):
        if f.suffix in {".pdf", ".md", ".txt"} and f.is_file() and not f.name.startswith("."):
            stat = f.stat()
            key = str(f)
            is_indexed = key in indexed and indexed[key] == stat.st_mtime
            files.append({
                "name":       f.name,
                "path":       key,
                "size_kb":    round(stat.st_size / 1024, 1),
                "indexed":    is_indexed,
                "mtime":      stat.st_mtime,
            })
    return files


def _load_indexed() -> dict:
    return json.loads(INDEX_FILE.read_text()) if INDEX_FILE.exists() else {}


async def start_indexing() -> bool:
    """Inicia indexação em background. Retorna False se já estiver rodando."""
    if _state["running"]:
        return False
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, _do_index)
    return True


def _do_index() -> None:
    global _state

    _state.update({
        "running":      True,
        "status":       "running",
        "message":      "Detectando documentos...",
        "progress_pct": 0,
        "total_chunks": 0,
        "done_chunks":  0,
        "files":        [],
        "elapsed_s":    0,
        "error":        None,
    })

    t0 = time.time()

    try:
        # ── 1. descobrir arquivos novos ──────────────────────────────────
        indexed = _load_indexed()

        if not DATA_DIR.exists():
            raise RuntimeError(f"Diretório {DATA_DIR} não existe")

        all_files = [
            f for f in DATA_DIR.rglob("*")
            if f.suffix in {".pdf", ".md", ".txt"} and f.is_file()
        ]
        new_files = [
            f for f in all_files
            if str(f) not in indexed or indexed[str(f)] != f.stat().st_mtime
        ]

        if not new_files:
            _state.update({
                "running":      False,
                "status":       "done",
                "message":      "Nenhum documento novo para indexar.",
                "progress_pct": 100,
                "elapsed_s":    round(time.time() - t0, 1),
            })
            return

        _state["files"] = [f.name for f in new_files]
        _state["message"] = f"{len(new_files)} arquivo(s) encontrado(s). Dividindo em chunks..."

        # ── 2. dividir em chunks para saber o total ──────────────────────
        from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
        from llama_index.core.node_parser import SentenceSplitter
        from llama_index.vector_stores.qdrant import QdrantVectorStore
        from rag.config import configure

        configure()

        documents = SimpleDirectoryReader(
            input_files=[str(f) for f in new_files],
        ).load_data()

        splitter = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OV)
        nodes = splitter.get_nodes_from_documents(documents)
        total = len(nodes)

        _state["total_chunks"] = total
        _state["message"] = f"Gerando embeddings: 0 / {total} chunks..."
        _state["progress_pct"] = 2

        # ── 3. contar vetores antes de indexar ───────────────────────────
        client = QdrantClient(url=QDRANT_URL)
        before = 0
        if client.collection_exists(COLLECTION):
            before = client.get_collection(COLLECTION).points_count or 0

        vector_store = QdrantVectorStore(client=client, collection_name=COLLECTION)
        storage_ctx  = StorageContext.from_defaults(vector_store=vector_store)

        # ── 4. polling thread para atualizar progresso ───────────────────
        import threading

        stop_poll = threading.Event()

        def _poll():
            while not stop_poll.is_set():
                time.sleep(2)
                try:
                    c = QdrantClient(url=QDRANT_URL)
                    current = c.get_collection(COLLECTION).points_count or 0
                    added = max(0, current - before)
                    pct = min(int(added / total * 95), 95) if total > 0 else 0
                    _state["done_chunks"]  = added
                    _state["progress_pct"] = max(pct, 2)
                    _state["message"] = f"Gerando embeddings: {added} / {total} chunks..."
                except Exception:
                    pass

        poll_thread = threading.Thread(target=_poll, daemon=True)
        poll_thread.start()

        # ── 5. indexar ───────────────────────────────────────────────────
        VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_ctx,
            show_progress=False,
        )

        stop_poll.set()
        poll_thread.join(timeout=3)

        # ── 6. salvar registros ──────────────────────────────────────────
        after = client.get_collection(COLLECTION).points_count or 0
        added_final = after - before
        elapsed = time.time() - t0
        real_speed = added_final / elapsed if elapsed > 0 else 0

        embed_speed = json.loads(SPEED_FILE.read_text()) if SPEED_FILE.exists() else {}
        model = os.getenv("EMBED_MODEL", "bge-m3")
        embed_speed[model] = real_speed
        SPEED_FILE.write_text(json.dumps(embed_speed, indent=2))

        for f in new_files:
            indexed[str(f)] = f.stat().st_mtime
        INDEX_FILE.write_text(json.dumps(indexed, indent=2))

        _state.update({
            "running":      False,
            "status":       "done",
            "message":      f"Concluído! {added_final} vetores adicionados em {int(elapsed // 60)}m{int(elapsed % 60):02d}s",
            "progress_pct": 100,
            "done_chunks":  added_final,
            "elapsed_s":    round(elapsed, 1),
        })

    except Exception as exc:
        _state.update({
            "running":      False,
            "status":       "error",
            "message":      str(exc),
            "error":        str(exc),
            "elapsed_s":    round(time.time() - t0, 1),
        })
