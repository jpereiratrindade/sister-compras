#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DIRS = [
    "src",
    "include",
    "tests",
    "adr",
    "ddd",
    "policies",
    "mcp",
    "mcp/contracts",
    "prompts",
    "ci",
    "examples",
    "scripts",
    ".github",
    ".github/workflows",
    ".githooks",
]

REQUIRED_FILES = [
    "README.md",
    "SISTER_INTEGRATION.md",
    "CMakeLists.txt",
    ".clang-format",
    ".clang-tidy",
    "mcp/tool_schema.json",
    "mcp/tool_contracts.md",
    "mcp/agent_interface.md",
    "policies/ai_usage_policy.md",
    "policies/approval_matrix.md",
    "policies/context_boundary_policy.md",
    "policies/evidence_and_audit_policy.md",
    "prompts/governance_task_packet.md",
    "examples/evidence_log.json",
    "adr/ADR-005-nexo-compras-federated-boundary.md",
    "storage/compras_data.example.json",
    "contracts/nexo_compras_integration.schema.json",
    ".env.example",
    "compose.yml",
    "scripts/validate_tool_contracts.py",
    "scripts/run_quality.sh",
    ".github/workflows/ci.yml",
]


def fail(message: str) -> int:
    print(f"[validate-governance-repo] FAIL: {message}")
    return 1


def main() -> int:
    missing_dirs = [rel for rel in REQUIRED_DIRS if not (ROOT / rel).is_dir()]
    if missing_dirs:
        return fail(f"missing directories: {missing_dirs}")

    missing_files = [rel for rel in REQUIRED_FILES if not (ROOT / rel).is_file()]
    if missing_files:
        return fail(f"missing files: {missing_files}")

    validator = ROOT / "scripts" / "validate_tool_contracts.py"
    result = subprocess.run(
        [sys.executable, str(validator)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        return fail("tool contract validation failed")

    print("[validate-governance-repo] OK: repository governance structure is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
