#!/usr/bin/env bash
set -euo pipefail

: "${PYTHON:=python}"
: "${RUFF:=ruff}"

if [ "$PYTHON" = "python" ] && [ -x ".venv/bin/python" ]; then
  PYTHON=".venv/bin/python"
fi

if [ "$RUFF" = "ruff" ] && [ -x ".venv/bin/ruff" ]; then
  RUFF=".venv/bin/ruff"
fi

"$PYTHON" -m pytest
"$RUFF" check .
"$RUFF" format --check .
