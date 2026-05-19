# Guia de Auditoria - Como Verificar Logs de Acesso

## Schema Atual (Limitado)

### Verificar todas as queries
```sql
-- Ver todas as queries realizadas
SELECT 
    id,
    question,
    LEFT(answer, 100) as answer_preview,
    sources,
    elapsed_ms,
    llm_provider,
    llm_model,
    tokens_total,
    created_at
FROM queries
ORDER BY created_at DESC;
```

### Estatísticas básicas
```sql
-- Estatísticas gerais
SELECT 
    COUNT(*) as total_queries,
    COUNT(DISTINCT DATE(created_at)) as dias_ativos,
    MIN(created_at) as primeira_query,
    MAX(created_at) as ultima_query,
    AVG(elapsed_ms) as tempo_medio_ms,
    SUM(tokens_total) as total_tokens
FROM queries;
```

### Queries por modelo
```sql
-- Queries por modelo de LLM
SELECT 
    llm_provider,
    llm_model,
    COUNT(*) as total_queries,
    AVG(elapsed_ms) as tempo_medio_ms,
    SUM(tokens_total) as total_tokens
FROM queries
GROUP BY llm_provider, llm_model
ORDER BY total_queries DESC;
```

### Queries por período
```sql
-- Queries por dia
SELECT 
    DATE(created_at) as dia,
    COUNT(*) as total_queries,
    AVG(elapsed_ms) as tempo_medio_ms
FROM queries
GROUP BY DATE(created_at)
ORDER BY dia DESC;
```

### Queries lentas
```sql
-- Queries que demoraram mais de 10 segundos
SELECT 
    question,
    elapsed_ms,
    llm_model,
    created_at
FROM queries
WHERE elapsed_ms > 10000
ORDER BY elapsed_ms DESC;
```

### Verificar via Docker
```bash
# Acessar o banco
docker compose exec postgres psql -U rag -d ragdb

# Ou executar query direto
docker compose exec postgres psql -U rag -d ragdb -c "SELECT * FROM queries ORDER BY created_at DESC LIMIT 10;"
```

---

## Schema Melhorado (Enterprise)

Após aplicar o schema `db/schema-auditoria-enterprise.sql`, você terá auditoria completa.

### 1. Verificar todos os acessos (audit_log)
```sql
-- Todos os acessos recentes
SELECT 
    al.created_at,
    al.action_type,
    al.resource_type,
    al.resource_id,
    al.user_email,
    u.department,
    al.ip_address,
    al.success,
    al.error_message
FROM audit_log al
LEFT JOIN users u ON al.user_id = u.id
ORDER BY al.created_at DESC
LIMIT 50;
```

### 2. Acessos por usuário
```sql
-- Atividade de um usuário específico
SELECT 
    u.email,
    u.name,
    u.department,
    COUNT(q.id) as total_queries,
    COALESCE(SUM(q.tokens_total), 0) as total_tokens,
    ROUND(AVG(q.elapsed_ms)::NUMERIC, 2) as avg_elapsed_ms,
    MIN(q.created_at) as first_query,
    MAX(q.created_at) as last_query
FROM users u
LEFT JOIN queries q ON u.id = q.user_id
WHERE u.email = 'dev1@empresa.com'
GROUP BY u.id, u.email, u.name, u.department;
```

### 3. Acessos por departamento
```sql
-- Estatísticas por departamento
SELECT 
    q.user_department,
    COUNT(DISTINCT q.user_id) as usuarios_ativos,
    COUNT(q.id) as total_queries,
    COALESCE(SUM(q.tokens_total), 0) as total_tokens,
    ROUND(AVG(q.elapsed_ms)::NUMERIC, 2) as avg_elapsed_ms,
    MIN(q.created_at) as first_query,
    MAX(q.created_at) as last_query
FROM queries q
WHERE q.user_department IS NOT NULL
GROUP BY q.user_department
ORDER BY total_queries DESC;
```

### 4. Documentos mais acessados
```sql
-- Documentos mais acessados (últimos 30 dias)
SELECT 
    d.file_name,
    d.department,
    d.sensitivity_level,
    COUNT(dal.id) as access_count,
    COUNT(DISTINCT dal.user_id) as unique_users,
    MAX(dal.created_at) as last_accessed
FROM documents d
JOIN document_access_log dal ON d.id = dal.document_id
WHERE dal.created_at >= NOW() - INTERVAL '30 days'
GROUP BY d.id, d.file_name, d.department, d.sensitivity_level
ORDER BY access_count DESC
LIMIT 20;
```

