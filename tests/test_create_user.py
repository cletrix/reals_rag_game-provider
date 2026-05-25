"""
Testes para o script de criação de usuários
"""
import pytest
import bcrypt


class TestCreateUserScript:
    """Testes para o script create_user.py"""

    def test_hash_password(self):
        """Testa geração de hash de senha"""
        password = "test_password_123"
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        
        # Hash deve ser diferente da senha original
        assert hashed != password
        # Hash deve ter formato bcrypt
        assert hashed.startswith("$2b$")
        # Hash deve ter 60 caracteres
        assert len(hashed) == 60

    def test_hash_password_different_salts(self):
        """Testa que hashes da mesma senha são diferentes (salt diferente)"""
        password = "test_password_123"
        hash1 = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        hash2 = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Hashes devem ser diferentes devido ao salt
        assert hash1 != hash2

    def test_verify_password(self):
        """Testa verificação de senha"""
        password = "test_password_123"
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Senha correta deve verificar
        assert bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8')) is True
        # Senha incorreta não deve verificar
        assert bcrypt.checkpw("wrong_password".encode('utf-8'), hashed.encode('utf-8')) is False
