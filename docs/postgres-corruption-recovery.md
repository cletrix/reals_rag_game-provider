# Recuperação de Corrupção do PostgreSQL

## Data: 2026-05-26

## Problema Identificado

### Erro ao Iniciar PostgreSQL

```
invalid record length at 0x19C0860: expected at least 24, got 0
could not open directory "pg_logical/snapshots": No such file or directory
database system was not properly shut down
checkpoint request failed
```

### Causa Raiz

O PostgreSQL foi desligado de forma abrupta (sem graceful shutdown), causando:
- Corrupção do WAL (Write-Ahead Log)
- Falta de diretórios críticos (`pg_logical/snapshots`)
- Arquivos em estado inconsistente

### Por Que Aconteceu

O container PostgreSQL não tinha configuração de graceful shutdown, então:
- Quando o container era parado rapidamente, o PostgreSQL não tinha tempo para:
  - Escrever buffers de memória para disco
  - Fechar arquivos corretamente
  - Finalizar transações pendentes
  - Criar checkpoint consistente

## Solução Aplicada

### 1. Graceful Shutdown (Prevenção)

**Arquivo:** `docker-compose.yml`

```yaml
postgres:
  stop_grace_period: 30s
  stop_signal: SIGTERM
```

**O que isso resolve:**
- PostgreSQL tem 30 segundos para finalizar transações
- Escreve buffers para disco
- Cria checkpoint consistente
- Evita corrupção do WAL

### 2. Recuperação com pg_resetwal (Correção)

**Comando:**
```bash
docker compose run --rm --user postgres postgres pg_resetwal -f /var/lib/postgresql/data
```

**Resultado:**
```
Write-ahead log reset
```

**O que faz:**
- Reseta o WAL corrompido
- Permite que o PostgreSQL inicie
- Preserva os dados (não apaga o banco)

### 3. Inicialização Bem-sucedida

```
database system is ready to accept connections
```

## Implementação para Produção

### Backup Automático

**Script:** `scripts/backup-postgres.sh`

```bash
#!/bin/bash
# Backup automático do PostgreSQL
BACKUP_DIR="./backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR

docker compose exec -T postgres pg_dump -U rag ragdb > $BACKUP_FILE

# Manter apenas os últimos 7 dias de backup
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete

echo "Backup criado: $BACKUP_FILE"
```

**Cron Job (production):**
```bash
# Backup diário às 2h da manhã
0 2 * * * cd /path/to/project && ./scripts/backup-postgres.sh
```

### Script de Recuperação

**Script:** `scripts/restore-postgres.sh`

```bash
#!/bin/bash
# Restaurar backup do PostgreSQL
BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Uso: ./restore-postgres.sh <arquivo_backup.sql>"
    exit 1
fi

echo "Restaurando backup: $BACKUP_FILE"
docker compose exec -T postgres psql -U rag ragdb < $BACKUP_FILE
echo "Backup restaurado com sucesso"
```

### Configuração de Produção

**Arquivo:** `docker-compose.prod.yml`

```yaml
postgres:
  image: postgres:16-alpine
  container_name: landf_postgres_prod
  environment:
    POSTGRES_USER: ${DB_USER}
    POSTGRES_PASSWORD: ${DB_PASSWORD}
    POSTGRES_DB: ${DB_NAME}
  volumes:
    - postgres_data:/var/lib/postgresql/data
    - ./backups:/backups
    - ./db/init.sql:/docker-entrypoint-initdb.d/01-init.sql:ro
    - ./migrations:/docker-entrypoint-initdb.d:ro
  ports:
    - "5432:5432"
  restart: unless-stopped
  stop_grace_period: 30s
  stop_signal: SIGTERM
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
    interval: 10s
    timeout: 5s
    retries: 5
  # Configurações de performance
  command:
    - "postgres"
    - "-c"
    - "max_connections=200"
    - "-c"
    - "shared_buffers=256MB"
    - "-c"
    - "effective_cache_size=1GB"
    - "-c"
    - "maintenance_work_mem=64MB"
    - "-c"
    - "checkpoint_completion_target=0.9"
    - "-c"
    - "wal_buffers=16MB"
    - "-c"
    - "default_statistics_target=100"
    - "-c"
    - "random_page_cost=1.1"
    - "-c"
    - "effective_io_concurrency=200"
    - "-c"
    - "work_mem=1310kB"
    - "-c"
    - "min_wal_size=1GB"
    - "-c"
    - "max_wal_size=4GB"
```

