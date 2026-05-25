import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from web import folder_scanner


@pytest.mark.asyncio
async def test_start_folder_scanner():
    """Testa início do scanner de pastas."""
    with patch('web.folder_scanner._scan_loop') as mock_scan:
        mock_scan.return_value = None
        
        started = await folder_scanner.start_folder_scanner()
        assert started is True
        assert folder_scanner.is_scanner_running() is True


@pytest.mark.asyncio
async def test_start_folder_scanner_already_running():
    """Testa início do scanner quando já está rodando."""
    folder_scanner._scanner_running = True
    
    started = await folder_scanner.start_folder_scanner()
    assert started is False
    
    folder_scanner._scanner_running = False


@pytest.mark.asyncio
async def test_stop_folder_scanner():
    """Testa parada do scanner de pastas."""
    folder_scanner._scanner_running = True
    folder_scanner._scanner_task = AsyncMock()
    
    await folder_scanner.stop_folder_scanner()
    assert folder_scanner.is_scanner_running() is False


@pytest.mark.asyncio
async def test_scan_folders(mock_db_pool):
    """Testa varredura de pastas."""
    mock_db_pool.fetch.return_value = [
        {
            'id': 'folder-1',
            'name': 'test_folder',
            'path': '/app/data/raw/test_folder',
            'size_bytes': 1024,
            'file_count': 1,
            'indexed_at': None,
            'auto_index': True,
            'created_at': '2026-05-25T18:00:00',
            'updated_at': '2026-05-25T18:00:00'
        }
    ]
    
    with patch('web.folder_scanner._scan_single_folder') as mock_scan:
        mock_scan.return_value = None
        
        await folder_scanner._scan_folders()
        mock_scan.assert_called_once()


@pytest.mark.asyncio
async def test_scan_single_folder_no_new_files(mock_db_pool):
    """Testa varredura de pasta sem novos arquivos."""
    folder = {
        'id': 'folder-1',
        'name': 'test_folder',
        'path': '/tmp/test_folder',
        'size_bytes': 0,
        'file_count': 0,
        'indexed_at': None,
        'auto_index': True,
        'created_at': '2026-05-25T18:00:00',
        'updated_at': '2026-05-25T18:00:00'
    }
    
    mock_db_pool.fetch.return_value = None  # documento não existe
    
    with patch('pathlib.Path.exists', return_value=True):
        with patch('pathlib.Path.is_dir', return_value=True):
            with patch('pathlib.Path.rglob', return_value=[]):
                await folder_scanner._scan_single_folder(folder)


@pytest.mark.asyncio
async def test_scan_single_folder_with_new_file(mock_db_pool):
    """Testa varredura de pasta com novo arquivo."""
    folder = {
        'id': 'folder-1',
        'name': 'test_folder',
        'path': '/tmp/test_folder',
        'size_bytes': 0,
        'file_count': 0,
        'indexed_at': None,
        'auto_index': True,
        'created_at': '2026-05-25T18:00:00',
        'updated_at': '2026-05-25T18:00:00'
    }
    
    # Mock do arquivo
    mock_file = MagicMock()
    mock_file.suffix = '.txt'
    mock_file.is_file.return_value = True
    mock_file.name = 'test.txt'
    mock_file.stat.return_value.st_mtime = 1716244800.0
    mock_file.stat.return_value.st_size = 1024
    
    mock_db_pool.fetch.return_value = None  # documento não existe
    mock_db_pool.fetchrow.return_value = {'id': 'doc-id-123'}
    mock_db_pool.execute.return_value = "UPDATE 1"
    
    with patch('pathlib.Path.exists', return_value=True):
        with patch('pathlib.Path.is_dir', return_value=True):
            with patch('pathlib.Path.rglob', return_value=[mock_file]):
                with patch('web.folder_scanner.indexer.start_indexing', new_callable=AsyncMock) as mock_index:
                    mock_index.return_value = True
                    
                    await folder_scanner._scan_single_folder(folder)
                    mock_index.assert_called_once()


def test_is_scanner_running():
    """Testa verificação de status do scanner."""
    folder_scanner._scanner_running = True
    assert folder_scanner.is_scanner_running() is True
    
    folder_scanner._scanner_running = False
    assert folder_scanner.is_scanner_running() is False
