#!/usr/bin/env python3
"""Compatibility wrapper for the installable ccfddl-query CLI."""
# ruff: noqa: E402, I001

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ccfddl_skills.query_conferences import main


if __name__ == "__main__":
    raise SystemExit(main())