### 5. Usando as funções de auditoria
```sql
-- Estatísticas de um usuário
SELECT * FROM get_user_stats(
    (SELECT id FROM users WHERE email = 'dev1@empresa.com')
);

-- Estatísticas de um departamento
SELECT * FROM get_department_stats('Game Development');

-- Documentos mais acessados
SELECT * FROM get_most_accessed_documents(10, 30);

-- Detectar acessos anômalos (mais de 100 acessos em 1 hora)
SELECT * FROM detect_anomalous_access(100, 60);
```

### 6. Usando as views de auditoria
```sql
-- Resumo de atividade por usuário
SELECT * FROM user_activity_summary
ORDER BY total_queries DESC
LIMIT 20;

-- Resumo de atividade por departamento
SELECT * FROM department_activity_summary
ORDER BY total_queries DESC;

-- Log de auditoria consolidado
SELECT * FROM audit_consolidated
WHERE action_type = 'query'
ORDER BY created_at DESC
LIMIT 50;
```

### 7. Histórico de configurações
```sql
-- Mudanças nas configurações
SELECT 
    sh.setting_key,
    sh.old_value,
    sh.new_value,
    sh.changed_by_email,
    sh.changed_at,
    sh.reason
FROM settings_history sh
ORDER BY sh.changed_at DESC
LIMIT 50;
```

### 8. Acessos a documentos sensíveis
```sql
-- Acessos a documentos confidenciais
SELECT 
    d.file_name,
    d.sensitivity_level,
    dal.user_email,
    dal.user_department,
    dal.access_type,
    dal.ip_address,
    dal.created_at
FROM document_access_log dal
JOIN documents d ON dal.document_id = d.id
WHERE d.sensitivity_level IN ('confidential', 'restricted')
ORDER BY dal.created_at DESC
LIMIT 50;
```

### 9. Detectar acessos não autorizados
```sql
-- Tentativas de acesso que falharam
SELECT 
    al.user_email,
    al.action_type,
    al.resource_type,
    al.ip_address,
    al.error_message,
    al.created_at
FROM audit_log al
WHERE al.success = false
ORDER BY al.created_at DESC
LIMIT 50;
```

### 10. Auditoria por período
```sql
-- Acessos nas últimas 24 horas
SELECT 
    DATE_TRUNC('hour', al.created_at) as hora,
    al.action_type,
    COUNT(*) as total
FROM audit_log al
WHERE al.created_at >= NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', al.created_at), al.action_type
ORDER BY hora DESC, total DESC;
```

---

## Ferramentas de Visualização

### Via Terminal (psql)
```bash
# Conectar ao banco
docker compose exec postgres psql -U rag -d ragdb

# Executar queries interativamente
\c ragdb
SELECT * FROM audit_log ORDER BY created_at DESC LIMIT 20;

# Exportar para CSV
\copy (SELECT * FROM queries ORDER BY created_at DESC) TO '/tmp/queries.csv' CSV HEADER
```

### Via Python (script)
```python
import psycopg2
import pandas as pd

# Conectar ao banco
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="ragdb",
    user="rag",
    password="rag"
)

# Query e converter para DataFrame
df = pd.read_sql_query("""
    SELECT * FROM queries 
    ORDER BY created_at DESC 
    LIMIT 100
""", conn)

# Exibir
print(df.head())

# Exportar para CSV
df.to_csv('auditoria_queries.csv', index=False)

conn.close()
```

### Via Grafana (Dashboard)
1. Instalar Grafana
2. Configurar datasource PostgreSQL
3. Criar dashboard com os queries acima
4. Adicionar alertas para acessos anômalos

---

## Relatórios de Auditoria Comuns

### Relatório Diário de Uso
```sql
-- Resumo do dia
SELECT 
    DATE(created_at) as dia,
    COUNT(*) as total_queries,
    COUNT(DISTINCT user_id) as usuarios_unicos,
    AVG(elapsed_ms) as tempo_medio_ms,
    SUM(tokens_total) as total_tokens
FROM queries
WHERE DATE(created_at) = CURRENT_DATE
GROUP BY DATE(created_at);
```

