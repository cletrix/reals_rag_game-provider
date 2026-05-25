import asyncio
import json
import os
import sys
import time
import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import List

import httpx
from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

sys.path.insert(0, "/app")

from db import (
    get_history, get_query_by_id, get_stats, save_query,
    get_conversations, get_conversation, get_conversation_messages,
    create_conversation, update_conversation_title, get_pool,
    create_folder, get_folders, get_folder, update_folder, delete_folder, get_folder_by_path,
    create_document, get_documents, get_document, update_document_indexed, delete_document, get_document_by_path,
    get_auto_index_folders,
    create_user, get_user_by_username, get_user_by_email, get_user_by_id,
    update_user_last_login, update_user, list_users
)
from logger import log
from settings_manager import get_all_settings, update_setting
from schemas import (
    SettingsResponse, SettingsUpdate,
    QueryResponse, QueryDetail,
    StatsResponse,
    ConversationResponse, ConversationDetail, ConversationUpdate,
    MessageResponse,
    ChatRequest,
    HealthResponse,
    ErrorResponse,
    FolderResponse, FolderCreate, FolderUpdate,
    DocumentResponse, FolderUploadResponse,
    UserCreate, UserLogin, UserResponse, TokenResponse, UserUpdate
)
import auth
import indexer
import folder_scanner

DATA_RAW = Path("/app/data/raw")

# ---------------------------------------------------------------------------
# Rate limiting simples (in-memory por IP)
# ---------------------------------------------------------------------------
_rate_counters: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "30"))  # requests
RATE_LIMIT_WINDOW  = int(os.getenv("RATE_LIMIT_WINDOW",   "60"))   # segundos


def _check_rate_limit(ip: str) -> bool:
    """Retorna True se o IP ainda está dentro do limite."""
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW
    hits = _rate_counters[ip]
    # remove registros fora da janela
    _rate_counters[ip] = [t for t in hits if t > window_start]
    if len(_rate_counters[ip]) >= RATE_LIMIT_REQUESTS:
        return False
    _rate_counters[ip].append(now)
    return True


app = FastAPI(
    title="RAG Game Provider API",
    description="API para sistema RAG híbrido com interface web estilo ChatGPT",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
templates = Jinja2Templates(directory="templates")


# ---------------------------------------------------------------------------
# Middleware — logging de requests + request_id
# ---------------------------------------------------------------------------

@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start = time.time()
    response = await call_next(request)
    duration_ms = int((time.time() - start) * 1000)
    log.info(
        "%s %s",
        request.method,
        request.url.path,
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "user_ip": request.client.host if request.client else "unknown",
        },
    )
    response.headers["X-Request-ID"] = request_id
    return response


# ---------------------------------------------------------------------------
# Middleware — rate limiting (aplica apenas em /api e /chat)
# ---------------------------------------------------------------------------

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    path = request.url.path
    if path.startswith("/api") or path.startswith("/chat"):
        ip = request.client.host if request.client else "unknown"
        if not _check_rate_limit(ip):
            log.warning("Rate limit excedido", extra={"user_ip": ip, "path": path})
            return JSONResponse(
                status_code=429,
                content={"error": "Too Many Requests", "message": "Limite de requisições excedido. Tente novamente em instantes."},
            )
    return await call_next(request)


