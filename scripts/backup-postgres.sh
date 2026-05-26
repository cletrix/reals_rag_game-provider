#!/bin/bash
# Backup automático do PostgreSQL
# Uso: ./scripts/backup-postgres.sh

BACKUP_DIR="./backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

# Criar diretório de backup se não existir
mkdir -p $BACKUP_DIR

echo "Iniciando backup do PostgreSQL..."
echo "Arquivo: $BACKUP_FILE"

# Executar backup
docker compose exec -T postgres pg_dump -U rag ragdb > $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✅ Backup criado com sucesso: $BACKUP_FILE"
    
    # Manter apenas os últimos 7 dias de backup
    find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
    
    # Listar backups disponíveis
    echo ""
    echo "Backups disponíveis:"
    ls -lh $BACKUP_DIR/backup_*.sql 2>/dev/null | tail -5
else
    echo "❌ Erro ao criar backup"
    exit 1
fi
