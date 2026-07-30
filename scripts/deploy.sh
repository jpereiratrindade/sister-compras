#!/usr/bin/env bash
set -euo pipefail

echo "=== Deploying SisTer Compras ==="

# Verifica se o arquivo env existe
if [[ ! -f /etc/sister/sister-compras.env ]]; then
  echo "Erro: Arquivo /etc/sister/sister-compras.env não encontrado."
  exit 1
fi

set -a
source /etc/sister/sister-compras.env
set +a

# 1. Puxa as novidades do git
echo "-> Atualizando repositório..."
git pull origin main

# 2. Levanta o banco de dados temporariamente para testes
echo "-> Garantindo banco de dados online..."
podman compose up -d compras-db

# Aguarda o banco ficar saudável
echo "-> Aguardando o PostgreSQL inicializar..."
for attempt in $(seq 1 30); do
  if podman exec "${COMPRAS_DB_CONTAINER:-sister-compras-db}" sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"' >/dev/null 2>&1; then
    break
  fi
  if [[ "$attempt" == "30" ]]; then
    echo "Erro: Banco de dados não ficou pronto." >&2
    exit 4
  fi
  sleep 1
done

# 3. Compilação Release da Aplicação
echo "-> Compilando aplicação em modo Release..."
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build

# 4. Validar governança e contratos
echo "-> Validando regras de governança e contratos de ferramentas..."
python3 scripts/validate_governance_repo.py || true
python3 scripts/validate_tool_contracts.py || true

# 5. Reinicia o serviço systemd
echo "-> Reiniciando o serviço sister-compras via systemd..."
sudo systemctl restart sister-compras

echo "=== Deploy finalizado com sucesso! ==="
