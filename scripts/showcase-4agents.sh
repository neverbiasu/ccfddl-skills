#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 1 ]]; then
  cat <<'EOF'
Usage: scripts/showcase-4agents.sh "your prompt"

Creates a 2x2 tmux layout that runs the same prompt through:
  - Claude Code
  - Codex
  - OpenCode
  - Antigravity

Example:
  scripts/showcase-4agents.sh "我做 Relighting，有哪些会议可以考虑？"
EOF
  exit 1
fi

if ! command -v tmux >/dev/null 2>&1; then
  echo "tmux is required but was not found on PATH." >&2
  exit 1
fi

for cmd in claude codex opencode agy; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Required command not found on PATH: $cmd" >&2
    exit 1
  fi
done

PROMPT="$1"
SESSION_NAME="ccfddl-showcase"
STAMP="$(date +%Y%m%d-%H%M%S)"
LOG_DIR="/tmp/${SESSION_NAME}-${STAMP}"
PROMPT_FILE="$LOG_DIR/prompt.txt"

mkdir -p "$LOG_DIR"
printf '%s\n' "$PROMPT" >"$PROMPT_FILE"

if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
  echo "tmux session '$SESSION_NAME' already exists. Attach with:" >&2
  echo "  tmux attach -t $SESSION_NAME" >&2
  exit 1
fi

ROOT_DIR="$(pwd)"

write_runner() {
  local path="$1"
  local label="$2"
  local command="$3"
  cat >"$path" <<EOF
#!/usr/bin/env bash
set -euo pipefail
cd $(printf '%q' "$ROOT_DIR")
$command | tee "$LOG_DIR/$label.txt"
echo
echo '[$label finished]'
exec "\$SHELL"
EOF
  chmod +x "$path"
}

CLAUDE_RUNNER="$LOG_DIR/run-claude.sh"
CODEX_RUNNER="$LOG_DIR/run-codex.sh"
OPENCODE_RUNNER="$LOG_DIR/run-opencode.sh"
AGY_RUNNER="$LOG_DIR/run-antigravity.sh"

write_runner \
  "$CLAUDE_RUNNER" \
  "Claude" \
  "claude -p < $(printf '%q' "$PROMPT_FILE")"

write_runner \
  "$CODEX_RUNNER" \
  "Codex" \
  "codex exec - < $(printf '%q' "$PROMPT_FILE")"

write_runner \
  "$OPENCODE_RUNNER" \
  "OpenCode" \
  "opencode run \"\$(cat $(printf '%q' "$PROMPT_FILE"))\""

write_runner \
  "$AGY_RUNNER" \
  "Antigravity" \
  "agy --print \"\$(cat $(printf '%q' "$PROMPT_FILE"))\""

tmux new-session -d -s "$SESSION_NAME" -n showcase
tmux split-window -h -t "$SESSION_NAME":0
tmux split-window -v -t "$SESSION_NAME":0.0
tmux split-window -v -t "$SESSION_NAME":0.1
tmux select-layout -t "$SESSION_NAME":0 tiled

tmux select-pane -t "$SESSION_NAME":0.0 -T "Claude"
tmux select-pane -t "$SESSION_NAME":0.1 -T "Codex"
tmux select-pane -t "$SESSION_NAME":0.2 -T "OpenCode"
tmux select-pane -t "$SESSION_NAME":0.3 -T "Antigravity"

tmux send-keys -t "$SESSION_NAME":0.0 "bash $(printf '%q' "$CLAUDE_RUNNER")" C-m
tmux send-keys -t "$SESSION_NAME":0.1 "bash $(printf '%q' "$CODEX_RUNNER")" C-m
tmux send-keys -t "$SESSION_NAME":0.2 "bash $(printf '%q' "$OPENCODE_RUNNER")" C-m
tmux send-keys -t "$SESSION_NAME":0.3 "bash $(printf '%q' "$AGY_RUNNER")" C-m

cat <<EOF
Created tmux session: $SESSION_NAME
Prompt: $PROMPT
Logs: $LOG_DIR

Attach with:
  tmux attach -t $SESSION_NAME

Suggested recording flow:
  1. Open Recordly and select the tmux window area.
  2. Start recording.
  3. Run: tmux attach -t $SESSION_NAME
  4. Stop recording after the four panes finish.
EOF
