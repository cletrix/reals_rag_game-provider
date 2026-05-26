import pytest
from unittest.mock import patch


def test_get_conversations(client, sample_conversation):
    """Testa listagem de conversas."""
    with patch('main.get_conversations', return_value=[sample_conversation]):
        response = client.get("/api/conversations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_conversation(client, sample_conversation):
    """Testa busca de conversa específica."""
    with patch('main.get_conversation', return_value=sample_conversation):
        response = client.get(f"/api/conversations/{sample_conversation['id']}")
    assert response.status_code == 200
    assert response.json()['id'] == sample_conversation['id']


def test_get_conversation_not_found(client):
    """Testa conversa não encontrada."""
    with patch('main.get_conversation', return_value=None):
        response = client.get("/api/conversations/nao-existe")
    assert response.status_code == 404


def test_create_conversation(client):
    """Testa criação de nova conversa."""
    with patch('main.create_conversation', return_value='new-id-123'):
        response = client.post("/api/conversations", json={"title": "Nova Conversa"})
    assert response.status_code == 200
    assert 'id' in response.json()


def test_create_conversation_no_title(client):
    """Testa criação de conversa sem título (deve aceitar — título é opcional)."""
    with patch('main.create_conversation', return_value='new-id-456'):
        response = client.post("/api/conversations", json={})
    assert response.status_code == 200


def test_update_conversation(client, sample_conversation):
    """Testa atualização de título de conversa."""
    with patch('main.update_conversation_title', return_value=True):
        response = client.patch(
            f"/api/conversations/{sample_conversation['id']}",
            json={"title": "Título Atualizado"}
        )
    assert response.status_code == 200
    assert response.json()['ok'] is True


def test_get_conversation_messages(client, sample_conversation):
    """Testa busca de mensagens de uma conversa."""
    messages = [
        {
            'id': 'msg-1',
            'question': 'Pergunta teste',
            'answer': 'Resposta teste',
            'created_at': '2026-05-25T18:00:00',
            'elapsed_ms': 100,
            'llm_provider': 'groq',
            'llm_model': 'llama-3.3-70b-versatile',
            'tokens_total': 50,
            'sources': [],
            'conversation_id': sample_conversation['id'],
        }
    ]
    with patch('main.get_conversation', return_value=sample_conversation):
        with patch('main.get_conversation_messages', return_value=messages):
            response = client.get(f"/api/conversations/{sample_conversation['id']}/messages")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_conversations_require_auth(client_no_auth):
    """Testa que /api/conversations exige autenticação."""
    response = client_no_auth.get("/api/conversations")
    assert response.status_code == 401
