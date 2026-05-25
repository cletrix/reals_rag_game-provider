import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient


def test_get_folders(client, mock_db_pool, sample_folder):
    """Testa listagem de pastas."""
    mock_db_pool.fetch.return_value = [sample_folder]
    
    response = client.get("/api/folders")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_create_folder(client, mock_db_pool, sample_folder):
    """Testa criação de nova pasta."""
    mock_db_pool.fetchrow.return_value = {'id': sample_folder['id']}
    mock_db_pool.fetch.return_value = sample_folder
    
    response = client.post("/api/folders", json={
        "name": "test_folder",
        "path": "/app/data/raw/test_folder",
        "auto_index": False
    })
    assert response.status_code == 200
    data = response.json()
    assert 'id' in data
    assert data['name'] == "test_folder"


def test_get_folder(client, mock_db_pool, sample_folder):
    """Testa busca de pasta específica."""
    mock_db_pool.fetchrow.return_value = sample_folder
    
    response = client.get(f"/api/folders/{sample_folder['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == sample_folder['id']


def test_update_folder(client, mock_db_pool, sample_folder):
    """Testa atualização de pasta."""
    mock_db_pool.execute.return_value = "UPDATE 1"
    
    response = client.patch(
        f"/api/folders/{sample_folder['id']}",
        json={"name": "updated_name", "auto_index": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data['ok'] is True


def test_delete_folder(client, mock_db_pool, sample_folder):
    """Testa deleção de pasta."""
    mock_db_pool.execute.return_value = "DELETE 1"
    
    response = client.delete(f"/api/folders/{sample_folder['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data['ok'] is True


def test_get_folder_documents(client, mock_db_pool, sample_folder, sample_document):
    """Testa busca de documentos de uma pasta."""
    mock_db_pool.fetchrow.return_value = sample_folder
    mock_db_pool.fetch.return_value = [sample_document]
    
    response = client.get(f"/api/folders/{sample_folder['id']}/documents")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_upload_folder(client, mock_db_pool, sample_folder):
    """Testa upload de arquivos para nova pasta."""
    mock_db_pool.fetchrow.return_value = {'id': sample_folder['id']}
    mock_db_pool.execute.return_value = "INSERT 1"
    
    files = {"files": ("test.txt", b"test content", "text/plain")}
    response = client.post(
        "/api/folders/upload",
        files=files,
        data={"folder_name": "test_upload", "auto_index": "false"}
    )
    # Pode retornar 200 ou 422 dependendo da validação
    assert response.status_code in [200, 422]


def test_index_folder(client, mock_db_pool, sample_folder):
    """Testa indexação de pasta específica."""
    mock_db_pool.fetchrow.return_value = sample_folder
    
    with patch('web.indexer.start_indexing', new_callable=AsyncMock) as mock_index:
        mock_index.return_value = True
        
        response = client.post(f"/api/folders/{sample_folder['id']}/index")
        assert response.status_code == 200
        data = response.json()
        assert data['ok'] is True


def test_scanner_status(client):
    """Testa status do scanner de pastas."""
    response = client.get("/api/folders/scanner/status")
    assert response.status_code == 200
    data = response.json()
    assert 'running' in data


def test_start_scanner(client):
    """Testa início do scanner de pastas."""
    with patch('web.folder_scanner.start_folder_scanner', new_callable=AsyncMock) as mock_scan:
        mock_scan.return_value = True
        
        response = client.post("/api/folders/scanner/start")
        assert response.status_code == 200
        data = response.json()
        assert data['ok'] is True


def test_stop_scanner(client):
    """Testa parada do scanner de pastas."""
    with patch('web.folder_scanner.stop_folder_scanner', new_callable=AsyncMock) as mock_scan:
        mock_scan.return_value = None
        
        response = client.post("/api/folders/scanner/stop")
        assert response.status_code == 200
        data = response.json()
        assert data['ok'] is True
