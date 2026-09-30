#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
args=(); speech=0; training=0
for arg in "$@"; do
 case "$arg" in
  --with-speech) speech=1;;
  --with-training) training=1;;
  *) args+=("$arg");;
 esac
done
if [[ -n "${ARTEMIS_PYTHON:-}" ]]; then
 py="$ARTEMIS_PYTHON"
else
 if [[ ! -d .venv ]]; then python3 -m venv .venv; fi
 py=".venv/bin/python"
fi
"$py" -m pip install -r requirements.txt
if [[ $speech == 1 ]]; then "$py" -m pip install -r requirements-speech.txt; fi
if [[ $training == 1 ]]; then
 "$py" -c 'import torch' || { echo 'Install the correct Torch CPU/CUDA build into this environment first. See README.'; exit 1; }
 "$py" -m pip install 'transformers>=4.50,<5' 'peft>=0.15,<1' 'safetensors>=0.5,<1'
fi
if [[ ! -f web/index.html ]]; then (cd frontend && npm ci && npm run build); fi
exec "$py" run.py "${args[@]}"
