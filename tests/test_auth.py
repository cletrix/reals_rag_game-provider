"""
Testes unitários para autenticação e gestão de usuários
"""
import pytest
from unittest.mock import AsyncMock, patch
from schemas import UserCreate, UserLogin, UserUpdate
from auth import create_access_token, decode_access_token, get_password_hash, verify_password


class TestAuthUtils:
    """Testes para utilitários de autenticação"""

    def test_password_hashing(self):
        """Testa hash de senha com bcrypt"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        # Hash deve ser diferente da senha original
        assert hashed != password
        # Hash deve ter formato bcrypt
        assert hashed.startswith("$2b$")
        # Hash deve ter 60 caracteres
        assert len(hashed) == 60

    def test_password_verification(self):
        """Testa verificação de senha com bcrypt"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        # Senha correta deve verificar
        assert verify_password(password, hashed) is True
        # Senha incorreta não deve verificar
        assert verify_password("wrong_password", hashed) is False

    def test_token_creation(self):
        """Testa criação de token JWT"""
        data = {"sub": "test@example.com", "user_id": "123"}
        token = create_access_token(data)
        
        # Token deve ser uma string
        assert isinstance(token, str)
        # Token deve ter 3 partes (header.payload.signature)
        assert len(token.split(".")) == 3

    def test_token_decoding(self):
        """Testa decodificação de token JWT"""
        data = {"sub": "test@example.com", "user_id": "123"}
        token = create_access_token(data)
        
        decoded = decode_access_token(token)
        
        # Token deve decodificar corretamente
        assert decoded is not None
        assert decoded["sub"] == "test@example.com"
        assert decoded["user_id"] == "123"
        assert "exp" in decoded

    def test_invalid_token_decoding(self):
        """Testa decodificação de token inválido"""
        invalid_token = "invalid.token.here"
        decoded = decode_access_token(invalid_token)
        
        # Token inválido deve retornar None
        assert decoded is None