### Relatório Semanal por Departamento
```sql
-- Atividade da última semana por departamento
SELECT 
    user_department,
    COUNT(*) as total_queries,
    COUNT(DISTINCT user_id) as usuarios_unicos,
    SUM(tokens_total) as total_tokens,
    AVG(elapsed_ms) as tempo_medio_ms
FROM queries
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY user_department
ORDER BY total_queries DESC;
```

### Relatório de Documentos Sensíveis Acessados
```sql
-- Documentos confidenciais acessados na última semana
SELECT 
    d.file_name,
    d.sensitivity_level,
    COUNT(dal.id) as access_count,
    COUNT(DISTINCT dal.user_id) as unique_users
FROM document_access_log dal
JOIN documents d ON dal.document_id = d.id
WHERE d.sensitivity_level = 'confidential'
  AND dal.created_at >= NOW() - INTERVAL '7 days'
GROUP BY d.file_name, d.sensitivity_level
ORDER BY access_count DESC;
```

### Relatório de Acessos Anômalos
```sql
-- Usuários com atividade suspeita
SELECT * FROM detect_anomalous_access(100, 60);
```

---

## Aplicar o Schema Melhorado

```bash
# Aplicar o schema de auditoria enterprise
docker compose exec postgres psql -U rag -d ragdb -f db/schema-auditoria-enterprise.sql

# Verificar se as tabelas foram criadas
docker compose exec postgres psql -U rag -d ragdb -c "\dt"

# Verificar as novas tabelas
docker compose exec postgres psql -U rag -d ragdb -c "\d audit_log"
docker compose exec postgres psql -U rag -d ragdb -c "\d users"
docker compose exec postgres psql -U rag -d ragdb -c "\d documents"
```

---

## Automatização de Relatórios

### Script Python para Relatório Diário
```python
import psycopg2
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

def generate_daily_report():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="ragdb",
        user="rag",
        password="rag"
    )
    
    cursor = conn.cursor()
    
    # Queries do dia
    cursor.execute("""
        SELECT 
            COUNT(*) as total_queries,
            COUNT(DISTINCT user_id) as usuarios_unicos,
            AVG(elapsed_ms) as tempo_medio_ms,
            SUM(tokens_total) as total_tokens
        FROM queries
        WHERE DATE(created_at) = CURRENT_DATE
    """)
    
    stats = cursor.fetchone()
    
    # Acessos anômalos
    cursor.execute("SELECT * FROM detect_anomalous_access(100, 60)")
    anomalous = cursor.fetchall()
    
    conn.close()
    
    # Gerar relatório
    report = f"""
    Relatório Diário de Auditoria - {datetime.now().strftime('%d/%m/%Y')}
    
    Estatísticas:
    - Total de queries: {stats[0]}
    - Usuários únicos: {stats[1]}
    - Tempo médio: {stats[2]:.2f}ms
    - Total de tokens: {stats[3]}
    
    Acessos Anômalos: {len(anomalous)}
    """
    
    return report

# Enviar por email (configurar SMTP)
def send_email_report(report):
    msg = MIMEText(report)
    msg['Subject'] = 'Relatório Diário de Auditoria RAG'
    msg['From'] = 'auditoria@empresa.com'
    msg['To'] = 'security@empresa.com'
    
    # Configurar SMTP e enviar
    # with smtplib.SMTP('smtp.empresa.com') as server:
    #     server.send_message(msg)
    
    print(report)

if __name__ == '__main__':
    report = generate_daily_report()
    send_email_report(report)
```

---

## Alertas Automáticos

### Configurar alerta no PostgreSQL
```sql
-- Criar função para alertar sobre acessos anômalos
CREATE OR REPLACE FUNCTION check_anomalous_access()
RETURNS INTEGER AS $$
DECLARE
    anomalous_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO anomalous_count
    FROM detect_anomalous_access(100, 60);
    
    IF anomalous_count > 0 THEN
        -- Aqui você pode integrar com sistema de notificações
        -- Slack, email, etc.
        RAISE NOTICE 'ALERTA: % acessos anômalos detectados', anomalous_count;
    END IF;
    
    RETURN anomalous_count;
END;
$$ LANGUAGE plpgsql;

-- Executar check a cada hora
-- (configurar via pg_cron ou job externo)
```

---

## Checklist de Auditoria

