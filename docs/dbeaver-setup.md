# Configuração do DBeaver para PostgreSQL

Este guia explica como configurar o DBeaver para conectar ao banco de dados PostgreSQL do projeto RAG Game Provider, tanto localmente quanto de outra máquina.

## Pré-requisitos

- DBeaver instalado (https://dbeaver.io/download/)
- Docker Compose rodando com o serviço PostgreSQL
- Senha do banco de dados (padrão: `rag`)

## Conexão Local (localhost)

### 1. Iniciar o PostgreSQL

Certifique-se de que o PostgreSQL está rodando:

```bash
docker compose up -d postgres
```

Verifique se está saudável:

```bash
docker compose ps postgres
```

### 2. Abrir o DBeaver

Abra o DBeaver e clique em **Database** → **New Database Connection**.

### 3. Selecionar PostgreSQL

Na lista de drivers, selecione **PostgreSQL** e clique em **Next**.

### 4. Configurar a Conexão

Preencha os campos conforme abaixo:

**Geral:**
- **Host:** `localhost`
- **Port:** `5432`
- **Database:** `ragdb`
- **Username:** `rag`
- **Password:** `rag`

**Avançado (opcional):**
- **URL JDBC:** `jdbc:postgresql://localhost:5432/ragdb`

### 5. Testar a Conexão

Clique em **Test Connection**. Se tudo estiver correto, você verá:

```
Connection successful
```

### 6. Salvar a Conexão

Clique em **Finish** para salvar a conexão. Dê um nome como `RAG Local`.

## Conexão Remota (de outra máquina)

### 1. Expor a Porta do PostgreSQL

Por padrão, o PostgreSQL só é acessível via Docker network. Para acessar de outra máquina, você precisa expor a porta.

**Opção A: Modificar docker-compose.yml (permanente)**

Edite `docker-compose.yml` e adicione o mapeamento de portas:

```yaml
postgres:
  ports:
    - "5432:5432"  # Adicione esta linha
```

Reinicie o serviço:

```bash
docker compose up -d postgres
```

**Opção B: Port forwarding temporário**

```bash
docker compose port postgres 5432
```

### 2. Obter o IP do Host

No Linux/Mac:
```bash
ifconfig | grep "inet "
```

No Windows:
```bash
ipconfig
```

Anote o endereço IP (ex: `192.168.1.100`).

### 3. Configurar o DBeaver

Siga os mesmos passos da conexão local, mas altere:

**Geral:**
- **Host:** `<IP_DO_HOST>` (ex: `192.168.1.100`)
- **Port:** `5432`
- **Database:** `ragdb`
- **Username:** `rag`
- **Password:** `rag`

### 4. Testar a Conexão

Clique em **Test Connection**. Se falhar, verifique:

- O firewall do host permite conexões na porta 5432
- O PostgreSQL está aceitando conexões externas
- O IP está correto

## Configuração Avançada do PostgreSQL

### Habilitar Acesso Remoto no PostgreSQL

Se a conexão remota falhar, você pode precisar configurar o PostgreSQL para aceitar conexões externas.

#### 1. Editar pg_hba.conf

```bash
docker compose exec postgres bash
cd /etc/postgresql/16/main
echo "host all all 0.0.0.0/0 md5" >> pg_hba.conf
exit
```

#### 2. Reiniciar o PostgreSQL

```bash
docker compose restart postgres
```

## Estrutura do Banco de Dados

Após conectar, você verá as seguintes tabelas:

### Tabela `conversations`
Armazena conversas do sistema de chat.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | Chave primária |
| title | VARCHAR(255) | Título da conversa |
| message_count | INT | Número de mensagens |
| created_at | TIMESTAMPTZ | Data de criação |
| updated_at | TIMESTAMPTZ | Data de atualização |

### Tabela `queries`
Armazena histórico de perguntas e respostas.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | Chave primária |
| conversation_id | UUID | FK para conversations |
| question | TEXT | Pergunta do usuário |
| answer | TEXT | Resposta do LLM |
| sources | JSONB | Documentos citados |
| elapsed_ms | INT | Tempo de resposta |
| llm_provider | VARCHAR | groq / ollama |
| llm_model | VARCHAR | Nome do modelo |
| tokens_total | INT | Tokens consumidos |
| created_at | TIMESTAMPTZ | Timestamp |

### Tabela `folders`
Armazena pastas de documentos.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | Chave primária |
| name | VARCHAR(255) | Nome da pasta |
| path | TEXT | Caminho no filesystem |
| size_bytes | BIGINT | Tamanho total |
| file_count | INT | Número de arquivos |
| indexed_at | TIMESTAMPTZ | Última indexação |
| auto_index | BOOLEAN | Auto-index habilitado |
| created_at | TIMESTAMPTZ | Data de criação |
| updated_at | TIMESTAMPTZ | Data de atualização |

### Tabela `documents`
Armazena documentos dentro de pastas.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | Chave primária |
| folder_id | UUID | FK para folders |
| name | VARCHAR(255) | Nome do arquivo |
| path | TEXT | Caminho completo |
| size_bytes | BIGINT | Tamanho do arquivo |
| indexed | BOOLEAN | Está indexado |
| indexed_at | TIMESTAMPTZ | Data de indexação |
| mtime | TIMESTAMPTZ | Modificação do arquivo |
| created_at | TIMESTAMPTZ | Data de criação |
| updated_at | TIMESTAMPTZ | Data de atualização |

### Tabela `settings`
Armazena configurações dinâmicas.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| key | VARCHAR(100) | Chave da configuração |
| value | TEXT | Valor da configuração |

## Queries Úteis

### Ver todas as conversas

```sql
SELECT id, title, message_count, created_at 
FROM conversations 
ORDER BY updated_at DESC;
```

### Ver queries de uma conversa

```sql
SELECT question, answer, elapsed_ms, llm_model 
FROM queries 
WHERE conversation_id = 'UUID_DA_CONVERSA'
ORDER BY created_at;
```

### Ver pastas com auto-index

```sql
SELECT id, name, file_count, auto_index 
FROM folders 
WHERE auto_index = true;
```

### Ver documentos não indexados

```sql
SELECT d.name, d.path, f.name as folder_name
FROM documents d
JOIN folders f ON d.folder_id = f.id
WHERE d.indexed = false;
```

### Estatísticas de uso

```sql
SELECT 
    llm_provider,
    llm_model,
    COUNT(*) as total_queries,
    AVG(elapsed_ms) as avg_time_ms,
    SUM(tokens_total) as total_tokens
FROM queries
GROUP BY llm_provider, llm_model;
```

## Solução de Problemas

### Erro: "Connection refused"

- Verifique se o PostgreSQL está rodando: `docker compose ps postgres`
- Verifique se a porta 5432 está exposta
- Tente conectar via psql: `docker compose exec postgres psql -U rag ragdb`

### Erro: "FATAL: password authentication failed"

- Verifique a senha no `.env` ou `docker-compose.yml`
- A senha padrão é `rag`

### Erro: "FATAL: no pg_hba.conf entry"

- O PostgreSQL não está configurado para aceitar conexões externas
- Siga a seção "Habilitar Acesso Remoto"

### Erro: "Timeout"

- Verifique o firewall do host
- Verifique se o IP está correto
- Tente pingar o host: `ping <IP_DO_HOST>`

## Exportar Dados

### Exportar para CSV

No DBeaver:
1. Clique com botão direito na tabela
2. Selecione **Export Data**
3. Escolha **CSV**
4. Configure as opções e clique em **Next**

### Exportar Schema

1. Clique com botão direito no banco de dados
2. Selecione **Generate SQL**
3. Escolha **DDL**
4. Salve o arquivo SQL

## Segurança

### Alterar Senha Padrão

Para produção, altere a senha padrão:

```bash
docker compose exec postgres psql -U rag ragdb
ALTER USER rag WITH PASSWORD 'nova_senha_segura';
\q
```

Atualize o `.env` e `docker-compose.yml` com a nova senha.

### Backup do Banco

```bash
docker compose exec postgres pg_dump -U rag ragdb > backup.sql
```

### Restore do Banco

```bash
docker compose exec -T postgres psql -U rag ragdb < backup.sql
```

## Recursos Adicionais

- [Documentação do DBeaver](https://dbeaver.io/docs/)
- [Documentação do PostgreSQL](https://www.postgresql.org/docs/)
- [Docker Compose PostgreSQL](https://hub.docker.com/_/postgres)
