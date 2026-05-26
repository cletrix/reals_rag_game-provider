# TODO - RAG Game Provider

## Prioridade Alta

### Sistema de Autenticação
- [x] Implementar autenticação com email
- [x] Implementar hash de senhas com bcrypt
- [x] Criar endpoints de autenticação
- [x] Criar testes unitários de autenticação
- [x] Criar script de criação de usuários
- [x] Documentar sistema de autenticação

### PostgreSQL - Recuperação de Corrupção
- [x] Documentar erro de corrupção do PostgreSQL
- [x] Implementar graceful shutdown
- [x] Implementar recuperação com pg_resetwal
- [x] Criar scripts de backup e restore
- [x] Adicionar targets ao Makefile

## Prioridade Média

### Arquitetura
- [x] Análise arquitetural do projeto
- [x] Avaliar necessidade de microserviços (não necessário)
- [ ] Refatorar main.py em módulos de rotas
- [ ] Refatorar db.py em módulos de acesso ao banco
- [ ] Refatorar schemas.py em módulos de schemas

### Backup e Recuperação
- [ ] Configurar backup automático com cron job
- [ ] Implementar backup em nuvem (S3/GCS/Azure)
- [ ] Implementar Point-in-Time Recovery (PITR)
- [ ] Configurar alertas de backup

## Prioridade Baixa

### Replicação em Tempo Real (Futuro)

**Objetivo:** Implementar replicação master-slave do PostgreSQL para alta disponibilidade e backup em tempo real.

**Benefícios:**
- Alta disponibilidade
- Failover automático
- Backup em tempo real
- Leitura distribuída
- Zero downtime durante manutenção

**Implementação Planejada:**

1. **Configuração Master-Slave**
   - PostgreSQL master (escrita e leitura)
   - PostgreSQL slave (apenas leitura)
   - Replicação streaming em tempo real
   - WAL shipping automático

2. **Arquitetura:**
   ```
   docker-compose.prod.yml:
   postgres-master:
     - Porta 5432
     - Escrita + Leitura
     - Primary database
   
   postgres-slave:
     - Porta 5433
     - Apenas leitura
     - Replicação em tempo real do master
   ```

3. **Configuração:**
   - `wal_level = replica`
   - `max_wal_senders = 5`
   - `wal_keep_size = 1GB`
   - `hot_standby = on`
   - `max_replication_slots = 5`

4. **Failover Automático:**
   - Usar repmgr ou pg_auto_failover
   - Detecção automática de falha
   - Promoção automática de slave para master
   - Virtual IP ou DNS para roteamento

5. **Monitoramento:**
   - Lag de replicação
   - Status de replicação
   - Health checks
   - Alertas de falha

**Tempo Estimado:** 3-5 dias

**Dependências:**
- Infraestrutura com 2 servidores
- Balanceador de carga
- Monitoramento configurado

**Referências:**
- PostgreSQL Streaming Replication
- repmgr - PostgreSQL Replication Manager
- pg_auto_failover

### Performance
- [ ] Otimizar consultas do PostgreSQL
- [ ] Adicionar índices necessários
- [ ] Configurar connection pooling (PgBouncer)
- [ ] Implementar cache (Redis)

### Segurança
- [ ] Implementar rate limiting por usuário
- [ ] Adicionar rate limiting por endpoint
- [ ] Implementar CORS apropriado
- [ ] Adicionar HTTPS/TLS
- [ ] Implementar rotação de secrets

### Monitoramento
- [ ] Configurar Prometheus + Grafana
- [ ] Adicionar alertas de performance
- [ ] Monitorar uso de recursos
- [ ] Logs centralizados (ELK ou Loki)

### CI/CD
- [ ] Configurar pipeline de CI/CD
- [ ] Testes automáticos em cada commit
- [ ] Deploy automático em staging
- [ ] Deploy manual em produção

## Notas

- Sistema de autenticação está completo e funcional
- 23 testes de autenticação passando
- PostgreSQL configurado com graceful shutdown
- Scripts de backup/restore implementados
- Documentação de recuperação de corrupção criada