### Diariamente
- [ ] Verificar acessos anômalos
- [ ] Revisar documentos sensíveis acessados
- [ ] Checar tentativas de acesso falhadas
- [ ] Gerar relatório de uso

### Semanalmente
- [ ] Analisar tendências de uso por departamento
- [ ] Revisar usuários inativos
- [ ] Verificar performance do sistema
- [ ] Revisar mudanças de configuração

### Mensalmente
- [ ] Relatório completo de auditoria
- [ ] Revisar políticas de retenção
- [ ] Atualizar lista de usuários
- [ ] Verificar compliance LGPD

### Trimestralmente
- [ ] Auditoria de segurança completa
- [ ] Revisar e atualizar políticas
- [ ] Testar procedimentos de backup/restore
- [ ] Revisar logs de acesso

---

## Exemplos Práticos

### Exemplo 1: Verificar quem acessou um documento específico
```sql
-- Acessos ao documento "contrato_vendedor.pdf"
SELECT 
    dal.user_email,
    dal.user_department,
    dal.access_type,
    dal.ip_address,
    dal.created_at
FROM document_access_log dal
JOIN documents d ON dal.document_id = d.id
WHERE d.file_name = 'contrato_vendedor.pdf'
ORDER BY dal.created_at DESC;
```

### Exemplo 2: Verificar queries sobre um tema específico
```sql
-- Queries que mencionam "contrato"
SELECT 
    question,
    user_email,
    user_department,
    created_at
FROM queries
WHERE question ILIKE '%contrato%'
  OR answer ILIKE '%contrato%'
ORDER BY created_at DESC;
```

### Exemplo 3: Usuários mais ativos
```sql
-- Top 10 usuários mais ativos
SELECT 
    user_email,
    user_department,
    COUNT(*) as total_queries,
    MAX(created_at) as ultima_atividade
FROM queries
WHERE user_email IS NOT NULL
GROUP BY user_email, user_department
ORDER BY total_queries DESC
LIMIT 10;
```

### Exemplo 4: Horários de pico de uso
```sql
-- Queries por hora do dia
SELECT 
    EXTRACT(HOUR FROM created_at) as hora,
    COUNT(*) as total_queries
FROM queries
GROUP BY EXTRACT(HOUR FROM created_at)
ORDER BY hora;
```

### Exemplo 5: Documentos nunca acessados
```sql
-- Documentos indexados mas nunca acessados
SELECT 
    d.file_name,
    d.department,
    d.indexed_at
FROM documents d
LEFT JOIN document_access_log dal ON d.id = dal.document_id
WHERE d.is_active = true
  AND dal.id IS NULL
ORDER BY d.indexed_at DESC;
```

---

## Exportação de Logs

### Exportar para CSV
```bash
# Exportar todas as queries
docker compose exec postgres psql -U rag -d ragdb -c "\copy (SELECT * FROM queries ORDER BY created_at DESC) TO '/tmp/queries.csv' CSV HEADER"

# Exportar logs de auditoria
docker compose exec postgres psql -U rag -d ragdb -c "\copy (SELECT * FROM audit_log ORDER BY created_at DESC) TO '/tmp/audit_log.csv' CSV HEADER"

# Copiar do container para host
docker compose exec postgres cat /tmp/queries.csv > queries.csv
```

### Exportar para JSON
```sql
-- Exportar como JSON
COPY (
    SELECT json_agg(t)
    FROM (
        SELECT * FROM queries ORDER BY created_at DESC LIMIT 100
    ) t
) TO '/tmp/queries.json';
```

---

## Integração com SIEM

### Enviar logs para Elasticsearch/ELK
```python
import psycopg2
import requests
import json

def send_logs_to_elk():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="ragdb",
        user="rag",
        password="rag"
    )
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM audit_log 
        WHERE created_at > NOW() - INTERVAL '1 hour'
    """)
    
    for row in cursor:
        log = {
            'timestamp': row[9].isoformat(),
            'action_type': row[1],
            'resource_type': row[2],
            'resource_id': row[3],
            'user_email': row[4],
            'ip_address': str(row[6]),
            'success': row[7]
        }
        
        requests.post(
            'http://elasticsearch:9200/rag-audit/_doc',
            json=log
        )
    
    conn.close()
```

---

## Referências

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [LGPD - Lei 13.709/2018](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- [ISO 27001](https://www.iso.org/standard/27001)