class TestAuthEndpoints:
    """Testes para endpoints de autenticação"""

    def test_register_user_success(self, client, mock_db_pool):
        """Testa registro de usuário com sucesso"""
        user_data = {
            "email": "newuser@example.com",
            "password": "password123",
            "name": "New User",
            "department": "IT",
            "role": "user"
        }
        
        mock_pool = AsyncMock()
        mock_pool.fetchrow.return_value = {"id": "550e8400-e29b-41d4-a716-446655440000"}
        mock_pool.fetch.return_value = None
        
        with patch('main.get_pool', return_value=mock_pool):
            with patch('main.get_user_by_email', return_value=None):
                with patch('main.create_user', return_value="550e8400-e29b-41d4-a716-446655440000"):
                    with patch('main.get_user_by_id', return_value={
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "newuser@example.com",
                        "name": "New User",
                        "department": "IT",
                        "role": "user",
                        "is_active": True,
                        "created_at": "2026-05-25T18:00:00+00:00",
                        "updated_at": "2026-05-25T18:00:00+00:00",
                        "last_login_at": None
                    }):
                        response = client.post("/api/auth/register", json=user_data)
                        
                        assert response.status_code == 200
                        data = response.json()
                        assert data["email"] == "newuser@example.com"
                        assert data["name"] == "New User"
                        assert "password_hash" not in data

    def test_register_user_duplicate_email(self, client):
        """Testa registro com email duplicado"""
        user_data = {
            "email": "admin@empresa.com",
            "password": "password123",
            "name": "Admin User",
            "department": "IT",
            "role": "user"
        }
        
        with patch('main.get_user_by_email', return_value={"id": "1"}):
            response = client.post("/api/auth/register", json=user_data)
            
            assert response.status_code == 400
            assert "Email já cadastrado" in response.json()["message"]

    def test_login_success(self, client):
        """Testa login com sucesso"""
        login_data = {
            "username": "admin@empresa.com",
            "password": "admin123"
        }
        
        mock_user = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "admin@empresa.com",
            "password_hash": get_password_hash("admin123"),
            "name": "Administrador",
            "department": "TI",
            "role": "admin",
            "is_active": True,
            "created_at": "2026-05-25T18:00:00+00:00",
            "updated_at": "2026-05-25T18:00:00+00:00",
            "last_login_at": None
        }
        
        with patch('main.get_user_by_email', return_value=mock_user):
            with patch('main.update_user_last_login', return_value=True):
                response = client.post("/api/auth/login", json=login_data)
                
                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                assert data["token_type"] == "bearer"
                assert data["user"]["email"] == "admin@empresa.com"
                assert "password_hash" not in data["user"]

    def test_login_invalid_credentials(self, client):
        """Testa login com credenciais inválidas"""
        login_data = {
            "username": "admin@empresa.com",
            "password": "wrongpassword"
        }
        
        mock_user = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "admin@empresa.com",
            "password_hash": get_password_hash("admin123"),
            "is_active": True
        }
        
        with patch('main.get_user_by_email', return_value=mock_user):
            response = client.post("/api/auth/login", json=login_data)
            
            assert response.status_code == 401
            assert "Credenciais inválidas" in response.json()["message"]

    def test_login_user_not_found(self, client):
        """Testa login com usuário não encontrado"""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "password123"
        }
        
        with patch('main.get_user_by_email', return_value=None):
            response = client.post("/api/auth/login", json=login_data)
                
            assert response.status_code == 401
            assert "Credenciais inválidas" in response.json()["message"]

    def test_login_inactive_account(self, client):
        """Testa login com conta desativada"""
        login_data = {
            "username": "admin@empresa.com",
            "password": "admin123"
        }
        
        mock_user = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "admin@empresa.com",
            "password_hash": get_password_hash("admin123"),
            "is_active": False
        }
        
        with patch('main.get_user_by_email', return_value=mock_user):
            response = client.post("/api/auth/login", json=login_data)
            
            assert response.status_code == 403
            assert "Conta desativada" in response.json()["message"]

    def test_get_current_user(self, client):
        """Testa obter usuário atual"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "testuser@empresa.com"
        assert "password_hash" not in data

    def test_get_current_user_no_token(self, client_no_auth):
        """Testa obter usuário atual sem token"""
        response = client_no_auth.get("/api/auth/me")
        
        assert response.status_code == 401
        assert "Token não fornecido" in response.json()["message"]

    def test_get_current_user_invalid_token(self, client_no_auth):
        """Testa obter usuário atual com token inválido"""
        response = client_no_auth.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
        assert "Token inválido ou expirado" in response.json()["message"]


class TestUserManagement:
    """Testes para gestão de usuários"""

    def test_list_users(self, client):
        """Testa listar usuários"""
        mock_users = [
            {
                "id": "1",
                "email": "admin@empresa.com",
                "name": "Administrador",
                "department": "TI",
                "role": "admin",
                "is_active": True,
                "created_at": "2026-05-25T18:00:00+00:00",
                "updated_at": "2026-05-25T18:00:00+00:00",
                "last_login_at": None
            },
            {
                "id": "2",
                "email": "dev1@empresa.com",
                "name": "Desenvolvedor 1",
                "department": "Game Development",
                "role": "user",
                "is_active": True,
                "created_at": "2026-05-25T18:00:00+00:00",
                "updated_at": "2026-05-25T18:00:00+00:00",
                "last_login_at": None
            }
        ]
        
        with patch('main.list_users', return_value=mock_users):
            response = client.get("/api/users")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["email"] == "admin@empresa.com"
        assert data[1]["email"] == "dev1@empresa.com"

    def test_get_user_by_id(self, client):
        """Testa obter usuário por ID"""
        mock_user = {
            "id": "1",
            "email": "admin@empresa.com",
            "name": "Administrador",
            "department": "TI",
            "role": "admin",
            "is_active": True,
            "created_at": "2026-05-25T18:00:00+00:00",
            "updated_at": "2026-05-25T18:00:00+00:00",
            "last_login_at": None
        }
        
        with patch('main.get_user_by_id', return_value=mock_user):
            response = client.get("/api/users/1")
        
        assert response.status_code == 200
        assert response.json()["email"] == "admin@empresa.com"

    def test_get_user_not_found(self, client):
        """Testa obter usuário não encontrado"""
        with patch('main.get_user_by_id', return_value=None):
            response = client.get("/api/users/1")
        assert response.status_code == 404

    def test_update_user(self, client):
        """Testa atualizar usuário"""
        update_data = {
            "email": "newemail@example.com",
            "name": "New Name"
        }
        
        mock_user = {
            "id": "1",
            "email": "newemail@example.com",
            "name": "New Name",
            "department": "IT",
            "role": "admin",
            "is_active": True,
            "created_at": "2026-05-25T18:00:00+00:00",
            "updated_at": "2026-05-25T18:00:00+00:00",
            "last_login_at": None
        }
        
        with patch('main.update_user', return_value=True):
            with patch('main.get_user_by_id', return_value=mock_user):
                response = client.put("/api/users/1", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newemail@example.com"
        assert data["name"] == "New Name"

    def test_update_user_password(self, client):
        """Testa atualizar senha do usuário"""
        update_data = {
            "password": "newpassword123"
        }
        
        mock_user = {
            "id": "1",
            "email": "admin@empresa.com",
            "name": "Administrador",
            "department": "TI",
            "role": "admin",
            "is_active": True,
            "created_at": "2026-05-25T18:00:00+00:00",
            "updated_at": "2026-05-25T18:00:00+00:00",
            "last_login_at": None
        }
        
        with patch('main.update_user', return_value=True):
            with patch('main.get_user_by_id', return_value=mock_user):
                response = client.put("/api/users/1", json=update_data)
        
        assert response.status_code == 200


class TestLoginPage:
    """Testes para página de login"""

    def test_login_page(self, client):
        """Testa renderização da página de login"""
        response = client.get("/login")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
