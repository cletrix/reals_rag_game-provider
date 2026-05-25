# Autenticação e Gestão de Usuários

Este guia explica como configurar e usar o sistema de autenticação do RAG Game Provider.

## Visão Geral

O sistema de autenticação inclui:
- Tabela `users` no PostgreSQL com login/senha
- Hash de senhas usando bcrypt (implementação direta, sem passlib)
- Tokens JWT para autenticação
- Endpoints REST para registro, login e gestão de usuários
- Usuários padrão criados automaticamente
- Login usando email como identificador

## Histórico de Mudanças

### 2026-05-25 - Correção do Problema Bcrypt/Passlib

**Problema Identificado:**
- A biblioteca `passlib` tinha incompatibilidade com a versão do `bcrypt` instalada
- Hashes bcrypt na migration estavam malformados (checksum com tamanho incorreto)
- Login falhava com erro: `ValueError: malformed bcrypt hash (checksum must be exactly 31 chars)`

**Solução Aplicada:**
1. **Substituição de passlib por bcrypt direto** em `web/auth.py`:
   - Removido `passlib.context.CryptContext`
   - Implementado `bcrypt.checkpw()` para verificação
   - Implementado `bcrypt.hashpw()` para hashing
   - `get_password_hash()` agora usa `bcrypt.gensalt()` e `bcrypt.hashpw()`
   - `verify_password()` agora usa `bcrypt.checkpw()`

2. **Geração de hashes corretos** na migration `004_add_password_hash.sql`:
   - `admin123`: `$2b$12$I3Nq0VMRGtwaFmEfXbYqOexlaguVHj06pzsVng0S/jYw1Fif3raru`
   - `dev123`: `$2b$12$OWX8gkFw/VeDaSze4zB5UudCo7NmcrQFHPU7bkfCcdlRe4m/xumd2`

3. **Atualização de testes unitários**:
   - 20 testes implementados cobrindo todo o sistema de autenticação
   - Testes de hashing/verification com bcrypt direto
   - Testes de endpoints de autenticação
   - Testes de gestão de usuários
   - Testes de página de login
   - Todos os testes passando (20/20)

**Comando para rodar testes:**
```bash
make test-auth
```

**Resultado:**
- Login funcional com `admin@empresa.com` / `admin123`
- Todos os testes unitários passando
- Sistema de autenticação estável e testado

## Configuração

### 1. Variáveis de Ambiente

Adicione ao seu arquivo `.env`:

```bash
# Authentication
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

**SECRET_KEY**: Chave secreta para assinar tokens JWT. Use uma string longa e aleatória em produção.

**ACCESS_TOKEN_EXPIRE_MINUTES**: Tempo de expiração do token em minutos (padrão: 1440 = 24 horas).

### 2. Dependências

As dependências já estão incluídas em `web/requirements.txt`:
- `bcrypt` - Hash de senhas
- `python-jose[cryptography]` - Geração/validação de tokens JWT
- `passlib[bcrypt]` - Biblioteca de hash de senhas

### 3. Migration Automática

A migration `004_add_password_hash.sql` é executada automaticamente quando o PostgreSQL inicia. Ela:
- Adiciona coluna `password_hash` à tabela `users` existente
- Adiciona índices para performance
- Configura senhas para usuários existentes

A tabela `users` é criada pelo script `schema-auditoria-enterprise.sql` com a seguinte estrutura:
- `id` (UUID) - Chave primária
- `email` (VARCHAR) - Email único (usado para login)
- `name` (VARCHAR) - Nome completo
- `department` (VARCHAR) - Departamento
- `role` (VARCHAR) - Role (admin, user, viewer)
- `is_active` (BOOLEAN) - Status da conta
- `created_at` (TIMESTAMPTZ) - Data de criação
- `updated_at` (TIMESTAMPTZ) - Data de atualização
- `last_login_at` (TIMESTAMPTZ) - Último login
- `password_hash` (VARCHAR) - Hash bcrypt da senha (adicionado pela migration)

## Usuários Padrão

Usuários são criados automaticamente pelo script `schema-auditoria-enterprise.sql` e recebem senhas via migration:

### Admin
- **Email**: `admin@empresa.com`
- **Password**: `admin123`
- **Role**: admin
- **Department**: TI

### Desenvolvedores
- **Email**: `dev1@empresa.com` / `dev2@empresa.com`
- **Password**: `dev123`
- **Role**: user
- **Department**: Game Development

### Outros Usuários
- **Email**: `bets1@empresa.com`
- **Password**: `dev123`
- **Role**: user
- **Department**: Bets

- **Email**: `rh1@empresa.com`
- **Password**: `dev123`
- **Role**: user
- **Department**: RH

⚠️ **IMPORTANTE**: Altere essas senhas em produção!

## API Endpoints

### Registro de Usuário

```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "joao@example.com",
  "password": "senha123",
  "name": "João Silva",
  "department": "IT",
  "role": "user"
}
```

**Resposta**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "joao@example.com",
  "name": "João Silva",
  "department": "IT",
  "role": "user",
  "is_active": true,
  "created_at": "2026-05-25T18:00:00+00:00",
  "updated_at": "2026-05-25T18:00:00+00:00",
  "last_login_at": null
}
```

### Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "joao@example.com",
  "password": "senha123"
}
```

**Nota**: O campo `username` deve conter o email do usuário.

**Resposta**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "joao@example.com",
    "name": "João Silva",
    "department": "IT",
    "role": "user",
    "is_active": true,
    "created_at": "2026-05-25T18:00:00+00:00",
    "updated_at": "2026-05-25T18:00:00+00:00",
    "last_login_at": "2026-05-25T19:30:00+00:00"
  }
}
```

### Obter Usuário Atual

```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

**Resposta**: Mesmo formato que o login.

### Listar Usuários

```http
GET /api/users?skip=0&limit=100
Authorization: Bearer <access_token>
```

**Resposta**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "admin@empresa.com",
    "name": "Administrador",
    "department": "TI",
    "role": "admin",
    "is_active": true,
    "created_at": "2026-05-25T18:00:00+00:00",
    "updated_at": "2026-05-25T18:00:00+00:00",
    "last_login_at": "2026-05-25T19:30:00+00:00"
  }
]
```

### Obter Usuário por ID

```http
GET /api/users/{user_id}
Authorization: Bearer <access_token>
```

### Atualizar Usuário

```http
PUT /api/users/{user_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "email": "novoemail@example.com",
  "name": "João Silva Jr.",
  "password": "nova_senha123",
  "is_active": true,
  "role": "user"
}
```

Todos os campos são opcionais. Apenas os campos fornecidos serão atualizados.

## Exemplos de Uso com cURL

### Registrar novo usuário

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "maria@example.com",
    "password": "senha123",
    "name": "Maria Santos",
    "department": "IT",
    "role": "user"
  }'
```

### Fazer login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@empresa.com",
    "password": "admin123"
  }'
```

### Usar token para acessar endpoint protegido

```bash
# Primeiro, faça login e salve o token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@empresa.com","password":"admin123"}' \
  | jq -r '.access_token')

# Use o token
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

## Estrutura da Tabela users

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | Chave primária |
| email | VARCHAR(255) | Email único (usado para login) |
| name | VARCHAR(255) | Nome completo |
| department | VARCHAR(100) | Departamento |
| role | VARCHAR(50) | Role (admin, user, viewer) |
| is_active | BOOLEAN | Se a conta está ativa |
| password_hash | VARCHAR(255) | Hash bcrypt da senha |
| created_at | TIMESTAMPTZ | Data de criação |
| updated_at | TIMESTAMPTZ | Data de atualização |
| last_login_at | TIMESTAMPTZ | Último login |

## Segurança

### Alterar Senhas Padrão

Para alterar as senhas dos usuários padrão:

```bash
docker exec -it landf_postgres psql -U rag ragdb
```

```sql
-- Alterar senha do admin
UPDATE users
SET password_hash = '$2b$12$...'
WHERE email = 'admin@empresa.com';

-- Alterar senha de outros usuários
UPDATE users
SET password_hash = '$2b$12$...'
WHERE email = 'dev1@empresa.com';
```

Para gerar um novo hash bcrypt:

```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
print(pwd_context.hash("nova_senha"))
```

### Gerar SECRET_KEY Seguro

```bash
# Linux/Mac
openssl rand -hex 32

# Python
python -c "import secrets; print(secrets.token_hex(32))"
```

## Troubleshooting

### Erro: "Nome de usuário já existe"

O username deve ser único. Escolha outro username.

### Erro: "Email já cadastrado"

O email deve ser único. Escolha outro email.

### Erro: "Credenciais inválidas"

Verifique se o username/email e senha estão corretos.

### Erro: "Conta desativada"

A conta foi desativada. Um administrador precisa reativá-la:

```sql
UPDATE users SET is_active = TRUE WHERE username = 'usuario';
```

### Erro: "Token inválido ou expirado"

O token expirou ou é inválido. Faça login novamente para obter um novo token.

## Próximos Passos

Para produção, considere:

1. **Implementar middleware de autenticação** para proteger endpoints sensíveis
2. **Adicionar refresh tokens** para melhor UX
3. **Implementar RBAC (Role-Based Access Control)** para permissões granulares
4. **Adicionar rate limiting** nos endpoints de auth
5. **Implementar recuperação de senha** com email
6. **Adicionar 2FA (Two-Factor Authentication)**
7. **Auditoria de ações de usuários**

## Documentação da API

A documentação completa da API está disponível em:
- Swagger UI: `http://localhost:2468/docs`
- ReDoc: `http://localhost:2468/redoc`
