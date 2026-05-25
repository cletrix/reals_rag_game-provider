"""
Testes unitários para autenticação e gestão de usuários
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from web.schemas import UserCreate, UserLogin, UserUpdate
from web.auth import get_password_hash, verify_password, create_access_token, decode_access_token


class TestAuthUtils:
    """Testes para utilitários de autenticação"""

    def test_password_hashing(self):
        """Testa hash de senha"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        # Hash deve ser diferente da senha original
        assert hashed != password
        # Hash deve ter formato bcrypt
        assert hashed.startswith("$2b$")

    def test_password_verification(self):
        """Testa verificação de senha"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        # Senha correta deve verificar
        assert verify_password(password, hashed) is True
        # Senha incorreta não deve verificar
        assert verify_password("wrong_password", hashed) is False

    def test_token_creation(self):
        """Testa criação de token JWT"""
        data = {"sub": "testuser", "user_id": "123"}
        token = create_access_token(data)
        
        # Token deve ser uma string
        assert isinstance(token, str)
        # Token deve ter 3 partes (header.payload.signature)
        assert len(token.split(".")) == 3

    def test_token_decoding(self):
        """Testa decodificação de token JWT"""
        data = {"sub": "testuser", "user_id": "123"}
        token = create_access_token(data)
        
        decoded = decode_access_token(token)
        
        # Token deve decodificar corretamente
        assert decoded is not None
        assert decoded["sub"] == "testuser"
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

    @pytest.mark.asyncio
    async def test_register_user_success(self, client: AsyncClient, mock_db_pool):
        """Testa registro de usuário com sucesso"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User"
        }
        
        # Mock database responses
        mock_pool = AsyncMock()
        mock_pool.fetchrow.return_value = {"id": "550e8400-e29b-41d4-a716-446655440000"}
        mock_pool.fetch.return_value = None  # No existing user
        
        with patch('web.main.get_pool', return_value=mock_pool):
            with patch('web.main.get_user_by_username', return_value=None):
                with patch('web.main.get_user_by_email', return_value=None):
                    with patch('web.main.create_user', return_value="550e8400-e29b-41d4-a716-446655440000"):
                        with patch('web.main.get_user_by_id', return_value={
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "username": "newuser",
                            "email": "newuser@example.com",
                            "full_name": "New User",
                            "is_active": True,
                            "is_admin": False,
                            "created_at": "2026-05-25T18:00:00+00:00",
                            "updated_at": "2026-05-25T18:00:00+00:00",
                            "last_login_at": None
                        }):
                            response = await client.post("/api/auth/register", json=user_data)
                            
                            assert response.status_code == 200
                            data = response.json()
                            assert data["username"] == "newuser"
                            assert data["email"] == "newuser@example.com"
                            assert "password_hash" not in data

    @pytest.mark.asyncio
    async def test_register_user_duplicate_username(self, client: AsyncClient):
        """Testa registro com username duplicado"""
        user_data = {
            "username": "admin",
            "email": "newuser@example.com",
            "password": "password123"
        }
        
        with patch('web.main.get_user_by_username', return_value={"id": "1"}):
            response = await client.post("/api/auth/register", json=user_data)
            
            assert response.status_code == 400
            assert "Nome de usuário já existe" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(self, client: AsyncClient):
        """Testa registro com email duplicado"""
        user_data = {
            "username": "newuser",
            "email": "admin@rag.local",
            "password": "password123"
        }
        
        with patch('web.main.get_user_by_username', return_value=None):
            with patch('web.main.get_user_by_email', return_value={"id": "1"}):
                response = await client.post("/api/auth/register", json=user_data)
                
                assert response.status_code == 400
                assert "Email já cadastrado" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        """Testa login com sucesso"""
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        mock_user = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "username": "admin",
            "email": "admin@rag.local",
            "password_hash": get_password_hash("admin123"),
            "full_name": "Administrator",
            "is_active": True,
            "is_admin": True,
            "created_at": "2026-05-25T18:00:00+00:00",
            "updated_at": "2026-05-25T18:00:00+00:00",
            "last_login_at": None
        }
        
        with patch('web.main.get_user_by_username', return_value=mock_user):
            with patch('web.main.update_user_last_login', return_value=True):
                response = await client.post("/api/auth/login", json=login_data)
                
                assert response.status_code == 200
                data = response.json()
                assert "access_token" in data
                assert data["token_type"] == "bearer"
                assert data["user"]["username"] == "admin"
                assert "password_hash" not in data["user"]

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Testa login com credenciais inválidas"""
        login_data = {
            "username": "admin",
            "password": "wrongpassword"
        }
        
        mock_user = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "username": "admin",
            "password_hash": get_password_hash("admin123"),
            "is_active": True
        }
        
        with patch('web.main.get_user_by_username', return_value=mock_user):
            response = await client.post("/api/auth/login", json=login_data)
            
            assert response.status_code == 401
            assert "Credenciais inválidas" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, client: AsyncClient):
        """Testa login com usuário não encontrado"""
        login_data = {
            "username": "nonexistent",
            "password": "password123"
        }
        
        with patch('web.main.get_user_by_username', return_value=None):
            with patch('web.main.get_user_by_email', return_value=None):
                response = await client.post("/api/auth/login", json=login_data)
                
                assert response.status_code == 401
                assert "Credenciais inválidas" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_inactive_account(self, client: AsyncClient):
        """Testa login com conta desativada"""
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        mock_user = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "username": "admin",
            "password_hash": get_password_hash("admin123"),
            "is_active": False
        }
        
        with patch('web.main.get_user_by_username', return_value=mock_user):
            response = await client.post("/api/auth/login", json=login_data)
            
            assert response.status_code == 403
            assert "Conta desativada" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_current_user(self, client: AsyncClient):
        """Testa obter usuário atual"""
        token = create_access_token({"sub": "admin", "user_id": "123"})
        
        mock_user = {
            "id": "123",
            "username": "admin",
            "email": "admin@rag.local",
            "full_name": "Administrator",
            "is_active": True,
            "is_admin": True,
            "created_at": "2026-05-25T18:00:00+00:00",
            "updated_at": "2026-05-25T18:00:00+00:00",
            "last_login_at": None
        }
        
        with patch('web.main.get_user_by_username', return_value=mock_user):
            response = await client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["username"] == "admin"
            assert "password_hash" not in data

    @pytest.mark.asyncio
    async def test_get_current_user_no_token(self, client: AsyncClient):
        """Testa obter usuário atual sem token"""
        response = await client.get("/api/auth/me")
        
        assert response.status_code == 401
        assert "Token não fornecido" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, client: AsyncClient):
        """Testa obter usuário atual com token inválido"""
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
        assert "Token inválido ou expirado" in response.json()["detail"]


class TestUserManagement:
    """Testes para gestão de usuários"""

    @pytest.mark.asyncio
    async def test_list_users(self, client: AsyncClient):
        """Testa listar usuários"""
        mock_users = [
            {
                "id": "1",
                "username": "admin",
                "email": "admin@rag.local",
                "full_name": "Administrator",
                "is_active": True,
                "is_admin": True,
                "created_at": "2026-05-25T18:00:00+00:00",
                "updated_at": "2026-05-25T18:00:00+00:00",
                "last_login_at": None
            },
            {
                "id": "2",
                "username": "user",
                "email": "user@rag.local",
                "full_name": "Test User",
                "is_active": True,
                "is_admin": False,
                "created_at": "2026-05-25T18:00:00+00:00",
                "updated_at": "2026-05-25T18:00:00+00:00",
                "last_login_at": None
            }
        ]
        
        with patch('web.main.list_users', return_value=mock_users):
            response = await client.get("/api/users")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["username"] == "admin"
            assert data[1]["username"] == "user"

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, client: AsyncClient):
        """Testa obter usuário por ID"""
        mock_user = {
            "id": "1",
            "username": "admin",
            "email": "admin@rag.local",
            "full_name": "Administrator",
            "is_active": True,
            "is_admin": True,
            "created_at": "2026-05-25T18:00:00+00:00",
            "updated_at": "2026-05-25T18:00:00+00:00",
            "last_login_at": None
        }
        
        with patch('web.main.get_user_by_id', return_value=mock_user):
            response = await client.get("/api/users/1")
            
            assert response.status_code == 200
            data = response.json()
            assert data["username"] == "admin"

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, client: AsyncClient):
        """Testa obter usuário não encontrado"""
        with patch('web.main.get_user_by_id', return_value=None):
            response = await client.get("/api/users/nonexistent")
            
            assert response.status_code == 404
            assert "Usuário não encontrado" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_user(self, client: AsyncClient):
        """Testa atualizar usuário"""
        update_data = {
            "email": "newemail@example.com",
            "full_name": "New Name"
        }
        
        mock_user = {
            "id": "1",
            "username": "admin",
            "email": "newemail@example.com",
            "full_name": "New Name",
            "is_active": True,
            "is_admin": True,
            "created_at": "2026-05-25T18:00:00+00:00",
            "updated_at": "2026-05-25T18:00:00+00:00",
            "last_login_at": None
        }
        
        with patch('web.main.update_user', return_value=True):
            with patch('web.main.get_user_by_id', return_value=mock_user):
                response = await client.put("/api/users/1", json=update_data)
                
                assert response.status_code == 200
                data = response.json()
                assert data["email"] == "newemail@example.com"
                assert data["full_name"] == "New Name"

    @pytest.mark.asyncio
    async def test_update_user_password(self, client: AsyncClient):
        """Testa atualizar senha do usuário"""
        update_data = {
            "password": "newpassword123"
        }
        
        mock_user = {
            "id": "1",
            "username": "admin",
            "email": "admin@rag.local",
            "full_name": "Administrator",
            "is_active": True,
            "is_admin": True,
            "created_at": "2026-05-25T18:00:00+00:00",
            "updated_at": "2026-05-25T18:00:00+00:00",
            "last_login_at": None
        }
        
        with patch('web.main.update_user', return_value=True):
            with patch('web.main.get_user_by_id', return_value=mock_user):
                response = await client.put("/api/users/1", json=update_data)
                
                assert response.status_code == 200


class TestLoginPage:
    """Testes para página de login"""

    @pytest.mark.asyncio
    async def test_login_page(self, client: AsyncClient):
        """Testa renderização da página de login"""
        response = await client.get("/login")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
