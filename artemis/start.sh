#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
args=(); speech=0; training=0; install=1; install_only=0
for arg in "$@"; do
 case "$arg" in
  --with-speech) speech=1;;
  --with-training) training=1;;
  --no-install) install=0;;
  --offline) install=0; export ARTEMIS_OFFLINE=1; args+=("$arg");;
  --install-only) install_only=1;;
  *) args+=("$arg");;
 esac
done
if [[ "${ARTEMIS_OFFLINE:-0}" == 1 ]]; then install=0; fi
if [[ -n "${ARTEMIS_PYTHON:-}" ]]; then
 py="$ARTEMIS_PYTHON"
else
 if [[ ! -d .venv ]]; then
  if [[ $install == 0 ]]; then echo 'No environment installed. Run bash start.sh --install-only once with Internet access, or select an existing ARTEMIS_PYTHON.' >&2; exit 1; fi
  python3 -m venv .venv
 fi
 py=".venv/bin/python"
fi
if [[ $install == 1 ]]; then
 "$py" -m pip install -r requirements.txt
 if [[ $speech == 1 ]]; then "$py" -m pip install -r requirements-speech.txt; fi
 if [[ $training == 1 ]]; then
  "$py" -c 'import torch' || { echo 'Install the correct Torch CPU/CUDA build into this environment first. See README.' >&2; exit 1; }
  "$py" -m pip install 'transformers>=4.50,<5' 'peft>=0.15,<1' 'safetensors>=0.5,<1'
 fi
else
 "$py" -c 'import fastapi,uvicorn,numpy,pandas,httpx,jsonschema,multipart' || { echo 'Dependencies missing. Offline/no-install mode never downloads them. See README.' >&2; exit 1; }
fi
if [[ ! -f web/index.html ]]; then
 if [[ $install == 0 ]]; then echo 'Built UI missing. Rebuild explicitly with npm ci && npm run build in frontend while online.' >&2; exit 1; fi
 (cd frontend && npm ci && npm run build)
fi
if [[ $install_only == 1 ]]; then echo 'Dependencies and built UI ready. No model weights downloaded. Start with bash start.sh --offline (or --no-install).'; exit 0; fi
exec "$py" run.py "${args[@]}"
