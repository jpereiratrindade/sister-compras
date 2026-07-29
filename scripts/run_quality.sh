#!/usr/bin/env bash

set -euo pipefail

BUILD_DIR="${BUILD_DIR:-build}"

cmake -S . -B "$BUILD_DIR" -G Ninja -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
cmake --build "$BUILD_DIR"
ctest --test-dir "$BUILD_DIR" --output-on-failure

if command -v clang-format >/dev/null 2>&1; then
    find src include tests -type f \( -name '*.cpp' -o -name '*.hpp' \) -print0 | xargs -0 -r clang-format --dry-run --Werror
fi

if command -v clang-tidy >/dev/null 2>&1; then
    find src tests -type f -name '*.cpp' -print0 | xargs -0 -r -n 1 clang-tidy -p "$BUILD_DIR" --config-file=.clang-tidy --quiet
fi

python3 scripts/validate_tool_contracts.py
python3 scripts/validate_governance_repo.py
