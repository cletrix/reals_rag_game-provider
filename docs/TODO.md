# Plano de Implementação RAG Enterprise - Empresa de Games

**Empresa:** 50 funcionários  
**Departamentos:** Game Developers, Bets, Administração  
**Integrações:** Jira, Git, outros sistemas  
**Compliance:** LGPD, ISO 27001 (conforme necessário)

---

## 🚨 Próximas Prioridades (Sprint Atual)

| # | Tarefa | Impacto | Status |
|---|--------|---------|--------|
| 1 | Refatorar `main.py` em `web/routers/` por domínio | Alto — 1000 linhas, 37 endpoints, inviabiliza testes | 🔴 Pendente |
| 2 | Adicionar testes unitários (pytest) | Alto — zero cobertura atual | � Em andamento |
| 3 | CI/CD com GitHub Actions | Médio — deploy manual atualmente | 🔴 Pendente |
| 4 | Autenticação obrigatória nos endpoints | Alto — endpoints sem proteção JWT | ✅ Concluído |
| 5 | Configuração por ambiente (`.env.dev` / `.env.prod`) | Médio — único `.env` para tudo | 🔴 Pendente |

---

## Falhas Críticas e Melhorias Necessárias

**Status Atual:** ✅ Funcional, mas ❌ Ainda não Enterprise-ready

### 10 Falhas Críticas — Ordenadas por Prioridade

> Ordenação por impacto real: Segurança → Estrutura de código → Qualidade → Operacional

#### � P1. Autenticação e Autorização ✅
> **Impacto:** Crítico — **RESOLVIDO**: JWT obrigatório em todos os endpoints `/api/*` e `/chat/stream`
- [ ] Implementar OAuth2/LDAP
- [x] Adicionar JWT tokens
- [x] Configurar `Depends(get_current_user)` obrigatório em todos os endpoints protegidos (30 rotas)
- [x] Frontend envia `Authorization: Bearer` em todas as chamadas com redirecionamento automático 401
- [ ] Implementar RBAC por departamento

#### 🔴 P2. Refatoração de Estrutura (main.py) ⚠️
> **Impacto:** Alto — 1000 linhas, 37 endpoints num único arquivo, inviabiliza testes e manutenção
- [ ] Separar rotas em `web/routers/` por domínio (chat, auth, conversations, folders, health...)
- [ ] Criar `web/middleware.py` com middlewares isolados
- [ ] `main.py` deve ter apenas ~40 linhas (bootstrap)

#### � P3. Testes Automatizados ⚠️
> **Impacto:** Alto — testes unitários e de proteção JWT implementados; E2E pendente
- [x] Adicionar pytest com testes unitários (auth, conversations, health, settings, folders, schemas)
- [x] Testes de proteção JWT: todos os endpoints protegidos verificados com `test_protected_endpoints.py`
- [x] `pytest.ini` configurado com coverage mínimo 60%
- [x] Script `scripts/run_tests.sh` para rodar antes do deploy
- [x] Serviço `test` no `docker-compose.yml` com profile `--profile test`
- [ ] **Camada 1 — Pre-commit hook**: bloquear `git commit` se testes falharem (offline, instantâneo)
- [ ] **Camada 2 — GitHub Actions CI**: rodar testes em todo push/PR, bloquear merge se CI falhar
- [ ] Aumentar coverage para 80%
- [ ] Adicionar Playwright/Cypress para E2E

#### 🟠 P4. Falta de CI/CD ⚠️
> **Impacto:** Médio — deploy manual, sem validação automática
- [ ] **Criar `.github/workflows/ci.yml`**: pipeline test → build → deploy
- [ ] Bloquear merge de PR sem CI verde (branch protection rules no GitHub)
- [ ] Deploy automático para staging/produção
- [ ] Configurar notificações de build (Slack/email em falha)

#### 🟠 P5. Falta de Configuração por Ambiente ⚠️
> **Impacto:** Médio — único `.env` para dev e prod, risco de vazamento de credenciais
- [ ] Criar .env.dev, .env.staging, .env.prod
- [ ] Usar variáveis de ambiente por ambiente
- [ ] Documentar configurações
- [ ] Adicionar docker-compose.override.yml para dev

#### 🟠 P6. Falta de Tratamento de Erros Robusto ⚠️
> **Impacto:** Médio — error handlers globais existem, mas faltam retries e exceções customizadas
- [x] Implementar logging estruturado de erros
- [x] Adicionar error handlers globais
- [ ] Adicionar retry com exponential backoff
- [ ] Criar exceções customizadas por domínio

#### 🟡 P7. Falta de Validação de Input ⚠️
> **Impacto:** Médio — maioria concluída, 2 endpoints ainda usam request.json() raw
- [x] Adicionar Pydantic para validação
- [x] Sanitizar inputs de usuário
- [x] Adicionar rate limiting
- [x] Validar tamanho de inputs
- [ ] Corrigir `api_create_folder` e `api_update_folder` (ainda sem Pydantic)

