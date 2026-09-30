# https://arena.ai/agent can be fully credited for consolidating nearly all of my GitHub repositories because were it not for them, none of this would've been possible! Thank You https://arena.ai/agent Any references in here about a "ZIP" file, is strictly due to https://arena.ai/agent compiling all the work it did there, into a "ZIP" file for me when asked to. So, basically just ignore that part, since I've already extracted that same "ZIP" file before uploading its contents here. All my repositories are a result of either personal work of mine, or work that other had done but I felt needed a personal touch to them. As for what you see here, this is just the beginning...

# ARTEMIS milestone 02

## Contents
- `artemis/`: application source, built frontend, local UI/avatar/worklet/narration assets, retained upstream source, test suites and recorded results, setup/import/verification scripts, dependency declarations, provenance and capability plan.
- `analysis/`: the complete seven-repository design/audit package, including the searchable report, decision ledger, source inventory, diagnostics, architecture and validation records.
- `BUNDLE_SHA256.txt`: integrity hashes for every payload file in this ZIP (excludes itself).

## Local launch (WSL2/Linux)
1. Extract the ZIP and open WSL2 in its `artemis` folder.
2. Run `bash start.sh`.
3. Open http://localhost:8000 and use the operator key printed in your terminal.
4. In Operations, connect your existing Ollama origin and choose an installed model.

The built UI is included; Node/npm is needed only for rebuilding it.

For existing Sage state, import into a fresh destination:
`bash start.sh --data-dir /absolute/path/to/new-artemis-state --import-sage /absolute/path/to/Sage/data`

For optional speech: `bash start.sh --with-speech`, then configure existing model files or compatible engine endpoints in Operations.
For training: install a Torch build matching your CUDA/driver first, then `bash start.sh --with-training`.
For real isolated execution: install working Bubblewrap namespaces (`sudo apt-get install bubblewrap`) or the documented Docker worker.
For World: install Godot 4 / set ARTEMIS_GODOT_BIN, or run `python scripts/setup_optional.py --godot` in the configured Python environment.

Read `artemis/README.md` and `artemis/docs/MILESTONE_02.md` for complete setup, contracts and limits.

## Authentication fix
Both server source and the bundled frontend contain the X-Artemis-Session fix. Standard Authorization remains supported for local clients. The recorded regression test checks the custom header when Authorization is rewritten, and rejects a forged session.

## Verification and limits
Recorded: 52 backend tests and 8 new Chromium UI/HTTP/WebGL checks passed; TypeScript and production build passed; 507 retained original source/asset files match pinned hashes. Current handoff verification checks ZIP integrity, every embedded checksum, workspace/package completeness and authentication-fix inclusion.

No real CUDA/NF4/large local LLM, physical microphone/speaker/lip-sync timing, original Qwen/Parakeet endpoints, Docker backend, completed articulated humanoid/zero-copy World, all diagnostic/adaptive-controller science, or production security certification is claimed.

## Deliberate exclusions
This is the complete milestone-02 application plus audit, not a full mirror of every environment/binary from the original repositories. Installed environments, dependency/model caches, native engine binaries, large model weights, runtime operator credentials and personal Sage databases/history are excluded. Their installation/import is explicit; original local repositories remain unchanged. The complete source inventory/provenance identifies referenced assets. This archive does not grant new rights to third-party assets.
