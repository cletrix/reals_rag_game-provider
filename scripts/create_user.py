#!/usr/bin/env python3
"""
Script para criar usuários no banco de dados
Uso: docker compose run web python /app/scripts/create_user.py <email> <password> <name> <department> [role]
Exemplo: docker compose run web python /app/scripts/create_user.py user@example.com senha123 "João Silva" TI admin
"""
import sys
import os
import bcrypt
import asyncpg
from datetime import datetime
from uuid import uuid4


async def hash_password(password: str) -> str:
    """Gera hash bcrypt da senha"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


async def create_user(email: str, password: str, name: str, department: str, role: str = "user"):
    """Cria um usuário no banco de dados"""
    try:
        # Conectar ao banco
        conn = await asyncpg.connect(
            host=os.getenv("DB_HOST", "postgres"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "ragdb"),
            user=os.getenv("DB_USER", "rag"),
            password=os.getenv("DB_PASSWORD", "rag")
        )

        # Verificar se email já existe
        existing = await conn.fetchval("SELECT id FROM users WHERE email = $1", email)
        if existing:
            print(f"❌ Erro: Email '{email}' já cadastrado")
            await conn.close()
            return False

        # Gerar hash da senha
        password_hash = await hash_password(password)

        # Inserir usuário
        user_id = str(uuid4())
        now = datetime.now()
        
        await conn.execute("""
            INSERT INTO users (id, email, password_hash, name, department, role, is_active, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """, user_id, email, password_hash, name, department, role, True, now, now)

        await conn.close()
        
        print(f"✅ Usuário criado com sucesso!")
        print(f"   Email: {email}")
        print(f"   Nome: {name}")
        print(f"   Departamento: {department}")
        print(f"   Role: {role}")
        print(f"   ID: {user_id}")
        
        return True

    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


async def main():
    """Função principal"""
    print("=" * 60)
    print("Criar Usuário no Banco de Dados")
    print("=" * 60)
    print()

    # Verificar se foram passados argumentos de linha de comando
    if len(sys.argv) >= 5:
        email = sys.argv[1].strip()
        password = sys.argv[2].strip()
        name = sys.argv[3].strip()
        department = sys.argv[4].strip()
        role = sys.argv[5].strip().lower() if len(sys.argv) >= 6 else "user"
    else:
        print("❌ Erro: Argumentos insuficientes")
        print()
        print("Uso: python create_user.py <email> <password> <name> <department> [role]")
        print("Exemplo: python create_user.py user@example.com senha123 \"João Silva\" TI admin")
        print()
        print("Role opcional: admin ou user (padrão: user)")
        sys.exit(1)

    # Validações
    if not email:
        print("❌ Email é obrigatório")
        sys.exit(1)

    if not password:
        print("❌ Senha é obrigatória")
        sys.exit(1)

    if not name:
        print("❌ Nome é obrigatório")
        sys.exit(1)

    if not department:
        print("❌ Departamento é obrigatório")
        sys.exit(1)

    if role not in ["admin", "user"]:
        print("❌ Role deve ser 'admin' ou 'user'")
        sys.exit(1)

    print()
    print("Resumo:")
    print(f"  Email: {email}")
    print(f"  Nome: {name}")
    print(f"  Departamento: {department}")
    print(f"  Role: {role}")
    print()

    # Criar usuário
    success = await create_user(email, password, name, department, role)
    
    if success:
        print()
        print("Você pode fazer login com:")
        print(f"  Email: {email}")
        print(f"  Senha: {password}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