#### 🟡 P8. Falta de Logging Estruturado ⚠️
> **Impacto:** Baixo — base implementada, falta configuração de alertas
- [x] Implementar logging estruturado (JSON)
- [x] Adicionar integração com Loki/ELK
- [x] Logar todas as ações críticas
- [ ] Configurar alertas baseados em logs

#### 🟢 P9. Falta de Health Checks Específicos ⚠️
> **Impacto:** Concluído ✅
- [x] Adicionar endpoint /health
- [x] Verificar dependências (Ollama, Qdrant)
- [x] Adicionar /readiness e /liveness
- [x] Configurar health checks no docker-compose

#### 🟢 P10. Falta de Documentação de API ⚠️
> **Impacto:** Concluído ✅
- [x] Adicionar FastAPI automatic docs (/docs)
- [x] Documentar todos os endpoints
- [x] Adicionar exemplos de requests/responses
- [x] Gerar OpenAPI spec
- [x] Criar documento docs/api-documentation.md

#### 🟠 P11. Falta de Backup Automatizado ⚠️
> **Impacto:** Alto para produção — sem backup, qualquer falha é perda de dados
- [ ] Implementar scripts de backup
- [ ] Configurar backup automatizado (cron)
- [ ] Testar restore regularmente
- [ ] Configurar retenção de backups

---

## Estrutura Organizacional

### Departamentos Principais

#### 1. Game Development (30-35 funcionários)
- **Game Designers:** Documentação de mecânicas, game docs, balanceamento
- **Programadores:** Código fonte, documentação técnica, APIs
- **Artistas:** Assets, conceitos, style guides, documentação de arte
- **QA:** Test cases, bug reports, planos de teste
- **Produção:** Roadmaps, sprints, cronogramas

#### 2. Bets/Apostas (10-12 funcionários)
- **Analistas de Odds:** Documentação de cálculos, algoritmos
- **Traders:** Regras de apostas, limites, compliance
- **Compliance:** Regulamentações, licenças, auditorias
- **Suporte:** FAQs, manuais de operação

#### 3. Administração (5-8 funcionários)
- **RH:** Políticas, contratos, treinamentos
- **Financeiro:** Relatórios, orçamentos, compliance fiscal
- **Legal:** Contratos, propriedade intelectual, termos de uso
- **TI/Infra:** Documentação técnica, procedimentos, SLAs

---

## Fases de Implementação

### Fase 1: Infraestrutura e Setup (Semanas 1-2)

**Objetivo:** Preparar infraestrutura robusta para produção

