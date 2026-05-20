# Sistema de Conversas - Resumo de Mudanças

## Problema Resolvido
Anteriormente, cada pergunta criava um novo item isolado no histórico. Agora, mensagens relacionadas são agrupadas em **conversas/sessões**, mantendo contexto e organização.

## Arquivos Modificados

### 1. `db/init.sql`
- **Adicionado**: Tabela `conversations` para agrupar queries
- **Modificado**: Tabela `queries` com nova coluna `conversation_id` (FK)
- **Adicionado**: Índices para performance

### 2. `db/migration-add-conversations.sql` (NOVO)
- Script de migração para bancos existentes
- Preserva dados existentes (opcional)

### 3. `web/db.py`
- **Novas funções**:
  - `create_conversation()` - Cria nova conversa
  - `get_conversation()` - Busca dados da conversa
  - `get_conversations()` - Lista conversas com contagem de mensagens
  - `get_conversation_messages()` - Busca todas mensagens de uma conversa
  - `update_conversation_timestamp()` - Atualiza timestamp
  - `update_conversation_title()` - Atualiza título
- **Modificado**: `save_query()` agora aceita `conversation_id` e retorna `(query_id, conversation_id)`

### 4. `web/main.py`
- **Novos endpoints**:
  - `GET /api/conversations` - Lista conversas
  - `POST /api/conversations` - Cria nova conversa
  - `GET /api/conversations/{id}` - Dados da conversa
  - `GET /api/conversations/{id}/messages` - Mensagens da conversa
  - `PATCH /api/conversations/{id}` - Atualiza conversa
- **Modificado**: `POST /chat/stream` aceita `conversation_id` no body

### 5. `web/templates/index.html`
- **Novos estados**: `conversations[]`, `currentConversationId`
- **Novas funções**:
  - `loadConversations()` - Carrega lista de conversas
  - `loadConversation(id)` - Carrega thread completa
- **Modificado**:
  - `newChat()` - Reseta `currentConversationId` para criar nova conversa
  - `sendMessage()` - Envia `conversation_id` no payload
  - Sidebar mostra conversas agrupadas com contagem de mensagens

## Fluxo de Funcionamento

### 1. Nova Conversa
```
Usuário clica "Nova conversa"
  ↓
Frontend: messages=[], currentConversationId=null
  ↓
Interface limpa, pronta para nova sessão
```

### 2. Primeira Mensagem
```
Usuário envia mensagem (conversation_id=null)
  ↓
Backend detecta null → cria nova conversa
  ↓
Título = truncate(pergunta, 50)
  ↓
Salva query com novo conversation_id
  ↓
Retorna conversation_id na resposta SSE
  ↓
Frontend atualiza currentConversationId
```

### 3. Continuidade
```
Usuário envia mensagem (conversation_id=xxx)
  ↓
Backend salva na mesma conversa
  ↓
Atualiza timestamp da conversa
  ↓
Recarrega lista de conversas (ordenação por updated_at)
```

### 4. Carregar Histórico
```
Usuário clica conversa no sidebar
  ↓
Frontend: GET /api/conversations/{id}/messages
  ↓
Popula messages[] com toda a thread
  ↓
Seta currentConversationId = id
```

## API Endpoints

### Conversas
```
GET    /api/conversations              → Lista conversas (com message_count)
POST   /api/conversations              → Cria nova conversa (body: {title})
GET    /api/conversations/{id}          → Dados da conversa
GET    /api/conversations/{id}/messages → Todas mensagens da conversa
PATCH  /api/conversations/{id}        → Atualiza título (body: {title})
```

### Chat (modificado)
```
POST   /chat/stream
  Body: {
    "question": "...",
    "conversation_id": "uuid-ou-null"
  }
  Response SSE: {
    "type": "done",
    "query_id": "...",
    "conversation_id": "..."  // NOVO
  }
```

## Deploy no Servidor

### 1. Subir código
```bash
git pull
# ou copiar arquivos modificados
```

### 2. Aplicar migração do banco
```bash
docker compose exec postgres psql -U rag -d ragdb -f db/migration-add-conversations.sql
```

### 3. Reiniciar containers
```bash
docker compose down
docker compose up -d
```

### 4. Verificar
```bash
# Verificar se tabela foi criada
docker compose exec postgres psql -U rag -d ragdb -c "\dt"

# Verificar coluna
docker compose exec postgres psql -U rag -d ragdb -c "\d queries"
```

## Testes de Validação

1. ✅ **Nova Conversa**: "Nova conversa" → interface limpa → enviar mensagem → nova sessão criada
2. ✅ **Continuidade**: Enviar 3 mensagens → verificar mesmo `conversation_id` no banco
3. ✅ **Histórico Agrupado**: Sidebar mostra 1 item por conversa, não queries individuais
4. ✅ **Carregar Conversa**: Clicar no histórico → carrega todas mensagens da thread
5. ✅ **Contexto Novo**: "Nova conversa" → enviar mensagem → cria sessão diferente
6. ✅ **Persistência**: Recarregar página → histórico mantém agrupamento correto

## Comportamento Esperado na UI

### Sidebar
- Mostra **"Conversas"** (não "Histórico")
- Cada item: título + contagem de mensagens (ex: "Configurar ambiente... (3)")
- Conversa ativa destacada em cinza (`bg-gray-700`)
- Ordenado por `updated_at` DESC (mais recente no topo)

### Chat
- Nova conversa: interface limpa, sem mensagens
- Enviar mensagem: aparece imediatamente + streaming da resposta
- Múltiplas mensagens: todas aparecem na thread (pergunta + resposta alternados)
- Fontes: cada resposta mostra documentos usados

### Estados do Alpine.js
```javascript
conversations: []           // Lista de conversas para sidebar
currentConversationId: null  // null = nova conversa, uuid = sessão ativa
messages: []                // Mensagens da conversa atual
```

## Observações

- **Backward Compatible**: Endpoints antigos (`/api/history`, `/api/query/{id}`) mantidos
- **Dados existentes**: Script de migração opcional para converter queries individuais em conversas
- **Performance**: Índices adicionados para queries eficientes por conversation_id
- **Cascata**: `ON DELETE CASCADE` na FK - deletar conversa remove todas mensagens
