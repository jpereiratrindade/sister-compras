# Contributing

## Before opening a change
- Configure and build the project
- Run tests
- Run local quality checks
- Update governance artifacts only when they reflect real behavior

## Local quality gates
- Install hooks:
  - `./scripts/dev/install-git-hooks.sh`
- Run checks:
  - `./scripts/run_quality.sh`
- Validate governance:
  - `python3 scripts/validate_tool_contracts.py`
  - `python3 scripts/validate_governance_repo.py`
