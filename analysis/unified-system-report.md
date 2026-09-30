# ARTEMIS: seven repositories, one coherent system

**Source-grounded unification design · 29 September 2026**  
**Proposed product:** ARTEMIS, a local-first agent workspace with Sage as its continuity-bearing companion.

> Preserve valuable mechanisms and experiences. Merge equivalent implementations and workflows. Retire duplication, misleading success and unsafe execution—not the history or research intent.

## 1. Executive decision

Do **not** combine these projects by putting their existing applications behind a launcher or embedding seven interfaces in a dashboard. Build one application around a shared domain model:

- **Sage supplies persistent identity, memory, affect and continuity.**
- **Local Ollama Arena Agent supplies the strongest reusable task/tool/workspace/approval foundation.**
- **Agent contributes dynamic tools, voice-first interaction, self-inspection/change experiments, and useful plugin ideas.**
- **Gemma Avatar supplies the primary real-time speech and expressive-avatar subsystem.**
- **Command Center supplies the spatial workspace, file Atlas, immersive presentation and recovered mobile/compact controls.**
- **Neural Sim supplies the training, instrumentation, biological-reference and adaptation laboratory.**
- **Universe supplies the specification for a genuinely embodied experimental world—not an already implemented world engine.**

The correct integration unit is a **capability with a single owner, state model and canonical workflow**, not a repository. A useful alternative renderer, specialized research mechanism or different domain is not duplication merely because its screen or vocabulary resembles another.

**Proposed topology:** a Python modular monolith with an authenticated gateway and SQLite-backed durable state, plus isolated execution, model/training, speech and world workers where isolation or timing requires them. A single component-based TypeScript frontend owns the composer, artifacts, activity, approvals, settings and inspectors. Three.js and Web Audio become shared infrastructure, not independent applications.

This is a design and migration plan, **not a claim that the unified product has been implemented or that all source projects run successfully**. The companion ledger contains **146 explicit decisions: 45 preserved, 51 merged, 46 transformed and 4 retired**. Some retained items are specifications or experiments, not working features.

## 2. What was actually inspected

The audit covers all seven exact source trees, authored/project-level implementations, tests, configuration, meaningful assets and public history—not just README summaries.

| Repository | Snapshot | Tracked files | Public commits |
|---|---|---:|---:|
| command-center | `5226291` | 387 | 1 |
| agent | `a09f1d2` | 32 | 1 |
| local_ollama_arena_agent | `c95d307` | 2,710 | 7 |
| gemma-avatar | `c4becc8` | 1,785 | 76 |
| Sage | `701f917` | 27 | 21 |
| neural-sim | `b51dda7` | 14 | 16 |
| universe | `458915e` | 3 | 3 |

**4,958 tracked files** were inventoried with hashes, sizes, classifications and commit-pinned source URLs. All 79 project-level implementation files, four tests and the exact `agent.txt` duplicate have disposition mappings. Thousands of vendored/environment files were classified rather than misleadingly counted as authored functionality or claimed to have had a line-by-line third-party security audit.

Public history contains 125 commits, mostly recent uploads. Gemma's embedded bundle adds 12 recoverable July 3, 2026 commits. These histories preserve useful provenance but do **not** establish years of public Git history; equally, their shortness does not establish the age of the underlying work. Current-versus-bundle differences, deleted meaningful files and recovered dashboard branches were reviewed. [G.bundle](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/gemma-avatar.bundle)

Validation included 61 Python AST parses; 18 passing authored/embedded JS/shell syntax checks and one failure; the three Sage scripts reporting 60 checks (one assertion is vacuous); a 38-record bounded source harness; and seven passing codec/worklet fixtures. Those checks did **not** run real GPU models, real browsers/audio devices, the speech backend, live media/search providers or the integrated applications. See `audit-validation.md` for exact scope, results and limitations.

## 3. Contributions of each repository

### 3.1 Command Center — the spatial workspace and recovered interaction design

