#!/usr/bin/env bash
# Run a skill's evals headlessly in Codex on a throwaway copy of the skill directory.
# Usage: ./run_evals.sh [skill] [case-id]   -> outputs in $OUT (default: mktemp)
# Grading is by hand against the expectations in evals.json; record the result in last_run.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")" && pwd); SKILL=${1:-ccfddl-query}; ONLY=${2:-}
SRC=$ROOT/skills/$SKILL; OUT=${OUT:-$(mktemp -d)}; mkdir -p "$OUT"
python3 - "$SRC/evals/evals.json" <<'PY' | while IFS=$'\x1f' read -r id prompt; do
import json,sys
for e in json.load(open(sys.argv[1]))["evals"]:
    print(e["id"], e["prompt"], sep="\x1f")
PY
  [ -n "$ONLY" ] && [ "$id" != "$ONLY" ] && continue
  W=$OUT/$SKILL-$id; rm -rf "$W"; cp -R "$SRC" "$W"; rm -rf "$W/evals"
  codex exec --skip-git-repo-check -s workspace-write -C "$W" --json -o "$W.reply.md" \
    "$prompt（skill 文件：SKILL.md，在当前目录）" > "$W.log.jsonl" 2>&1 < /dev/null || echo "case $id: codex exit $?"
  diff -rq -x __pycache__ -x evals "$SRC" "$W" > "$W.diff.txt" || true
  echo "case $id -> $W"
done
echo "outputs: $OUT"
