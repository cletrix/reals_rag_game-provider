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


async def save_query(
    *,
    question: str,
    answer: str,
    sources: list,
    elapsed_ms: int,
    llm_provider: str,
    llm_model: str | None,
    tokens_total: int | None,
) -> UUID:
    pool = await get_pool()
    row = await pool.fetchrow(
        """INSERT INTO queries
             (question, answer, sources, elapsed_ms, llm_provider, llm_model, tokens_total)
           VALUES ($1, $2, $3, $4, $5, $6, $7)
           RETURNING id""",
        question,
        answer,
        json.dumps(sources),
        elapsed_ms,
        llm_provider,
        llm_model,
        tokens_total,
    )
    return row["id"]


async def get_history(limit: int = 50) -> list[dict]:
    pool = await get_pool()
    rows = await pool.fetch(
        """SELECT id, question, LEFT(answer, 120) AS answer_preview,
                  elapsed_ms, llm_provider, llm_model, created_at
           FROM queries
           ORDER BY created_at DESC
           LIMIT $1""",
        limit,
    )
    return [dict(r) for r in rows]


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
