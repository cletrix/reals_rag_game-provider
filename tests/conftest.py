import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from web.main import app


@pytest.fixture
def client():
    """Fixture para cliente de teste FastAPI."""
    return TestClient(app)


@pytest.fixture
def mock_db_pool():
    """Mock do pool de conexões do banco de dados."""
    with patch('web.db.get_pool') as mock:
        pool = AsyncMock()
        mock.return_value = pool
        yield pool


@pytest.fixture
def mock_settings():
    """Mock das configurações."""
    with patch('web.settings_manager.get_all_settings') as mock:
        mock.return_value = {
            'llm_provider': 'groq',
            'groq_model': 'llama-3.3-70b-versatile',
            'ollama_model': 'qwen2.5:7b',
            'similarity_top_k': 4
        }
        yield mock


@pytest.fixture
def sample_conversation():
    """Dados de exemplo para conversa."""
    return {
        'id': '550e8400-e29b-41d4-a716-446655440000',
        'title': 'Test Conversation',
        'message_count': 2,
        'created_at': '2026-05-25T18:00:00',
        'updated_at': '2026-05-25T18:05:00'
    }


@pytest.fixture
def sample_folder():
    """Dados de exemplo para pasta."""
    return {
        'id': '550e8400-e29b-41d4-a716-446655440001',
        'name': 'test_folder',
        'path': '/app/data/raw/test_folder',
        'size_bytes': 1024,
        'file_count': 1,
        'indexed_at': None,
        'auto_index': False,
        'created_at': '2026-05-25T18:00:00',
        'updated_at': '2026-05-25T18:00:00'
    }


@pytest.fixture
def sample_document():
    """Dados de exemplo para documento."""
    return {
        'id': '550e8400-e29b-41d4-a716-446655440002',
        'folder_id': '550e8400-e29b-41d4-a716-446655440001',
        'name': 'test.txt',
        'path': '/app/data/raw/test_folder/test.txt',
        'size_bytes': 1024,
        'indexed': False,
        'indexed_at': None,
        'mtime': 1716244800.0,
        'created_at': '2026-05-25T18:00:00',
        'updated_at': '2026-05-25T18:00:00'
    }
