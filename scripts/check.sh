#!/usr/bin/env bash
set -euo pipefail

: "${PYTHON:=python}"
: "${RUFF:=ruff}"
: "${BLACK:=black}"

if [ "$PYTHON" = "python" ] && [ -x ".venv/bin/python" ]; then
  PYTHON=".venv/bin/python"
fi

if [ "$RUFF" = "ruff" ] && [ -x ".venv/bin/ruff" ]; then
  RUFF=".venv/bin/ruff"
fi

if [ "$BLACK" = "black" ] && [ -x ".venv/bin/black" ]; then
  BLACK=".venv/bin/black"
fi

"$PYTHON" -m pytest
"$RUFF" check .
"$BLACK" --check .
