#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

MODE="${1:-dev}"
if [[ ! -f "${ROOT_DIR}/.env" ]]; then
    echo "Configuração ausente: copie .env.example para .env e defina COMPRAS_DB_PASSWORD." >&2
    exit 2
fi
set -a
source "${ROOT_DIR}/.env"
set +a

PORT="${2:-${COMPRAS_APP_PORT:-8016}}"
export NEXO_COMPRAS_HOST="${NEXO_COMPRAS_HOST:-127.0.0.1}"
export DATABASE_URL="postgresql://${COMPRAS_DB_USER}:${COMPRAS_DB_PASSWORD}@127.0.0.1:${COMPRAS_DB_PORT}/${COMPRAS_DB_NAME}"

echo "============================================================"
echo "          SisTer-Compras — Script Orquestrador              "
echo "============================================================"
echo "Diretório do projeto: ${ROOT_DIR}"
echo "Modo: ${MODE}"
echo "Porta Web: ${PORT}"
echo "============================================================"
echo ""

cd "${ROOT_DIR}"

echo "[+] Garantindo PostgreSQL exclusivo em 127.0.0.1:${COMPRAS_DB_PORT}..."
podman compose up -d compras-db
for attempt in $(seq 1 30); do
    if podman exec "${COMPRAS_DB_CONTAINER}" \
        sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"' >/dev/null 2>&1; then
        break
    fi
    if [[ "${attempt}" == "30" ]]; then
        echo "PostgreSQL do Nexo-Compras não ficou pronto." >&2
        exit 3
    fi
    sleep 1
done

# 1. Configurar build CMake
echo "[1/5] Configurando build CMake..."
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug

# 2. Compilar projeto C++20
echo "[2/5] Compilando SisTer-Compras C++20..."
cmake --build build

# 3. Executar testes CTest
echo "[3/5] Executando suíte de testes CTest..."
ctest --test-dir build --output-on-failure

# 4. Validar governança e contratos
echo "[4/5] Validando regras de governança e contratos de ferramentas..."
python3 scripts/validate_governance_repo.py
python3 scripts/validate_tool_contracts.py

# 5. Executar demonstração CLI e salvar estado APENAS se o banco/arquivo de armazenamento não existir
echo "[5/5] Verificando persistência do banco de dados..."
STORAGE_FILE="storage/compras_data.json"
if [ ! -f "${STORAGE_FILE}" ]; then
    echo "[+] Banco/Armazenamento novo. Executando demonstração de domínio para criar dados iniciais..."
    ./build/sister_compras demo
else
    echo "[+] Base de dados existente preservada com sucesso em '${STORAGE_FILE}' (ignorado re-seeding para proteger registros do usuário)."
fi

# Liberar porta se houver processo anterior travado
if command -v fuser >/dev/null 2>&1; then
    fuser -k "${PORT}/tcp" >/dev/null 2>&1 || true
fi

echo ""
echo "============================================================"
echo "   Todos os testes e validações passaram com SUCESSO!     "
echo "============================================================"
echo "Iniciando Nexo-Compras em http://${NEXO_COMPRAS_HOST}:${PORT}"
echo "Dados 100% persistentes no Banco de Dados / Armazenamento em Disco."
if [[ -z "${SISTER_HOME:-}" ]]; then
    echo "Pressione Ctrl+C para encerrar."
else
    echo "Processo HTTP será mantido em segundo plano pelo orquestrador do SisTer."
fi
echo "============================================================"
echo ""

if [[ -z "${SISTER_HOME:-}" ]]; then
    exec python3 scripts/app/serve.py "${PORT}"
fi

mkdir -p .run
python3 scripts/app/serve.py "${PORT}" >>.run/nexo-compras.log 2>&1 &
SERVER_PID=$!
echo "${SERVER_PID}" >.run/nexo-compras.pid
for attempt in $(seq 1 30); do
    if curl --fail --silent "http://127.0.0.1:${PORT}/api/health" >/dev/null; then
        echo "Nexo-Compras saudável com PID ${SERVER_PID}."
        exit 0
    fi
    if ! kill -0 "${SERVER_PID}" 2>/dev/null; then
        echo "Nexo-Compras encerrou antes de ficar saudável." >&2
        exit 4
    fi
    sleep 1
done
echo "Nexo-Compras não ficou saudável." >&2
exit 5
