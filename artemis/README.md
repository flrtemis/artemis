# ARTEMIS — integration milestone 03

**A Reality That Enhances My Integrated Services**. One canonical gateway,
conversation, continuity, jobs/approvals, workspace and capability registry.
Substantial partial unification, **not** every source contribution connected.

[Website / first-run guide](https://flrtemis.github.io/artemis/) (live from `main` + `/`; feature preview requires owner source selection) · [Current twelve-source matrix](docs/CURRENT_CAPABILITIES.md) ·
[Fresh milestone handoff](docs/MILESTONE_03.md) · [Local extensions/example](docs/EXTENSIONS.md)

**New:** approved, versioned JSON-only hot tools in the same durable model
loop; real isolated test before registration, separate invocation approval,
rollback/export; audio yield distinct from job cancellation, safe same-job
corrections and held busy-model inputs. No real Ollama/physical-PC/audio/GPU
proof is implied by scripted-provider tests. The existing Pages deployment is verified separately; no new preview deployment is claimed.

**Additive Sage helper:** available across main views, projecting the same
thread, registry, approvals, files and audio owner. [Current answer-reading slice/tests](docs/SAGE_HELPER_02.md) · [original surface](docs/SAGE_HELPER_01.md), [research](docs/SAGE_HELPER_RESEARCH.md), and [cumulative plan](docs/ONGOING_WORK.md). The owner-only `ideas/` inbox remains read-only/branch-only and is never a runtime or website input.

The sections below continue the milestone-02 architecture. **Their old optional
Godot, CPU training and installed voice-model results are explicitly historical**,
not fresh checks in this session. Current exact commands/counts/skips are in
[verification-03.json](docs/verification-03.json). Originals are preserved.

## Run locally in WSL2/Linux

```bash
cd artemis
bash start.sh
```

Open **http://localhost:8000** and use the **operator key printed by the launcher**. Core Python dependencies install into `.venv`. The built frontend is included; Node is only needed to rebuild it. Your original projects are not edited or replaced. A model-free first task: Workspace → New artifact → review Activity → approve and open the actual file.

Connect your existing Ollama origin and select an installed model in **Operations**. Or launch with:

```bash
ARTEMIS_OLLAMA_URL=http://127.0.0.1:11434 \
ARTEMIS_OLLAMA_MODEL=YOUR_ACTUAL_INSTALLED_TAG bash start.sh
```

Use your actual installed tag and existing WSL Ollama origin/fixed IP. The shown loopback address is only an example; Windows environment does not configure WSL. No second server, replacement model, new hardware or 24 GB WSL setting is prescribed. No LLM weights are downloaded automatically. The hosted preview runs in this shared workspace, **not on your PC**, and cannot reach your PC’s localhost. The same project running locally can use your existing services, models and GPU.

### Installed/cached offline run

```bash
bash start.sh --offline
# First-time setup, without starting the server: bash start.sh --install-only
```

Offline mode never installs packages or resolves public/DNS model/audio endpoints.
Configured private-literal WSL/LAN endpoints still require explicit context/audio
consent. Optional engines themselves need local/cached configuration; this is
not a host firewall or absolute privacy guarantee.

### Reuse an existing Python environment

```bash
ARTEMIS_PYTHON=/absolute/path/to/your/venv/bin/python bash start.sh
```

This avoids copying uploaded environments/binaries. Core packages are installed into the explicitly selected environment; no hidden activation of another project’s server occurs.

## Preserve your Sage continuity

Before first launch, explicitly import a backup-consistent copy:

```bash
bash start.sh --import-sage /absolute/path/to/Sage/data
```

If you already initialized state, choose a **fresh destination**:

```bash
bash start.sh --data-dir /absolute/path/to/new-artemis-state \
  --import-sage /absolute/path/to/Sage/data
```

Stop the old Sage daemon before switching, so the original and imported histories do not keep diverging. Import uses SQLite backup (including committed WAL data), preserves profile/state/history/letters/private entries, projects old user/reply events into one canonical thread with source references, and refuses to overwrite occupied state. It never prints private content or mutates the originals.

Private diary/raw wake/provider-thinking payloads are not served by the UI/event projections. Models receive bounded source-derived context; non-loopback context/audio export requires explicit consent.

## Autonomous Sage

**Operations → Autonomous Sage** exposes interval, operator name and bounded memory/goal/affect/outbox permissions. Scheduling is **opt-in and paused by default**. Configure a real model before enabling it.

- Original Sage moment/system/parser, quality retry, relevance/importance/recency recall, review/lookup and letters are used in the same runtime.
- User turns preempt a pending reflection; stale wake results cannot overwrite intervening interactive activity.
- Rest, private journaling, bounded affect, selected memories/wants and outbox messages remain distinct operations.
- Messages are delivered into the existing Conversation surface. No second independent chat or autonomous daemon server.
- Self-profile changes become exact canonical proposals requiring approval; no silent Genesis/host overwrite.
- Letters use opaque material IDs, not model-supplied paths.

Autonomy still depends on a functioning model. Failed/degenerate output is reported rather than replaced with an anthropomorphic stand-in. No consciousness claim follows from clocks, PAD state or generated reflection.

## Realtime speech

```bash
bash start.sh --with-speech
```

Configure the real local **Whisper model directory** and **Piper ONNX voice file**, or compatible STT/TTS HTTP endpoints in Operations. Existing local voices can be selected; no browser WebSpeech/cloud fallback is silently substituted.

An optional small CPU baseline can be explicitly downloaded:

```bash
.venv/bin/python scripts/setup_optional.py --cpu-speech
```

The helper prints paths to enter in Operations. This optional baseline is not claimed to be your current Qwen/Parakeet/voice profile. For your existing engine stack, configure adapters supplying transcription and PCM16 mono 16k speech; the old speech service must not own a competing LLM/history.

- Original Gemma realtime client, codec and worklets are reused behind a **same-origin, short-lived, single-use authenticated WebSocket grant**.
- One host-owned AudioContext handles speech, MFCC lip-sync, avatar and recorded tours. Text/read-aloud do not require the microphone.
- Actual STT feeds the canonical conversation/tool/approval loop; completed replies produce sentence-chunked real PCM playback.
- Barge-in/audio-yield epochs discard transient stale transcription/synthesis and clear playback, **not durable work**. Explicit job cancel is separate; corrections safely invalidate stale proposals in the same job. Busy follow-ups are held for reconciliation.
- Typed/attachment replies in the same active thread can be read through that same audio owner.
- Local energy/silence VAD is identified honestly as **energy VAD**, not Silero. STT operates on committed utterances; synthesis chunks start after a committed model reply, not fabricated token-by-token inference.

**Historical milestone-02 verification:** actual Piper → PCM → faster-whisper transcription, actual WebSocket PCM output through the same stored thread, cancellation epochs, and browser graph initialization. **Not freshly verified in milestone 03:** your physical microphone/speakers, original Qwen/Parakeet endpoints or live device-level viseme timing.

## Isolated execution

Install working Bubblewrap namespaces on WSL2/Linux:

```bash
sudo apt-get install bubblewrap libseccomp2
```

`run_bash`/`run_python` become available only when a real isolation probe succeeds. Otherwise they fail closed. Jobs have user/pid/mount/network/ipc isolation, a copied workspace, no host home/Sage private state, no host network, resource/output/time limits and reviewed output diffs.

**Execution approval is not file-promotion approval.** Review the staged result and submit `promote_execution_changes`; stale originals or modified job outputs block promotion. No regex/rlimits-only soft execution fallback.

Optional Docker fallback:

```bash
docker build -t artemis-worker:local -f engines/execution/Dockerfile .
```

It uses no network, read-only root, dropped capabilities, unprivileged user and constrained resources. Actual Bubblewrap isolation was tested here; Docker requires a real local daemon/image and was not exercised here.

## Facility, mobile and wrist

**Workspace → Facility** is a projection of the same workspace/actions:

- Original nine-room layout, 26 source scene/geometry builders, furnishings, lighting, monitor/sign textures and paired 8,192-point illustrative brain shapes.
- WASD, sprint, AABB collision, drag-to-look, terminal interaction and shared navigation/actions.
- Recovered touch joystick deadzone/response curve, independent pointer IDs and frame-drained look deltas; no 10×/frame touch stacking.
- Recovered animated wrist geometry with actual artifacts, Sage goals, source room map and audio controls—no mock quest/inventory/radio state.
- Original recorded narration routes through the same audio owner as speech.

External tool labels remain identifiable, but are not claimed installed/running. Full scientific diagnostic/reactivity, every cinematic effect and the recovered alternate expressive controller remain continuation work; the source is preserved. The facility is **spatial UX, not the authoritative embodied World**.

## Training and GPU path

Install a Torch build compatible with your actual GPU/driver in the selected environment first. Then:

```bash
bash start.sh --with-training
```

For explicit CPU conformance only:

```bash
.venv/bin/python -m pip install torch --index-url https://download.pytorch.org/whl/cpu
bash start.sh --with-training
```

**Operations → Training models:** register a real local Hugging Face safetensors model directory. **Laboratory → Training:** choose a contained corpus/device/recipe and propose the run. GGUF files, catalogue entries and mesh/model-name placeholders are not represented as trainable HF weights.

The actual managed worker supports LoRA, CUDA/CPU selection, optional CUDA NF4 with compatible bitsandbytes, checkpointing, layerwise learning rates/warmup/cosine, repaired SAM/replay composite gradients, differentiable student distillation/EMA teacher, Fisher-based EWC, token weights, first-order meta-learning and PCGrad. Metrics identify real CE/perplexity/token accuracy/ECE/gradient/adapter deltas. Jobs have dataset/config/model lineage, pause/resume/cancel, safetensors candidates and explicit evaluation/promotion.

A tiny random fixture is **clearly conformance-only**, cannot be promoted as your production agent, and does not pretend to be a trained Sage/GPU run. Promotion registers an evaluated adapter candidate; it does not secretly convert to GGUF or swap Ollama’s serving model.

**Historical milestone-02 verification:** real CPU Torch/HF/PEFT parameter updates, composite objective paths, managed jobs and checkpoints. **CUDA hardware was absent in milestone 02 and here**, so no GPU/NF4 throughput or your large model’s correctness is claimed verified. Advanced adaptive-controller/rank surgery and full diagnostic science remain explicit continuation work.

## Native World

Install Godot 4 or explicitly download the pinned Linux x86_64 worker:

```bash
.venv/bin/python scripts/setup_optional.py --godot
# Or: ARTEMIS_GODOT_BIN=/absolute/path/to/godot bash start.sh
```

**Laboratory → World:** start an episode, advance/pause/run its independent clock, submit motor/gaze intents, inspect sensors and replay.

Godot owns native capsule/floor/obstacle collisions at 60Hz. The browser is only a projection. Vision is bounded and ray/occlusion tested; immutable sensor frames exclude world seed/full scene truth. Participant tokens authorize **only sensors and bounded intents** and cannot access operator truth, files, continuity or tools. Model actor steps receive sensors/goal with `tools=[]`, not the operator’s scene state. Replay compares recorded sensor hashes for fixed seed/actions.

**Historical milestone-02 verification:** actual Godot dynamics/contacts/occlusion, stale-intent rejection, participant isolation and exact replay in the tested build. This is an authoritative **baseline World**, not a finished articulated humanoid, every biological sensor, zero-copy tensor bridge or a consciousness demonstration.

## Historical milestone-02 verification and remaining scope

- **52 backend tests pass**, including real namespace execution, real Godot, real CPU training and actual CPU speech models where installed.
- **8 new actual Chromium UI/HTTP/WebGL checks pass** across Operations, facility/wrist, native World, shared audio graph and mobile layout.
- TypeScript checking/production build pass; **507 retained source mappings verified** (505 byte-identical blobs plus 2 pinned LFS-pointer/runtime-payload mappings).
- Language-model decisions use deterministic fixtures in tests; a real Ollama model was not available here. No physical audio device or CUDA validation is claimed.

See `docs/MILESTONE_02.md`, test logs/XML, `SOURCE_MAP.json` and `docs/capability-plan.csv`. This is continued integration—not a security/science certification or a claim that every preserved research idea is complete.

## Developer commands

```bash
python -m pytest tests -q
python scripts/verify_sources.py
cd frontend && npm ci && npm run typecheck && npm run build
```

Optional-model tests skip explicitly when their dependencies/model files are absent. Models, personal databases, runtime tokens, installed environments and native engine binaries are excluded from the download; setup is explicit. Original dependency/asset terms remain applicable (the avatar is declared CC BY-NC 4.0). No blanket commercial redistribution rights are granted.
