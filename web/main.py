import asyncio
import json
import os
import sys
import time
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

sys.path.insert(0, "/app")

from db import get_history, get_query_by_id, get_stats, save_query
from settings_manager import get_all_settings, update_setting
import indexer

DATA_RAW = Path("/app/data/raw")

app = FastAPI()
templates = Jinja2Templates(directory="templates")


# ---------------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    history = await get_history(limit=50)
    stats = await get_stats()
    return templates.TemplateResponse(request, "index.html", {
        "history": history,
        "stats": stats,
    })


# ---------------------------------------------------------------------------
# API — histórico e detalhes
# ---------------------------------------------------------------------------

@app.get("/api/history")
async def api_history():
    rows = await get_history(limit=50)
    for r in rows:
        if hasattr(r.get("created_at"), "isoformat"):
            r["created_at"] = r["created_at"].isoformat()
        if r.get("id"):
            r["id"] = str(r["id"])
    return rows


@app.get("/api/query/{query_id}")
async def api_query_detail(query_id: str):
    row = await get_query_by_id(query_id)
    if not row:
        raise HTTPException(status_code=404, detail="Query não encontrada")
    if hasattr(row.get("created_at"), "isoformat"):
        row["created_at"] = row["created_at"].isoformat()
    if row.get("id"):
        row["id"] = str(row["id"])
    return row


# ---------------------------------------------------------------------------
# API — configurações
# ---------------------------------------------------------------------------

@app.get("/api/settings")
async def api_get_settings():
    return await get_all_settings()


@app.post("/api/settings")
async def api_update_settings(request: Request):
    body = await request.json()
    for key, value in body.items():
        await update_setting(key, str(value))
    return {"ok": True}


# ---------------------------------------------------------------------------
# API — estatísticas
# ---------------------------------------------------------------------------

@app.get("/api/stats")
async def api_stats():
    local = await get_stats()
    groq_data = await _fetch_groq_usage()
    return {
        "total_queries": local["total_queries"],
        "total_tokens": local["total_tokens"],
        "groq_api_usage": groq_data,
    }


async def _fetch_groq_usage() -> dict | None:
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        return None
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(
                "https://api.groq.com/v1/usage",
                headers={"Authorization": f"Bearer {groq_key}"},
            )
            if r.status_code == 200:
                return r.json()
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Chat streaming (SSE)
# ---------------------------------------------------------------------------

@app.post("/chat/stream")
async def chat_stream(request: Request):
    body = await request.json()
    question = (body.get("question") or "").strip()
    if not question:
        return {"error": "question vazia"}

    settings = await get_all_settings()
    provider = settings.get("llm_provider", "groq")
    model_key = "groq_model" if provider == "groq" else "ollama_model"
    model = settings.get(model_key)
    top_k = int(settings.get("similarity_top_k", "2"))

    async def generate():
        try:
            # importa aqui para pegar a versão montada via volume
            from rag.config import configure
            from rag.pipeline import get_streaming_query_engine

            configure(llm_provider=provider, llm_model=model)
            engine = get_streaming_query_engine(similarity_top_k=top_k)

            t0 = time.time()

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, engine.query, question)

            full_answer = ""
            for token in response.response_gen:
                full_answer += token
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

            elapsed_ms = int((time.time() - t0) * 1000)

            # extrai fontes sem duplicatas
            sources = _extract_sources(response)
            if sources:
                yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"

            # extrai tokens (Groq retorna, Ollama não)
            tokens_total = _extract_tokens(response)

            query_id = await save_query(
                question=question,
                answer=full_answer,
                sources=sources,
                elapsed_ms=elapsed_ms,
                llm_provider=provider,
                llm_model=model,
                tokens_total=tokens_total,
            )

            yield f"data: {json.dumps({'type': 'done', 'elapsed_ms': elapsed_ms, 'query_id': str(query_id)})}\n\n"

        except Exception as exc:
            yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


def _extract_sources(response) -> list[dict]:
    if not response.source_nodes:
        return []
    seen: dict[tuple, float] = {}
    for node in response.source_nodes:
        fname = node.metadata.get("file_name", "desconhecido")
        page = node.metadata.get("page_label", "")
        score = node.score or 0.0
        key = (fname, page)
        if key not in seen or score > seen[key]:
            seen[key] = score
    return [
        {"file": k[0], "page": k[1], "score": round(v, 3)}
        for k, v in seen.items()
    ]


def _extract_tokens(response) -> int | None:
    try:
        meta = response.metadata or {}
        usage = meta.get("usage") or {}
        return usage.get("total_tokens")
    except Exception:
        return None


# ---------------------------------------------------------------------------
# API — documentos
# ---------------------------------------------------------------------------

@app.get("/api/files")
async def api_files():
    loop = asyncio.get_event_loop()
    files = await loop.run_in_executor(None, indexer.get_files)
    return files


@app.post("/api/files/upload")
async def api_upload(files: list[UploadFile] = File(...)):
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    saved = []
    for upload in files:
        suffix = Path(upload.filename).suffix.lower()
        if suffix not in {".pdf", ".md", ".txt"}:
            continue
        dest = DATA_RAW / upload.filename
        content = await upload.read()
        dest.write_bytes(content)
        saved.append(upload.filename)
    return {"saved": saved}


@app.post("/api/index")
async def api_index():
    started = await indexer.start_indexing()
    if not started:
        return {"ok": False, "message": "Indexação já em andamento"}
    return {"ok": True, "message": "Indexação iniciada"}


@app.get("/api/index/status")
async def api_index_status():
    return indexer.get_state()
