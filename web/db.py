import os
import json
import asyncpg
from uuid import UUID

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=os.getenv("DATABASE_URL"),
            min_size=2,
            max_size=10,
        )
    return _pool


async def create_conversation(title: str | None = None) -> UUID:
    """Cria uma nova conversa e retorna o ID."""
    pool = await get_pool()
    row = await pool.fetchrow(
        """INSERT INTO conversations (title)
           VALUES ($1)
           RETURNING id""",
        title,
    )
    return row["id"]


async def get_conversation(conversation_id: str) -> dict | None:
    """Retorna dados de uma conversa específica."""
    pool = await get_pool()
    row = await pool.fetchrow(
        """SELECT id, title, created_at, updated_at
           FROM conversations
           WHERE id = $1::uuid""",
        conversation_id,
    )
    if not row:
        return None
    result = dict(row)
    if hasattr(result.get("created_at"), "isoformat"):
        result["created_at"] = result["created_at"].isoformat()
    if hasattr(result.get("updated_at"), "isoformat"):
        result["updated_at"] = result["updated_at"].isoformat()
    return result


async def get_conversations(limit: int = 50) -> list[dict]:
    """Retorna lista de conversas com contagem de mensagens e preview."""
    pool = await get_pool()
    rows = await pool.fetch(
        """SELECT 
               c.id,
               c.title,
               c.created_at,
               c.updated_at,
               COUNT(q.id) as message_count,
               (SELECT question FROM queries 
                WHERE conversation_id = c.id 
                ORDER BY created_at DESC LIMIT 1) as preview
           FROM conversations c
           LEFT JOIN queries q ON c.id = q.conversation_id
           GROUP BY c.id, c.title, c.created_at, c.updated_at
           ORDER BY c.updated_at DESC
           LIMIT $1""",
        limit,
    )
    result = []
    for r in rows:
        item = dict(r)
        if hasattr(item.get("created_at"), "isoformat"):
            item["created_at"] = item["created_at"].isoformat()
        if hasattr(item.get("updated_at"), "isoformat"):
            item["updated_at"] = item["updated_at"].isoformat()
        if item.get("id"):
            item["id"] = str(item["id"])
        result.append(item)
    return result


async def get_conversation_messages(conversation_id: str) -> list[dict]:
    """Retorna todas as mensagens de uma conversa, ordenadas por tempo."""
    pool = await get_pool()
    rows = await pool.fetch(
        """SELECT id, question, answer, sources, elapsed_ms, 
                  llm_provider, llm_model, tokens_total, created_at
           FROM queries
           WHERE conversation_id = $1::uuid
           ORDER BY created_at ASC""",
        conversation_id,
    )
    result = []
    for r in rows:
        item = dict(r)
        if isinstance(item.get("sources"), str):
            item["sources"] = json.loads(item["sources"])
        if hasattr(item.get("created_at"), "isoformat"):
            item["created_at"] = item["created_at"].isoformat()
        if item.get("id"):
            item["id"] = str(item["id"])
        result.append(item)
    return result


async def update_conversation_timestamp(conversation_id: str) -> None:
    """Atualiza o timestamp de atualização da conversa."""
    pool = await get_pool()
    await pool.execute(
        """UPDATE conversations 
           SET updated_at = NOW() 
           WHERE id = $1::uuid""",
        conversation_id,
    )


async def update_conversation_title(conversation_id: str, title: str) -> None:
    """Atualiza o título da conversa."""
    pool = await get_pool()
    await pool.execute(
        """UPDATE conversations 
           SET title = $2, updated_at = NOW() 
           WHERE id = $1::uuid""",
        conversation_id,
        title,
    )


