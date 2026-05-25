# Datadog Integration

Este projeto foi migrado do Grafana para Datadog para monitoramento e observabilidade.

**Nota:** O Datadog Agent é opcional e usa Docker Compose profiles. Ele só será iniciado quando você configurar a API Key e usar o profile `monitoring`.

## Configuração

### 1. Obter API Key do Datadog

1. Acesse [Datadog](https://app.datadoghq.com/)
2. Vá em Organization Settings > API Keys
3. Crie uma nova API Key ou use uma existente
4. Copie a API Key

### 2. Configurar Variáveis de Ambiente

Adicione ao arquivo `.env`:

```bash
DD_API_KEY=sua_api_key_aqui
DD_SITE=datadoghq.com  # ou datadoghq.eu para região europeia
```

### 3. Iniciar o Datadog Agent

O Datadog Agent usa o profile `monitoring` do Docker Compose. Para iniciá-lo:

```bash
docker compose --profile monitoring up -d
```

Isso iniciará todos os serviços principais (postgres, qdrant, web, rag) + o Datadog Agent.

Para iniciar apenas os serviços principais (sem Datadog):

```bash
docker compose up -d
```

## Funcionalidades Habilitadas

O Datadog Agent está configurado para coletar:

- **Logs**: Coleta logs de todos os containers
- **APM**: Application Performance Monitoring para rastreamento de requisições
- **Metrics**: Métricas de CPU, memória, rede e disco dos containers
- **Container Monitoring**: Monitoramento automático de containers Docker

## Portas

- **8126**: Porta do Datadog Agent (APM trace receiver)

## Verificar Status

Para verificar se o agent está funcionando:

```bash
docker compose --profile monitoring logs datadog
```

Ou verifique o status do container:

```bash
docker compose --profile monitoring ps datadog
```

## Dashboard no Datadog

Após a configuração, você verá os seguintes dashboards no Datadog:

1. **Container Dashboard**: Visão geral de todos os containers
2. **PostgreSQL Dashboard**: Métricas do banco de dados
3. **Web Application Dashboard**: Métricas da API FastAPI
4. **Logs Viewer**: Visualização de logs agregados

## APM (Application Performance Monitoring)

Para habilitar APM em sua aplicação Python, instale o ddtrace:

```bash
pip install ddtrace
```

E execute sua aplicação com:

```bash
ddtrace-run uvicorn main:app --host 0.0.0.0 --port 8000
```

## Comparação Grafana vs Datadog

| Característica | Grafana | Datadog |
|----------------|---------|---------|
| Instalação | Self-hosted | SaaS |
| Configuração | Manual complexa | Automática simples |
| Logs | Requer plugins | Nativo |
| APM | Requer plugins | Nativo |
| Alertas | Configuração manual | Inteligente automático |
| Integrações | Manual | 700+ nativas |
| Custo | Gratuito (self-hosted) | Assinatura |

## Troubleshooting

### Agent não conecta ao Datadog

Verifique se a API Key está correta no `.env`:

```bash
docker compose logs datadog | grep "API key"
```

### Logs não aparecem

Verifique se a coleta de logs está habilitada:

```bash
docker compose exec datadog agent config check
```

### APM não coleta traces

Certifique-se de que a porta 8126 está acessível e que o DD_APM_ENABLED=true.

## Remoção do Grafana

O Grafana foi removido da stack. Se você ainda tem volumes do Grafana, pode removê-los:

```bash
docker volume rm reals_rag_game-provider_grafana_data
```

## Mais Informações

- [Documentação Oficial do Datadog](https://docs.datadoghq.com/)
- [Datadog Agent Docker](https://docs.datadoghq.com/agent/docker/)
- [APM Python](https://docs.datadoghq.com/tracing/setup_overview/setup/python/)
