"""
Logging estruturado em JSON para produção.
Cada log é emitido como uma linha JSON para facilitar ingestão por Loki/ELK.
"""
import json
import logging
import sys
import time
from typing import Any


class JSONFormatter(logging.Formatter):
    """Formata logs como JSON lines."""

    def format(self, record: logging.LogRecord) -> str:
        log: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            log["exc"] = self.formatException(record.exc_info)
        # campos extras adicionados via extra={}
        for key in ("request_id", "path", "method", "status_code", "duration_ms",
                     "conversation_id", "query_id", "user_ip"):
            if hasattr(record, key):
                log[key] = getattr(record, key)
        return json.dumps(log, ensure_ascii=False)


def get_logger(name: str = "rag") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


# Logger raiz do aplicativo
log = get_logger("rag.api")
