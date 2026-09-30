#!/usr/bin/env bash
# run.sh — start her in the background and keep a log. `tail -f awake.log` to watch.
cd "$(dirname "$0")"
export AWAKE_LLM_BASE_URL="${AWAKE_LLM_BASE_URL:-http://127.0.0.1:11434/v1}"
export AWAKE_LLM_MODEL="${AWAKE_LLM_MODEL:-gemma4:12b}"
if pgrep -f "python3 -m awake" >/dev/null; then echo "already running (pid $(pgrep -f 'python3 -m awake' | head -1))"; exit 0; fi
nohup python3 -m awake >> awake.log 2>&1 &
sleep 1
echo "started pid $! — http://localhost:${AWAKE_PORT:-8770}  (log: $(pwd)/awake.log)"
