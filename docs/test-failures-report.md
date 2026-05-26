# Relatório de Falhas em Testes

**Data:** 2026-05-26
**Comando:** `make test-docker`
**Resultado:** 72 passed, 36 failed

## Resumo

- ✅ **Testes de autenticação (test_auth.py):** 20/20 passaram
- ❌ **Outros módulos:** 36 testes falharam

## Testes que Falharam

### test_db.py (2 falhas)
- `test_get_pool` - OSError: Multiple exceptions
- `test_save_query` - TypeError: save_query() missing 1 argument

### test_folder_scanner.py (5 falhas)
- `test_start_folder_scanner` - ModuleNotFoundError
- `test_stop_folder_scanner` - TypeError: object of type 'NoneType' has no len()
- `test_scan_folders` - ModuleNotFoundError
- `test_scan_single_folder_with_new_file` - ModuleNotFoundError
- `test_scan_folder_with_existing_file` - ModuleNotFoundError

### test_folders.py (4 falhas)
- `test_create_folder` - fastapi.exceptions.ResponseValidationError
- `test_index_folder` - NameError: name 'patch' is not defined
- `test_start_scanner` - NameError: name 'patch' is not defined
- `test_stop_scanner` - NameError: name 'patch' is not defined

### test_health.py (2 falhas)
- `test_health_check` - assert 207 == 200
- `test_readiness` - assert 503 == 200

### test_protected_endpoints.py (13 falhas)
- `test_requires_auth[GET-/api/history]` - assert 429 == 401
- `test_requires_auth[GET-/api/conversations]` - assert 429 == 401
- `test_requires_auth[POST-/api/conversations]` - assert 429 == 401
- `test_requires_auth[GET-/api/settings]` - assert 429 == 401
- `test_requires_auth[POST-/api/settings]` - assert 429 == 401
- `test_requires_auth[GET-/api/stats]` - assert 429 == 401
- `test_requires_auth[GET-/api/files]` - assert 429 == 401
- `test_requires_auth[GET-/api/folders]` - assert 429 == 401
- `test_requires_auth[POST-/api/index]` - assert 429 == 401
- `test_requires_auth[GET-/api/index/status]` - assert 429 == 401
- `test_requires_auth[GET-/api/users]` - assert 429 == 401
- `test_requires_auth[GET-/api/auth/me]` - assert 429 == 401
- `test_readiness_is_public` - assert 503 == 200

### test_schemas.py (5 falhas)
- `test_message_response` - pydantic_core._pydantic_core.ValidationError
- `test_query_response` - pydantic_core._pydantic_core.ValidationError
- `test_source` - pydantic_core._pydantic_core.ValidationError
- `test_settings_response` - pydantic_core._pydantic_core.ValidationError
- `test_settings_update` - pydantic_core._pydantic_core.ValidationError

### test_settings.py (5 falhas)
- `test_get_settings` - assert 429 == 200 (Rate limit excedido)
- `test_update_settings` - assert 429 == 200 (Rate limit excedido)
- `test_update_settings_invalid_payload` - pydantic_core._pydantic_core.ValidationError
- `test_settings_require_auth` - assert 429 == 401 (Rate limit excedido)
- `test_get_stats` - assert 429 == 200 (Rate limit excedido)
- `test_stats_require_auth` - assert 429 == 401 (Rate limit excedido)

## Principais Causas

### 1. Rate Limiting (429 Too Many Requests)
Muitos testes estão falhando devido ao rate limit sendo atingido durante a execução dos testes. Isso afeta principalmente:
- test_settings.py
- test_protected_endpoints.py

**Solução sugerida:** Desabilitar rate limit durante testes ou aumentar o limite para testes.

### 2. Erros de Importação e Mocks
Testes de folder_scanner e folders estão falhando devido a:
- Módulos não encontrados (ModuleNotFoundError)
- Mocks não definidos (NameError: name 'patch' is not defined)

**Solução sugerida:** Verificar imports e adicionar mocks necessários.

### 3. Erros de Validação de Schemas (Pydantic)
Testes de schemas estão falhando devido a erros de validação do Pydantic.

**Solução sugerida:** Atualizar schemas para compatibilidade com versão atual do Pydantic.

### 4. Erros de Autenticação em Protected Endpoints
Testes de protected_endpoints estão falhando com 429 em vez de 401, indicando que o rate limit está sendo aplicado antes da verificação de autenticação.

**Solução sugerida:** Ajustar ordem de middlewares ou desabilitar rate limit em testes.

### 5. Health Check
Testes de health check estão retornando códigos de status incorretos (207 em vez de 200, 503 em vez de 200).

**Solução sugerida:** Verificar implementação dos endpoints de health check.

## Prioridade de Correção

1. **Alta:** Rate limit em testes (afeta muitos testes)
2. **Alta:** Erros de importação em folder_scanner/folders
3. **Média:** Validação de schemas (Pydantic)
4. **Média:** Health check endpoints
5. **Baixa:** Erros de autenticação em protected endpoints (depende de rate limit)

## Notas

- Os testes de autenticação (test_auth.py) estão funcionando corretamente
- As falhas são em módulos que não foram modificados recentemente
- Este relatório serve como referência para correções futuras