async def save_query(
    *,
    question: str,
    answer: str,
    sources: list,
    elapsed_ms: int,
    llm_provider: str,
    llm_model: str | None,
    tokens_total: int | None,
    conversation_id: str | None = None,
) -> tuple[UUID, UUID | None]:
    """
    Salva uma query. Se conversation_id não fornecido, cria nova conversa.
    Retorna (query_id, conversation_id).
    """
    pool = await get_pool()
    
    # Se não tem conversation_id, criar nova conversa com título da pergunta
    if conversation_id is None:
        title = question[:50] + "..." if len(question) > 50 else question
        conv_row = await pool.fetchrow(
            """INSERT INTO conversations (title)
               VALUES ($1)
               RETURNING id""",
            title,
        )
        conversation_id = str(conv_row["id"])
    else:
        # Atualizar timestamp da conversa existente
        await update_conversation_timestamp(conversation_id)
    
    row = await pool.fetchrow(
        """INSERT INTO queries
             (conversation_id, question, answer, sources, elapsed_ms, llm_provider, llm_model, tokens_total)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
           RETURNING id""",
        conversation_id,
        question,
        answer,
        json.dumps(sources),
        elapsed_ms,
        llm_provider,
        llm_model,
        tokens_total,
    )
    return row["id"], UUID(conversation_id)


async def get_history(limit: int = 50) -> list[dict]:
    """Mantido para compatibilidade - retorna queries individuais."""
    pool = await get_pool()
    rows = await pool.fetch(
        """SELECT id, question, LEFT(answer, 120) AS answer_preview,
                  elapsed_ms, llm_provider, llm_model, created_at, conversation_id
           FROM queries
           ORDER BY created_at DESC
           LIMIT $1""",
        limit,
    )
    result = []
    for r in rows:
        item = dict(r)
        if hasattr(item.get("created_at"), "isoformat"):
            item["created_at"] = item["created_at"].isoformat()
        if item.get("id"):
            item["id"] = str(item["id"])
        if item.get("conversation_id"):
            item["conversation_id"] = str(item["conversation_id"])
        result.append(item)
    return result


async def get_query_by_id(query_id: str) -> dict | None:
    pool = await get_pool()
    row = await pool.fetchrow(
        "SELECT * FROM queries WHERE id = $1::uuid", query_id
    )
    if not row:
        return None
    result = dict(row)
    if isinstance(result.get("sources"), str):
        result["sources"] = json.loads(result["sources"])
    return result


async def get_stats() -> dict:
    pool = await get_pool()
    row = await pool.fetchrow(
        """SELECT COUNT(*) AS total_queries,
                  COALESCE(SUM(tokens_total), 0) AS total_tokens
           FROM queries"""
    )
    return dict(row)


# ---------------------------------------------------------------------------
# Folders CRUD
# ---------------------------------------------------------------------------

async def create_folder(name: str, path: str, auto_index: bool = False) -> UUID:
    """Cria uma nova pasta e retorna o ID."""
    pool = await get_pool()
    row = await pool.fetchrow(
        """INSERT INTO folders (name, path, auto_index)
           VALUES ($1, $2, $3)
           RETURNING id""",
        name,
        path,
        auto_index,
    )
    return row["id"]


async def get_folders(limit: int = 100) -> list[dict]:
    """Retorna lista de pastas ordenadas por atualização mais recente."""
    pool = await get_pool()
    rows = await pool.fetch(
        """SELECT id, name, path, size_bytes, file_count,
                  indexed_at, auto_index, created_at, updated_at
           FROM folders
           ORDER BY updated_at DESC
           LIMIT $1""",
        limit,
    )
    result = []
    for r in rows:
        item = dict(r)
        if hasattr(item.get("created_at"), "isoformat"):
            item["created_at"] = item["created_at"].isoformat()
        if hasattr(item.get("updated_at"), "isoformat"):
            item["updated_at"] = item["updated_at"].isoformat()
        if hasattr(item.get("indexed_at"), "isoformat"):
            item["indexed_at"] = item["indexed_at"].isoformat()
        if item.get("id"):
            item["id"] = str(item["id"])
        result.append(item)
    return result


