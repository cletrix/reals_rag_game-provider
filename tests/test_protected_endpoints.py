"""
Testes de proteção JWT — verifica que todos os endpoints protegidos
retornam 401 quando chamados sem token.
"""
import pytest


PROTECTED_ENDPOINTS = [
    ("GET",    "/api/history"),
    ("GET",    "/api/conversations"),
    ("POST",   "/api/conversations"),
    ("GET",    "/api/settings"),
    ("POST",   "/api/settings"),
    ("GET",    "/api/stats"),
    ("GET",    "/api/files"),
    ("GET",    "/api/folders"),
    ("POST",   "/api/index"),
    ("GET",    "/api/index/status"),
    ("GET",    "/api/users"),
    ("GET",    "/api/auth/me"),
]

PUBLIC_ENDPOINTS = [
    ("POST",   "/api/auth/login"),
    ("POST",   "/api/auth/register"),
    ("GET",    "/health"),
    ("GET",    "/readiness"),
    ("GET",    "/liveness"),
    ("GET",    "/login"),
]


class TestProtectedEndpoints:

    @pytest.mark.parametrize("method,path", PROTECTED_ENDPOINTS)
    def test_requires_auth(self, client_no_auth, method, path):
        """Endpoint protegido deve retornar 401 sem token."""
        response = getattr(client_no_auth, method.lower())(path)
        assert response.status_code == 401, (
            f"{method} {path} deveria retornar 401, retornou {response.status_code}"
        )


class TestPublicEndpoints:

    def test_health_is_public(self, client_no_auth):
        """GET /health deve ser público."""
        response = client_no_auth.get("/health")
        assert response.status_code in (200, 207)

    def test_readiness_is_public(self, client_no_auth):
        """GET /readiness deve ser público."""
        response = client_no_auth.get("/readiness")
        assert response.status_code == 200

    def test_liveness_is_public(self, client_no_auth):
        """GET /liveness deve ser público."""
        response = client_no_auth.get("/liveness")
        assert response.status_code == 200

    def test_login_page_is_public(self, client_no_auth):
        """GET /login deve ser público."""
        response = client_no_auth.get("/login")
        assert response.status_code == 200
