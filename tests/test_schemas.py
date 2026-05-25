import pytest
from pydantic import ValidationError
from web.schemas import (
    FolderResponse, FolderCreate, FolderUpdate,
    DocumentResponse, FolderUploadResponse,
    ConversationResponse, ConversationDetail, ConversationUpdate,
    MessageResponse,
    QueryResponse, QueryDetail, Source,
    SettingsResponse, SettingsUpdate,
    HealthResponse,
    ErrorResponse
)


def test_folder_response():
    """Testa schema FolderResponse."""
    data = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "test_folder",
        "path": "/app/data/raw/test_folder",
        "size_bytes": 1024,
        "file_count": 1,
        "indexed_at": None,
        "auto_index": False,
        "created_at": "2026-05-25T18:00:00",
        "updated_at": "2026-05-25T18:00:00"
    }
    folder = FolderResponse(**data)
    assert folder.id == data["id"]
    assert folder.name == data["name"]
    assert folder.auto_index is False


def test_folder_create():
    """Testa schema FolderCreate."""
    data = {
        "name": "test_folder",
        "path": "/app/data/raw/test_folder",
        "auto_index": True
    }
    folder = FolderCreate(**data)
    assert folder.name == data["name"]
    assert folder.auto_index is True


def test_folder_create_validation():
    """Testa validação de FolderCreate."""
    with pytest.raises(ValidationError):
        FolderCreate(name="", path="/app/data/raw/test")  # nome vazio
    
    with pytest.raises(ValidationError):
        FolderCreate(name="a" * 300, path="/app/data/raw/test")  # nome muito longo


def test_folder_update():
    """Testa schema FolderUpdate."""
    data = {"name": "updated_name", "auto_index": True}
    folder = FolderUpdate(**data)
    assert folder.name == data["name"]
    assert folder.auto_index is True


def test_folder_update_optional():
    """Testa campos opcionais de FolderUpdate."""
    folder = FolderUpdate()
    assert folder.name is None
    assert folder.auto_index is None


def test_document_response():
    """Testa schema DocumentResponse."""
    data = {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "folder_id": "550e8400-e29b-41d4-a716-446655440000",
        "name": "test.txt",
        "path": "/app/data/raw/test_folder/test.txt",
        "size_bytes": 1024,
        "indexed": False,
        "indexed_at": None,
        "mtime": 1716244800.0,
        "created_at": "2026-05-25T18:00:00",
        "updated_at": "2026-05-25T18:00:00"
    }
    doc = DocumentResponse(**data)
    assert doc.id == data["id"]
    assert doc.name == data["name"]
    assert doc.indexed is False


def test_folder_upload_response():
    """Testa schema FolderUploadResponse."""
    data = {
        "folder_id": "550e8400-e29b-41d4-a716-446655440000",
        "folder_name": "test_upload",
        "files_uploaded": 3,
        "total_size_bytes": 3072,
        "files": ["file1.txt", "file2.txt", "file3.txt"]
    }
    response = FolderUploadResponse(**data)
    assert response.folder_id == data["folder_id"]
    assert response.files_uploaded == 3
    assert len(response.files) == 3


def test_conversation_response():
    """Testa schema ConversationResponse."""
    data = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Test Conversation",
        "message_count": 2,
        "created_at": "2026-05-25T18:00:00",
        "updated_at": "2026-05-25T18:05:00"
    }
    conv = ConversationResponse(**data)
    assert conv.id == data["id"]
    assert conv.title == data["title"]


def test_conversation_update():
    """Testa schema ConversationUpdate."""
    data = {"title": "Updated Title"}
    conv = ConversationUpdate(**data)
    assert conv.title == data["title"]


def test_message_response():
    """Testa schema MessageResponse."""
    data = {
        "id": "msg-1",
        "conversation_id": "conv-1",
        "role": "user",
        "content": "Test message",
        "created_at": "2026-05-25T18:00:00"
    }
    msg = MessageResponse(**data)
    assert msg.id == data["id"]
    assert msg.role == data["role"]


def test_query_response():
    """Testa schema QueryResponse."""
    data = {
        "id": "query-1",
        "question": "Test question",
        "answer": "Test answer",
        "sources": [],
        "elapsed_ms": 1000,
        "llm_model": "llama-3.3-70b-versatile"
    }
    query = QueryResponse(**data)
    assert query.id == data["id"]
    assert query.question == data["question"]


def test_source():
    """Testa schema Source."""
    data = {
        "file": "test.pdf",
        "page": 1,
        "score": 0.95
    }
    source = Source(**data)
    assert source.file == data["file"]
    assert source.page == data["page"]


def test_settings_response():
    """Testa schema SettingsResponse."""
    data = {
        "llm_provider": "groq",
        "groq_model": "llama-3.3-70b-versatile",
        "ollama_model": "qwen2.5:7b",
        "similarity_top_k": 4
    }
    settings = SettingsResponse(**data)
    assert settings.llm_provider == data["llm_provider"]
    assert settings.similarity_top_k == 4


def test_settings_update():
    """Testa schema SettingsUpdate."""
    data = {
        "llm_provider": "ollama",
        "similarity_top_k": 5
    }
    settings = SettingsUpdate(**data)
    assert settings.llm_provider == data["llm_provider"]
    assert settings.similarity_top_k == 5


def test_health_response():
    """Testa schema HealthResponse."""
    data = {
        "status": "healthy",
        "timestamp": "2026-05-25T18:00:00",
        "services": {
            "postgres": "healthy",
            "qdrant": "healthy",
            "ollama": "healthy"
        }
    }
    health = HealthResponse(**data)
    assert health.status == data["status"]
    assert "postgres" in health.services


def test_error_response():
    """Testa schema ErrorResponse."""
    data = {
        "error": "ValidationError",
        "message": "Invalid input",
        "detail": "Field required"
    }
    error = ErrorResponse(**data)
    assert error.error == data["error"]
    assert error.message == data["message"]