async def get_folder(folder_id: str) -> dict | None:
    """Retorna dados de uma pasta específica."""
    pool = await get_pool()
    row = await pool.fetchrow(
        """SELECT id, name, path, size_bytes, file_count,
                  indexed_at, auto_index, created_at, updated_at
           FROM folders
           WHERE id = $1::uuid""",
        folder_id,
    )
    if not row:
        return None
    result = dict(row)
    if hasattr(result.get("created_at"), "isoformat"):
        result["created_at"] = result["created_at"].isoformat()
    if hasattr(result.get("updated_at"), "isoformat"):
        result["updated_at"] = result["updated_at"].isoformat()
    if hasattr(result.get("indexed_at"), "isoformat"):
        result["indexed_at"] = result["indexed_at"].isoformat()
    if result.get("id"):
        result["id"] = str(result["id"])
    return result


async def update_folder(folder_id: str, name: str | None = None, auto_index: bool | None = None) -> bool:
    """Atualiza dados de uma pasta."""
    pool = await get_pool()
    updates = []
    params = []
    param_idx = 1

    if name is not None:
        updates.append(f"name = ${param_idx}")
        params.append(name)
        param_idx += 1

    if auto_index is not None:
        updates.append(f"auto_index = ${param_idx}")
        params.append(auto_index)
        param_idx += 1

    if not updates:
        return False

    params.append(folder_id)
    query = f"""UPDATE folders SET {', '.join(updates)}, updated_at = NOW()
                WHERE id = ${param_idx}::uuid"""

    result = await pool.execute(query, *params)
    return result == "UPDATE 1"


async def delete_folder(folder_id: str) -> bool:
    """Deleta uma pasta (cascade deleta documentos)."""
    pool = await get_pool()
    result = await pool.execute(
        "DELETE FROM folders WHERE id = $1::uuid",
        folder_id,
    )
    return result == "DELETE 1"


async def get_folder_by_path(path: str) -> dict | None:
    """Retorna pasta pelo caminho do filesystem."""
    pool = await get_pool()
    row = await pool.fetchrow(
        """SELECT id, name, path, size_bytes, file_count,
                  indexed_at, auto_index, created_at, updated_at
           FROM folders
           WHERE path = $1""",
        path,
    )
    if not row:
        return None
    result = dict(row)
    if hasattr(result.get("created_at"), "isoformat"):
        result["created_at"] = result["created_at"].isoformat()
    if hasattr(result.get("updated_at"), "isoformat"):
        result["updated_at"] = result["updated_at"].isoformat()
    if hasattr(result.get("indexed_at"), "isoformat"):
        result["indexed_at"] = result["indexed_at"].isoformat()
    if result.get("id"):
        result["id"] = str(result["id"])
    return result


# ---------------------------------------------------------------------------
# Documents CRUD
# ---------------------------------------------------------------------------

async def create_document(
    folder_id: str,
    name: str,
    path: str,
    size_bytes: int,
    mtime: float,
) -> UUID:
    """Cria um novo documento e retorna o ID."""
    import datetime
    pool = await get_pool()
    # Converter timestamp float para datetime sem timezone
    mtime_dt = datetime.datetime.fromtimestamp(mtime)
    row = await pool.fetchrow(
        """INSERT INTO documents (folder_id, name, path, size_bytes, mtime)
           VALUES ($1::uuid, $2, $3, $4, $5)
           RETURNING id""",
        folder_id,
        name,
        path,
        size_bytes,
        mtime_dt,
    )
    return row["id"]


async def get_documents(folder_id: str | None = None, limit: int = 100) -> list[dict]:
    """Retorna lista de documentos. Se folder_id fornecido, filtra por pasta."""
    import datetime
    pool = await get_pool()
    if folder_id:
        rows = await pool.fetch(
            """SELECT id, folder_id, name, path, size_bytes,
                      indexed, indexed_at, mtime, created_at, updated_at
               FROM documents
               WHERE folder_id = $1::uuid
               ORDER BY name ASC
               LIMIT $2""",
            folder_id,
            limit,
        )
    else:
        rows = await pool.fetch(
            """SELECT id, folder_id, name, path, size_bytes,
                      indexed, indexed_at, mtime, created_at, updated_at
               FROM documents
               ORDER BY name ASC
               LIMIT $1""",
            limit,
        )
    result = []
    for r in rows:
        item = dict(r)
        if hasattr(item.get("created_at"), "isoformat"):
            item["created_at"] = item["created_at"].isoformat()
        if hasattr(item.get("updated_at"), "isoformat"):
            item["updated_at"] = item["updated_at"].isoformat()
        if hasattr(item.get("indexed_at"), "isoformat"):
            item["indexed_at"] = item["indexed_at"].isoformat()
        # Converter datetime mtime para timestamp float
        if isinstance(item.get("mtime"), datetime.datetime):
            item["mtime"] = item["mtime"].timestamp()
        if item.get("id"):
            item["id"] = str(item["id"])
        if item.get("folder_id"):
            item["folder_id"] = str(item["folder_id"])
        result.append(item)
    return result


