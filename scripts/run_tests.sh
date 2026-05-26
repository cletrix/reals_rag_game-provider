#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# run_tests.sh — Executa testes antes do deploy
# Uso:  ./scripts/run_tests.sh [--fast]
#   --fast: pula coverage report (CI rápido)
# ---------------------------------------------------------------------------
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WEB_DIR="$ROOT_DIR/web"
TESTS_DIR="$ROOT_DIR/tests"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== RAG Game Provider — Pre-Deploy Tests ===${NC}"
echo "Root: $ROOT_DIR"

# Verifica dependências
if ! command -v python3 &>/dev/null; then
  echo -e "${RED}ERRO: python3 não encontrado${NC}"
  exit 1
fi

# Instala dependências de teste se necessário
if ! python3 -c "import pytest" &>/dev/null 2>&1; then
  echo "Instalando dependências de teste..."
  pip install -r "$ROOT_DIR/requirements-dev.txt" -q
fi

# Monta PYTHONPATH para que os imports do web/ funcionem
export PYTHONPATH="$WEB_DIR:$PYTHONPATH"

# Configura variáveis mínimas para testes (sem banco real)
export SECRET_KEY="${SECRET_KEY:-test-secret-key-for-ci-only}"
export DATABASE_URL="${DATABASE_URL:-postgresql://rag:rag@localhost:5432/ragdb}"
export QDRANT_URL="${QDRANT_URL:-http://localhost:6333}"

echo ""
echo -e "${YELLOW}Executando testes unitários...${NC}"

if [[ "${1:-}" == "--fast" ]]; then
  python3 -m pytest "$TESTS_DIR" \
    --tb=short \
    -q \
    --no-header \
    --ignore="$TESTS_DIR/test_db.py" \
    --ignore="$TESTS_DIR/test_folder_scanner.py" \
    -x
else
  python3 -m pytest "$TESTS_DIR" \
    --tb=short \
    -q \
    --no-header \
    --ignore="$TESTS_DIR/test_db.py" \
    --ignore="$TESTS_DIR/test_folder_scanner.py" \
    --cov="$WEB_DIR" \
    --cov-report=term-missing \
    --cov-fail-under=50 \
    -x
fi

EXIT_CODE=$?

echo ""
if [[ $EXIT_CODE -eq 0 ]]; then
  echo -e "${GREEN}✅ Todos os testes passaram — deploy autorizado${NC}"
else
  echo -e "${RED}❌ Testes falharam — deploy BLOQUEADO${NC}"
  exit $EXIT_CODE
fi
