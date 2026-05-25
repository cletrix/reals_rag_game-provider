# Testes Unitários

Este diretório contém os testes unitários da aplicação RAG LandF.

## Estrutura

```
tests/
├── __init__.py
├── conftest.py           # Fixtures compartilhadas
├── test_health.py        # Testes de health checks
├── test_conversations.py # Testes de endpoints de conversas
├── test_folders.py       # Testes de endpoints de pastas
├── test_schemas.py       # Testes de schemas Pydantic
├── test_db.py            # Testes de funções do banco de dados
├── test_folder_scanner.py # Testes do scanner de pastas
└── test_rate_limiting.py # Testes de rate limiting
```

## Pré-requisitos

Instale as dependências de desenvolvimento:

```bash
pip install -r requirements-dev.txt
```

## Executar Testes

### Executar todos os testes

```bash
make test
```

Ou diretamente:

```bash
python -m pytest tests/ -v
```

### Executar com cobertura de código

```bash
make test-cov
```

Ou diretamente:

```bash
python -m pytest tests/ --cov=web --cov-report=html --cov-report=term
```

O relatório HTML será gerado em `htmlcov/index.html`.

### Executar testes específicos

```bash
# Testar apenas health checks
python -m pytest tests/test_health.py -v

# Testar apenas folders
python -m pytest tests/test_folders.py -v

# Testar uma função específica
python -m pytest tests/test_schemas.py::test_folder_response -v
```

## Fixtures

O arquivo `conftest.py` fornece fixtures compartilhadas:

- `client`: Cliente de teste FastAPI
- `mock_db_pool`: Mock do pool de conexões do banco
- `mock_settings`: Mock das configurações
- `sample_conversation`: Dados de exemplo para conversa
- `sample_folder`: Dados de exemplo para pasta
- `sample_document`: Dados de exemplo para documento

## Cobertura Atual

Os testes cobrem:

- ✅ Health checks (`/health`, `/readiness`, `/liveness`)
- ✅ Endpoints de conversas (CRUD completo)
- ✅ Endpoints de pastas (CRUD completo + upload + scanner)
- ✅ Schemas Pydantic (validação de dados)
- ✅ Funções do banco de dados (asyncpg)
- ✅ Scanner de pastas (indexação automática)
- ✅ Rate limiting (limitação por IP)

## Adicionando Novos Testes

1. Crie um novo arquivo `test_<modulo>.py` no diretório `tests/`
2. Importe as fixtures necessárias de `conftest.py`
3. Use `@pytest.mark.asyncio` para testes assíncronos
4. Use mocks para isolar dependências externas

Exemplo:

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_minha_funcao(mock_db_pool):
    mock_db_pool.fetch.return_value = {'id': 'test'}
    result = await minha_funcao()
    assert result is not None
```

## CI/CD

Estes testes podem ser integrados em pipelines de CI/CD para garantir que mudanças não quebram funcionalidades existentes.
