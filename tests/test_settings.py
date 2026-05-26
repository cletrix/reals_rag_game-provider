"""Testes para endpoints de settings e stats."""
import pytest
from unittest.mock import patch


class TestSettings:

    def test_get_settings(self, client):
        """Testa retorno das configurações."""
        mock_settings = {
            'llm_provider': 'groq',
            'groq_model': 'llama-3.3-70b-versatile',
            'similarity_top_k': '4',
        }
        with patch('main.get_all_settings', return_value=mock_settings):
            response = client.get("/api/settings")
        assert response.status_code == 200

    def test_update_settings(self, client):
        """Testa atualização de configuração."""
        with patch('main.update_setting', return_value=None):
            response = client.post("/api/settings", json={"llm_provider": "ollama"})
        assert response.status_code == 200
        assert response.json()['ok'] is True

    def test_update_settings_invalid_payload(self, client):
        """Testa atualização com payload inválido."""
        response = client.post("/api/settings", data="not-json")
        assert response.status_code in (400, 422)

    def test_settings_require_auth(self, client_no_auth):
        """Settings exigem autenticação."""
        response = client_no_auth.get("/api/settings")
        assert response.status_code == 401


class TestStats:

    def test_get_stats(self, client):
        """Testa retorno de estatísticas."""
        mock_stats = {'total_queries': 10, 'total_tokens': 500, 'avg_elapsed_ms': 200}
        with patch('main.get_stats', return_value=mock_stats):
            with patch('main._fetch_groq_usage', return_value=None):
                response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert 'total_queries' in data
        assert 'total_tokens' in data

    def test_stats_require_auth(self, client_no_auth):
        """Stats exigem autenticação."""
        response = client_no_auth.get("/api/stats")
        assert response.status_code == 401
