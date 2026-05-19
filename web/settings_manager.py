import time
from db import get_pool

_cache: dict = {}
_cache_ts: float = 0.0
_CACHE_TTL = 30  # segundos


async def get_all_settings() -> dict:
    global _cache, _cache_ts
    if time.time() - _cache_ts < _CACHE_TTL and _cache:
        return _cache
    pool = await get_pool()
    rows = await pool.fetch("SELECT key, value FROM settings")
    _cache = {r["key"]: r["value"] for r in rows}
    _cache_ts = time.time()
    return _cache


async def update_setting(key: str, value: str) -> None:
    global _cache_ts
    pool = await get_pool()
    await pool.execute(
        """INSERT INTO settings (key, value, updated_at)
           VALUES ($1, $2, NOW())
           ON CONFLICT (key) DO UPDATE
             SET value = EXCLUDED.value, updated_at = NOW()""",
        key,
        value,
    )
    _cache_ts = 0.0  # invalida cache
