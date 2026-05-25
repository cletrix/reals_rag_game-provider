# Autenticação e Gestão de Usuários

Este guia explica como configurar e usar o sistema de autenticação do RAG Game Provider.

## Visão Geral

O sistema de autenticação inclui:
- Tabela `users` no PostgreSQL com login/senha
- Hash de senhas usando bcrypt
- Tokens JWT para autenticação
- Endpoints REST para registro, login e gestão de usuários
- Usuários padrão criados automaticamente

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

A migration `003_add_users.sql` é executada automaticamente quando o PostgreSQL inicia. Ela cria:
- Tabela `users` com todos os campos necessários
- Índices para performance
- Trigger para atualizar `updated_at`
- Usuários padrão (admin e user)

## Usuários Padrão

Dois usuários são criados automaticamente:

### Admin
- **Username**: `admin`
- **Email**: `admin@rag.local`
- **Password**: `admin123`
- **Role**: Administrador

### User
- **Username**: `user`
- **Email**: `user@rag.local`
- **Password**: `user123`
- **Role**: Usuário comum

⚠️ **IMPORTANTE**: Altere essas senhas em produção!

## API Endpoints

### Registro de Usuário

```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "joao",
  "email": "joao@example.com",
  "password": "senha123",
  "full_name": "João Silva"
}
```

**Resposta**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "joao",
  "email": "joao@example.com",
  "full_name": "João Silva",
  "is_active": true,
  "is_admin": false,
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
  "username": "joao",
  "password": "senha123"
}
```

**Nota**: O campo `username` aceita tanto username quanto email.

**Resposta**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "joao",
    "email": "joao@example.com",
    "full_name": "João Silva",
    "is_active": true,
    "is_admin": false,
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
    "username": "admin",
    "email": "admin@rag.local",
    "full_name": "Administrator",
    "is_active": true,
    "is_admin": true,
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
  "full_name": "João Silva Jr.",
  "password": "nova_senha123",
  "is_active": true,
  "is_admin": false
}
```

Todos os campos são opcionais. Apenas os campos fornecidos serão atualizados.

## Exemplos de Uso com cURL

### Registrar novo usuário

```bash
curl -X POST http://localhost:2468/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "maria",
    "email": "maria@example.com",
    "password": "senha123",
    "full_name": "Maria Santos"
  }'
```

### Fazer login

```bash
curl -X POST http://localhost:2468/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "maria",
    "password": "senha123"
  }'
```

### Usar token para acessar endpoint protegido

```bash
# Primeiro, faça login e salve o token
TOKEN=$(curl -s -X POST http://localhost:2468/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# Use o token
curl -X GET http://localhost:2468/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

## Estrutura da Tabela users

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | Chave primária |
| username | VARCHAR(50) | Nome de usuário único |
| email | VARCHAR(255) | Email único |
| password_hash | VARCHAR(255) | Hash bcrypt da senha |
| full_name | VARCHAR(255) | Nome completo |
| is_active | BOOLEAN | Se a conta está ativa |
| is_admin | BOOLEAN | Se é administrador |
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
WHERE username = 'admin';

-- Alterar senha do user
UPDATE users 
SET password_hash = '$2b$12$...' 
WHERE username = 'user';
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