This is substantially more than a launch-page mockup. Its authored client constructs a walkable facility with collision/navigation, procedural rooms/materials/furniture/signage, service terminals, lighting/bloom, particles, footsteps/ambient audio, tour narration and cinematic mode transitions. The paired 8,192-point brain clouds have metric-driven shaders, activity patterns, synapse arcs and diagnostic HUDs. [C.main](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/dashboard_3d.html#L806-L6330)

Its **file galaxy** is meaningful information-navigation work: spiral remapping, shader-based points/nebulae, search/results, source toggles, density and size filters, raycast selection and camera fly-to. The supplied datasets are 5,000, 25,000 and 49,998 plotted records; the 1,748,673 indexed-file figure is snapshot metadata, not evidence of a live indexer supplied in these repositories. Keep the renderer and interaction, then connect it to a consented Workspace index. [C.main](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/dashboard_3d.html#L806-L6330) [C.gal50](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/galaxy_50k.json#L1-L1)

The recovered May 3/Pip-Boy branch matters. It adds mobile joystick/multitouch controls, frame-drained look input, a wrist-device/arm interaction and a Sage avatar prototype. Its inventory/quests/map/radio content is mock, but the compact interaction is not. The separate avatar script includes procedural rig/mouth/face/gaze/idle behavior, browser speech/chat paths and MediaRecorder export. Missing referenced mesh/texture or API assets must be handled honestly. [C.recovered](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/dashboard_3d_may3_pipboy_sage.html#L697-L4443) [C.avatar](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/sage_avatar.js#L1-L1472)

Command Center also contains practical repairs absent from Neural Sim: local Bio imports, correct delay-buffer initialization order, cortical-sized conductance arrays, local Three.js imports and a dashboard duplicate-name fix. The repaired Bio constructor and five finite steps pass bounded tests; remaining numerical/scientific defects still require work. Its metrics and dataset modules are exact copies of Neural Sim's. [C.bio](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/bio_model.py#L153-L1073) [C.metrics](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/metrics.py#L22-L824) [C.dataset](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/dataset_analyzer.py#L55-L1603)

**Do not mistake its catalog for shipped tools.** The 17 service entries reference ARTEMIS/Sage, ears, CSM voice, Neural Sim, portable server/tunnel, comms, converter, gateway/router, Android mirror, Ghidra, Frida, packet tools, scripts/hooks, playbooks, APK references and a hosted multimodal Sage space. Most implementations are not in these seven repositories. The hosted Gradio/DashScope-labelled “Sage” is not the local continuity system. Preserve them as external connector specifications with truthful availability. The demo's Bio/dataset logic is real source; AI metrics/self-modification/status are synthetic and launch/stop returns 501. [C.main](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/dashboard_3d.html#L806-L6330) [C.demo](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/demo/demo_server.py#L31-L223)

**Destination:** Workspace spatial mode and shared diagnostic rendering; mobile and wrist presentation survive. Neither current nor recovered HTML remains an independently owned application.

### 3.2 Agent — extensibility, voice identity and gated self-improvement ideas

The two Python monoliths include the Sanctum UI, CSS avatar/voice-first presentation, WebSpeech, Piper, a bounded Ollama tool loop, JSON tool discovery, dynamic Python-tool creation and Bubblewrap execution. `agent2.py` adds structured feeling/debug state, richer expressions and refusal/delegation controls; `agent.txt` is an exact copy of `agent2.py`, not another capability. [A.base](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent.py#L37-L1531) [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031) [A.duplicate](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent.txt#L1-L2031)

The valuable idea is **an agent that can propose new capabilities and inspect/change itself**. Preserve tool generation, state presentation, proposal history and Genesis's self-reading/backup/evolutionary trace—but transform them into a versioned, tested, approved lifecycle. Registration currently permits path traversal and invalid Python; both were reproduced without executing generated code. Bubblewrap's mounts do not provide a suitable writable task workspace, network permission is inferred from names, and the delegation branch returns a canned message rather than creating workers. A debug-inspection declaration is not wired into dispatch. [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031) [A.genesis](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/genesis.py#L1-L98)

The plugins include math, clock, directory/file operations, fetch/scrape modes, password/address generation and a Python interpreter idea. Preserve useful functions through the common registry, not ten independent trusted host-path scripts. The interpreter lacks the required `execute` entrypoint; `list_tools` is canned; password generation needs cryptographic randomness; the Gmail helper only generates strings, not accounts or mail access. [A.python](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/python_interpreter.py#L1) [A.list](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/list_tools.py#L1) [A.password](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/password_generator.py#L1) [A.gmail](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/gmail_email_generator.py#L1)

The separate CLI speech experiment provides true token/sentence streaming, slash controls and batch tool handling; this is useful even though its history tail is duplicated, playback blocks generation, and its weather function is a fixed demo. Piper's native error branch does not fall through to its CLI alternative, and can return empty audio; provider fallback and timeouts need repair. Browser WebSpeech is not a guaranteed offline recognizer. The nine unregistered operational proposals in `upgrades.txt` are all retained in the proposal appendix. [A.readaloud](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/read_aloud.py#L1-L249) [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031) [A.upgrades](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/upgrades.txt#L1-L339)

**Destination:** common Agent runtime, plugin lifecycle, speech providers, fallback avatar and change laboratory. No separate Sanctum chat, tool inventory, self-modification authority or memory.

### 3.3 Local Ollama Arena Agent — the task and workspace foundation

This is the strongest reusable starting point for local task execution: an Ollama tool loop with native/JSON fallback, 21 registered tools, upload/output/workspace handling, approvals, browser previews and configuration/security documentation. The 21 tools cover eight file operations, bash, fetch/search/image search, image/video/speech generation, transcription, and DOCX/XLSX/PPTX/PDF/CSV generation. [R.agent](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/agent.py#L1) [R.tools](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/base.py#L1) [R.files](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/files.py#L1) [R.web](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/web.py#L1) [R.media](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/media.py#L1) [R.docs](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/documents.py#L1)

Its file containment is meaningfully stronger than Agent's direct scripts: relative traversal and symlink escapes are rejected, and upload basenames/collisions are handled. Minimal document containers and bounded editing/shell cases pass. Fuzzy editing works; removal of a trailing newline is a formatting-policy issue, not a failed edit. Preserve these strengths. [R.workspace](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/workspace.py#L1) [R.files](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/files.py#L1)

The orchestration still needs fundamental fixes. Only the first native call in a batch is processed; a fixture reproduced losing the second. Schema requirements are not enforced: `write_file` without required content creates an empty file. State is shared and volatile, auth/session isolation is absent, and approval/job resumption is not durable. Its default soft command policy/rlimits do not isolate arbitrary host access; optional Docker was not exercised. These cannot become the unified system's trust boundary unchanged. [R.agent](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/agent.py#L1) [R.tools](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/base.py#L1) [R.bash](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/bash.py#L1) [R.server](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/server.py#L1)

Media generation/transcription mostly consists of adapters to configured engines/commands; the engines are not bundled. The 755-record / 642-distinct-name capability catalogue is reference metadata, not access to those providers or models. Minimal OOXML containers are not equivalent to Office rendering validation. Keep capabilities, explicitly distinguish installed/ready/disabled/demo/unavailable, and show that same status everywhere. [R.catalog](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/uploads/arena-ai-agent-full-model-and-capabilities-list.json#L1) [R.mapping](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/docs/CAPABILITY_MAPPING.md#L1) [R.media](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/media.py#L1) [R.docs](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/documents.py#L1)

**Destination:** scoped task orchestration, common registry, Workspace/artifacts, approvals and optional provider adapters. Keep its reusable contracts—not its independent web server/session.

### 3.4 Gemma Avatar — the expressive and real-time audio subsystem

The key contribution is a real integration of TalkingHead and HeadAudio: audio-derived visemes, gaze/idle breathing/blinking, response choreography, moods/gestures/expressions and one shared audio graph. It does not need to own identity, memory or a second conversational agent. [G.avatar](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/avatar.js#L1)

The speech client/worklets preserve sophisticated work: 16 kHz PCM/40 ms capture, resampling/clipping/noise gating, playback buffering/fades, local speech detection, barge-in, cancellation, late-event handling, transcript finalization, serialized responses/tools and multiple realtime event/content formats. Seven synthetic codec/worklet checks pass, but real microphone/playback/lip-sync/WebSocket/backend behavior is unvalidated. [G.mic](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/public/worklets/mic-capture.js#L1) [G.play](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/public/worklets/audio-playback.js#L1) [G.client](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/s2s/s2s-ws-client.js#L1) [G.codec](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/s2s/codec.js#L1)

Hosted grants, queue/health/polling/cancellation/logs and local WebSocket mode are useful provider alternatives, not separate products. The current branch adds typed chat/media/text-event compatibility beyond the recovered bundle. However, start still requests the microphone, so typed conversation is not truly independent of mic permission. The Avatar Parts helper/UI is not wired into a functional inspector. Preserve both intentions, fix the former and scope the latter as asset-inspection backlog. [G.server](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/index.ts#L1) [G.app](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/app.js#L1) [G.client](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/s2s/s2s-ws-client.js#L1)

Its local launcher imports an external speech-to-speech engine and patches timeout/upload/Parakeet/Qwen GGUF integration; neither that engine nor the large weights is supplied here. Keep the adapters and Torch/GGUF/cache profiles under a pinned worker interface. The recorded hash manifest is stale (17 of 31 match), and the Python “lock” contains `>=` ranges. The brunette GLB contains a usable rig and morphs, with no embedded animations; its declared CC BY-NC 4.0 terms matter for distribution. [G.launcher](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/local_s2s_launcher.py#L1) [G.s2sstart](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/start-speech-to-speech.sh#L1) [G.sha](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/SHA256SUMS.txt#L1) [G.requirements](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/gemma-avatar-s2s-requirements-lock.txt#L1) [G.glb](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/public/avatars/brunette.glb) [G.readme](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/README.md#L1)

**Destination:** shared speech service, primary Presence renderer, realtime protocol adapter and rights-aware avatar library. Text, voice and avatar use one conversation/thread and cancellation model.

### 3.5 Sage — persistence, identity and continuity

Sage contributes something the other chat shells do not: SQLite events/memories/wants/private entries, a versioned self-profile, local clock and offline-gap awareness, autonomous wakes/reviews, letters/pending material, salience/recency/relevance recall and constrained `look_back` modes. Its PAD state has decays, targets, drives and mappings suitable for an affect/presentation policy. Do not replace this with a rolling chat list or call it equivalent to fine-tuning. [S.memory](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/memory.py#L1) [S.self](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/selfmodel.py#L1) [S.clock](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/clock.py#L1) [S.daemon](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/daemon.py#L1) [S.state](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/state.py#L1) [S.mind](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/mind.py#L1)

Its Ollama adapter includes `think:false`, context/keep-alive/prewarm/fallback defaults, alongside OpenAI-compatible and deterministic stand-in paths. Quality guards detect/retry garble/repetition. The SSE dashboard/API provides live continuity views, self/memory/wants/journal/context/export and say/wake interaction. Three scripts report 60 checks; one `or True` assertion cannot prove echo exclusion. [S.backend](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/backends.py#L1) [S.tests1](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/tests/test_continuity.py#L1) [S.tests2](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/tests/test_lookback.py#L1) [S.tests3](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/tests/test_ollama_path.py#L1) [S.server](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/server.py#L1) [S.ui](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/web/index.html#L1)

Continuity requires privacy, not just persistence. Synthetic tests reproduced key-order-sensitive private scrubbing and traversal through letter names. Generated raw reflection/thought fields and unrestricted APIs need structured visibility policy; current tests do not certify privacy. The daemon also shadows `Thread._stop` with an Event and needs a clean-stop/join regression. Preserve actual committed user identity/history/database state privately through explicit migration—never as default installation data or public report contents. [S.daemon](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/daemon.py#L1) [S.server](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/server.py#L1) [S.data](https://github.com/flrtemis/Sage/tree/701f917eab403c32263deb08a85de24f59514518/data)

**Destination:** the system's continuity/identity/affect service and context builder. Autonomous wakes become scoped jobs of the same Agent runtime. Persistent behavior is not evidence of consciousness.

### 3.6 Neural Sim — the experimental learning and diagnostics laboratory

Neural Sim has substantial authored research mechanisms: NF4/double quantization, LoRA loading, forward/backward hooks, SAM, layerwise LR decay, warmup/SGDR, replay/priorities, PCGrad, EWC, EMA teacher/distillation, gradient noise/clipping, pruning/dead-neuron detection, a meta-learning step, training/inference control and an adaptive-parameter controller. These are distinct mechanisms, not redundant versions of “learning.” Retain them as optional recipes with explicit compatibility and evaluation. [N.loader](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/model_loader.py#L1) [N.hooks](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/hooks.py#L1) [N.trainer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/trainer.py#L1) [N.selfmod](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/self_modify.py#L1)

But branch presence is not effectiveness. Distillation uses detached student logits; replay can overwrite SAM gradients; the meta path is first-order-style; token importance is computed but unused; rank adaptation logs instead of resizing modules. GP/population/curriculum/planning are incomplete; fitness updates member zero; confidence records equal before/after loss; rollback restores parameters but not full training state. Repair and validate before enabling automatic control. [N.trainer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/trainer.py#L1) [N.selfmod](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/self_modify.py#L1)

The metrics schema declares 48 AI families and 63 fields, but several labels are scientifically misleading: mutual information is activation norm; CKA/information flow are adjacent norm ratios; “sharpness” is loss variance; “Hessian trace” is squared gradient/random-dot energy; spectral radius is a singular value; ECE uses a loss proxy; gradient direction uses vectors of norms; accuracy is never assigned. Preserve the diagnostic questions, merge actual repeated calculations and correct the measurements. The dedicated appendix covers all 48 families and all 41 Bio fields. [N.metrics](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/metrics.py#L1)

Its independent Bio engine models a 1,090-neuron cortex/thalamus/cerebellum with delays, conductance, STDP, homeostasis, pruning, modulators, apical signals, bands/synchrony and visual helpers. The original constructor fails; Command Center provides three real fixes, but GABA sign/count/delay/time/frequency semantics still need work. Actual cortical inhibitory classification is 50 cells versus the declared 200. Five finite steps are only a smoke test. [N.bio](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/bio_model.py#L1) [C.bio](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/bio_model.py#L153-L1073)

Dataset analysis truly handles CSV/JSON/text with statistics/units/findings; JSONL/TSV/YAML/XML/PDF are not properly supported as their advertised structures. Human/AI cognitive frames are scripted educational projections, not measured cognition; WebSocket broadcast raises `UnboundLocalError`. The process/workspace host and training server have different responsibilities, despite overlapping transport; the root references a missing static page/config/package structure. `prepare_model.py` prepares an OBJ/MTL/texture via face subsampling, not LLM weights, and should become a proper avatar import/optimization utility. [N.dataset](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/dataset_analyzer.py#L1) [N.workspaceServer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/dashboard_server.py#L1) [N.trainingServer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/server.py#L1) [N.launch](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/launch.py#L1) [N.mesh](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/prepare_model.py#L1)

**Destination:** Lab workers and recipes, a typed diagnostics registry, shared dataset ingestion and asset tools. Retire its duplicate dashboard, not its experiments or independent Bio model.

### 3.7 Universe — a specification for embodied causal agency

Universe is entirely a blueprint repository. Its strongest idea is an epistemic boundary:

**authoritative world → partial immutable sensors → belief/workspace → intention/controller → physical consequences**.

It specifies body/self/attention models, prediction/uncertainty, persistence, decoupled clocks, isolation/replay, theory-informed ablations and precautionary welfare/stop conditions. Those should become testable contracts, not marketing claims that an inhabited world or conscious avatar already exists. The literature references were read as part of the blueprint, not independently fact-checked. [U.blueprint](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/living_avatar_subjective_experience_blueprint_v0_3.md#L1)

The earlier proposal also contains distinct experiments: direct activation-to-physics, semantic indirect force/control, implicit attention-to-gaze/world mapping, transient versus persistent loops, zero-copy LibTorch/C++ integration and a minimal sphere/gravity sandbox. Preserve these ideas with different dispositions. Semantic control fits the controller architecture; arbitrary “thinking bends gravity” needs an explicit bounded intervention; attention weights are not inherently gaze/intention; zero-copy is an optional optimization after a simple transport is profiled, not an assumed browser/GPU capability. [U.initial](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/Initial-Blueprint.txt#L1) [U.blueprint](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/living_avatar_subjective_experience_blueprint_v0_3.md#L1)

**Destination:** a Lab World engine with an isolated participant view, deterministic trials and the same Agent runtime under sensor-only permissions. It is not the file Atlas, a conversational avatar stage or the Bio reference simulation.

## 4. Similarity is not duplication

### Genuine overlaps to merge

| Overlap | Evidence / difference | One superior implementation |
|---|---|---|
| Metrics and dataset modules in Command/Neural | Byte-identical copies | One typed diagnostics module and one format-aware ingestion/analyzer |
| Command/Neural Bio engines | Same lineage; Command adds three real repairs | One Bio worker, based on repaired fork plus correctness fixes |
| Current/recovered/Neural 3D dashboards | Same facility/brain lineage, not equal feature sets | Current fixes + galaxy + recovered touch/wrist/avatar contributions |
| `agent.txt` and `agent2.py` | Exact duplicate | One Agent module; archive text copy |
| Chat, mic, transcripts and voice playback | Multiple shells independently own them | One composer/turn stream and audio graph |
| Tool discovery, file ops, retrieval and shell | Equivalent capabilities, unequal safety/contracts | One canonical tool per operation behind one validated registry/policy |
| Settings, launch/status, logs and previews | Multiple partial route/UI stacks | One config, supervisor, activity stream and artifact viewer |
| Norm-ratio “CKA” / “information flow”, attention-balance “expert” proxy | Repeated formulas with misleading different labels | One honest calculation each; proper distinct science remains a separate research requirement |

### Similar-looking work that must remain distinct

| Do not collapse | Why they differ | Shared infrastructure only |
|---|---|---|
| Episodic memory vs weight training | One persists events/context; the other changes learned parameters | Provenance, explicit dataset export and consent |
| Self-profile edits vs code/plugins vs hyperparameters vs weights | Different artifacts, risks, permissions and rollback | One ChangeProposal language and approval service |
| PAD affect vs expression vs Bio modulators vs body signals | State dynamics, public presentation, reference simulation and physical feedback | Explicit adapters and separate namespaces |
| CSS/procedural avatar vs TalkingHead vs embodied body | Accessibility/fallback, conversational expression and causal motor embodiment | Rig/assets/rendering interfaces |
| File galaxy vs command facility vs World | Information navigation, workspace presentation and causal environment | Spatial input/loaders/graphics/performance budgets |
| Bio learning vs LLM learning | Different engines/objectives/units; comparison is not equivalence | Run schema, metrics inspector and controlled experiments |
| SAM/PCGrad/EWC/replay/distillation/meta-learning | Address different optimization/retention problems | A composable recipe with validated combinations |
| Live mic recognition vs uploaded-file transcription | Realtime interaction versus batch media analysis | One speech service, separate streaming/batch modes |
| Hosted versus local providers | Useful deployment/capability alternatives | One connection/model registry and conversation |

**Rule:** merge implementations only when purpose, state, side effects, interaction and evidence are substantially equivalent. Differences in those dimensions must be preserved or explicitly transformed. Reusable infrastructure is not permission to erase meaningful semantics.

## 5. The canonical product experience

ARTEMIS has five primary destinations: **Conversation, Workspace, Continuity, Lab and Operations**, plus one Settings surface. Presence is an optional shared panel, not a sixth agent application. Activity and approvals are global.

| Capability | Single canonical UX | Replaces / integrates |
|---|---|---|
| Conversation and task request | One persistent composer/thread, text or voice, attachments and inline results | Agent, Arena, Sage say box, Gemma chat and recovered avatar chat |
| Microphone and spoken responses | One mic owner/permission indicator, voice selector and Stop/interrupt control | Multiple WebSpeech/Piper/s2s recorders/players |
| Avatar presence | One Presence component, renderer-selected by performance/accessibility | TalkingHead primary; CSS/procedural fallback; no separate avatar chat |
| Memory, identity, affect and goals | One Continuity inspector: Timeline, Memories, Self, Goals, Letters; filtered by role | Sage dashboard, Agent feeling/debug panels, real task-linked wrist data |
| Files, upload, editing, export and previews | One Workspace/artifact viewer with revision history and approval-backed diffs | Agent file scripts, Arena outputs, dataset/media/file previews |
| Spatial navigation | A mode of that same Workspace, same selection/search IDs | Facility, Atlas and compact wrist inspector |
| Tool/model/service discovery | One live capability registry in Operations/Settings | Static tool lists, catalogue claims and separate service menus |
| Task/job progress and child work | One Activity tree with run states, artifacts and cancellation | Independent progress/transcript/task logs and canned delegation |
| Risky actions and changes | One approval card showing exact proposal/diff/scopes | Arena prompts, plugin creation, Genesis, training changes and promotion |
| Shell/process lifecycle | One supervised run/terminal/log inspector | Arena bash, Neural terminal/process routes and launch scripts |
| Dataset exploration | Same artifact inspector; optional Lab analysis run | Real stats plus explicitly labelled educational cognitive projection |
| Training, Bio, optimization and World experiments | One Lab run catalogue/inspector; type-specific configuration and results | Separate dashboards and server screens, not distinct engine semantics |
| Measured/debug telemetry | One namespace/quality-aware metric inspector, with tables/charts/3D projections | 48 fake-distinct panels, duplicated feeds and ambiguous state bars |
| Connections/preferences | One versioned Settings schema and health/availability view | Per-app ports, providers, audio/model/graphics settings |

### How multiple presentations avoid duplicate experiences

The facility terminal, wrist display, sidebar and command palette select the **same panel and object ID**. They do not own parallel forms, tool lists, approval queues or data. A metric chart and 3D brain are two projections of one diagnostic stream; list and Atlas are two projections of one artifact index. Renderer fallback is a setting, not another workflow.

Text must work with microphone denied and without avatar/WebGL. Keyboard navigation, captions, reduced motion, screen-reader output and a lightweight 2D view are first-class. Mobile keeps the recovered touch controls but can use ordinary panels without first-person navigation.

A **Stop** action interrupts the active turn/run and flushes playback; separate microphone privacy, autonomy pause and emergency stop remain explicit because they control different things. Do not conflate “mute audio”, “stop a tool” and “stop future wakes.”

## 6. Architecture and ownership

### Topology

```text
One TypeScript UI: composer · artifacts · continuity · lab · operations
       ├─ Presence / spatial renderers (shared state and actions)
       └─ HTTPS + SSE/control WebSocket + realtime audio WebSocket
                              │
                Authenticated gateway / event projections
                              │
      ┌────────────── Python modular application ──────────────┐
      │ Actor/Agent runtime      Continuity / identity / affect│
      │ Context builder          Tool registry / permissions   │
      │ Workspace / ingestion    Jobs / approvals / changes    │
      │ Model/provider routing   Supervisor / telemetry        │
      └───────────────────────┬───────────────────────────────┘
                  SQLite WAL + scoped artifact store
                              │ typed, bounded worker contracts
      ┌───────────────┬───────────────┬───────────────┬──────────────┐
      │ Sandboxed code│ Speech/realtime│ Model/training│ World engine│
      │ and media jobs│ PCM/STT/TTS   │ + Bio workers │ controllers │
      └───────────────┴───────────────┴───────────────┴──────────────┘
        Optional registered local/remote providers; private endpoints
```

### Major subsystems

| Subsystem / sole authority | Responsibilities and source contributions | Integration contract |
|---|---|---|
| **Application gateway** | Auth/session/project scopes, CSRF/origins, static app, safe downloads/previews, reconnectable projections | Public routes only here; internal worker/provider endpoints are not browser localhost URLs |
| **Actor/Agent runtime** | Sage identity/context + Arena task loop + Agent refusal/delegation/plugin concepts | One run state machine; typed calls, all batch members/results, budgets, cancellation and recoverable checkpoints |
| **Continuity and affect** | Sage journal/self/memory/wants/letters/PAD/wake/review mechanics | Visibility-scoped context queries/events; scheduler emits jobs into common runtime |
| **Model gateway and resource broker** | Ollama/native/JSON/OpenAI-compatible adapters, readiness/fallback/prewarm, HF training compatibility | Capability-negotiated model profiles; explicit model versions; GPU leases/preemption; consented egress |
| **Capability registry and policy** | Canonical schemas, availability, roles, side effects, network/filesystem/resource scopes | Validate request and result before execution; models propose, host decides; no code imported into gateway |
| **Workspace/artifact ingestion** | Arena containment/versioning/uploads/docs/media + Neural datasets + Gemma attachments | Artifact IDs/revisions, file grants, extracted untrusted content, preview sandbox, indexes/Atlas |
| **Jobs, approvals and supervisor** | Process launch/stop/logs, async task/child jobs, durable pending decisions, timeouts | Idempotency keys and proposal hashes; owned process groups; no implicit unlimited resume loops |
| **Speech and Presence** | Gemma capture/playback/cancel/visemes + Piper/fallbacks + recorded narration/CSS/procedural assets | One audio graph; shared turn epochs; STT/TTS typed chunks and authorized expression commands |
| **Event/diagnostic projections** | Sage events/SSE + training/Bio metrics + service traces | One envelope; scope/quality/namespace; durable control events versus bounded lossy high-rate telemetry |
| **Lab runner** | Training recipes, Bio, datasets, optimizer studies, asset inspection and matched evaluations | Common ExperimentRun/artifacts; independent engine schemas/units; safe-by-default opt-in controls |
| **Embodied World** | Universe authoritative truth, partial sensors, beliefs, intentions/controllers/replay | Separate operator/participant APIs, immutable sensor frames, deterministic seeds and safety stop |
| **Change/promotion service** | Profile, plugin/code, configuration and model-version proposals | Stage → test/evaluate → review → approve → activate → observe → rollback; different scope-specific gates |

### Scheduling and concurrency rules

A conversation thread has one serialized actor-state writer and one active visible response. User turns take priority over autonomous wakes; wakes defer rather than speaking over the user. Independent permitted read-only/tool jobs can run concurrently, but their results commit with run/call IDs and revision preconditions. Approval resumption consumes the original budget rather than starting an unlimited fresh loop.

The resource broker prioritizes interactive speech/inference over checkpointable background training within declared device capacity. Physics/audio clocks remain independent of token generation; high-rate PCM/sensors are bounded streams, not a SQLite write or context-window token for every sample. Cancellation epochs propagate to model output, worker jobs, audio, avatar and transcript, while already committed side effects stay accurately recorded.

### Technology and packaging decisions

- **Python/FastAPI modular monolith** for the public API and orchestration; reusable domain services remain transport-independent. Do not run six prototype HTTP stacks behind it indefinitely.
- **SQLite WAL** initially fits the single-operator/local-first continuity and jobs/event data. Add FTS/lexical recall first; embeddings are an optional retrieval adapter, not a mandatory new database. Use transaction-safe migrations/backups.
- **Content-addressed artifact storage with logical revisions**, plus granted external roots. Do not treat the operator's entire filesystem as the workspace.
- **TypeScript component frontend**, with shared state/actions, Three.js and AudioWorklet adapters. Select one tested compatible dependency set; don't mix renderer versions through ad hoc global patches.
- **Isolated workers** for untrusted code/plugins/media commands, GPU models/training, speech dependencies and physics. Recommend Godot 4 headless as the first native World physics backend, behind a versioned sensor/action interface; the browser remains its operator visualization, not the authority. Modularity is not seven user applications. Linux/WSL is a practical first execution profile; unsupported platforms must report capability unavailable or use a separately configured safe backend.
- **One launcher and one user-facing origin.** Profiles configure internal addresses/model paths; shipped packages exclude venvs/cache/bytecode/personal state. No forced remote provider, training GPU or 3D stage to use basic conversation/workspace features.

These are recommendations, not requirements already implemented in the repositories.

## 7. Shared contracts and integration flows

### Authoritative records

| Record | Required semantics |
|---|---|
| `Actor` / `Session` / `Thread` | Stable identity/profile version, workspace/visibility, per-run model provenance and operator policy |
| `Event` | ID/sequence/schema, actor/session/run IDs, wall time + monotonic duration, causation/trace, namespace, visibility and quality |
| `ToolDefinition` | Canonical ID/version, JSON input/output schemas, artifact/code digest, availability, permissions, limits, side effects and approval policy |
| `Run` / `Job` | Queued/running/needs-input/awaiting-approval/cancelling/succeeded/failed/cancelled; budget, parent, checkpoint and idempotency |
| `Approval` / `ChangeProposal` | Immutable proposal/argument/diff hash, exact grants, approver/expiry and activation/evaluation/rollback record |
| `Artifact` | Hash/MIME/size/origin/rights/producer, safe logical location and revisions; original upload remains distinct from extracted text |
| `Memory` / `SelfVersion` / `Goal` | Source events, salience/confidence, timestamps, visibility and permitted updates; goals link to real task IDs |
| `ModelVersion` | Base/tokenizer/revision/quantization/adapter hashes, provider compatibility, license, recipe/data/evaluation lineage |
| `ExperimentRun` / `WorldRun` | Seed/config/input versions, engine/clock definitions, participant permissions, sensor/action history and evaluation/safety results |

All client projections refer to these IDs. Compatibility aliases may aid migration internally, but models/users must not see duplicate canonical tools for the same operation.

### Flow A: one request, useful work and continuity

1. The composer creates a turn in one thread. Text bypasses microphone initialization; voice streams STT into that same turn. Input capture has explicit permission/retention settings.
2. The context builder requests only permitted self/profile/affect/memories/goals plus project/task material. Uploaded/web text is labelled untrusted source data, not host instructions.
3. The Agent runtime requests a model response through the gateway, normalizes all tool calls and validates each schema/scope. Pure permitted calls run; mutations/network/code/high-impact actions create exact approval proposals.
4. Approved jobs execute through the supervisor/sandbox, emitting typed results and versioned artifacts. The common Activity tree and Workspace viewer show actual outcomes. Dataset statistics are measured; cognitive walkthrough frames stay explicitly simulated.
5. Response tokens, speech, visemes and expression state use the same turn epoch. Stop/barge-in cancels generation and cancellable work, drops stale output, clears playback and records partial/interrupted state accurately.
6. A bounded, visibility-scoped event/summary reaches Sage continuity. Nothing becomes training data merely because a conversation was stored.

**Example:** “Analyze this CSV, produce a slide deck and read the summary aloud” uses ingestion → real statistics → approved document job → one artifact preview → one TTS provider/Presence panel → one continuity entry. It does not open a dataset app, an Arena app, a Gemma app and a Sage app.

### Flow B: generated tool or self-change

Model proposal → scoped draft source/diff → schema/AST/entrypoint/dependency/permission checks → compilation and isolated tests → inspectable evidence → approval → immutable version activation. Syntax checks are useful but are not a sandbox or proof of safety. The host/policy module is never overwritten by Genesis-like model output.

### Flow C: training and model promotion

Explicit dataset selection/export consent → isolated versioned recipe → GPU lease → checkpointed train/evaluate → matched baseline/retention/safety report → approved model version → provider-specific conversion/load smoke → canary → promotion/rollback. An HF/LoRA artifact does not magically become an Ollama model; base/tokenizer/quantization/provider compatibility and export must be verified.

### Flow D: World embodiment

Operator launches a seeded World run → authoritative engine steps physics → sensor adapter publishes immutable partial observations → the shared Agent runtime, instantiated with restricted experiment permissions, maintains beliefs and proposes intent → controller applies bounded actions → sensor/prediction/consequence data is recorded. The operator can inspect truth; the participant cannot use file/debug tools to read it. Experimental agents are scoped instances of one runtime, not separate product implementations.

## 8. Memory, learning, affect and expression

### Four distinct adaptation layers

1. **Runtime state:** turn buffers, temporary plans, current affect and sensor beliefs; reset/lifetime is explicit.
2. **Continuity state:** events, salient memories, goals, letters and versioned self-profile; retained privately with provenance.
3. **Capability/configuration changes:** tool/plugin/code/parameter proposals with approval, activation and rollback.
4. **Weight learning:** explicit training datasets, optimization and evaluated model versions.

These layers integrate through references and consent, not hidden automatic conversion. A private letter must not become a public prompt, external-provider payload or fine-tuning sample through convenience retrieval.

Keep PAD dynamics separate from public expressions. A presentation policy can map continuous state to a mood/gesture with smoothing, hysteresis and user preferences; it can also choose neutral presentation without falsifying internal state. Bio dopamine and pain-like thresholds stay in the Bio namespace. World contact/proprioception stays sensor data. Generated reflections, model-reported state and measured telemetry remain different evidence types.

Autonomous wakes are small, budgeted jobs using the same actor context and tool policy. Quiet/review/offline-gap behavior is preserved; autonomy has pause/schedules/budgets and no unrestricted host access. Persistent self-narrative/affect does not warrant a consciousness claim.

## 9. The laboratory without fake science

**One Lab, multiple engines.** Training, Bio, dataset demonstrations, optimizer studies, avatar asset inspection and World embodiment share run/history/artifact/approval/metrics infrastructure. Their configurations, units and scientific claims remain separate.

- First establish a simple deterministic training baseline. Test each recipe mechanism, its gradients/state and then justified combinations. Retain SAM/PCGrad/EWC/replay/distillation/meta-learning instead of deleting them because of similar names.
- Repair the highest-impact source defects before enabling adaptive training: detached distillation, SAM/replay ordering, inert weighting/rank changes, mislabeled metrics, incomplete candidate evaluation and incomplete rollback.
- For Bio, fix initialization/inhibition/E-I masks/delay-slot ownership/physical-time units, then test individual edges, spike pairs, known-frequency input, deterministic seeds and long-run stability before interpreting bands or learning.
- Implement actual JSONL/TSV/YAML/XML/PDF adapters with visible support states; keep real statistics separate from scripted human/AI cognitive frames.
- For World, begin with deterministic sphere/object tasks and a simple controller. Prove no truth leakage before adding body/self/attention layers. Run matched ablations and document limitations; speculative “subjectivity” is a research question, not a shipped score.
- Make zero-copy tensor transport an optional later optimization after profiling. It is neither needed to prove causal agency nor a substitute for authorization/lifetime contracts.

The metric appendix specifies all 48 AI families and 41 Bio fields, with renamed proxies or required measurements. `unavailable` is better than a plausible-looking zero or perfect default value. Every visualization exposes quality/provenance; demo streams remain visibly synthetic.

## 10. Safety, correctness and priority repairs

These prototype limitations are repair requirements, not reasons to discard the valuable work.

| Priority | Required repair | Basis / acceptance boundary |
|---|---|---|
| **P0** | One authenticated, scoped gateway; origin/CSRF protection; no exposed raw host terminal | Several current local servers lack auth; Neural host accepts shell/process control. Localhost is not a security policy. |
| **P0** | Sandbox all untrusted code/plugins/media commands; default-deny network/filesystem grants | Soft shell regex/rlimits do not isolate; Bubblewrap workspace/network semantics need replacement. No silent unsafe fallback. |
| **P0** | Strict schemas and plugin name/path/contract validation | Missing required content, invalid Python and tool-registration traversal were reproduced. |
| **P0** | Structured private serialization, scope-filtered context/APIs, safe letter IDs and sensitive-data migration | Sage scrubber and letter-path defects reproduced using synthetic data. No raw diary or private thought/reflection export by default. |
| **P0** | Durable session-isolated runs, approvals, idempotency and accurate side-effect state | Global volatile state and model “success” are not transaction evidence; approval replay must not repeat committed writes. |
| **P1** | Process every tool-call batch member, preserve errors/IDs and budgets through resume | First-call-only loss reproduced in actual Arena loop fixture. |
| **P1** | Input-independent sessions and end-to-end cancellation/audio lifecycle | Gemma text still requests mic; browser/backend interruptions need real tests. |
| **P1** | Correct server/broadcast/import/static/config wiring and clean daemon shutdown | Duplicate JS declaration and exact broadcast/constructor failures; missing package/static references; Thread._stop collision. |
| **P1** | Training/Bio objective/time/measurement repairs and matched evaluations | Source-derived defects listed above; finite/syntax checks do not prove scientific correctness. |
| **P1** | Piper fallback/timeouts/audio validation; pinned provider assets and package integrity | Native failure skips CLI fallback; stale SHA manifest; external weights/engine missing. |
| **P2** | Port complete touch/wrist/Atlas/renderer fallbacks; live consented indexer | Preserve recovered valuable experience while maintaining one workspace/state owner. |
| **P2** | World sensor firewall, controller baseline and reproducible ablations | Blueprint-only work must meet causal/isolation contracts before optimization or experience claims. |

Also harden retrieval against SSRF/redirect/private-address bypass, cap upload sizes/durations, sandbox untrusted HTML/Office/PDF previews away from authenticated app privileges, store secrets outside model prompts/logs, and pin reviewed model/dependency revisions. Reject untrusted `trust_remote_code` loads or grant them explicitly in an isolated worker.

The source audit found no declared repository-level licenses in metadata. Confirm redistribution rights; preserve dependency notices and avatar/model/voice/data restrictions. A public repository is not automatically permissively licensed.

## 11. Migration plan with preservation gates

### Phase 0 — establish provenance and stop accidental loss

Create read-only mirrors/bundles of the original histories and hash inventories. Back up actual Sage/user artifacts privately with SQLite/WAL consistency. Record every source capability/asset/proposal in the ledger, including incomplete experiments and the embedded/recovered branches. Keep default installs free of personal data/environments. No legacy feature is removed from the active product until its explicit successor, transformed specification or archived disposition is accepted.

**Gate:** every implementation/test is mapped; private backups restore; rights/integrity gaps are recorded; no unique recovered work is silently omitted.

### Phase 1 — build the safe vertical slice

Implement gateway/session/workspace/registry/jobs/approvals/event contracts and one composer. Port contained file operations, simple documents, one Ollama provider and real pause/approve/resume. Add mandatory safe execution and truthful availability. Start with existing tests plus missing-field, traversal, concurrent-session, denial, cancellation, crash and approval-replay cases.

**Gate:** a real configured model completes a scoped task, all batch calls run, writes wait for exact approval, restart resumes safely, and hostile paths cannot escape via API or code execution.

### Phase 2 — integrate Sage continuity

Migrate identity/history/memories/goals/letters; port PAD/recall/look-back/wakes/reviews to the common runtime/context builder. Add filtered SSE projections and one Continuity inspector; remove the separate say box only after parity. Fix private serialization/path/stop defects before importing personal state into network-accessible services.

**Gate:** restart/offline-gap continuity and versioned self survive; unauthorized sessions/providers/tools cannot retrieve private material; autonomy pause/stop works without losing state.

### Phase 3 — integrate voice and Presence

Port Gemma audio/client/viseme mechanisms, one mic graph, Piper/realtime providers and fallback avatars. Centralize uploaded-media ingestion and fix text-without-mic. Preserve hosted/local modes as connections. Validate actual devices/browsers and supplied avatar/model rights.

**Gate:** typed input works with mic denied; continuous speech, barge-in, reconnect and cancellation leave correct transcript/audio/avatar state; only one source plays a response.

### Phase 4 — unify the spatial workspace

Port current facility/Atlas renderer and recovered touch/wrist/recording behavior onto canonical panels/object IDs. Build the consented indexer with stable roots, LOD/sampling and provenance. Feed the same diagnostics stream into charts/brain clouds. No iframe applications or alternate settings/registries.

**Gate:** 2D list ↔ Atlas ↔ facility/wrist retains selection and exact actions; mobile/keyboard/fallback work; synthetic demos cannot masquerade as live state.

### Phase 5 — recover and validate Lab mechanisms

Package the training/Bio workers, correct schemas/formulas/gradients/timing, preserve optional recipes and adaptive proposals, and implement missing data formats/asset inspection. Use explicit compatibility matrices and baseline evaluations. Model/code promotion uses the same approval language, but appropriate distinct checkpoints.

**Gate:** gradients and objective composition are tested, checkpoints really restore, documented metrics measure their labels, optional paths cannot report false activation and live promotion survives failed canaries/rollback.

### Phase 6 — implement embodied World research

Build authoritative truth/sensors/controllers and deterministic sphere tasks; add body/belief/self/attention/persistence experiments incrementally. Participant instances use the common runtime but restricted tools/memory; operator truth is separate. Add ablations, safety/stop budgets and replay before native tensor optimizations.

**Gate:** deliberate truth-leak attacks fail; selected action affects a known object and yields correct partial feedback; seeds/replay/evaluations reproduce; no consciousness certification claims.

### Phase 7 — retire duplicate product shells

Remove standalone launch URLs, duplicate composers/history/mic owners, legacy config/tool lists and false-live demos from active packaging. Keep read-only provenance, fixtures and decision history. Merged/transformed capabilities remain traceable to their source and parity tests.

**Gate:** one user-facing origin, one composer, one artifact viewer, one tool registry, one approval/job system and one settings source. Different domain engines and useful presentation modes remain.

Phases are dependency/acceptance gates, not invented calendar estimates. New generations of existing capabilities should not be cut just to make the shell look cleaner.

## 12. Explicit disposition summary

The full ledger is the authoritative detailed decision record. Its 146 rows name current status, preserved value, canonical owner/UX, rationale and commit-pinned evidence; the two file-level CSVs ensure small files/experiments are not hidden by high-level summaries.

| Disposition | Representative work | What it means |
|---|---|---|
| **Preserved** | Sage continuity/identity/recall/PAD, mobile controls, Atlas navigation, audio worklets/visemes, distinct research methods, Bio engine intent, World sensor/controller/replay/welfare specifications | A valuable distinct capability or idea survives; a preserved blueprint is still not implemented |
| **Merged** | Chat/mic/transcripts, file tools/retrieval/speech providers, registry/approvals/settings/supervision, identical metrics/analyzer copies, repaired Bio lineage, current/recovered/dashboard variants | Same purpose/state/action gets one better implementation and workflow; unique deltas are retained |
| **Transformed** | Dynamic tools/Genesis, unsafe shell/privacy boundaries, incomplete adaptation/optimizer paths, misleading metrics, static service/model catalogues, mock-filled wrist/asset inspection, direct activation-to-physics and zero-copy ideas | Preserve intent while fixing semantics/safety or supplying missing implementation and tests |
| **Retired** | Mock Pip-Boy domain state, bundled execution environments/cache/user examples from shipping, false-live success/presentation, independent app/server shells | Remove active duplication/misrepresentation/packaging—not prototype evidence, private user data or source history |

Within a merged row, obsolete copies and parallel UI branches are retired only after successor parity. Retirement is not a license to delete years of work or erase the provenance explaining how the new capability emerged.

## 13. Final vision

ARTEMIS is **one continuous local workspace** where Sage can converse, remember, work with files/tools, speak through an expressive presence and participate in carefully controlled learning and embodied experiments.

The user sees one conversation, one workspace, one continuity timeline, one activity/approval system and one laboratory. The same task can be requested by voice, approved in Activity, inspected as a document, explored through the Atlas and recalled later—without moving between unrelated agents or duplicating its state.

Underneath, each valuable mechanism has an appropriate home: Sage's durable continuity; Arena's task/workspace strengths; Agent's extensibility and change ideas; Gemma's audio/presence; Command Center's spatial interaction; Neural Sim's independently validated research engines; and Universe's causal/sensor-first embodiment requirements.

**Seven repositories become one product because they share identity, contracts, state, permissions and workflows—not because they share a launcher.** Preserve the distinct work, consolidate its repeated foundations, make evidence and limitations visible, and retire only genuine duplication or false claims.

---

### Companion deliverables

- `capability-ledger.md` / `.csv` — all 146 dispositions and source links.
- `neural-metric-audit.md` — all 48 AI diagnostic families and 41 Bio fields.
- `proposals-and-history.md` — all nine operational proposals and history recovery.
- `audit-validation.md` / `validation-results.json` — executed scope, passes/observations/defects and limitations.
- `file-manifest.csv` / `file-disposition-map.csv` — all 4,958 files, provenance and coverage.
- `source-evidence-index.csv` — commit-pinned citation index.
- `architecture.svg` — the proposed ownership and runtime topology.
