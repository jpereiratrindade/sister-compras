#!/usr/bin/env python3

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "mcp" / "tool_schema.json"
CONTRACTS_DIR = ROOT / "mcp" / "contracts"


def fail(message: str) -> int:
    print(f"[validate-tool-contracts] FAIL: {message}")
    return 1


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require_keys(data, keys, path: Path):
    missing = [key for key in keys if key not in data]
    if missing:
        raise ValueError(f"{path}: missing keys {missing}")


def validate_contract(contract: dict, path: Path):
    require_keys(
        contract,
        [
            "contract_version",
            "tool_name",
            "tool",
            "description",
            "allowed_modes",
            "risk_level",
            "policy_refs",
            "human_approval",
            "preconditions",
            "required_evidence",
            "forbidden_actions",
            "input_schema",
            "output_schema",
        ],
        path,
    )

    if contract["risk_level"] not in {"low", "moderate", "high", "critical"}:
        raise ValueError(f"{path}: invalid risk_level '{contract['risk_level']}'")
    if not contract["contract_version"].startswith("v"):
        raise ValueError(f"{path}: contract_version must start with 'v'")
    if contract["tool_name"] != contract["tool"]:
        raise ValueError(f"{path}: tool_name and tool must match")

    allowed_modes = set(contract["allowed_modes"])
    if not allowed_modes:
        raise ValueError(f"{path}: allowed_modes must not be empty")
    if not allowed_modes.issubset({"explore", "safe-change", "restricted"}):
        raise ValueError(f"{path}: invalid allowed_modes {sorted(allowed_modes)}")

    approval = contract["human_approval"]
    require_keys(approval, ["required", "policy"], path)
    if approval["policy"] not in {"never", "required_if_core_module", "required_if_destructive", "always"}:
        raise ValueError(f"{path}: invalid approval policy '{approval['policy']}'")

    if not contract["forbidden_actions"]:
        raise ValueError(f"{path}: forbidden_actions must not be empty")
    if not contract["policy_refs"]:
        raise ValueError(f"{path}: policy_refs must not be empty")
    if contract["risk_level"] in {"high", "critical"} and not approval["required"]:
        raise ValueError(f"{path}: high-risk tools must require human approval")
    if contract["risk_level"] in {"high", "critical"}:
        required_evidence = set(contract["required_evidence"])
        for field in {"task_id", "human_owner", "contract_ref", "approval_decision"}:
            if field not in required_evidence:
                raise ValueError(f"{path}: high-risk tools must require evidence field '{field}'")

    for policy_ref in contract["policy_refs"]:
        policy_path = ROOT / policy_ref
        if not policy_path.is_file():
            raise ValueError(f"{path}: policy ref not found '{policy_ref}'")


def main() -> int:
    if not SCHEMA_PATH.exists():
        return fail(f"schema not found: {SCHEMA_PATH}")
    if not CONTRACTS_DIR.exists():
        return fail(f"contracts dir not found: {CONTRACTS_DIR}")

    try:
        schema = load_json(SCHEMA_PATH)
    except Exception as exc:
        return fail(f"unable to load schema: {exc}")

    if "required" not in schema or "properties" not in schema:
        return fail("schema must declare 'required' and 'properties'")

    contracts = sorted(CONTRACTS_DIR.glob("*.json"))
    if not contracts:
        return fail("no contracts found")

    try:
        for contract_path in contracts:
            contract = load_json(contract_path)
            validate_contract(contract, contract_path)
    except Exception as exc:
        return fail(str(exc))

    print(f"[validate-tool-contracts] OK: validated {len(contracts)} contract(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
