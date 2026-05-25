import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from uuid import UUID
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'web'))

import db


@pytest.mark.asyncio
async def test_get_pool():
    """Testa obtenção do pool de conexões."""
    with pytest.MonkeyPatch().context() as m:
        m.setenv("DATABASE_URL", "postgresql://test:test@localhost/test")
        pool = await db.get_pool()
        assert pool is not None


@pytest.mark.asyncio
async def test_create_folder(mock_db_pool):
    """Testa criação de pasta no banco."""
    mock_db_pool.fetchrow.return_value = {'id': 'test-id-123'}
    
    folder_id = await db.create_folder(
        name="test_folder",
        path="/app/data/raw/test_folder",
        auto_index=False
    )
    assert folder_id == 'test-id-123'
    mock_db_pool.fetchrow.assert_called_once()


@pytest.mark.asyncio
async def test_get_folders(mock_db_pool):
    """Testa listagem de pastas."""
    mock_db_pool.fetch.return_value = [
        {
            'id': 'id-1',
            'name': 'folder1',
            'path': '/app/data/raw/folder1',
            'size_bytes': 1024,
            'file_count': 1,
            'indexed_at': None,
            'auto_index': False,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
    ]
    
    folders = await db.get_folders(limit=10)
    assert len(folders) == 1
    assert folders[0]['name'] == 'folder1'


@pytest.mark.asyncio
async def test_get_folder(mock_db_pool):
    """Testa busca de pasta específica."""
    mock_db_pool.fetchrow.return_value = {
        'id': 'id-1',
        'name': 'folder1',
        'path': '/app/data/raw/folder1',
        'size_bytes': 1024,
        'file_count': 1,
        'indexed_at': None,
        'auto_index': False,
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    folder = await db.get_folder('id-1')
    assert folder is not None
    assert folder['name'] == 'folder1'


@pytest.mark.asyncio
async def test_update_folder(mock_db_pool):
    """Testa atualização de pasta."""
    mock_db_pool.execute.return_value = "UPDATE 1"
    
    updated = await db.update_folder('id-1', name='new_name', auto_index=True)
    assert updated is True
    mock_db_pool.execute.assert_called_once()


@pytest.mark.asyncio
async def test_delete_folder(mock_db_pool):
    """Testa deleção de pasta."""
    mock_db_pool.execute.return_value = "DELETE 1"
    
    deleted = await db.delete_folder('id-1')
    assert deleted is True
    mock_db_pool.execute.assert_called_once()


@pytest.mark.asyncio
async def test_create_document(mock_db_pool):
    """Testa criação de documento."""
    mock_db_pool.fetchrow.return_value = {'id': 'doc-id-123'}
    
    doc_id = await db.create_document(
        folder_id='folder-id',
        name='test.txt',
        path='/app/data/raw/test.txt',
        size_bytes=1024,
        mtime=1716244800.0
    )
    assert doc_id == 'doc-id-123'
    mock_db_pool.fetchrow.assert_called_once()


@pytest.mark.asyncio
async def test_get_documents(mock_db_pool):
    """Testa listagem de documentos."""
    mock_db_pool.fetch.return_value = [
        {
            'id': 'doc-1',
            'folder_id': 'folder-1',
            'name': 'test.txt',
            'path': '/app/data/raw/test.txt',
            'size_bytes': 1024,
            'indexed': False,
            'indexed_at': None,
            'mtime': datetime.now(),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
    ]
    
    docs = await db.get_documents(folder_id='folder-1', limit=10)
    assert len(docs) == 1
    assert docs[0]['name'] == 'test.txt'


@pytest.mark.asyncio
async def test_get_document(mock_db_pool):
    """Testa busca de documento específico."""
    mock_db_pool.fetchrow.return_value = {
        'id': 'doc-1',
        'folder_id': 'folder-1',
        'name': 'test.txt',
        'path': '/app/data/raw/test.txt',
        'size_bytes': 1024,
        'indexed': False,
        'indexed_at': None,
        'mtime': datetime.now(),
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    doc = await db.get_document('doc-1')
    assert doc is not None
    assert doc['name'] == 'test.txt'


@pytest.mark.asyncio
async def test_update_document_indexed(mock_db_pool):
    """Testa atualização de status de indexação."""
    mock_db_pool.execute.return_value = "UPDATE 1"
    
    updated = await db.update_document_indexed('doc-1', indexed=True)
    assert updated is True
    mock_db_pool.execute.assert_called_once()


@pytest.mark.asyncio
async def test_delete_document(mock_db_pool):
    """Testa deleção de documento."""
    mock_db_pool.execute.return_value = "DELETE 1"
    
    deleted = await db.delete_document('doc-1')
    assert deleted is True
    mock_db_pool.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_auto_index_folders(mock_db_pool):
    """Testa busca de pastas com auto_index."""
    mock_db_pool.fetch.return_value = [
        {
            'id': 'id-1',
            'name': 'auto_folder',
            'path': '/app/data/raw/auto_folder',
            'size_bytes': 1024,
            'file_count': 1,
            'indexed_at': None,
            'auto_index': True,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
    ]
    
    folders = await db.get_auto_index_folders()
    assert len(folders) == 1
    assert folders[0]['auto_index'] is True


@pytest.mark.asyncio
async def test_create_conversation(mock_db_pool):
    """Testa criação de conversa."""
    mock_db_pool.fetchrow.return_value = {'id': 'conv-id-123'}
    
    conv_id = await db.create_conversation(title="Test Conversation")
    assert conv_id == 'conv-id-123'
    mock_db_pool.fetchrow.assert_called_once()


@pytest.mark.asyncio
async def test_get_conversations(mock_db_pool):
    """Testa listagem de conversas."""
    mock_db_pool.fetch.return_value = [
        {
            'id': 'conv-1',
            'title': 'Conversation 1',
            'message_count': 2,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
    ]
    
    convs = await db.get_conversations(limit=10)
    assert len(convs) == 1
    assert convs[0]['title'] == 'Conversation 1'


@pytest.mark.asyncio
async def test_save_query(mock_db_pool):
    """Testa salvamento de query."""
    mock_db_pool.fetchrow.return_value = {'id': 'query-id-123'}
    
    query_id = await db.save_query(
        conversation_id='conv-1',
        question='Test question',
        answer='Test answer',
        sources=[],
        elapsed_ms=1000,
        llm_model='llama-3.3-70b-versatile',
        tokens_total=100
    )
    assert query_id == 'query-id-123'
    mock_db_pool.fetchrow.assert_called_once()
