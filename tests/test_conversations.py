import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient


def test_get_conversations(client, mock_db_pool, sample_conversation):
    """Testa listagem de conversas."""
    mock_db_pool.fetch.return_value = [sample_conversation]
    
    response = client.get("/api/conversations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_conversation(client, mock_db_pool, sample_conversation):
    """Testa busca de conversa específica."""
    mock_db_pool.fetchrow.return_value = sample_conversation
    
    response = client.get(f"/api/conversations/{sample_conversation['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == sample_conversation['id']


def test_create_conversation(client, mock_db_pool):
    """Testa criação de nova conversa."""
    mock_db_pool.fetchrow.return_value = {'id': 'new-id-123'}
    
    response = client.post("/api/conversations", json={"title": "Nova Conversa"})
    assert response.status_code == 200
    data = response.json()
    assert 'id' in data


def test_update_conversation(client, mock_db_pool, sample_conversation):
    """Testa atualização de título de conversa."""
    mock_db_pool.execute.return_value = "UPDATE 1"
    
    response = client.patch(
        f"/api/conversations/{sample_conversation['id']}",
        json={"title": "Título Atualizado"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data['ok'] is True


def test_delete_conversation(client, mock_db_pool, sample_conversation):
    """Testa deleção de conversa."""
    mock_db_pool.execute.return_value = "DELETE 1"
    
    response = client.delete(f"/api/conversations/{sample_conversation['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data['ok'] is True


def test_get_conversation_messages(client, mock_db_pool, sample_conversation):
    """Testa busca de mensagens de uma conversa."""
    mock_db_pool.fetch.return_value = [
        {
            'id': 'msg-1',
            'conversation_id': sample_conversation['id'],
            'role': 'user',
            'content': 'Pergunta teste',
            'created_at': '2026-05-25T18:00:00'
        }
    ]
    
    response = client.get(f"/api/conversations/{sample_conversation['id']}/messages")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