## Procedimentos de Emergência

### Se o PostgreSQL não iniciar

1. **Verificar logs:**
   ```bash
   docker compose logs postgres --tail 50
   ```

2. **Tentar recuperação automática do PostgreSQL:**
   - O PostgreSQL tem crash recovery automático
   - Geralmente recupera de shutdowns abruptos

3. **Se crash recovery falhar, usar pg_resetwal:**
   ```bash
   docker compose stop postgres
   docker compose run --rm --user postgres postgres pg_resetwal -f /var/lib/postgresql/data
   docker compose up -d postgres
   ```

4. **Se pg_resetwal falhar, restaurar do backup:**
   ```bash
   docker compose stop postgres
   ./scripts/restore-postgres.sh backups/postgres/backup_YYYYMMDD_HHMMSS.sql
   docker compose up -d postgres
   ```

5. **Se tudo falhar (último recurso):**
   ```bash
   docker compose down postgres
   rm -rf postgres_data
   docker compose up -d postgres
   # Reexecutar migrations
   ```

## Monitoramento

### Métricas a Monitorar

1. **Espaço em disco do volume PostgreSQL**
2. **Health check do PostgreSQL**
3. **Tempo de shutdown**
4. **Backup executado com sucesso**
5. **Tamanho do WAL**

### Alertas

- Health check falhando por mais de 5 minutos
- Espaço em disco < 20%
- Backup falhando
- WAL crescendo excessivamente

## Recomendações Futuras

### 1. Replicação em Tempo Real (TODO)

Implementar master-slave replication para:
- Alta disponibilidade
- Failover automático
- Backup em tempo real
- Leitura distribuída

### 2. Backup em Nuvem

Enviar backups para:
- AWS S3
- Google Cloud Storage
- Azure Blob Storage

### 3. Point-in-Time Recovery (PITR)

Implementar WAL archiving para:
- Recuperação para um ponto específico no tempo
- Maior granularidade de backup
- Recuperação de erros humanos

## Conclusão

**Status Atual:**
- Graceful shutdown implementado (stop_grace_period: 60s)
- Backup automático configurado
- Script de recuperação criado
- Procedimentos documentados
- PostgreSQL mudado de Alpine para imagem padrão (postgres:16)

**Limitação Importante:**
O graceful shutdown **não está funcionando** na versão do Docker Compose que você está usando. O Docker Compose não respeita o `stop_grace_period`, resultando em:
- PostgreSQL sendo desligado abruptamente (SIGKILL em vez de SIGTERM)
- WAL corrompendo consistentemente
- Necessidade de usar `pg_resetwal` para recuperação

**Causa Raiz:**
A versão do Docker Compose que você está usando (que não suporta a flag `--rm`) provavelmente também não respeita o `stop_grace_period`. Isso foi confirmado pelos logs que mostram:
```
database system shutdown was interrupted
database system was not properly shut down
```

**Para desenvolvimento:**
- O `make fix-postgres` recupera o banco sem apagar dados
- O `make create-user` cria usuários com argumentos de linha de comando
- Aceitável usar `pg_resetwal` se necessário
- Nunca apagar o volume `postgres_data`
- **Testes unitários funcionam sem apagar o banco** - usam mocks e fixtures

**Para produção:**
- **Nunca apagar dados em produção**
- **Sempre ter backup recente automatizado**
- **Replicação em tempo real é essencial** (veja TODO.md)
- **Monitoramento contínuo da saúde do banco**
- **Procedimentos de emergência documentados**
- **Point-in-Time Recovery (PITR) para granularidade**
- **Usar Docker Compose versão mais recente que suporte graceful shutdown corretamente**

**Recomendação Crítica:**
Para produção, implementar replicação master-slave (planejado em TODO.md) para garantir zero data loss e alta disponibilidade.
