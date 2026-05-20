#!/bin/bash

# Script de Deploy Automático - RAG Game Provider
# Facilita o deploy do sistema com todas as configurações

set -e  # Para em caso de erro

echo "=========================================="
echo "  Deploy RAG Game Provider"
echo "=========================================="

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_step() {
    echo -e "${YELLOW}▶ $1${NC}"
}

# Verificar se Docker está instalado
print_step "Verificando Docker..."
if ! command -v docker &> /dev/null; then
    print_error "Docker não está instalado. Por favor, instale Docker primeiro."
    exit 1
fi
print_success "Docker encontrado"

# Verificar se Docker Compose está instalado
print_step "Verificando Docker Compose..."
if ! command -v docker compose &> /dev/null; then
    print_error "Docker Compose não está instalado. Por favor, instale Docker Compose primeiro."
    exit 1
fi
print_success "Docker Compose encontrado"

# Verificar se .env existe
print_step "Verificando arquivo .env..."
if [ ! -f .env ]; then
    print_warning "Arquivo .env não encontrado. Criando .env padrão..."
    cat > .env << EOF
# Ollama Configuration
OLLAMA_BASE_URL=http://host.docker.internal:11434
LLM_MODEL=qwen2.5:7b-instruct
EMBED_MODEL=bge-m3
EMBED_BATCH_SIZE=50

# Groq Configuration (opcional)
# GROQ_API_KEY=your_groq_api_key_here

# Chunking
CHUNK_SIZE=1024
CHUNK_OVERLAP=200
EOF
    print_success "Arquivo .env criado com configurações padrão"
else
    print_success "Arquivo .env encontrado"
fi

# Verificar se Ollama está rodando
print_step "Verificando Ollama..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    print_warning "Ollama não está rodando em localhost:11434"
    print_warning "Por favor, inicie o Ollama com: ollama serve"
    read -p "Deseja continuar mesmo assim? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Deploy cancelado."
        exit 1
    fi
else
    print_success "Ollama está rodando"
    
    # Verificar se o modelo existe
    print_step "Verificando modelo LLM..."
    if ! curl -s http://localhost:11434/api/tags | grep -q "qwen2.5:7b-instruct"; then
        print_warning "Modelo qwen2.5:7b-instruct não encontrado no Ollama"
        read -p "Deseja puxar o modelo agora? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_step "Puxando modelo qwen2.5:7b-instruct..."
            ollama pull qwen2.5:7b-instruct
            print_success "Modelo puxado com sucesso"
        fi
    else
        print_success "Modelo qwen2.5:7b-instruct encontrado"
    fi
    
    # Verificar se o modelo de embedding existe
    print_step "Verificando modelo de embedding..."
    if ! curl -s http://localhost:11434/api/tags | grep -q "bge-m3"; then
        print_warning "Modelo bge-m3 não encontrado no Ollama"
        read -p "Deseja puxar o modelo agora? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            print_step "Puxando modelo bge-m3..."
            ollama pull bge-m3
            print_success "Modelo puxado com sucesso"
        fi
    else
        print_success "Modelo bge-m3 encontrado"
    fi
fi

# Parar containers existentes
print_step "Parando containers existentes..."
docker compose down 2>/dev/null || true
print_success "Containers parados"

# Reconstruir imagens
print_step "Reconstruindo imagens Docker..."
docker compose build
print_success "Imagens reconstruídas"

# Iniciar containers
print_step "Iniciando containers..."
docker compose up -d
print_success "Containers iniciados"

# Aguardar containers ficarem saudáveis
print_step "Aguardando containers ficarem saudáveis..."
sleep 10

# Verificar status dos containers
print_step "Verificando status dos containers..."
docker compose ps

# Aplicar migrações do banco de dados
print_step "Aplicando migrações do banco de dados..."
if [ -f db/migration-add-conversations.sql ]; then
    docker cp db/migration-add-conversations.sql landf_postgres:/tmp/migration-add-conversations.sql
    docker compose exec -T postgres psql -U rag -d ragdb -f /tmp/migration-add-conversations.sql 2>/dev/null || true
    print_success "Migração de conversas aplicada"
fi

if [ -f db/schema-auditoria-enterprise.sql ]; then
    print_warning "Schema de auditoria enterprise encontrado"
    read -p "Deseja aplicar o schema de auditoria enterprise? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker cp db/schema-auditoria-enterprise.sql landf_postgres:/tmp/schema-auditoria-enterprise.sql
        docker compose exec -T postgres psql -U rag -d ragdb -f /tmp/schema-auditoria-enterprise.sql 2>/dev/null || true
        print_success "Schema de auditoria enterprise aplicado"
    fi
fi

# Verificar se containers estão saudáveis
print_step "Verificando saúde dos containers..."
sleep 5

if docker compose ps | grep -q "healthy"; then
    print_success "Todos os containers estão saudáveis"
else
    print_warning "Alguns containers podem não estar saudáveis ainda"
    print_warning "Verifique com: docker compose ps"
fi

# Mostrar informações de acesso
echo ""
echo "=========================================="
echo "  Deploy Concluído!"
echo "=========================================="
echo ""
print_success "Sistema disponível em:"
echo "  - Web Interface: http://localhost:2468"
echo "  - Qdrant: http://localhost:6333"
echo "  - PostgreSQL: localhost:5432"
echo ""
echo "=========================================="
echo "  Comandos Úteis"
echo "=========================================="
echo "  Ver logs:          docker compose logs -f"
echo "  Ver status:        docker compose ps"
echo "  Parar:             docker compose down"
echo "  Reiniciar:         docker compose restart"
echo "  Acessar banco:     docker compose exec postgres psql -U rag -d ragdb"
echo ""
print_success "Deploy concluído com sucesso!"