#### 1.1 Hardware e Servidor
- [ ] Avaliar necessidade de servidor dedicado vs cloud
- [ ] Configurar servidor com mínimo 32GB RAM (recomendado 64GB)
- [ ] Instalar Docker e Docker Compose em produção
- [ ] **Implementar Grafana para dashboard de auditoria** (ver seção "Dashboard de Auditoria")
- [ ] Configurar scripts de backup e restore (ver falha #10)

#### 1.2 Segurança Básica
- [ ] Configurar firewall (UFW/iptables)
- [ ] Configurar SSL/TLS (Let's Encrypt ou certificado próprio)
- [ ] Configurar VPN para acesso remoto
- [ ] **Aplicar schema de auditoria enterprise** (db/schema-auditoria-enterprise.sql)
- [ ] Implementar rate limiting (ver falha #4)
- [ ] Adicionar endpoint /health (ver falha #7)

#### 1.3 Compliance Inicial
- [ ] Documentar política de retenção de dados
- [ ] Configurar criptografia em repouso (discos)
- [ ] Configurar criptografia em trânsito (TLS)
- [ ] Estabelecer política de acesso por departamento

---

### Fase 2: Pilotagem - Game Development (Semanas 3-4)

**Objetivo:** Testar com um departamento menor antes de expandir

#### 2.1 Documentação Game Dev
- [ ] Mapear documentos existentes (Confluence, Google Docs, etc.)
- [ ] Categorizar por tipo: código, design, arte, QA
- [ ] Identificar documentos sensíveis (código fonte, IPs)
- [ ] Definir política de acesso para código fonte

#### 2.2 Indexação Inicial
- [ ] Indexar documentação não-sensível (game docs, FAQs)
- [ ] Configurar coleções separadas por departamento
- [ ] Testar qualidade das respostas
- [ ] Coletar feedback dos desenvolvedores

#### 2.3 Integração Git
- [ ] Configurar webhook do GitHub/GitLab
- [ ] Indexar READMEs e documentação de repositórios
- [ ] **NÃO indexar código fonte** (security risk)
- [ ] Indexar wikis e issues documentadas

#### 2.4 Avaliação
- [ ] Medir taxa de adoção (número de queries)
- [ ] Avaliar qualidade das respostas
- [ ] Identificar gaps de documentação
- [ ] Ajustar configurações do modelo

---

### Fase 3: Expansão - Bets/Apostas (Semanas 5-6)

**Objetivo:** Implementar para departamento de apostas com compliance rigoroso

#### 3.1 Documentação Bets
- [ ] Mapear documentos de regras e regulamentos
- [ ] Identificar documentos de compliance (licenças, auditorias)
- [ ] Categorizar documentos por sensibilidade
- [ ] Definir acesso restrito para compliance

#### 3.2 Segurança Adicional
- [ ] Implementar controle de acesso granular (RBAC - ver falha #3)
- [ ] Configurar auditoria de acessos (usar audit_log)
- [ ] Criar políticas de retenção específicas
- [ ] Implementar anonimização de dados pessoais (LGPD)
- [ ] Configurar alertas para acessos a documentos sensíveis
- [ ] Implementar logging estruturado (ver falha #5)

#### 3.3 Integração Jira
- [ ] Configurar integração com Jira
- [ ] Indexar tickets documentados (não dados pessoais)
- [ ] Indexar wikis do Jira
- [ ] Configurar atualizações automáticas

#### 3.4 Compliance Específico
- [ ] Documentar conformidade com regulamentações de apostas
- [ ] Implementar logs imutáveis para auditoria
- [ ] Configurar alertas para acessos não autorizados
- [ ] Realizar teste de penetração

---

### Fase 4: Administração e TI (Semanas 7-8)

**Objetivo:** Centralizar documentação administrativa

#### 4.1 Documentação Admin
- [ ] Indexar políticas de RH (públicas)
- [ ] Indexar manuais de TI e procedimentos
- [ ] Indexar documentação financeira (com acesso restrito)
- [ ] Indexar contratos e documentos legais

#### 4.2 Controle de Acesso
- [ ] Implementar RBAC (Role-Based Access Control)
- [ ] Configurar grupos por departamento
- [ ] Definir níveis de sensibilidade
- [ ] Implementar aprovação para documentos sensíveis

#### 4.3 Automação
- [ ] Configurar indexação automática de novos documentos
- [ ] Implementar webhook para atualizações
- [ ] Configurar limpeza de documentos obsoletos
- [ ] Automatizar backups

---

### Fase 5: Produção e Treinamento (Semanas 9-10)

**Objetivo:** Lançamento oficial e treinamento

#### 5.1 Lançamento
- [ ] Realizar UAT (User Acceptance Testing)
- [ ] Configurar alta disponibilidade (se necessário)
- [ ] Implementar disaster recovery
- [ ] Configurar alertas e monitoramento

#### 5.2 Treinamento
- [ ] Criar guia de usuário por departamento
- [ ] Realizar treinamentos presenciais
- [ ] Criar vídeos tutoriais
- [ ] Estabelecer canal de suporte

#### 5.3 Documentação Interna
- [ ] Documentar arquitetura do sistema
- [ ] Documentar procedimentos de backup/restore
- [ ] Documentar procedimentos de emergência
- [ ] Criar runbooks operacionais

---

## Tipos de Documentos por Departamento

### Game Development

#### Documentos Públicos (Todos podem acessar)
- Game Design Documents (GDDs)
- Wikis de desenvolvimento
- FAQs e manuais
- Documentação de APIs públicas
- Style guides de arte
- Roadmaps e cronogramas

#### Documentos Restritos (Acesso: Game Dev)
- Documentação técnica interna
- Especificações de APIs privadas
- Planos de teste detalhados
- Métricas de performance

#### Documentos Sensíveis (Acesso: Líderes/Arquitetos)
- **CÓDIGO FONTE** (NÃO indexar)
- Chaves de API e secrets
- Algoritmos proprietários
- IPs não patenteados

### Bets/Apostas

#### Documentos Públicos (Todos podem acessar)
- FAQs para clientes
- Regras básicas de apostas (públicas)
- Manuais de operação
- Documentação de suporte

#### Documentos Restritos (Acesso: Bets)
- Cálculos de odds e algoritmos
- Regras detalhadas de apostas
- Limites e thresholds
- Histórico de decisões

#### Documentos Sensíveis (Acesso: Compliance/Legal)
- Contratos com parceiros
- Licenças e regulamentações
- Auditorias e relatórios de compliance
- Dados de clientes (NÃO indexar dados pessoais)

### Administração

#### Documentos Públicos (Todos podem acessar)
- Políticas da empresa (públicas)
- Manuais de onboarding
- Benefícios e perks
- Procedimentos de TI básicos

#### Documentos Restritos (Acesso: Admin)
- Relatórios financeiros internos
- Orçamentos e previsões
- Políticas de RH internas
- Contratos de fornecedores

#### Documentos Sensíveis (Acesso: Executivos/Legal)
- Dados pessoais de funcionários (LGPD)
- Estratégias confidenciais
- Negociações em andamento
- Propriedade intelectual crítica

---

## Dashboard de Auditoria - Grafana

### Opções de Dashboard

#### Opção 1: Grafana (Escolhido para Implementação)
- **Vantagens:** Alertas avançados, integração com monitoramento, profissional
- **Acesso:** `http://192.168.15.4:3001` (após configuração)
- **Implementação:** Ver detalhes abaixo

#### Opção 2: Metabase (Alternativa)
- **Vantagens:** Open-source, fácil de configurar, interface amigável
- **Acesso:** `http://192.168.15.4:3000`
- **Implementação:** Mais simples, menos recursos de alerta

#### Opção 3: Interface Web Customizada
- **Vantagens:** Controle total, integrado ao sistema
- **Acesso:** `http://192.168.15.4:2468/audit`
- **Implementação:** Requer desenvolvimento adicional

#### Opção 4: pgAdmin (Interface Administrativa)
- **Vantagens:** Interface familiar para administradores de banco
- **Acesso:** `http://192.168.15.4:5050`
- **Implementação:** Focado em administração de banco, não dashboard

### Implementação do Grafana

#### Passo 1: Adicionar ao docker-compose.yml
```yaml
grafana:
  image: grafana/grafana:latest
  container_name: landf_grafana
  ports:
    - "3001:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
    - GF_SERVER_ROOT_URL=http://192.168.15.4:3001
  volumes:
    - ./grafana_data:/var/lib/grafana
  depends_on:
    - postgres
  restart: unless-stopped
```

#### Passo 2: Criar diretório para dados
```bash
mkdir -p grafana_data
chmod 777 grafana_data
```

#### Passo 3: Reiniciar containers
```bash
docker compose up -d grafana
```

#### Passo 4: Configurar Datasource PostgreSQL
1. Acessar http://localhost:3001 (user: admin, password: admin)
2. Navegar para Configuration → Data Sources → Add data source
3. Selecionar PostgreSQL
4. Configurar:
   - Host: postgres
   - Database: ragdb
   - User: rag
   - Password: rag
   - SSL Mode: disable
5. Clicar em "Save & Test"

#### Passo 5: Criar Dashboards

**Dashboard 1: Visão Geral de Auditoria**
- [ ] Panel: Total de queries (últimas 24h)
- [ ] Panel: Queries por departamento
- [ ] Panel: Queries por modelo de LLM
- [ ] Panel: Tempo médio de resposta
- [ ] Panel: Total de tokens consumidos
- [ ] Panel: Usuários ativos

**Dashboard 2: Acessos por Usuário**
- [ ] Panel: Top 10 usuários mais ativos
- [ ] Panel: Queries por usuário (gráfico de linha)
- [ ] Panel: Tempo médio por usuário
- [ ] Table: Detalhes de queries por usuário

**Dashboard 3: Acessos a Documentos**
- [ ] Panel: Documentos mais acessados
- [ ] Panel: Acessos a documentos sensíveis
- [ ] Panel: Acessos por departamento
- [ ] Table: Log de acessos a documentos

**Dashboard 4: Acessos Anômalos**
- [ ] Panel: Acessos anômalos detectados
- [ ] Panel: Tentativas de acesso falhadas
- [ ] Panel: Acessos de IPs desconhecidos
- [ ] Table: Detalhes de acessos suspeitos

#### Passo 6: Configurar Queries no Grafana

**Query Exemplo - Total de Queries:**
```sql
SELECT COUNT(*) as total_queries
FROM queries
WHERE created_at >= NOW() - INTERVAL '24 hours'
```

**Query Exemplo - Queries por Departamento:**
```sql
SELECT user_department, COUNT(*) as total
FROM queries
WHERE created_at >= NOW() - INTERVAL '24 hours'
  AND user_department IS NOT NULL
GROUP BY user_department
ORDER BY total DESC
```

**Query Exemplo - Documentos Mais Acessados:**
```sql
SELECT d.file_name, COUNT(dal.id) as access_count
FROM documents d
JOIN document_access_log dal ON d.id = dal.document_id
WHERE dal.created_at >= NOW() - INTERVAL '24 hours'
GROUP BY d.file_name
ORDER BY access_count DESC
LIMIT 10
```

**Query Exemplo - Acessos Anômalos:**
```sql
SELECT * FROM detect_anomalous_access(100, 60)
```

#### Passo 7: Configurar Alertas

**Alerta 1: Acessos Anômalos Detectados**
- Condição: Query `detect_anomalous_access(100, 60)` retorna > 0
- Frequência: A cada 5 minutos
- Notificação: Email, Slack, ou webhook
- Mensagem: "ALERTA: X acessos anômalos detectados"

**Alerta 2: Sistema Fora do Ar**
- Condição: Sem novas queries por 5 minutos
- Frequência: A cada 1 minuto
- Notificação: Email, Slack
- Mensagem: "ALERTA: Sistema RAG fora do ar"

**Alerta 3: Latência Alta**
- Condição: Tempo médio de resposta > 10 segundos
- Frequência: A cada 5 minutos
- Notificação: Email
- Mensagem: "ALERTA: Latência alta detectada"

**Alerta 4: Acesso a Documento Sensível**
- Condição: Acesso a documento com sensitivity_level = 'confidential'
- Frequência: Imediato
- Notificação: Email para DPO
- Mensagem: "ALERTA: Acesso a documento sensível"

#### Passo 8: Acesso Externo

**Liberar porta no firewall:**
```bash
sudo ufw allow 3001/tcp
```

**Configurar SSL/TLS (recomendado):**
```bash
# Usar Nginx como reverse proxy com Let's Encrypt
# Ou configurar SSL no próprio Grafana
```

**Acesso via VPN:**
- Configurar VPN para acesso seguro
- Acessar Grafana via IP interno da VPN

#### Passo 9: Autenticação e Autorização

**Opção 1: Autenticação LDAP/AD (Enterprise)**
- Configurar no Grafana
- Integrar com Active Directory da empresa

**Opção 2: OAuth2 (GitHub, Google)**
- Configurar OAuth providers
- Apenas usuários autorizados

**Opção 3: Autenticação Básica (Simples)**
- Usuário: admin
- Senha: configurada no docker-compose.yml
- **Não recomendado para produção**

#### Passo 10: Backup do Grafana

**Backup de dashboards:**
```bash
# Exportar dashboards via UI
# Ou usar API do Grafana para backup automático
```

**Backup de configurações:**
```bash
# Backup do diretório grafana_data
docker run --rm -v $(pwd)/grafana_data:/data -v $(pwd)/backup:/backup alpine tar czf /backup/grafana_backup.tar.gz /data
```

### Cronograma de Implementação

#### Semana 1 (Fase 1)
- [x] Adicionar Grafana ao docker-compose.yml
- [x] Criar diretório grafana_data (volume nomeado Docker)
- [x] Iniciar container Grafana
- [x] Configurar datasource PostgreSQL (provisioning automático)
- [x] Criar dashboard básico de visão geral

#### Semana 2 (Fase 1)
- [ ] Criar dashboard de acessos por usuário
- [x] Criar dashboard de acessos a documentos (rag-conversations.json)
- [ ] Configurar alertas básicos
- [ ] Testar alertas
- [x] Documentar procedimentos (docs/CHANGELOG.md)

#### Semana 3 (Fase 2 - Pilotagem)
- [ ] Refinar dashboards com feedback real
- [ ] Adicionar alertas específicos para Game Dev
- [ ] Configurar autenticação LDAP/OAuth2
- [ ] Liberar acesso externo via VPN

#### Semana 5 (Fase 3 - Bets)
- [ ] Adicionar dashboards específicos para Bets
- [ ] Configurar alertas para documentos sensíveis
- [ ] Configurar relatórios automáticos
- [ ] Integrar com sistema de compliance

### Alternativas Futuras

#### Metabase (Se Grafana for complexo demais)
- [ ] Adicionar Metabase ao docker-compose.yml
- [ ] Configurar datasource PostgreSQL
- [ ] Criar questions e dashboards
- [ ] Acesso: `http://192.168.15.4:3000`

#### Interface Web Customizada (Se precisar de mais controle)
- [ ] Criar endpoint `/api/audit` na aplicação web
- [ ] Criar página de dashboard em `web/templates/audit.html`
- [ ] Adicionar autenticação para administradores
- [ ] Acesso: `http://192.168.15.4:2468/audit`

---

## Implementação de Auditoria Enterprise

### Schema de Auditoria (db/schema-auditoria-enterprise.sql)

#### Tabelas Adicionais
- [ ] **users** - Autenticação e autorização (user_id, email, department, role)
- [ ] **audit_log** - Log de TODAS as ações (queries, visualizações, mudanças)
- [ ] **documents** - Rastrear documentos indexados (file_name, sensitivity_level)
- [ ] **document_access_log** - Auditoria específica de acessos a documentos
- [ ] **settings_history** - Histórico de mudanças de configuração

#### Alterações na Tabela Queries
- [ ] Adicionar user_id (UUID references users)
- [ ] Adicionar user_email (redundante para auditoria)
- [ ] Adicionar user_department (para análises por departamento)
- [ ] Adicionar ip_address (para auditoria de segurança)

#### Funcionalidades de Auditoria
- [ ] get_user_stats() - Estatísticas por usuário
- [ ] get_department_stats() - Estatísticas por departamento
- [ ] get_most_accessed_documents() - Documentos mais acessados
- [ ] detect_anomalous_access() - Detecção de acessos anômalos
- [ ] Views para relatórios (user_activity_summary, department_activity_summary)
- [ ] Função de anonimização para LGPD (anonymize_old_data)

### Aplicação do Schema

#### Passo 1: Aplicar Schema ao Banco
```bash
docker compose exec postgres psql -U rag -d ragdb -f db/schema-auditoria-enterprise.sql
```

#### Passo 2: Implementar Autenticação
- [ ] Configurar OAuth2/LDAP
- [ ] Criar middleware para identificar usuário em cada request
- [ ] Atualizar API para incluir user_id em todas as operações

#### Passo 3: Implementar Logging Automático
- [ ] Criar middleware para logar todas as ações em audit_log
- [ ] Logar: queries, visualizações de documentos, mudanças de configuração
- [ ] Implementar logging de acessos a documentos (document_access_log)

#### Passo 4: Configurar Monitoramento
- [ ] Configurar dashboard de auditoria (Grafana/Metabase)
- [ ] Configurar alertas para acessos anômalos
- [ ] Configurar relatórios automáticos (diários/semanais)

### Consultas de Auditoria

#### Exemplos de Uso
- Ver guia completo em `docs/guia-auditoria.md`
- Queries para verificar acessos por usuário/departamento
- Relatórios de documentos sensíveis acessados
- Detecção de acessos anômalos
- Exportação de logs para CSV/JSON

### Checklist de Auditoria

#### Diariamente
- [ ] Verificar acessos anômalos (detect_anomalous_access)
- [ ] Revisar documentos sensíveis acessados
- [ ] Checar tentativas de acesso falhadas
- [ ] Gerar relatório de uso

#### Semanalmente
- [ ] Analisar tendências de uso por departamento
- [ ] Revisar usuários inativos
- [ ] Verificar performance do sistema
- [ ] Revisar mudanças de configuração (settings_history)

#### Mensalmente
- [ ] Relatório completo de auditoria
- [ ] Revisar políticas de retenção
- [ ] Executar anonimização de dados antigos (LGPD)
- [ ] Atualizar lista de usuários

#### Trimestralmente
- [ ] Auditoria de segurança completa
- [ ] Revisar e atualizar políticas
- [ ] Testar procedimentos de backup/restore
- [ ] Revisar logs de acesso

---

## Estratégia de Segurança e Compliance

### Controle de Acesso

#### Níveis de Permissão
1. **Nível 1 - Público:** Todos os funcionários
2. **Nível 2 - Departamento:** Acesso apenas ao departamento
3. **Nível 3 - Restrito:** Acesso com aprovação
4. **Nível 4 - Confidencial:** Acesso apenas executivos/legal

#### Implementação
- [ ] Configurar autenticação centralizada (LDAP/OAuth2)
- [ ] Implementar grupos por departamento
- [ ] Configurar coleções Qdrant separadas por nível
- [ ] Implementar logging de todos os acessos
- [ ] Configurar alertas para acessos anômalos

### LGPD (Lei Geral de Proteção de Dados)

#### Requisitos
- [ ] Mapear dados pessoais indexados
- [ ] Implementar direito de esquecimento (delete requests)
- [ ] Anonimizar dados pessoais quando possível
- [ ] Documentar base legal para processamento
- [ ] Estabelecer política de retenção (máximo 5 anos)
- [ ] Configurar consentimento para dados sensíveis

#### Implementação
- [ ] Criar processo para solicitação de exclusão de dados
- [ ] Implementar rotina de limpeza automática
- [ ] Configurar backups com retenção definida
- [ ] Documentar todos os processos de dados
- [ ] Nomear DPO (Data Protection Officer)

### ISO 27001 (Opcional)

#### Requisitos Principais
- [ ] Política de segurança da informação
- [ ] Gestão de riscos
- [ ] Controle de acesso
- [ ] Criptografia
- [ ] Continuidade de negócios
- [ ] Conformidade legal

#### Implementação
- [ ] Realizar avaliação de riscos
- [ ] Documentar todos os controles
- [ ] Implementar monitoramento contínuo
- [ ] Realizar auditorias internas
- [ ] Manter evidências de conformidade

---

## Integrações com Sistemas Externos

### Jira

#### Configuração
- [ ] Criar usuário de serviço no Jira
- [ ] Configurar API token
- [ ] Configurar webhook para atualizações
- [ ] Mapear projetos por departamento

#### Indexação
- [ ] Indexar descrições de tickets (não dados pessoais)
- [ ] Indexar wikis do Jira
- [ ] Indexar comentários documentados
- [ ] **NÃO indexar** campos personalizados com dados sensíveis
- [ ] Configurar atualização incremental

#### Segurança
- [ ] Usar permissões mínimas do usuário de serviço
- [ ] Criptografar credenciais no .env
- [ ] Rotacionar tokens periodicamente
- [ ] Auditar acessos ao Jira

### Git (GitHub/GitLab)

#### Configuração
- [ ] Criar personal access token
- [ ] Configurar webhook para push events
- [ ] Mapear repositórios por departamento
- [ ] Configurar filtros de arquivos

#### Indexação
- [ ] Indexar READMEs e documentação em /docs
- [ ] Indexar wikis dos repositórios
- [ ] Indexar issues documentadas
- [ ] **NÃO indexar** código fonte (.py, .js, .cpp, etc.)
- [ ] **NÃO indexar** arquivos de configuração com secrets

#### Segurança
- [ ] Configurar gitignore para arquivos sensíveis
- [ ] Usar token com permissões read-only
- [ ] Auditar quais repositórios são indexados
- [ ] Implementar revisão manual para repositórios novos

### Outras Integrações (Futuras)

#### Confluence
- [ ] Configurar API integration
- [ ] Indexar spaces por departamento
- [ ] Respeitar permissões do Confluence

#### Google Workspace
- [ ] Configurar OAuth2
- [ ] Indexar Google Docs compartilhados
- [ ] Respeitar permissões de compartilhamento

#### Slack
- [ ] Configurar bot para indexação
- [ ] Indexar canais públicos
- [ ] **NÃO indexar** canais privados/DMs

---

## Documentos Sensíveis - Estratégia de Tratamento

### CATEGORIA 1: NÃO INDEXAR (Security Critical)

#### Código Fonte
- **Razão:** Propriedade intelectual crítica, risco de vazamento
- **Alternativa:** Indexar apenas documentação e READMEs
- **Armazenamento:** Repositórios Git privados com controle de acesso rigoroso

#### Dados Pessoais (LGPD)
- **Razão:** Violação direta da LGPD, multas pesadas
- **Alternativa:** Anonimizar antes de indexar, usar IDs
- **Armazenamento:** Sistemas separados com criptografia forte

#### Chaves e Secrets
- **Razão:** Risco de comprometimento de segurança
- **Alternativa:** Usar vault (HashiCorp Vault, AWS Secrets Manager)
- **Armazenamento:** Nunca indexar, armazenar em sistema dedicado

### CATEGORIA 2: INDEXAR COM ACESSO RESTRITO

#### Contratos e Acordos
- **Razão:** Informação confidencial comercial
- **Acesso:** Apenas legal e executivos
- **Retenção:** 7 anos após término

#### Dados Financeiros Detalhados
- **Razão:** Informação sensível comercial
- **Acesso:** Financeiro e executivos
- **Retenção:** 5 anos (conforme lei fiscal)

#### Algoritmos Proprietários
- **Razão:** Vantagem competitiva
- **Acesso:** Líderes técnicos e arquitetos
- **Retenção:** Indeterminada (IP da empresa)

### CATEGORIA 3: INDEXAR COM ANONIMIZAÇÃO

#### Relatórios com Dados Pessoais
- **Tratamento:** Remover nomes, CPFs, emails antes de indexar
- **Exemplo:** "Funcionário X" em vez de "João Silva"
- **Compliance:** Ainda precisa de consentimento

#### Tickets com Informações de Clientes
- **Tratamento:** Remover identificadores pessoais
- **Exemplo:** "Cliente #12345" em vez de "Maria Santos (maria@email.com)"
- **Compliance:** Base legal: legítimo interesse

---

## Procedimentos Operacionais

### Indexação de Novos Documentos

#### Processo Manual
1. Usuário faz upload via interface web
2. Sistema classifica automaticamente por departamento
3. Revisor aprova (se documento sensível)
4. Documento é indexado
5. Sistema envia confirmação

#### Processo Automático (Webhooks)
1. Sistema externo envia webhook
2. Sistema valida origem e permissões
3. Documento é processado e anonimizado (se necessário)
4. Documento é indexado na coleção apropriada
5. Sistema loga a operação

### Exclusão de Documentos

#### Solicitação de Exclusão (LGPD)
1. Usuário solicita exclusão via formulário
2. DPO avalia a solicitação
3. Se aprovada, documento é removido de Qdrant
4. Backup é marcado para exclusão (após período de retenção)
5. Usuário recebe confirmação

#### Exclusão Automática
1. Documentos expiram após período de retenção
2. Sistema remove de Qdrant
3. Backup é arquivado ou excluído
4. Sistema loga a operação

### Monitoramento e Alertas

#### Métricas a Monitorar
- Número de queries por departamento
- Latência média das respostas
- Taxa de erro do sistema
- Uso de CPU/RAM
- Acessos não autorizados (tentativas)
- Índice de relevância das respostas

#### Alertas Configurados
- Sistema fora do ar (>5 minutos)
- Acessos não autorizados detectados
- Latência >10 segundos
- Uso de CPU >90% por >10 minutos
- Tentativas de brute force
- Falha no backup

---

## Backup e Disaster Recovery

### Estratégia de Backup

#### Componentes a Backup
1. **Qdrant (Vector Store):** Diário + incremental
2. **PostgreSQL (Histórico):** Diário + WAL
3. **Documentos originais:** Diário
4. **Configurações:** Semanal
5. **Logs:** Mensal (após anonimização)

#### Retenção
- Backups diários: 30 dias
- Backups semanais: 12 semanas
- Backups mensais: 12 meses
- Backups anuais: 7 anos (compliance)

### Disaster Recovery

#### RTO (Recovery Time Objective): 4 horas
- [ ] Documentar procedimento de restore
- [ ] Testar restore mensalmente
- [ ] Manter backup offsite (cloud)
- [ ] Configurar servidor standby (opcional)

#### RPO (Recovery Point Objective): 1 hora
- [ ] Backups incrementais a cada hora
- [ ] Replicação síncrona para standby (opcional)
- [ ] Testar integridade dos backups diariamente

---

## Custos Estimados

### Hardware (Opção On-Premise)
- Servidor dedicado (64GB RAM, 16 vCPU, 2TB SSD): R$ 15.000-25.000
- Storage adicional (NAS): R$ 5.000-10.000
- UPS e redundância: R$ 3.000-5.000
- **Total inicial: R$ 23.000-40.000**

### Cloud (Opção AWS/GCP)
- Instância (r6g.2xlarge - 16 vCPU, 128GB RAM): R$ 2.500/mês
- Storage (EBS gp3 1TB): R$ 400/mês
- Backup (S3): R$ 200/mês
- Monitoramento: R$ 100/mês
- **Total mensal: R$ 3.200/mês**

### Licenças e Certificações
- SSL Certificate (Let's Encrypt): Gratuito
- Auditoria de segurança (inicial): R$ 10.000-20.000
- Consultoria LGPD: R$ 5.000-10.000
- Certificação ISO 27001 (opcional): R$ 30.000-50.000

### Pessoal
- Administrador do sistema (parcial): 20h/mês
- DPO (pode ser existente): 10h/mês
- Suporte e manutenção: 10h/mês

---

## Cronograma Resumido

| Semana | Fase | Entregáveis |
|--------|------|-------------|
| 1-2 | Infraestrutura | Servidor configurado, segurança básica |
| 3-4 | Pilotagem Game Dev | Sistema testado com desenvolvedores |
| 5-6 | Expansão Bets | Sistema integrado com Jira, compliance |
| 7-8 | Administração | Sistema completo para todos departamentos |
| 9-10 | Produção | Lançamento oficial, treinamento |

**Total: 10 semanas (2.5 meses)**

---

## Próximos Passos Imediatos

### Esta Semana
1. [ ] Aprovar orçamento de hardware/cloud
2. [ ] Designar equipe responsável (1-2 pessoas)
3. [ ] Definir provedor (on-premise vs cloud)
4. [ ] Iniciar compra/configuração de servidor

### Próxima Semana
1. [ ] Configurar infraestrutura básica
2. [ ] Configurar segurança inicial
3. [ ] Mapear documentos existentes
4. [ ] Criar políticas de acesso

### Em 2 Semanas
1. [ ] Iniciar pilotagem com Game Development
2. [ ] Configurar integração Git inicial
3. [ ] Coletar feedback inicial
4. [ ] Ajustar configurações

---

## Contatos e Responsabilidades

### Equipe de Implementação
- **Sponsor Executivo:** [Nome] - Aprovação orçamento e decisões estratégicas
- **Líder Técnico:** [Nome] - Configuração técnica e integrações
- **DPO:** [Nome] - Compliance LGPD e políticas de dados
- **Líder de Departamento (Game Dev):** [Nome] - Pilotagem e feedback
- **Líder de Departamento (Bets):** [Nome] - Requisitos específicos
- **Administrador TI:** [Nome] - Infraestrutura e operações

### Fornecedores
- **Servidor/Cloud:** [Fornecedor]
- **Consultoria de Segurança:** [Fornecedor] (opcional)
- **Consultoria LGPD:** [Fornecedor] (opcional)
- **Auditoria ISO:** [Fornecedor] (opcional)

---

## Referências

- [Documentação do Projeto RAG](./modelo-configurado.md)
- [Guia de Auditoria](./guia-auditoria.md) - Como verificar logs de acesso
- [Schema de Auditoria Enterprise](../db/schema-auditoria-enterprise.sql)
- [LGPD - Lei 13.709/2018](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)
- [ISO 27001](https://www.iso.org/standard/27001)
- [Ollama Documentation](https://ollama.com/docs)
- [Qdrant Documentation](https://qdrant.tech/documentation/)

---

**Versão:** 1.0  
**Data:** 19/05/2026  
**Status:** Planejamento  
**Próxima Revisão:** Após aprovação executiva
