#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

MODE="${1:-dev}"
PORT="${2:-8002}"

echo "============================================================"
echo "          SisTer-Compras — Script Orquestrador              "
echo "============================================================"
echo "Diretório do projeto: ${ROOT_DIR}"
echo "Modo: ${MODE}"
echo "Porta Web: ${PORT}"
echo "============================================================"
echo ""

cd "${ROOT_DIR}"

# Garantir container PostgreSQL dedicado 'sister-compras-db' na porta 55435
if command -v podman >/dev/null 2>&1; then
    if ! podman ps --format "{{.Names}}" | grep -q "^sister-compras-db$"; then
        echo "[+] Garantindo banco de dados PostgreSQL independente (sister-compras-db:55435)..."
        podman start sister-compras-db 2>/dev/null || podman run -d --name sister-compras-db -e POSTGRES_DB=sister_compras -e POSTGRES_USER=sister -e POSTGRES_PASSWORD=sister -p 127.0.0.1:55435:5432 docker.io/library/postgres:17-alpine || true
    fi
elif command -v docker >/dev/null 2>&1; then
    if ! docker ps --format "{{.Names}}" | grep -q "^sister-compras-db$"; then
        echo "[+] Garantindo banco de dados PostgreSQL independente (sister-compras-db:55435)..."
        docker start sister-compras-db 2>/dev/null || docker run -d --name sister-compras-db -e POSTGRES_DB=sister_compras -e POSTGRES_USER=sister -e POSTGRES_PASSWORD=sister -p 127.0.0.1:55435:5432 postgres:17-alpine || true
    fi
fi

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
echo "Iniciando servidor da interface Web do SisTer-Compras em http://localhost:${PORT}"
echo "Dados 100% persistentes no Banco de Dados / Armazenamento em Disco."
echo "Pressione Ctrl+C para encerrar."
echo "============================================================"
echo ""

python3 scripts/app/serve.py "${PORT}"
