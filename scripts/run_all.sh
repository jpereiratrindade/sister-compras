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

# 5. Executar demonstração CLI e salvar estado
echo "[5/5] Executando demonstração de domínio e gerando relatórios..."
./build/sister_compras demo

# Liberar porta se houver processo anterior travado
if command -v fuser >/dev/null 2>&1; then
    fuser -k "${PORT}/tcp" >/dev/null 2>&1 || true
fi

echo ""
echo "============================================================"
echo "   Todos os testes e validações passaram com SUCESSO!     "
echo "============================================================"
echo "Iniciando servidor da interface Web do SisTer-Compras em http://localhost:${PORT}"
echo "Pressione Ctrl+C para encerrar."
echo "============================================================"
echo ""

python3 scripts/app/serve.py "${PORT}"
