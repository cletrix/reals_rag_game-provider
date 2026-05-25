"""
Scanner de pastas para indexação automática.

Verifica periodicamente pastas com auto_index habilitado e indexa novos arquivos.
"""
import asyncio
import os
import time
from pathlib import Path
from typing import Optional

import indexer
from db import (
    get_auto_index_folders,
    get_folder_by_path,
    get_document_by_path,
    create_document,
    update_document_indexed,
    update_folder,
)
from logger import log

DATA_DIR = Path("/app/data/raw")
SCAN_INTERVAL = int(os.getenv("FOLDER_SCAN_INTERVAL_SECONDS", "300"))  # 5 minutos padrão

_scanner_running = False
_scanner_task: Optional[asyncio.Task] = None


async def start_folder_scanner():
    """Inicia o scanner de pastas em background."""
    global _scanner_running, _scanner_task

    if _scanner_running:
        log.warning("Folder scanner já está rodando")
        return False

    _scanner_running = True
    _scanner_task = asyncio.create_task(_scan_loop())
    log.info("Folder scanner iniciado")
    return True


async def stop_folder_scanner():
    """Para o scanner de pastas."""
    global _scanner_running, _scanner_task

    _scanner_running = False
    if _scanner_task:
        _scanner_task.cancel()
        try:
            await _scanner_task
        except asyncio.CancelledError:
            pass
    log.info("Folder scanner parado")


async def _scan_loop():
    """Loop principal do scanner."""
    while _scanner_running:
        try:
            await _scan_folders()
        except Exception as exc:
            log.exception("Erro no scan de pastas: %s", str(exc))

        # Aguarda próximo scan
        for _ in range(SCAN_INTERVAL):
            if not _scanner_running:
                break
            await asyncio.sleep(1)


async def _scan_folders():
    """Varre pastas com auto_index habilitado."""
    folders = await get_auto_index_folders()

    if not folders:
        return

    log.info("Scanning %d pasta(s) com auto_index", len(folders))

    for folder in folders:
        try:
            await _scan_single_folder(folder)
        except Exception as exc:
            log.exception("Erro ao scan pasta %s: %s", folder["path"], str(exc))


async def _scan_single_folder(folder: dict):
    """Scana uma pasta específica por novos arquivos."""
    folder_path = Path(folder["path"])

    if not folder_path.exists() or not folder_path.is_dir():
        log.warning("Pasta não existe: %s", folder["path"])
        return

    # Buscar arquivos válidos
    valid_extensions = {".pdf", ".md", ".txt"}
    new_files = []

    for f in folder_path.rglob("*"):
        if f.suffix.lower() in valid_extensions and f.is_file():
            # Verificar se já está no banco
            doc = await get_document_by_path(str(f))

            if not doc:
                # Arquivo novo
                new_files.append(f)
            elif doc["mtime"] != f.stat().st_mtime:
                # Arquivo modificado - marcar para reindexação
                await update_document_indexed(doc["id"], indexed=False)
                new_files.append(f)

    if not new_files:
        return

    log.info("Encontrados %d arquivo(s) novo(s)/modificado(s) em %s", len(new_files), folder["name"])

    # Criar registros para arquivos novos
    for f in new_files:
        try:
            await create_document(
                folder_id=folder["id"],
                name=f.name,
                path=str(f),
                size_bytes=f.stat().st_size,
                mtime=f.stat().st_mtime,
            )
            log.info("Documento registrado: %s", f.name)
        except Exception as exc:
            log.exception("Erro ao registrar documento %s: %s", f.name, str(exc))

    # Atualizar timestamp da pasta
    await update_folder(folder["id"], auto_index=True)

    # Iniciar indexação se houver arquivos novos
    if new_files:
        log.info("Iniciando indexação para pasta %s", folder["name"])
        await indexer.start_indexing()


def is_scanner_running() -> bool:
    """Retorna se o scanner está rodando."""
    return _scanner_running
