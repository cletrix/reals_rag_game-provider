#!/bin/bash
# Restaurar backup do PostgreSQL
# Uso: ./scripts/restore-postgres.sh <arquivo_backup.sql>

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "❌ Erro: Arquivo de backup não especificado"
    echo "Uso: ./scripts/restore-postgres.sh <arquivo_backup.sql>"
    echo ""
    echo "Backups disponíveis:"
    ls -lh ./backups/postgres/backup_*.sql 2>/dev/null | tail -5
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Erro: Arquivo não encontrado: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  ATENÇÃO: Isso vai substituir todo o banco de dados atual"
echo "Backup a ser restaurado: $BACKUP_FILE"
echo ""
read -p "Deseja continuar? (s/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Operação cancelada"
    exit 0
fi

echo "Restaurando backup..."
docker compose exec -T postgres psql -U rag ragdb < $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✅ Backup restaurado com sucesso"
else
    echo "❌ Erro ao restaurar backup"
    exit 1
fi
