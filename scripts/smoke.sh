#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${NEXO_COMPRAS_BASE_URL:-http://127.0.0.1:8016}"
headers=(
  -H "X-Sister-Subject: smoke-test"
  -H "X-Sister-Name: Teste de Integração"
  -H "X-Sister-Email: smoke@sister.local"
  -H "X-Sister-Role: admin"
)

health="$(curl -fsS "${BASE_URL}/api/health")"
python3 -c '
import json, sys
value = json.loads(sys.argv[1])
assert value["status"] == "ok"
assert value["service"] == "nexo-compras"
assert value["database"] == "ok"
' "$health"

status="$(curl -sS -o /dev/null -w '%{http_code}' "${BASE_URL}/")"
[[ "$status" == "401" ]]

curl -fsS "${headers[@]}" "${BASE_URL}/api/me" |
  python3 -c 'import json,sys; value=json.load(sys.stdin); assert value["subject"] == "smoke-test"'

curl -fsS "${headers[@]}" "${BASE_URL}/api/nexo/context" |
  python3 -c '
import json, sys
value = json.load(sys.stdin)
assert value["contract_version"] == "1.0.0"
assert value["system_id"] == "sister_nexo"
assert value["project"]["project_id"]
assert isinstance(value["research_activities"], list)
assert isinstance(value["operational_activities"], list)
'

page="$(curl -fsS "${headers[@]}" "${BASE_URL}/")"
grep -q "<title>Nexo-Compras" <<<"$page"
grep -q 'nexo-compras.integration/1.0.0' <<<"$page"

echo "Smoke test do Nexo-Compras: ok"
