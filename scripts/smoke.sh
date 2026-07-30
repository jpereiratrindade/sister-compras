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

curl -fsS "${headers[@]}" "${BASE_URL}/api/data" |
  python3 -c '
import json, sys
value = json.load(sys.stdin)
assert isinstance(value["projects"], list)
assert isinstance(value["needs"], list)
assert isinstance(value["decisions"], list)
'

context_response="$(
  curl -sS -w $'\n%{http_code}' "${headers[@]}" \
    "${BASE_URL}/api/nexo/context"
)"
context_status="${context_response##*$'\n'}"
context_body="${context_response%$'\n'*}"
if [[ "$context_status" == "200" ]]; then
  python3 -c '
import json, sys
value = json.loads(sys.argv[1])
assert value["contract_version"] == "1.0.0"
assert value["system_id"] == "sister_nexo"
assert value["project"]["project_id"]
assert isinstance(value["research_activities"], list)
assert isinstance(value["operational_activities"], list)
' "$context_body"
elif [[ "$context_status" != "403" ]]; then
  echo "Contexto do Nexo retornou HTTP ${context_status}." >&2
  exit 1
fi

page="$(curl -fsS "${headers[@]}" "${BASE_URL}/")"
grep -q "<title>Nexo-Compras" <<<"$page"
grep -q 'nexo-compras.profile/1.0.0' <<<"$page"
grep -q 'id="need-project-select"' <<<"$page"
grep -q 'id="edit-need-project"' <<<"$page"
grep -q '20260730-parent-navigation' <<<"$page"
grep -q 'class="mini-brand" href="./"' <<<"$page"
grep -q 'class="nav-link nav-parent-link" href="../#dashboard"' <<<"$page"
python3 -c '
from html.parser import HTMLParser
import sys

class DialogValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.dialogs = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag != "dialog":
            return
        dialog_id = dict(attrs).get("id")
        if self.stack:
            raise AssertionError(
                f"dialog {dialog_id!r} aninhado em {self.stack[-1]!r}"
            )
        self.stack.append(dialog_id)
        self.dialogs.append(dialog_id)

    def handle_endtag(self, tag):
        if tag == "dialog":
            assert self.stack, "fechamento de dialog sem abertura"
            self.stack.pop()

validator = DialogValidator()
validator.feed(sys.stdin.read())
assert not validator.stack, f"dialog não fechado: {validator.stack[-1]!r}"
assert "modal-ai-chat" in validator.dialogs
assert "modal-project" in validator.dialogs
' <<<"$page"

echo "Smoke test do Nexo-Compras: ok"
