# Milestone 02 verification

52 backend tests pass (0 skipped in this prepared sandbox); see `test-results-02.xml` / `test-run-02.log`.

Includes all 32 original contracts plus 20 new autonomy, isolation, World, training and speech tests. Actual Bubblewrap, Godot, Torch/HF/PEFT, Piper and faster-whisper were exercised; fixtures control language-model outputs. Optional dependency/model tests skip explicitly on machines without those assets.

8 new actual Chromium checks pass: authenticated worker controls, real source facility, wrist nine-room mapping, canonical room navigation, native World projection/ticks, host-owned TalkingHead/HeadAudio graph, mobile layout and zero uncaught exceptions. See `browser-results-02.json`. The earlier 11 UI checks remain recorded as milestone 01 results; they are not represented as a fresh milestone 02 re-run.

TypeScript and production build pass. All 507 retained original source/asset hashes pass. Original repositories unchanged.

Limits: no CUDA/NF4/large user model inference, physical microphone/speakers/live lip-sync device timing, original external Qwen/Parakeet endpoints, Docker runtime, cross-platform floating-point replay identity, complete articulated World or security/scientific certification.

The CPU training fixture is random/conformance-only, cannot be promoted as Sage, and performs actual gradient updates; it is not a fabricated GPU graph. Native speech tests generate real PCM with a downloaded optional baseline voice/model (cache excluded from delivery), not a claim about the user’s original voice profile.

Two non-failing library warnings: Starlette TestClient recommends httpx2; PEFT adjusts fan_in_fan_out for the fixture GPT2 Conv1D layer.

Re-run: `python -m pytest tests -q`; `python scripts/verify_sources.py`; `cd frontend && npm ci && npm run typecheck && npm run build`.