async def get_document(document_id: str) -> dict | None:
    """Retorna dados de um documento específico."""
    pool = await get_pool()
    row = await pool.fetchrow(
        """SELECT id, folder_id, name, path, size_bytes,
                  indexed, indexed_at, mtime, created_at, updated_at
           FROM documents
           WHERE id = $1::uuid""",
        document_id,
    )
    if not row:
        return None
    result = dict(row)
    if hasattr(result.get("created_at"), "isoformat"):
        result["created_at"] = result["created_at"].isoformat()
    if hasattr(result.get("updated_at"), "isoformat"):
        result["updated_at"] = result["updated_at"].isoformat()
    if hasattr(result.get("indexed_at"), "isoformat"):
        result["indexed_at"] = result["indexed_at"].isoformat()
    if result.get("id"):
        result["id"] = str(result["id"])
    if result.get("folder_id"):
        result["folder_id"] = str(result["folder_id"])
    return result


async def update_document_indexed(document_id: str, indexed: bool = True) -> bool:
    """Atualiza status de indexação de um documento."""
    pool = await get_pool()
    result = await pool.execute(
        """UPDATE documents
           SET indexed = $1, indexed_at = NOW(), updated_at = NOW()
           WHERE id = $2::uuid""",
        indexed,
        document_id,
    )
    return result == "UPDATE 1"


async def delete_document(document_id: str) -> bool:
    """Deleta um documento."""
    pool = await get_pool()
    result = await pool.execute(
        "DELETE FROM documents WHERE id = $1::uuid",
        document_id,
    )
    return result == "DELETE 1"


async def get_document_by_path(path: str) -> dict | None:
    """Retorna documento pelo caminho do filesystem."""
    pool = await get_pool()
    row = await pool.fetchrow(
        """SELECT id, folder_id, name, path, size_bytes,
                  indexed, indexed_at, mtime, created_at, updated_at
           FROM documents
           WHERE path = $1""",
        path,
    )
    if not row:
        return None
    result = dict(row)
    if hasattr(result.get("created_at"), "isoformat"):
        result["created_at"] = result["created_at"].isoformat()
    if hasattr(result.get("updated_at"), "isoformat"):
        result["updated_at"] = result["updated_at"].isoformat()
    if hasattr(result.get("indexed_at"), "isoformat"):
        result["indexed_at"] = result["indexed_at"].isoformat()
    if result.get("id"):
        result["id"] = str(result["id"])
    if result.get("folder_id"):
        result["folder_id"] = str(result["folder_id"])
    return result


async def get_auto_index_folders() -> list[dict]:
    """Retorna pastas com auto_index habilitado."""
    pool = await get_pool()
    rows = await pool.fetch(
        """SELECT id, name, path, size_bytes, file_count,
                  indexed_at, auto_index, created_at, updated_at
           FROM folders
           WHERE auto_index = TRUE
           ORDER BY updated_at DESC"""
    )
    result = []
    for r in rows:
        item = dict(r)
        if hasattr(item.get("created_at"), "isoformat"):
            item["created_at"] = item["created_at"].isoformat()
        if hasattr(item.get("updated_at"), "isoformat"):
            item["updated_at"] = item["updated_at"].isoformat()
        if hasattr(item.get("indexed_at"), "isoformat"):
            item["indexed_at"] = item["indexed_at"].isoformat()
        if item.get("id"):
            item["id"] = str(item["id"])
        result.append(item)
    return result