# ---------------------------------------------------------------------------
# Error handlers globais
# ---------------------------------------------------------------------------

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    log.warning(
        "HTTP %s: %s",
        exc.status_code,
        exc.detail,
        extra={"path": request.url.path, "status_code": exc.status_code},
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "HTTPException", "message": str(exc.detail)},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    log.warning(
        "Validation error: %s",
        errors,
        extra={"path": request.url.path, "status_code": 422},
    )
    return JSONResponse(
        status_code=422,
        content={
            "error": "ValidationError",
            "message": "Dados de entrada inválidos",
            "detail": errors,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    log.exception(
        "Erro não tratado: %s",
        str(exc),
        extra={"path": request.url.path, "status_code": 500},
    )
    return JSONResponse(
        status_code=500,
        content={"error": "InternalServerError", "message": "Erro interno do servidor"},
    )


# ---------------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------------

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login."""
    return templates.TemplateResponse(request, "login.html")


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

@app.get("/api/history", response_model=List[QueryResponse], tags=["History"])
async def api_history():
    """
    Retorna histórico de queries.

    Retorna lista de queries com preview da resposta e metadados.
    """
    rows = await get_history(limit=50)
    for r in rows:
        if hasattr(r.get("created_at"), "isoformat"):
            r["created_at"] = r["created_at"].isoformat()
        if r.get("id"):
            r["id"] = str(r["id"])
        if r.get("conversation_id"):
            r["conversation_id"] = str(r["conversation_id"])
    return rows


@app.get("/api/query/{query_id}", response_model=QueryDetail, tags=["History"])
async def api_query_detail(query_id: str):
    """
    Retorna detalhes completos de uma query específica.

    - **query_id**: ID da query a ser recuperada
    """
    row = await get_query_by_id(query_id)
    if not row:
        raise HTTPException(status_code=404, detail="Query não encontrada")
    if hasattr(row.get("created_at"), "isoformat"):
        row["created_at"] = row["created_at"].isoformat()
    if row.get("id"):
        row["id"] = str(row["id"])
    if row.get("conversation_id"):
        row["conversation_id"] = str(row["conversation_id"])
    return row


# ---------------------------------------------------------------------------
# API — conversas (sessões)
# ---------------------------------------------------------------------------

@app.get("/api/conversations", response_model=List[ConversationResponse], tags=["Conversations"])
async def api_get_conversations():
    """
    Retorna lista de conversas com contagem de mensagens e preview.

    Retorna lista de conversas ordenadas por atualização mais recente.
    """
    conversations = await get_conversations(limit=50)
    return conversations


@app.post("/api/conversations", response_model=ConversationDetail, tags=["Conversations"])
async def api_create_conversation(request: Request):
    """
    Cria uma nova conversa.

    - **title**: Título opcional da conversa
    """
    body = await request.json()
    title = body.get("title")
    conversation_id = await create_conversation(title)
    return {"id": str(conversation_id), "title": title}


@app.get("/api/conversations/{conversation_id}", response_model=ConversationDetail, tags=["Conversations"])
async def api_get_conversation(conversation_id: str):
    """
    Retorna dados de uma conversa específica.

    - **conversation_id**: ID da conversa a ser recuperada
    """
    conversation = await get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    return conversation


@app.get("/api/conversations/{conversation_id}/messages", response_model=List[MessageResponse], tags=["Conversations"])
async def api_get_conversation_messages(conversation_id: str):
    """
    Retorna todas as mensagens de uma conversa.

    Retorna todas as mensagens (queries e respostas) de uma conversa específica, ordenadas por tempo.

    - **conversation_id**: ID da conversa
    """
    # Verifica se conversa existe
    conversation = await get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    
    messages = await get_conversation_messages(conversation_id)
    return messages


@app.patch("/api/conversations/{conversation_id}", tags=["Conversations"])
async def api_update_conversation(conversation_id: str, request: Request):
    """
    Atualiza dados de uma conversa (título).

    - **conversation_id**: ID da conversa a ser atualizada
    """
    body = await request.json()
    title = body.get("title")
    if title:
        await update_conversation_title(conversation_id, title)
    return {"ok": True}


# ---------------------------------------------------------------------------
# API — configurações
# ---------------------------------------------------------------------------

@app.get("/api/settings", response_model=SettingsResponse, tags=["Settings"])
async def api_get_settings():
    """
    Retorna todas as configurações do sistema.
    """
    return await get_all_settings()


@app.post("/api/settings", tags=["Settings"])
async def api_update_settings(request: Request):
    """
    Atualiza configurações do sistema.

    Aceita um objeto JSON com as chaves a serem atualizadas.
    """
    body = await request.json()
    for key, value in body.items():
        await update_setting(key, str(value))
    return {"ok": True}


# ---------------------------------------------------------------------------
# API — estatísticas
# ---------------------------------------------------------------------------

@app.get("/api/stats", response_model=StatsResponse, tags=["Stats"])
async def api_stats():
    """
    Retorna estatísticas do sistema.

    Retorna total de queries, tokens consumidos e uso da API Groq (se configurado).
    """
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

@app.post("/chat/stream", tags=["Chat"])
async def chat_stream(request: Request):
    """
    Endpoint de chat streaming com Server-Sent Events (SSE).

    Recebe uma pergunta e retorna resposta em streaming.
    Mantém contexto de conversação se conversation_id for fornecido.

    - **question**: Pergunta a ser feita (obrigatório)
    - **conversation_id**: ID da conversa (opcional, cria nova se não fornecido)
    """
    body = await request.json()
    try:
        payload = ChatRequest(**body)
    except Exception:
        return JSONResponse(status_code=422, content={"error": "ValidationError", "message": "Campo 'question' é obrigatório e não pode estar vazio"})

    question = payload.question.strip()
    conversation_id = payload.conversation_id

    if not question:
        return JSONResponse(status_code=422, content={"error": "ValidationError", "message": "question não pode estar vazia"})

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

            # Salva query com conversation_id (cria nova conversa se não fornecido)
            query_id, conv_id = await save_query(
                question=question,
                answer=full_answer,
                sources=sources,
                elapsed_ms=elapsed_ms,
                llm_provider=provider,
                llm_model=model,
                tokens_total=tokens_total,
                conversation_id=conversation_id,
            )

            log.info(
                "Chat respondido",
                extra={
                    "query_id": str(query_id),
                    "conversation_id": str(conv_id),
                    "duration_ms": elapsed_ms,
                },
            )
            yield f"data: {json.dumps({'type': 'done', 'elapsed_ms': elapsed_ms, 'query_id': str(query_id), 'conversation_id': str(conv_id)})}\n\n"

        except Exception as exc:
            log.exception("Erro no chat streaming: %s", str(exc))
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

@app.get("/api/files", tags=["Documents"])
async def api_files():
    """
    Retorna lista de arquivos indexados.
    """
    loop = asyncio.get_event_loop()
    files = await loop.run_in_executor(None, indexer.get_files)
    return files


@app.post("/api/files/upload", tags=["Documents"])
async def api_upload(files: list[UploadFile] = File(...)):
    """
    Faz upload de arquivos para indexação.

    Aceita arquivos PDF, MD e TXT.
    """
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


@app.post("/api/files/{filename}/toggle")
async def api_toggle_file(filename: str):
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, indexer.toggle_file, filename)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")


@app.delete("/api/files/{filename}")
async def api_delete_file(filename: str):
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, indexer.delete_file, filename)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")


@app.post("/api/index", tags=["Documents"])
async def api_index():
    """
    Inicia indexação de documentos.

    Inicia processo de indexação dos arquivos no diretório data/raw.
    """
    started = await indexer.start_indexing()
    if not started:
        return {"ok": False, "message": "Indexação já em andamento"}
    return {"ok": True, "message": "Indexação iniciada"}


@app.get("/api/index/status", tags=["Documents"])
async def api_index_status():
    """
    Retorna status atual da indexação.
    """
    return indexer.get_state()


# ---------------------------------------------------------------------------
# API — Folders (pastas de documentos)
# ---------------------------------------------------------------------------

@app.get("/api/folders", response_model=List[FolderResponse], tags=["Folders"])
async def api_get_folders():
    """
    Retorna lista de pastas ordenadas por atualização mais recente.
    """
    folders = await get_folders(limit=100)
    return folders


@app.post("/api/folders", response_model=FolderResponse, tags=["Folders"])
async def api_create_folder(request: Request):
    """
    Cria uma nova pasta.

    - **name**: Nome da pasta
    - **path**: Caminho do filesystem
    - **auto_index**: Habilitar indexação automática (opcional)
    """
    body = await request.json()
    try:
        payload = FolderCreate(**body)
    except Exception:
        return JSONResponse(status_code=422, content={"error": "ValidationError", "message": "Dados inválidos"})

    folder_id = await create_folder(
        name=payload.name,
        path=payload.path,
        auto_index=payload.auto_index
    )
    folder = await get_folder(str(folder_id))
    return folder


@app.get("/api/folders/{folder_id}", response_model=FolderResponse, tags=["Folders"])
async def api_get_folder(folder_id: str):
    """
    Retorna dados de uma pasta específica.

    - **folder_id**: ID da pasta
    """
    folder = await get_folder(folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Pasta não encontrada")
    return folder


@app.patch("/api/folders/{folder_id}", tags=["Folders"])
async def api_update_folder(folder_id: str, request: Request):
    """
    Atualiza dados de uma pasta (nome ou auto_index).

    - **folder_id**: ID da pasta
    """
    body = await request.json()
    try:
        payload = FolderUpdate(**body)
    except Exception:
        return JSONResponse(status_code=422, content={"error": "ValidationError", "message": "Dados inválidos"})

    updated = await update_folder(
        folder_id=folder_id,
        name=payload.name,
        auto_index=payload.auto_index
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Pasta não encontrada")
    return {"ok": True}


@app.delete("/api/folders/{folder_id}", tags=["Folders"])
async def api_delete_folder(folder_id: str):
    """
    Deleta uma pasta (cascade deleta documentos).

    - **folder_id**: ID da pasta
    """
    deleted = await delete_folder(folder_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Pasta não encontrada")
    return {"ok": True}


@app.get("/api/folders/{folder_id}/documents", response_model=List[DocumentResponse], tags=["Folders"])
async def api_get_folder_documents(folder_id: str):
    """
    Retorna todos os documentos de uma pasta.

    - **folder_id**: ID da pasta
    """
    folder = await get_folder(folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Pasta não encontrada")

    documents = await get_documents(folder_id=folder_id, limit=1000)
    return documents


@app.post("/api/folders/upload", response_model=FolderUploadResponse, tags=["Folders"])
async def api_upload_folder(files: list[UploadFile] = File(...), folder_name: str = None, auto_index: bool = False):
    """
    Faz upload de múltiplos arquivos e cria uma pasta para organizá-los.

    - **files**: Lista de arquivos para upload
    - **folder_name**: Nome da pasta (opcional, usa timestamp se não fornecido)
    - **auto_index**: Habilitar indexação automática (opcional)
    """
    MAX_FOLDER_SIZE = int(os.getenv("MAX_FOLDER_SIZE_MB", "100")) * 1024 * 1024  # 100MB padrão

    DATA_RAW.mkdir(parents=True, exist_ok=True)

    # Determinar nome da pasta
    if not folder_name:
        folder_name = f"upload_{int(time.time())}"

    # Criar caminho da pasta
    folder_path = DATA_RAW / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)

    # Validar tamanho total
    total_size = 0
    valid_files = []

    for upload in files:
        suffix = Path(upload.filename).suffix.lower()
        if suffix not in {".pdf", ".md", ".txt"}:
            continue

        content = await upload.read()
        file_size = len(content)
        total_size += file_size

        if total_size > MAX_FOLDER_SIZE:
            return JSONResponse(
                status_code=413,
                content={"error": "PayloadTooLarge", "message": f"Tamanho total excede limite de {MAX_FOLDER_SIZE // (1024*1024)}MB"}
            )

        valid_files.append((upload.filename, content))

    if not valid_files:
        return JSONResponse(status_code=400, content={"error": "BadRequest", "message": "Nenhum arquivo válido fornecido"})

    # Criar pasta no banco
    folder_id = await create_folder(
        name=folder_name,
        path=str(folder_path),
        auto_index=auto_index
    )

    # Salvar arquivos e criar registros
    saved_files = []
    for filename, content in valid_files:
        dest = folder_path / filename
        dest.write_bytes(content)

        # Criar registro de documento
        await create_document(
            folder_id=str(folder_id),
            name=filename,
            path=str(dest),
            size_bytes=len(content),
            mtime=dest.stat().st_mtime
        )

        saved_files.append(filename)

    return {
        "folder_id": str(folder_id),
        "folder_name": folder_name,
        "files_uploaded": len(saved_files),
        "total_size_bytes": total_size,
        "files": saved_files
    }


@app.post("/api/folders/{folder_id}/index", tags=["Folders"])
async def api_index_folder(folder_id: str):
    """
    Inicia indexação de documentos de uma pasta específica.

    - **folder_id**: ID da pasta
    """
    folder = await get_folder(folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Pasta não encontrada")

    started = await indexer.start_indexing()
    if not started:
        return {"ok": False, "message": "Indexação já em andamento"}
    return {"ok": True, "message": f"Indexação iniciada para pasta {folder['name']}"}


@app.post("/api/folders/scanner/start", tags=["Folders"])
async def api_start_scanner():
    """
    Inicia o scanner de pastas para indexação automática.
    """
    started = await folder_scanner.start_folder_scanner()
    if not started:
        return {"ok": False, "message": "Scanner já está rodando"}
    return {"ok": True, "message": "Scanner iniciado"}


@app.post("/api/folders/scanner/stop", tags=["Folders"])
async def api_stop_scanner():
    """
    Para o scanner de pastas.
    """
    await folder_scanner.stop_folder_scanner()
    return {"ok": True, "message": "Scanner parado"}


@app.get("/api/folders/scanner/status", tags=["Folders"])
async def api_scanner_status():
    """
    Retorna status do scanner de pastas.
    """
    return {"running": folder_scanner.is_scanner_running()}


# ---------------------------------------------------------------------------
# Health Check / Readiness / Liveness
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check completo do sistema.

    Verifica saúde dos serviços dependentes (PostgreSQL, Qdrant, Ollama).
    """
    services = {}

    # Check PostgreSQL
    try:
        pool = await get_pool()
        await pool.fetchval("SELECT 1")
        services["postgres"] = "healthy"
    except Exception:
        services["postgres"] = "unhealthy"

    # Check Qdrant
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get("http://qdrant:6333/health")
            services["qdrant"] = "healthy" if resp.status_code == 200 else "unhealthy"
    except Exception:
        services["qdrant"] = "unhealthy"

    # Check Ollama
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get("http://host.docker.internal:11434/api/tags")
            services["ollama"] = "healthy" if resp.status_code == 200 else "unhealthy"
    except Exception:
        services["ollama"] = "unhealthy"

    overall_status = "healthy" if all(s == "healthy" for s in services.values()) else "degraded"
    status_code = 200 if overall_status == "healthy" else 207

    return JSONResponse(
        status_code=status_code,
        content={
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "services": services,
        },
    )


# --- Authentication Endpoints ---

@app.post("/api/auth/register", tags=["Auth"])
async def register(user_data: UserCreate):
    """
    Registra um novo usuário.

    Cria uma conta de usuário com username e email únicos.
    """
    # Check if username already exists
    existing_user = await get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Nome de usuário já existe")
    
    # Check if email already exists
    existing_email = await get_user_by_email(user_data.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Hash password
    password_hash = auth.get_password_hash(user_data.password)
    
    # Create user
    user_id = await create_user(
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash,
        full_name=user_data.full_name,
        is_admin=False
    )
    
    # Get created user
    user = await get_user_by_id(str(user_id))
    return user


@app.post("/api/auth/login", tags=["Auth"])
async def login(login_data: UserLogin):
    """
    Faz login de usuário e retorna token JWT.

    Aceita username ou email no campo username.
    """
    # Try to find user by username or email
    user = await get_user_by_username(login_data.username)
    if not user:
        user = await get_user_by_email(login_data.username)
    
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    # Check if user is active
    if not user.get("is_active"):
        raise HTTPException(status_code=403, detail="Conta desativada")
    
    # Verify password
    if not auth.verify_password(login_data.password, user.get("password_hash")):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    
    # Update last login
    await update_user_last_login(user["id"])
    
    # Create access token
    access_token = auth.create_access_token(
        data={"sub": user["username"], "user_id": user["id"]}
    )
    
    # Remove password_hash from response
    user.pop("password_hash", None)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(**user)
    )


@app.get("/api/auth/me", tags=["Auth"])
async def get_current_user_info(request: Request):
    """
    Retorna informações do usuário autenticado.

    Requer header Authorization: Bearer <token>
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token não fornecido")
    
    token = auth_header.split(" ")[1]
    payload = auth.decode_access_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    
    username = payload.get("sub")
    user = await get_user_by_username(username)
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Remove password_hash from response
    user.pop("password_hash", None)
    
    return UserResponse(**user)


# --- User Management Endpoints ---

@app.get("/api/users", tags=["Users"])
async def get_users(skip: int = 0, limit: int = 100):
    """
    Lista todos os usuários.

    Retorna lista de usuários sem senhas.
    """
    users = await list_users(skip=skip, limit=limit)
    return users


@app.get("/api/users/{user_id}", tags=["Users"])
async def get_user(user_id: str):
    """
    Retorna um usuário específico pelo ID.

    Retorna dados do usuário sem senha.
    """
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user


@app.put("/api/users/{user_id}", tags=["Users"])
async def update_user_endpoint(user_id: str, user_data: UserUpdate):
    """
    Atualiza dados de um usuário.

    Permite atualizar email, nome, senha, status e admin.
    """
    # Build password hash if provided
    password_hash = None
    if user_data.password:
        password_hash = auth.get_password_hash(user_data.password)
    
    # Update user
    success = await update_user(
        user_id=user_id,
        email=user_data.email,
        full_name=user_data.full_name,
        password_hash=password_hash,
        is_active=user_data.is_active,
        is_admin=user_data.is_admin
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Usuário não encontrado ou nenhum dado para atualizar")
    
    # Return updated user
    user = await get_user_by_id(user_id)
    return user


@app.get("/readiness", tags=["Health"])
async def readiness():
    """
    Readiness probe — indica se o serviço está pronto para receber tráfego.

    Usado pelo orquestrador (Docker / Kubernetes) para aguardar dependências.
    """
    try:
        pool = await get_pool()
        await pool.fetchval("SELECT 1")
        return {"status": "ready"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Banco não disponível: {exc}")


@app.get("/liveness", tags=["Health"])
async def liveness():
    """
    Liveness probe — indica se o processo está vivo.

    Retorna sempre 200 enquanto o processo estiver rodando.
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
