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

mkdir -p "$LOG_DIR"

if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
  echo "tmux session '$SESSION_NAME' already exists. Attach with:" >&2
  echo "  tmux attach -t $SESSION_NAME" >&2
  exit 1
fi

shell_quote() {
  printf "%q" "$1"
}

PROMPT_Q="$(shell_quote "$PROMPT")"
ROOT_Q="$(shell_quote "$(pwd)")"

CLAUDE_CMD="cd $ROOT_Q && claude -p $PROMPT_Q | tee \"$LOG_DIR/claude.txt\"; echo; echo '[Claude finished]'; exec \$SHELL"
CODEX_CMD="cd $ROOT_Q && codex exec $PROMPT_Q | tee \"$LOG_DIR/codex.txt\"; echo; echo '[Codex finished]'; exec \$SHELL"
OPENCODE_CMD="cd $ROOT_Q && opencode run $PROMPT_Q | tee \"$LOG_DIR/opencode.txt\"; echo; echo '[OpenCode finished]'; exec \$SHELL"
AGY_CMD="cd $ROOT_Q && agy --print $PROMPT_Q | tee \"$LOG_DIR/antigravity.txt\"; echo; echo '[Antigravity finished]'; exec \$SHELL"

tmux new-session -d -s "$SESSION_NAME" -n showcase
tmux split-window -h -t "$SESSION_NAME":0
tmux split-window -v -t "$SESSION_NAME":0.0
tmux split-window -v -t "$SESSION_NAME":0.1
tmux select-layout -t "$SESSION_NAME":0 tiled

tmux select-pane -t "$SESSION_NAME":0.0 -T "Claude"
tmux select-pane -t "$SESSION_NAME":0.1 -T "Codex"
tmux select-pane -t "$SESSION_NAME":0.2 -T "OpenCode"
tmux select-pane -t "$SESSION_NAME":0.3 -T "Antigravity"

tmux send-keys -t "$SESSION_NAME":0.0 "$CLAUDE_CMD" C-m
tmux send-keys -t "$SESSION_NAME":0.1 "$CODEX_CMD" C-m
tmux send-keys -t "$SESSION_NAME":0.2 "$OPENCODE_CMD" C-m
tmux send-keys -t "$SESSION_NAME":0.3 "$AGY_CMD" C-m

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
