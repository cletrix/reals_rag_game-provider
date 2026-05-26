#!/bin/bash
# Script que verifica se PostgreSQL está healthy e recupera se necessário

# Verificar se PostgreSQL está healthy
docker compose ps postgres | grep -q "healthy"

if [ $? -ne 0 ]; then
    echo "PostgreSQL não está healthy, recuperando..."
    docker compose stop postgres
    docker compose run --user postgres postgres pg_resetwal -f /var/lib/postgresql/data
    docker compose up -d postgres
    echo "PostgreSQL recuperado"
else
    echo "PostgreSQL está healthy"
fi
