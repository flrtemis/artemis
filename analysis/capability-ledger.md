# Capability and disposition ledger

146 decisions. **Preserved** = value retained as a distinct capability; **Merged** = overlapping implementations become one; **Transformed** = intention retained with changed semantics/boundaries or missing implementation; **Retired** = removed from active runtime/UX, not destroyed from the source/provenance archive.

A preserved specification is still a specification: implementation status below is independent of disposition. Every row names its canonical owner, workflow and commit-pinned evidence.

## Command Center

### C01 · Walkable command facility, rooms, collision, terminals and navigation
**Preserved** · Implemented client  
**Owner:** Spatial workspace renderer · **Canonical UX:** Workspace spatial mode
Keep the facility, procedural materials/furniture/signage and first-person exploration as a spatial projection of the canonical workspace; terminals open the same real panels as 2D navigation.
**Evidence:** [C.main](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/dashboard_3d.html#L806-L6330) [C.recovered](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/dashboard_3d_may3_pipboy_sage.html#L697-L4443)

### C02 · Lighting, bloom, particles, ambient audio, footsteps and cinematic transitions
**Preserved** · Implemented client  
**Owner:** Spatial workspace renderer · **Canonical UX:** Workspace spatial mode
Preserve atmosphere and enter/exit cinematics, with reduced-motion/audio options, performance budgets and a non-WebGL fallback. These are experience design, not a second agent.
**Evidence:** [C.main](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/dashboard_3d.html#L806-L6330) [C.recovered](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/dashboard_3d_may3_pipboy_sage.html#L697-L4443)

### C03 · Paired AI and bio brain clouds, synapse arcs and metric-driven shaders
**Merged** · Implemented renderer; mixed data provenance  
**Owner:** Diagnostics renderer · **Canonical UX:** Lab run inspector
Use one renderer from the command-center fork; retain both namespaces and paired comparisons. Its two 8,192-point clouds are visualizations, not two actual biological/neural agents.
**Evidence:** [C.main](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/dashboard_3d.html#L806-L6330) [N.dashboard](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/dashboard_3d.html#L1) [C.bio](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/bio_model.py#L153-L1073) [N.metrics](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/metrics.py#L1)

### C04 · File galaxy: star/nebula rendering, spiral remapping, search, filters, density, size and fly-to
**Preserved** · Implemented client; snapshot data  
**Owner:** Workspace Atlas · **Canonical UX:** Workspace spatial mode
Retain file navigation and cinematics as the Atlas projection of Workspace artifacts. Shared selection/search prevents a second file manager. Build a consented live indexer; do not imply the snapshot renderer already supplies one.
**Evidence:** [C.main](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/dashboard_3d.html#L806-L6330) [C.gal5](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/galaxy_5k.json#L1-L1) [C.gal25](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/galaxy_25k.json#L1-L1) [C.gal50](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/galaxy_50k.json#L1-L1)

### C05 · 5k/25k/49,998 galaxy snapshots and 1,748,673 indexed-file metadata
**Transformed** · Data assets, not a supplied indexer  
**Owner:** Workspace Atlas import/LOD · **Canonical UX:** Workspace spatial mode
Keep as provenance-labelled fixtures and import examples; deduplicate root/path identities and support level-of-detail sampling. The largest file contains 49,998 plotted records, not 1.75 million rendered points.
**Evidence:** [C.gal5](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/galaxy_5k.json#L1-L1) [C.gal25](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/galaxy_25k.json#L1-L1) [C.gal50](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/galaxy_50k.json#L1-L1)

### C06 · Mobile joystick, multi-touch roles and frame-drained look input from recovered fork
**Preserved** · Implemented unique branch  
**Owner:** Shared spatial input adapter · **Canonical UX:** Workspace spatial mode
Carry the recovered mobile work forward into the current renderer; desktop controls alone are not its replacement. Add touch/pointer/browser tests.
**Evidence:** [C.recovered](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/dashboard_3d_may3_pipboy_sage.html#L697-L4443)

### C07 · Pip-Boy wrist device, animated arm, tab/keyboard controls and compact HUD
**Transformed** · Implemented interaction with mock contents  
**Owner:** Shared compact inspector · **Canonical UX:** Same workspace/operations panels
Preserve the wrist/HUD interaction as a presentation of existing information and actions. Do not make a second inventory, task tracker, map, radio or tool registry.
**Evidence:** [C.recovered](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/dashboard_3d_may3_pipboy_sage.html#L697-L4443)

### C08 · Pip-Boy mock inventory, quests, map and radio
**Retired** · Mocks  
**Owner:** Archived design fixtures · **Canonical UX:** No production feature
Retire fictional duplicated application state from production; retain prototype fixtures and art direction. Real artifacts/jobs/navigation/approved audio can populate the same compact inspector.
**Evidence:** [C.recovered](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/dashboard_3d_may3_pipboy_sage.html#L697-L4443)

### C09 · Room narration WAVs, synthesized narration, captions and tour transitions
**Merged** · Implemented client plus recorded assets  
**Owner:** Shared speech/audio service · **Canonical UX:** Spatial tour overlay
Keep the room-specific recordings, captions and interrupt-on-room-change behavior; route audio through the shared mixer, not a competing microphone/assistant channel.
**Evidence:** [C.main](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/dashboard_3d.html#L806-L6330) [C.narration1](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/The%20Center%20Narration.wav) [C.narration2](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/The%20Workshop.wav)

### C10 · Movement, graphics, keybinding, audio settings and visual lock screen
**Merged** · Implemented preferences; lock not authentication  
**Owner:** Settings and access control · **Canonical UX:** Settings
Merge configurable movement/sensitivity/keybindings/pixel ratio/bloom and volume. Preserve lock-screen aesthetics but replace cosmetic access control with authenticated sessions.
**Evidence:** [C.main](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/dashboard_3d.html#L806-L6330) [C.recovered](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/dashboard_3d_may3_pipboy_sage.html#L697-L4443)

### C11 · Service catalogue, room launch/stop/output panels and linked HF spaces
**Transformed** · Descriptors and client controls; incomplete host  
**Owner:** Capability registry and supervisor · **Canonical UX:** Operations
Retain organization and launch/inspect affordances; replace static status with registered service health. Linked Sage/CSM/ears/comms/converter/router/mirror/security tools are external references, not implementations in these seven repos.
**Evidence:** [C.main](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/dashboard_3d.html#L806-L6330) [C.recovered](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/dashboard_3d_may3_pipboy_sage.html#L697-L4443) [C.start](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/START-HERE.txt#L1-L25) [N.workspaceServer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/dashboard_server.py#L1)

### C12 · Demo metrics server and simulated tool/self-modification status
**Transformed** · Bio and dataset logic real; other streams synthetic  
**Owner:** Explicit demo provider · **Canonical UX:** Lab demo mode
Keep reproducible demos, visibly tagged synthetic. Launch/stop return 501 in this demo. Never surface synthetic loss, model changes or service health as observations.
**Evidence:** [C.demo](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/demo/demo_server.py#L31-L223) [C.bio](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/bio_model.py#L153-L1073) [C.dataset](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/dataset_analyzer.py#L55-L1603)

### C13 · Command-center bio fork: local import, delay setup ordering and cortical conductance shapes
**Merged** · Implemented repairs, bounded smoke passes  
**Owner:** Bio simulation worker · **Canonical UX:** Lab / Bio run
Use these three concrete fixes as the merge baseline rather than choosing neural-sim merely by repository name. Repair remaining inhibition, delay, timestep/count and frequency issues before scientific use.
**Evidence:** [C.bio](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/bio_model.py#L153-L1073) [N.bio](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/bio_model.py#L1)

### C14 · Copied metrics and dataset analyzer modules
**Merged** · Byte-identical to neural-sim  
**Owner:** Diagnostics schema and ingestion service · **Canonical UX:** Lab run inspector
Keep one implementation of each exact duplicate; do not discard dataset analysis or diagnostics because of their location in two repos.
**Evidence:** [C.metrics](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/metrics.py#L22-L824) [N.metrics](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/metrics.py#L1) [C.dataset](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/dataset_analyzer.py#L55-L1603) [N.dataset](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/dataset_analyzer.py#L1)

### C15 · Current versus recovered dashboards
**Merged** · Same facility lineage with distinct additions  
**Owner:** Single spatial frontend · **Canonical UX:** Workspace spatial mode
Current supplies local Three.js and duplicate-name fixes plus richer galaxy controls; recovered supplies mobile/Pip-Boy/avatar. Merge these valuable deltas; retire both standalone shells after parity.
**Evidence:** [C.main](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/dashboard_3d.html#L806-L6330) [C.recovered](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/dashboard_3d_may3_pipboy_sage.html#L697-L4443) [N.dashboard](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/dashboard_3d.html#L1)

### C16 · Sage procedural skeleton, face/mouth animation, blending, gaze and idle motion
**Merged** · Implemented fallback-oriented avatar prototype  
**Owner:** Avatar presentation adapter · **Canonical UX:** Shared Presence panel
Preserve rig abstraction, fallback rendering, gaze/body choreography and expression transitions; use the Gemma talking-head/audio pipeline as primary lip-sync. Missing referenced OBJ/GLB/texture files must not be assumed supplied.
**Evidence:** [C.avatar](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/sage_avatar.js#L1-L1472) [C.recovered](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/dashboard_3d_may3_pipboy_sage.html#L697-L4443) [G.avatar](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/avatar.js#L1) [N.mesh](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/prepare_model.py#L1)

### C17 · Avatar browser speech input/output, chat history and MediaRecorder playback/download
**Merged** · Implemented client paths; external endpoints incomplete  
**Owner:** Conversation and media capture · **Canonical UX:** Shared composer and artifact viewer
Merge chat/voice controls into the canonical conversation. Keep session recording as an opt-in media artifact, not an extra assistant transcript. Browser speech APIs are explicitly optional, not guaranteed offline.
**Evidence:** [C.avatar](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/sage_avatar.js#L1-L1472) [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031) [G.client](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/s2s/s2s-ws-client.js#L1)

### C18 · Global Object3D.add monkeypatch and renderer-specific resilience patches
**Transformed** · Technical workaround  
**Owner:** Typed renderer boundaries · **Canonical UX:** No separate UX
Keep graceful optional-asset handling, but replace global mutation/swallowed invalid objects with localized checks and observable errors.
**Evidence:** [C.main](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/dashboard_3d.html#L806-L6330)

### C19 · ARTEMIS logo and recovered branding assets
**Preserved** · Assets  
**Owner:** Product asset library · **Canonical UX:** Shared shell
Preserve coherent branding and provenance/rights records, without treating image assets as capabilities.
**Evidence:** [C.logo](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/ArtemisLOGO.png)

## Agent

### A01 · Sanctum conversation UI, CSS face, statuses and voice-first identity
**Merged** · Implemented monolithic client/server  
**Owner:** Conversation + avatar presentation · **Canonical UX:** Shared composer and Presence
Keep style/identity, accessible CSS low-resource avatar and status choreography as renderer fallback; no separate Sanctum chat or unrelated model memory.
**Evidence:** [A.base](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent.py#L37-L1531) [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031) [G.avatar](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/avatar.js#L1) [S.ui](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/web/index.html#L1)

### A02 · Five-round Ollama tool loop and native tool manifests
**Merged** · Implemented; global volatile history  
**Owner:** Agent runtime · **Canonical UX:** Shared composer / job activity
Merge loop ideas with Arena registry and bounded task orchestration, retaining every call/result ID and one durable session/thread. Replace arbitrary five-round truncation with explicit per-run budget.
**Evidence:** [A.base](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent.py#L37-L1531) [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031) [R.agent](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/agent.py#L1)

### A03 · Dynamic tool discovery, JSON schemas and runtime creation of Python plugins
**Transformed** · Implemented registration; unsafe boundaries  
**Owner:** Versioned plugin lifecycle · **Canonical UX:** Operations / Tools; one approval flow
Preserve tool creation as proposals: validate slug/path/schema/AST/execute contract, compile and test in isolated workspace, inspect permissions, approve then activate a version. Traversal and invalid Python registration were reproduced.
**Evidence:** [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031) [R.tools](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/base.py#L1)

### A04 · Bubblewrap execution with optional network inferred from tool name
**Merged** · Implemented sandbox command; unsuitable workspace mounts  
**Owner:** Isolated execution workers · **Canonical UX:** Job inspector
Retain process/namespace confinement intent. Replace read-only-host/workspace conflict and name-derived network access with explicit filesystem/network grants, resource limits and a writable scoped job mount.
**Evidence:** [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031) [R.bash](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/bash.py#L1)

### A05 · Feeling/debug state channel, feeling bars, richer avatar CSS and state inspector
**Transformed** · Enhanced variant only; partly model-reported  
**Owner:** Affect + explainable state projections · **Canonical UX:** Memory/continuity inspector and Presence
Preserve the structured state/debug idea; distinguish reported values from measured telemetry and drive expressions from the shared affect state. Do not automatically expose generated private reflection or claim the bars measure feelings.
**Evidence:** [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031) [S.state](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/state.py#L1) [G.avatar](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/avatar.js#L1)

### A06 · Refusal command
**Preserved** · Implemented control branch  
**Owner:** Agent policy result · **Canonical UX:** Conversation / job activity
Keep refusal as a structured terminal/needs-input outcome; policy remains host-enforced and cannot be bypassed by subsequent model instructions.
**Evidence:** [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031)

### A07 · Delegation command
**Transformed** · Canned response, not a worker system  
**Owner:** Child jobs on shared runtime · **Canonical UX:** Activity tree
Preserve the delegation interface as a typed child-run proposal. Implement scoped child agents with budgets and real results; remove false success messages until workers exist.
**Evidence:** [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031)

### A08 · Debug-inspection tool schema
**Transformed** · Declared but not dispatched  
**Owner:** Read-only introspection tools · **Canonical UX:** Same state/run inspector
Implement only sanctioned state/model/tool health projections through the common registry; private storage and full unfiltered raw traces are not debug APIs.
**Evidence:** [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031) [R.tools](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/base.py#L1)

### A09 · Piper ONNX voice, Python/native and CLI paths
**Merged** · Asset and implementations; broken fallback  
**Owner:** Speech synthesis providers · **Canonical UX:** One voice selector and shared audio graph
Keep the bundled Amy voice/config and native/CLI alternatives. A native Piper exception does not reach the current CLI else branch and returns empty audio; repair provider fallback, timeouts and WAV validation.
**Evidence:** [A.base](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent.py#L37-L1531) [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031) [A.voice](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/en_US-amy-medium.onnx) [A.voicecfg](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/en_US-amy-medium.onnx.json#L1-L493) [R.media](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/media.py#L1)

### A10 · Browser WebSpeech recognition/synthesis
**Merged** · Implemented optional browser path  
**Owner:** Speech provider fallback · **Canonical UX:** Same mic and voice controls
Offer as explicitly browser-dependent/possibly networked fallback with consent, not as the offline speech backbone. No second microphone owner or independent spoken-response loop.
**Evidence:** [A.base](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent.py#L37-L1531) [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031) [C.avatar](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/sage_avatar.js#L1-L1472)

### A11 · CLI streaming Ollama + sentence-chunked Piper, slash commands and batched tool handling
**Transformed** · Implemented experiment; not exercised with real models/audio  
**Owner:** Streaming conversation/TTS adapter · **Canonical UX:** Shared composer; optional thin CLI
Preserve true token streaming, sentence-level speech and batch-processing ideas. Replace blocking playback, duplicated tail in stored history, independent prompts/history and unbounded inner loop. CLI is a client of the same runtime.
**Evidence:** [A.readaloud](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/read_aloud.py#L1-L249)

### A12 · CLI example weather tool
**Transformed** · Hard-coded London/New York/default responses  
**Owner:** Demo tool fixtures · **Canonical UX:** Explicit demo mode
Keep as a function-calling test fixture, never a live weather capability. A real weather connector would require a separately configured provider.
**Evidence:** [A.readaloud](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/read_aloud.py#L1-L249)

### A13 · Genesis self-reading, mutation trace, backup, syntax check and restart loop
**Transformed** · Implemented experiment; unsafe self-overwrite  
**Owner:** Gated change proposals · **Canonical UX:** Lab / Changes via one approval UI
Keep self-inspection, patch generation and bounded evolutionary trace. Mutate a disposable branch, run tests/evaluations, review a diff, sign/promote and support rollback; never overwrite/re-exec the host from model output.
**Evidence:** [A.genesis](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/genesis.py#L1-L98)

### A14 · agent.py / agent2.py / agent.txt shells
**Merged** · Base + enhanced fork; agent.txt exact duplicate of agent2.py  
**Owner:** Single Agent runtime + frontend · **Canonical UX:** Shared composer
Retain enhanced deltas and base behavior in one implementation; remove duplicate text artifact from active packaging and archive variant history.
**Evidence:** [A.base](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent.py#L37-L1531) [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031) [A.duplicate](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent.txt#L1-L2031)

### A15 · Base64 local_encoder convenience script
**Merged** · Implemented utility  
**Owner:** Artifact import/export · **Canonical UX:** Workspace artifacts
Keep encoding/transfer convenience in a format-aware artifact importer instead of a standalone user workflow.
**Evidence:** [A.encode](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/local_encoder.py#L1-L16) [R.workspace](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/workspace.py#L1)

### A16 · Calculator plugin
**Transformed** · Implemented structured arithmetic plugin  
**Owner:** Math tool · **Canonical UX:** Shared tool registry
Retain the existing add/subtract/multiply/divide plugin with required numeric arguments, finite-result checks and bounded input sizes. It is structured arithmetic, not an eval-based expression engine.
**Evidence:** [A.calc](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/calculator.py#L1) [A.calcSchema](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/calculator.json#L1)

### A17 · Current time plugin
**Merged** · Implemented  
**Owner:** Clock service · **Canonical UX:** Shared tool registry / continuity timestamps
Use one timezone-aware wall/monotonic clock for tools, events and wake scheduling rather than inconsistent dates across systems.
**Evidence:** [A.clock](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/current_time.py#L1) [A.clockSchema](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/current_time.json#L1) [S.clock](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/clock.py#L1)

### A18 · Directory create/list/delete and file read/write/append/delete plugins
**Merged** · Implemented host-path operations  
**Owner:** Workspace service · **Canonical UX:** Workspace / shared tools
Merge useful filesystem operations with Arena containment and revisions. Paths/capabilities are scoped; old direct host-path access does not survive as an alternate route.
**Evidence:** [A.dir](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/directory_manager.py#L1) [A.dirSchema](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/directory_manager.json#L1) [A.files](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/file_manager.py#L1) [A.filesSchema](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/file_manager.json#L1) [R.files](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/files.py#L1) [R.workspace](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/workspace.py#L1)

### A19 · Gmail email generator
**Transformed** · String generator, not Gmail access  
**Owner:** Synthetic test-data utility · **Canonical UX:** Shared tool registry if useful
Preserve address-generation convenience as explicitly synthetic/example-domain test data. Retire implied account creation/availability and do not confuse this with an email connector.
**Evidence:** [A.gmail](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/gmail_email_generator.py#L1) [A.gmailSchema](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/gmail_email_generator.json#L1)

### A20 · list_tools plugin
**Merged** · Hard-coded list  
**Owner:** Capability registry · **Canonical UX:** Operations / Tools
Derive tool list and availability from the single live registry. Archive the canned list; it must not override discovery.
**Evidence:** [A.list](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/list_tools.py#L1) [A.listSchema](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/list_tools.json#L1) [R.tools](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/base.py#L1)

### A21 · Password generator
**Transformed** · Implemented using non-cryptographic randomness  
**Owner:** Credential-safe utility · **Canonical UX:** Shared tool registry / private output
Keep secure-password generation using secrets, bounded options and non-logged private delivery; do not retain random.choices for real secrets.
**Evidence:** [A.password](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/password_generator.py#L1) [A.passwordSchema](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/password_generator.json#L1)

### A22 · Persistent-looking Python interpreter plugin
**Merged** · Python function exists; missing required execute entrypoint  
**Owner:** Sandbox Python kernel/job adapter · **Canonical UX:** Job inspector
Repair the adapter contract and preserve optional session-local variables only in isolated kernels, with explicit reset/lifetime. No host-global REPL or duplicate shell UI.
**Evidence:** [A.python](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/python_interpreter.py#L1) [A.pythonSchema](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/python_interpreter.json#L1) [R.bash](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/bash.py#L1)

### A23 · Simple fetcher and BeautifulSoup scraper with raw/title/meta/links/text outputs
**Merged** · Implemented plugins  
**Owner:** Web retrieval tools · **Canonical UX:** Shared tools / source artifacts
Keep purpose-specific extraction modes in one retrieval implementation with timeout/size/redirect/egress rules and injection-resistant provenance; not two separate fetch experiences.
**Evidence:** [A.fetch](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/simple_web_fetcher.py#L1) [A.fetchSchema](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/simple_web_fetcher.json#L1) [A.scrape](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/web_scraper.py#L1) [A.scrapeSchema](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/web_scraper.json#L1) [R.web](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/web.py#L1)

### A24 · Nine operational tools proposed in upgrades.txt
**Transformed** · Unregistered proposal collection  
**Owner:** Operations adapters · **Canonical UX:** Operations, using common jobs/approvals
Preserve boundary enforcement, telemetry, network readiness, endpoint ping, atomic state, schema verification, latency analysis, failover and trend ideas as testable specifications; not installed tools. See the dedicated proposal appendix.
**Evidence:** [A.upgrades](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/upgrades.txt#L1-L339)

## Local Ollama Arena Agent

### R01 · Local agent HTTP app and upload/approval/preview conversation flow
**Merged** · Implemented; not end-to-end model tested  
**Owner:** Agent runtime + gateway · **Canonical UX:** Shared composer
Use its workspace/task primitives as a foundation, joined with Sage continuity and Gemma voice; do not keep a separate Arena conversation, server session or tool inventory.
**Evidence:** [R.agent](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/agent.py#L1) [R.server](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/server.py#L1) [R.run](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/run.py#L1) [R.entry](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/__main__.py#L1) [R.init](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/__init__.py#L1)

### R02 · Ollama native tools with JSON fallback
**Merged** · Implemented; fixture loop tests  
**Owner:** Model gateway + tool-call normalization · **Canonical UX:** Shared composer
Keep both formats, add strict schema validation and call IDs, execute all batch members, preserve per-call errors and resume all pending approvals deterministically. First-call-only loss was reproduced.
**Evidence:** [R.ollama](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/ollama.py#L1) [R.agent](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/agent.py#L1) [R.tools](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/base.py#L1) [R.toolboot](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/__init__.py#L1)

### R03 · Human approval queue and pause/resume
**Merged** · Implemented; approved write fixture passes  
**Owner:** Durable approvals service · **Canonical UX:** One approval card in Activity
Preserve pause/approve/deny/resume. Store immutable proposal hash, args, permission diff, approver, expiry and run state; isolate sessions and carry budgets across approvals.
**Evidence:** [R.agent](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/agent.py#L1) [R.server](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/server.py#L1)

### R04 · Workspace path resolution, uploads, outputs and collision handling
**Merged** · Implemented; traversal/symlink/name tests pass  
**Owner:** Workspace service · **Canonical UX:** Workspace artifacts
Adopt containment and upload basename/collision logic, add descriptors/root grants, revision-safe writes, MIME limits, races/TOCTOU hardening and a separately isolated execution filesystem.
**Evidence:** [R.workspace](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/workspace.py#L1) [R.files](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/files.py#L1)

### R05 · Eight file tools: list/read/write/append/edit/delete/move/present
**Merged** · Implemented; bounded subset tested  
**Owner:** Workspace tool family · **Canonical UX:** One Workspace panel / artifact viewer
Keep all eight operations. Fuzzy replacement succeeds; it removes the test file trailing newline. Add previewed diffs, explicit newline policy and revision preconditions; no duplicate agent file tools.
**Evidence:** [R.files](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/files.py#L1) [R.workspace](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/workspace.py#L1) [A.files](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/file_manager.py#L1) [A.dir](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/directory_manager.py#L1)

### R06 · Bounded bash execution, command policy and rlimits
**Transformed** · Implemented; soft backend not isolation  
**Owner:** Sandbox job worker · **Canonical UX:** One terminal/log inspector
Retain command limits and nonpersistent shell semantics. Production execution must use a tested isolated backend with scoped mounts and default-deny egress; regex/rlimits alone cannot confine host files.
**Evidence:** [R.bash](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/bash.py#L1) [R.security](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/SECURITY.md#L1) [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031)

### R07 · Optional Docker execution backend
**Merged** · Implemented adapter; not exercised  
**Owner:** Execution backend interface · **Canonical UX:** Same jobs and terminal
Keep as one backend option alongside a tested Linux namespace/VM implementation. No second shell capability or accidental unsafe soft fallback when Docker is unavailable.
**Evidence:** [R.bash](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/bash.py#L1) [R.config](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/config.py#L1)

### R08 · fetch_page and web_search (SearXNG / best-effort DuckDuckGo HTML)
**Merged** · Implemented adapters; live providers untested  
**Owner:** Retrieval service · **Canonical UX:** Shared tool registry / citations
Keep cleaned text, links and binary downloads; respect SSRF/redirect/size/egress constraints. Retrieval availability is provider-dependent, not guaranteed by manifest presence.
**Evidence:** [R.web](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/web.py#L1) [A.fetch](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/simple_web_fetcher.py#L1) [A.scrape](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/web_scraper.py#L1)

### R09 · image_search downloading up to five images
**Preserved** · Implemented SearXNG-dependent adapter  
**Owner:** Retrieval service · **Canonical UX:** Workspace search results
Retain image discovery/download as a distinct retrieval mode, with MIME validation, source attribution and explicit configured availability.
**Evidence:** [R.web](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/web.py#L1)

### R10 · generate_image: AUTOMATIC1111/Forge HTTP or command template
**Preserved** · Implemented adapter, generation engine external  
**Owner:** Media jobs + provider adapter · **Canonical UX:** Shared composer / artifact viewer
Preserve prompts/negative prompts/dimensions/steps and image artifacts. Registry shows unavailable until provider is configured and healthy; provider commands run in the shared sandbox policy.
**Evidence:** [R.media](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/media.py#L1) [R.config](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/config.py#L1)

### R11 · generate_video command backend
**Preserved** · Adapter only; video models not bundled  
**Owner:** Media jobs + provider adapter · **Canonical UX:** Shared composer / artifact viewer
Keep video-generation capability and input/output contract as optional providers, not a pretend embedded engine or second media application.
**Evidence:** [R.media](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/media.py#L1) [R.config](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/config.py#L1)

### R12 · generate_speech: Piper or command backend
**Merged** · Adapter; optional engine and format risks  
**Owner:** Speech service · **Canonical UX:** One voice selector / audio artifact
Merge with agent/Gemma speech providers; validate actual encoded audio and provider settings, unique temp paths and fallback behavior. Preserve downloadable narration separate from conversational playback.
**Evidence:** [R.media](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/media.py#L1) [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031) [G.client](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/s2s/s2s-ws-client.js#L1)

### R13 · transcribe_audio command backend
**Merged** · Adapter; recognizer not bundled  
**Owner:** Speech recognition service · **Canonical UX:** Shared attachments / microphone
Keep batch-file transcription and live recognition as two modes of the same speech service, with one transcript artifact format and no duplicate recorder.
**Evidence:** [R.media](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/media.py#L1) [G.client](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/s2s/s2s-ws-client.js#L1)

### R14 · create_docx / create_xlsx / create_pptx
**Preserved** · Implemented minimal OOXML writers; container smoke passes  
**Owner:** Document tools · **Canonical UX:** Workspace artifacts / shared viewer
Retain Word, spreadsheet and slide outputs. Upgrade writers/validation where needed; structural ZIP tests are not proof of rendering fidelity or full Office support.
**Evidence:** [R.docs](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/documents.py#L1)

### R15 · create_pdf / create_csv
**Preserved** · Implemented minimal writers; container smoke passes  
**Owner:** Document tools · **Canonical UX:** Workspace artifacts / shared viewer
Preserve simple text-PDF and CSV generation. Add encoding, escaping, pagination, locale and data/size validation without separate document-generation UIs.
**Evidence:** [R.docs](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/tools/documents.py#L1)

### R16 · 755-record / 642-distinct-name model-capability catalogue
**Transformed** · Reference data, not installed providers  
**Owner:** Provider catalogue and availability registry · **Canonical UX:** Settings / Connections
Keep modality/provider reference metadata with provenance and duplicate-name/version normalization. Only configured and tested adapters become available capabilities.
**Evidence:** [R.catalog](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/uploads/arena-ai-agent-full-model-and-capabilities-list.json#L1) [R.mapping](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/docs/CAPABILITY_MAPPING.md#L1)

### R17 · API/static preview server, permissive CORS and shared in-memory agent
**Transformed** · Implemented local prototype; no auth/session isolation  
**Owner:** Authenticated gateway · **Canonical UX:** Single application origin
Replace global agent state and permissive origins, add session/project roles, CSRF/origin validation and isolated untrusted previews. A localhost URL is not an authentication boundary.
**Evidence:** [R.server](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/server.py#L1) [R.config](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/config.py#L1)

### R18 · Deep-merged JSON config, quickstarts, safety docs and capability mapping
**Merged** · Implemented config and useful documentation  
**Owner:** Versioned configuration schema · **Canonical UX:** Settings / Connections
Preserve configurable model/tool/provider/sandbox options and clear setup docs; collapse entrypoints/configs into one launcher with explicit per-provider profiles and health checks.
**Evidence:** [R.config](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/config.py#L1) [R.readme](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/README.md#L1) [R.security](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/SECURITY.md#L1) [R.mapping](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/docs/CAPABILITY_MAPPING.md#L1) [R.run](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/run.py#L1)

### R19 · Committed venv, caches, bytecode, example workspace and uploaded images
**Retired** · Environment/examples, not features  
**Owner:** Source provenance archive · **Canonical UX:** No production capability
Remove bundled environments/caches and seed user uploads from shipping packages; retain examples as fixtures and migrate real user artifacts only by explicit import. Do not count dependencies as authored capabilities.
**Evidence:** [R.readme](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/README.md#L1) [R.workspace](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/workspace.py#L1)

## Gemma Avatar

### G01 · TalkingHead + HeadAudio stage with MFCC-driven Oculus visemes
**Preserved** · Implemented integration; browser/audio not exercised  
**Owner:** Avatar presentation · **Canonical UX:** Shared Presence panel
Retain audio-derived lip-sync, blinking, breathing, gaze, idle motion and response choreography. The stage presents conversation state; it is not an independent conversational agent.
**Evidence:** [G.avatar](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/avatar.js#L1) [G.app](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/app.js#L1)

### G02 · One shared AudioContext for capture/playback/lip-sync and reverb
**Preserved** · Implemented audio architecture  
**Owner:** Shared audio graph · **Canonical UX:** One mic/playback ownership model
Make this the primary audio graph, shared by conversation, avatar and narration; avoid duplicated contexts/speakers or lip-sync driven by a different signal.
**Evidence:** [G.avatar](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/avatar.js#L1) [G.client](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/s2s/s2s-ws-client.js#L1)

### G03 · set_mood / make_hand_gesture / make_facial_expression tools
**Merged** · Implemented client dispatch  
**Owner:** Expression tool family · **Canonical UX:** Presence / shared tool registry
Retain eight mood choices, seven gestures and emoji/expression affordances with strict schemas; host authorizes low-risk expression commands. Internal affect and chosen public expression remain distinct.
**Evidence:** [G.avatar](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/avatar.js#L1) [G.app](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/app.js#L1) [S.state](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/state.py#L1) [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031)

### G04 · 16 kHz PCM capture, 40 ms packets, resampling, clipping, noise gate and local speech detection
**Preserved** · Implemented worklet; pure logic fixtures pass  
**Owner:** Realtime speech capture · **Canonical UX:** Shared mic control
Keep codec and streaming worklet logic, add real microphone/browser/echo tests, explicit privacy indicator and device-independent input lifecycle. Fixtures are not microphone integration validation.
**Evidence:** [G.mic](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/public/worklets/mic-capture.js#L1) [G.codec](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/s2s/codec.js#L1) [G.client](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/s2s/s2s-ws-client.js#L1)

### G05 · PCM playback queue, resampling, startup buffering, fades and output gating
**Preserved** · Implemented worklet; bounded fixtures pass  
**Owner:** Realtime speech playback · **Canonical UX:** Shared audio controls
Preserve robust playback buffering/resampling and reset/fade semantics in the shared audio service; test underruns, clock drift and slow/fast device rates.
**Evidence:** [G.play](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/public/worklets/audio-playback.js#L1) [G.client](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/s2s/s2s-ws-client.js#L1)

### G06 · Barge-in, cancellation, late-event suppression, transcript finalization and response serialization
**Merged** · Implemented stream-control logic  
**Owner:** Turn/run cancellation coordinator · **Canonical UX:** One Stop/interrupt action
Retain interruption behavior and serialized response tools; propagate run/turn epoch to generation, tools, playback, avatar and stored partial transcript, not just local speaker mute.
**Evidence:** [G.client](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/s2s/s2s-ws-client.js#L1) [G.play](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/public/worklets/audio-playback.js#L1)

### G07 · OpenAI-style realtime WebSocket events, text/audio transcripts and tool-call normalization
**Merged** · Implemented compatibility client  
**Owner:** Realtime/model protocol adapter · **Canonical UX:** Shared composer / transcript
Keep mixed content/event compatibility and tool/result normalization behind the common protocol; model backends cannot bypass host policy through browser-dispatched task tools.
**Evidence:** [G.client](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/s2s/s2s-ws-client.js#L1) [G.codec](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/s2s/codec.js#L1) [R.agent](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/agent.py#L1)

### G08 · Hosted session grants, health/queue status, polling, cancellation and logs
**Preserved** · Implemented frontend/proxy integration; remote service external  
**Owner:** Optional remote realtime provider · **Canonical UX:** Settings connection + Activity
Preserve hosted-session capability with explicit consent, encrypted transport and secrets handled by server. Local and hosted are provider modes in one conversation, not two products.
**Evidence:** [G.server](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/index.ts#L1) [G.client](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/s2s/s2s-ws-client.js#L1) [G.app](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/app.js#L1)

### G09 · Local WebSocket mode and configurable backend
**Merged** · Implemented client/launcher integration  
**Owner:** Local realtime provider · **Canonical UX:** Same composer and connection settings
Use relative gateway WebSocket URLs in the browser and server-side provider addresses; no hardcoded browser localhost endpoints or standalone local avatar application.
**Evidence:** [G.client](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/s2s/s2s-ws-client.js#L1) [G.server](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/index.ts#L1) [G.s2sstart](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/start-speech-to-speech.sh#L1)

### G10 · Typed chat and typed response compatibility
**Transformed** · Implemented latest branch; start still requests microphone  
**Owner:** Input-independent turn transport · **Canonical UX:** Shared composer
Preserve current text/chat additions but decouple transport/session start from getUserMedia. Text must work with mic denied, unavailable or disabled; voice is an independent optional input.
**Evidence:** [G.app](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/app.js#L1) [G.client](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/s2s/s2s-ws-client.js#L1) [G.index](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/index.html#L1) [G.style](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/style.css#L1)

### G11 · Image, video, audio and text-file uploads; input_file event normalization
**Merged** · Implemented adapter; external decoder/STT dependencies  
**Owner:** Artifact ingestion + realtime attachments · **Canonical UX:** One attachment tray
Keep multimodal upload compatibility, image frames and video-audio transcription. Centralize sniffing/size/duration limits, extraction, sanitization, provenance and preview; do not append arbitrary untrusted file contents as authoritative instructions.
**Evidence:** [G.app](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/app.js#L1) [G.client](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/s2s/s2s-ws-client.js#L1) [G.launcher](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/local_s2s_launcher.py#L1) [R.workspace](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/workspace.py#L1) [N.dataset](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/dataset_analyzer.py#L1)

### G12 · Avatar Parts UI: body/face/clothes tabs, selection helpers and model hook
**Transformed** · UI helpers/stub; not wired into useful part inspection  
**Owner:** Avatar asset inspector · **Canonical UX:** Lab / Avatar assets
Retain the asset-inspection/customization intention and tab work as a backlog specification; use actual rig/mesh/morph/material information. Do not ship an inert second model inspector.
**Evidence:** [G.app](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/app.js#L1) [G.index](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/index.html#L1) [G.glb](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/public/avatars/brunette.glb) [N.mesh](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/prepare_model.py#L1)

### G13 · Local s2s launcher: Parakeet/STT imports, upload normalization, timeout and Qwen GGUF resolver patch
**Transformed** · External-engine compatibility adapter  
**Owner:** Pinned speech worker package · **Canonical UX:** Settings provider health
Preserve patches as tested versioned adapters around a separately installed speech-to-speech engine. Pin its API/version, replace monkeypatches with explicit interfaces where possible, and expose true readiness.
**Evidence:** [G.launcher](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/local_s2s_launcher.py#L1) [G.requirements](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/gemma-avatar-s2s-requirements-lock.txt#L1) [G.s2sstart](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/start-speech-to-speech.sh#L1)

### G14 · Torch versus GGUF TTS, model cache bootstrap and downloader
**Preserved** · Implemented setup adapters; large models absent  
**Owner:** Speech model asset manager · **Canonical UX:** Settings / Models
Keep selectable runtime profiles, cache/download checks and talker/codec resolution. The tracked .txt files are placeholders, not usable GGUF weights; downloads need manifest/hash/rights checks.
**Evidence:** [G.s2sstart](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/start-speech-to-speech.sh#L1) [G.download](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/download_tts_assets.py#L1) [G.placeholder1](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/models/qwen3-tts-gguf/qwen-talker-1.7b-customvoice-BF16.txt#L1) [G.placeholder2](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/models/qwen3-tts-gguf/qwen-tokenizer-12hz-BF16.txt#L1)

### G15 · Shell launch stack: Ollama, speech backend and avatar frontend
**Merged** · Implemented operational scripts; platform-dependent  
**Owner:** Single launcher/supervisor · **Canonical UX:** Operations
Preserve endpoint readiness, reuse/detection and teardown ideas. Replace hardcoded machine/WSL paths, independent public ports and ad hoc child processes with one config and durable process ownership.
**Evidence:** [G.runall](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/run-all-local.sh#L1) [G.ollamastart](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/start-ollama.sh#L1) [G.s2sstart](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/start-speech-to-speech.sh#L1) [G.frontendstart](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/start-avatar-frontend.sh#L1) [N.launch](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/launch.py#L1) [S.run](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/run.sh#L1) [R.run](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/run.py#L1)

### G16 · Embedded git bundle and July 2026 avatar history
**Preserved** · Real development/provenance archive  
**Owner:** Source/history archive · **Canonical UX:** No duplicate runtime
Retain the 12 bundle commits and compare their meaningful deltas. Current typed/media compatibility should survive; old shared files do not justify another application. Public main history alone does not capture this archive.
**Evidence:** [G.bundle](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/gemma-avatar.bundle) [G.readme](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/README.md#L1)

### G17 · GLB avatar: rig, meshes and blendshapes
**Preserved** · Usable asset; declared CC BY-NC 4.0  
**Owner:** Rights-aware avatar library · **Canonical UX:** Shared Presence / asset settings
Preserve brunette GLB and attribution: 78 nodes, 10 meshes, 1 skin, 72 morph targets across 4 meshes, no embedded animations. Respect declared noncommercial terms or substitute a permitted rig for commercial distribution.
**Evidence:** [G.glb](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/public/avatars/brunette.glb) [G.readme](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/README.md#L1)

### G18 · Vendored TalkingHead/HeadAudio/Three.js/fonts/models
**Merged** · Third-party integration assets  
**Owner:** Pinned frontend/audio dependencies · **Canonical UX:** No separate capability inventory
Preserve required runtime assets and license notices; choose one tested compatible dependency set and produce an SBOM. Do not count upstream source as original capability or delete it as apparent duplicate art.
**Evidence:** [G.package](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/package.json#L1) [G.avatar](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/avatar.js#L1) [G.codec](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/s2s/codec.js#L1)

### G19 · SHA256SUMS, Python requirements lock, Docker and tool smoke script
**Transformed** · Packaging/test scaffolding; integrity not reproducible  
**Owner:** Reproducible package and CI · **Canonical UX:** Operations / health
Keep the integrity/installation/test intent. Regenerate a non-self-referential manifest (17/31 entries match; 14 stale), truly pin requirements (some use >=), verify container/build compatibility and replace endpoint-only checks with contracts.
**Evidence:** [G.sha](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/SHA256SUMS.txt#L1) [G.requirements](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/gemma-avatar-s2s-requirements-lock.txt#L1) [G.docker](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/Dockerfile#L1) [G.test](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/test-tools.sh#L1) [G.guide](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/SETUP-GUIDE.md#L1)

### G20 · Avatar style/layout, status, transcript, provider and mic UI
**Merged** · Implemented dedicated shell  
**Owner:** Shared frontend components · **Canonical UX:** Shared composer + Presence
Carry expressive stage, transcript/status design and responsive layout into one shell; remove duplicate session, settings, transcript and microphone controls after parity.
**Evidence:** [G.app](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/app.js#L1) [G.index](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/index.html#L1) [G.style](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/style.css#L1)

## Sage

### S01 · SQLite event journal, memories, wants and private storage
**Preserved** · Implemented durable core  
**Owner:** Continuity service · **Canonical UX:** Memory / continuity inspector
Use as the persistence foundation with schema migrations, visibility scopes, workspace/session/actor IDs and recoverable backups. It is not replaced by chat history or LoRA weights.
**Evidence:** [S.memory](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/memory.py#L1) [S.daemon](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/daemon.py#L1)

### S02 · Autonomous wakes, last-wake continuity, offline gaps and periodic review
**Preserved** · Implemented daemon/state  
**Owner:** Continuity scheduler · **Canonical UX:** One continuity timeline / autonomy controls
Retain idle wakes, gap awareness and review intervals as budgeted jobs feeding the same actor/runtime; make start/pause/stop/operator control explicit. No second always-on chat loop.
**Evidence:** [S.daemon](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/daemon.py#L1) [S.clock](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/clock.py#L1) [S.state](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/state.py#L1)

### S03 · Clock, local timestamps, awake/runtime ages and calendar awareness
**Merged** · Implemented  
**Owner:** Clock/event service · **Canonical UX:** Continuity timeline / time tool
Keep timezone-aware wall time, monotonic durations and recorded wake/offline transitions. Share one clock with the agent and jobs.
**Evidence:** [S.clock](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/clock.py#L1) [S.daemon](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/daemon.py#L1) [A.clock](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/tools/current_time.py#L1)

### S04 · Versioned self.md, seed identity, bounded edits and self history
**Preserved** · Implemented; user state committed  
**Owner:** Identity/profile versions · **Canonical UX:** Continuity / Self profile
Preserve version history and bounded self-updates with provenance and explicit policy. Import existing self profiles as private user state rather than shipping one person’s history as the default identity.
**Evidence:** [S.self](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/selfmodel.py#L1) [S.daemon](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/daemon.py#L1) [S.data](https://github.com/flrtemis/Sage/tree/701f917eab403c32263deb08a85de24f59514518/data)

### S05 · PAD affect, decay, targets, drive names, gain and mood/avatar values
**Preserved** · Implemented state model  
**Owner:** Affect engine · **Canonical UX:** Continuity state + shared Presence
Preserve continuous valence/arousal/dominance dynamics and drive/target logic; map into avatar expressions through an explicit presentation policy. These variables are simulation/design state, not proof of subjective feeling.
**Evidence:** [S.state](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/state.py#L1) [S.daemon](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/daemon.py#L1) [G.avatar](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/avatar.js#L1)

### S06 · Weighted recall with relevance, age and emotional weighting
**Preserved** · Implemented retrieval  
**Owner:** Memory retrieval · **Canonical UX:** Continuity / Memories
Retain salience/recency/relevance mechanics, add scope/provenance and explainable recall. Do not silently turn all memories into training data or universal context.
**Evidence:** [S.memory](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/memory.py#L1) [S.mind](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/mind.py#L1)

### S07 · look_back modes for wakes, events, memories, letters and self
**Preserved** · Implemented deliberation tool and follow-up  
**Owner:** Continuity query tools · **Canonical UX:** Shared composer / continuity inspector
Keep mode-specific retrieval and model follow-up as one typed tool family, with path/visibility limits and bounded context. It is not just generic file search.
**Evidence:** [S.mind](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/mind.py#L1) [S.daemon](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/daemon.py#L1) [S.memory](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/memory.py#L1) [S.tests2](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/tests/test_lookback.py#L1)

### S08 · Letters, reading/reflection and pending material across turns
**Preserved** · Implemented continuity flow; path defect reproduced  
**Owner:** Continuity material intake · **Canonical UX:** Continuity inbox / same conversation
Preserve asynchronous letters/pending reminders. Replace letter names with stored IDs and safe resolution: exact method reads outside letters for ../../outside in a fresh fixture.
**Evidence:** [S.daemon](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/daemon.py#L1) [S.mind](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/mind.py#L1) [S.data](https://github.com/flrtemis/Sage/tree/701f917eab403c32263deb08a85de24f59514518/data)

### S09 · Wants/goals, memory edits and constrained action vocabulary
**Merged** · Implemented mind/action handling  
**Owner:** Goals and agent policy · **Canonical UX:** Continuity / Goals + job proposals
Keep wants, salience and constrained action semantics; bind approved actionable wants to real task IDs instead of duplicating Pip-Boy quests or inventing a second planner.
**Evidence:** [S.memory](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/memory.py#L1) [S.mind](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/mind.py#L1) [S.daemon](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/daemon.py#L1) [R.agent](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/agent.py#L1)

### S10 · Generated public reflections and private inward entries
**Transformed** · Implemented visibility concept; filtering inadequate  
**Owner:** Privacy-scoped event/material storage · **Canonical UX:** Continuity, filtered by role
Preserve private/public distinction with structured serialization and access policy. Key-order-sensitive regex scrubber leaks synthetic private text; raw generated thought/reflection fields need policy too. Never publish private diary contents by default.
**Evidence:** [S.mind](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/mind.py#L1) [S.daemon](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/daemon.py#L1) [S.memory](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/memory.py#L1) [S.server](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/server.py#L1)

### S11 · Prompt construction joining self/state/pending, history and recall
**Merged** · Implemented continuity-oriented mind  
**Owner:** Context builder · **Canonical UX:** Same Agent runtime
Keep continuity context and bounded look-back decisions; add project/task/tool schemas and untrusted-source separation. One context builder combines Sage identity with Arena task reasoning, not concatenated independent system prompts.
**Evidence:** [S.mind](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/mind.py#L1) [R.agent](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/agent.py#L1) [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031)

### S12 · Garble/repetition/echo guards, retry and graceful provider failures
**Preserved** · Implemented; tests with one tautological assertion  
**Owner:** Generation quality gate · **Canonical UX:** Conversation / job error states
Preserve bounded retry and continuity-friendly failures. Strengthen actual echo/loop tests and deterministic retry budgets; a passing or True assertion is not evidence.
**Evidence:** [S.daemon](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/daemon.py#L1) [S.backend](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/backends.py#L1) [S.tests1](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/tests/test_continuity.py#L1)

### S13 · Ollama think:false, 8192 context, 24h keep-alive, prewarm and installed-model fallback
**Merged** · Implemented adapter; fake-provider tests  
**Owner:** Model gateway policies · **Canonical UX:** Settings / Models
Keep per-model readiness/fallback/prewarm behavior as configurable profiles; do not hardcode every model or silently switch identity/model provenance. The defaults are not performance guarantees.
**Evidence:** [S.backend](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/backends.py#L1) [S.config](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/config.py#L1) [S.tests3](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/tests/test_ollama_path.py#L1) [R.ollama](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/ollama.py#L1)

### S14 · OpenAI-compatible backend and offline stand-in
**Merged** · Implemented adapters  
**Owner:** Model gateway · **Canonical UX:** Settings / Connections and explicit demo badge
Retain compatible local/remote endpoint mode and deterministic stand-in for testing. The stand-in remains explicitly synthetic, and remote egress requires consent.
**Evidence:** [S.backend](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/backends.py#L1) [S.config](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/config.py#L1)

### S15 · Live SSE state/events, journal/self/memory/wants/context/export APIs
**Merged** · Implemented local server; no access control  
**Owner:** Gateway/event projections · **Canonical UX:** Continuity panels + shared event stream
Preserve live feed, context export and history views; add durable replay cursors, per-visibility projections and auth. Do not expose private raw context via unrestricted diagnostics.
**Evidence:** [S.server](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/server.py#L1) [S.daemon](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/daemon.py#L1) [S.memory](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/memory.py#L1)

### S16 · Continuity dashboard: live state, age, thought/reflection, feed, self, memory/wants and say/wake
**Merged** · Implemented client  
**Owner:** Shared continuity components · **Canonical UX:** Memory/continuity + shared composer
Preserve the non-chat-centric observability and manual wake affordance inside the unified shell. Remove duplicate say/chat input and independently owned event feed.
**Evidence:** [S.ui](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/web/index.html#L1) [S.server](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/server.py#L1)

### S17 · CLI, stdlib startup, systemd service and update/backup instructions
**Merged** · Implemented deployment continuity work  
**Owner:** Launcher, service and data migration · **Canonical UX:** Operations
Retain inexpensive always-on worker, backup-first update practices and supervised start/stop; fix Thread._stop Event name collision and verify clean joining/restart.
**Evidence:** [S.entry](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/__main__.py#L1) [S.run](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/run.sh#L1) [S.service](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake.service#L1) [S.update](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/UPDATE-HOW-TO.txt#L1) [S.start](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/START-HERE.txt#L1) [S.daemon](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/daemon.py#L1) [S.init](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/__init__.py#L1)

### S18 · Continuity/look-back/Ollama path tests
**Preserved** · 60 checks reported; one vacuous assertion  
**Owner:** Unified contract/regression suite · **Canonical UX:** No separate product UX
Retain meaningful fixtures and strengthen privacy, non-vacuous echo checks, clean shutdown, interruption/restart and migration tests. Existing passes do not certify consciousness or end-to-end behavior.
**Evidence:** [S.tests1](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/tests/test_continuity.py#L1) [S.tests2](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/tests/test_lookback.py#L1) [S.tests3](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/tests/test_ollama_path.py#L1)

### S19 · Committed SQLite/WAL/SHM, self/history, letter and state data
**Preserved** · Sensitive real user state, not examples  
**Owner:** Private migration/vault · **Canonical UX:** Explicit import/export/backup
Preserve actual continuity via transaction-safe SQLite backups including WAL consistency, user consent and visibility migration. Exclude personal records from new-install packages and public reports; do not erase them as duplication.
**Evidence:** [S.data](https://github.com/flrtemis/Sage/tree/701f917eab403c32263deb08a85de24f59514518/data) [S.memory](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/memory.py#L1) [S.update](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/UPDATE-HOW-TO.txt#L1)

## Neural Sim

### N01 · NF4/double-quantized Hugging Face model + LoRA for Qwen/Llama
**Preserved** · Implemented training loader; GPU stack unvalidated  
**Owner:** Training/model worker · **Canonical UX:** Lab / Training runs
Keep quantization/dtype/device/adapter options and architecture hooks. Pin model revision/code permissions; trust_remote_code=True is a trust grant, not a safe default. Ollama-serving weights and trainable HF adapters need explicit compatibility/export steps.
**Evidence:** [N.loader](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/model_loader.py#L1) [N.trainer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/trainer.py#L1)

### N02 · Training start/stop/step, callbacks, inference lock, state/parameter control and checkpointing
**Transformed** · Implemented worker; not model-executed  
**Owner:** Experiment runner + GPU resource broker · **Canonical UX:** Lab run inspector
Preserve lifecycle/state/callback/inference controls and extend them to real resume/checkpoint contracts, typed parameters and resource arbitration. One job schema hosts all experiments, without combining scientifically different engines.
**Evidence:** [N.trainer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/trainer.py#L1) [N.trainingServer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/server.py#L1) [N.launch](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/launch.py#L1)

### N03 · Forward/backward HookManager, activation/gradient/attention/weight snapshots
**Preserved** · Implemented instrumentation; exception-heavy  
**Owner:** Sampled diagnostic capture · **Canonical UX:** Lab run inspector
Keep architecture-aware hooks, PCA/histograms/correlations/rank/Fisher snapshots; validate snapshot consistency, lock capture, budget expensive SVD/CPU copies and mark unsupported measurements absent rather than zero.
**Evidence:** [N.hooks](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/hooks.py#L1) [N.metrics](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/metrics.py#L1)

### N04 · 48 declared AI metric families / 63 AIMetrics fields and serialization
**Transformed** · Implemented; many proxies or duplicate formulas  
**Owner:** Typed measured diagnostic registry · **Canonical UX:** Single metric inspector
Preserve every diagnostic question, repair or honestly rename estimates, namespace quality/provenance, and merge equal formulas such as CKA/information-flow norm ratios. Accuracy is never assigned. See all 48 in the metric appendix.
**Evidence:** [N.metrics](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/metrics.py#L1) [C.metrics](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/metrics.py#L22-L824) [N.hooks](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/hooks.py#L1)

### N05 · SAM two-step perturbation optimization
**Transformed** · Implemented branch; composition broken with replay  
**Owner:** Selectable training recipe · **Canonical UX:** Lab / Training configuration
Keep the SAM experiment, but validate closure/objective/restore/step ordering with replay/distillation/EWC. Current replay path overwrites SAM gradients; mere branch presence is not working combination evidence.
**Evidence:** [N.trainer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/trainer.py#L1)

### N06 · Layerwise LR decay, warmup and SGDR/cosine restarts
**Preserved** · Implemented optimization mechanisms  
**Owner:** Training recipe optimizer/scheduler · **Canonical UX:** Training configuration
Retain distinct layer/temporal schedule controls and complete state serialization. They are not duplicates of high-level self-modification proposals.
**Evidence:** [N.trainer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/trainer.py#L1)

### N07 · Replay buffer, surprise-weighted priorities, replay ratio and forgetting probes
**Transformed** · Implemented mechanism; measurement/gradient interactions need repair  
**Owner:** Continual-learning recipe · **Canonical UX:** Training configuration / evaluations
Retain replay/prioritization and retention intent, fix objective composition and compare matched before/after evaluation sets. A different minibatch’s loss is not causal replay benefit.
**Evidence:** [N.trainer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/trainer.py#L1) [N.metrics](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/metrics.py#L1)

### N08 · PCGrad conflict projection
**Preserved** · Implemented optimizer experiment; integration unvalidated  
**Owner:** Selectable multi-objective recipe · **Canonical UX:** Training configuration
Keep gradient-conflict handling as optional recipe when true multiple objectives exist; test projection and interactions, rather than treating its purpose as identical to clipping or SAM.
**Evidence:** [N.trainer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/trainer.py#L1)

### N09 · EWC Fisher accumulation and consolidation penalty
**Transformed** · Implemented continual-learning mechanism  
**Owner:** Continual-learning recipe · **Canonical UX:** Training configuration / retention evaluation
Retain parameter/Fisher anchoring, repair correct objective/parameter mapping and checkpoints, and validate actual forgetting mitigation. Sage episodic persistence does not replace it.
**Evidence:** [N.trainer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/trainer.py#L1) [N.hooks](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/hooks.py#L1) [N.metrics](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/metrics.py#L1)

### N10 · EMA teacher / temperature distillation
**Transformed** · Implemented experiment; student detached  
**Owner:** Distillation recipe · **Canonical UX:** Training configuration / teacher lineage
Preserve teacher updating/temperature/KL objective intention; repair detached student logits so the term can backpropagate, isolate teacher hooks and verify gradient change and held-out benefit.
**Evidence:** [N.trainer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/trainer.py#L1) [N.metrics](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/metrics.py#L1)

### N11 · Gradient noise, clipping, LoRA pruning and dead-neuron detection
**Preserved** · Implemented interventions/monitoring  
**Owner:** Training recipe safeguards · **Canonical UX:** Training configuration / metric inspector
Keep these separate mechanisms with measurable intervention logs and bounded settings. Do not infer biological learning or safety from their names.
**Evidence:** [N.trainer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/trainer.py#L1) [N.hooks](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/hooks.py#L1) [N.metrics](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/metrics.py#L1)

### N12 · Meta-learning inner step and meta loss
**Transformed** · Implemented first-order-style experiment  
**Owner:** Selectable adaptation recipe · **Canonical UX:** Training configuration / evaluations
Preserve fast-adaptation research but label it first-order, repair baseline/optimizer state and evaluate held-out adaptation; do not describe as demonstrated full second-order MAML.
**Evidence:** [N.trainer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/trainer.py#L1) [N.metrics](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/metrics.py#L1)

### N13 · Token importance weighting
**Transformed** · Computed importance; not used in training objective  
**Owner:** Optional token-weighted objective · **Canonical UX:** Training configuration
Keep the intended token salience experiment; wire a validated weighted unreduced loss and test its effect or mark unavailable. Logging an unused scalar is not a capability.
**Evidence:** [N.trainer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/trainer.py#L1) [N.metrics](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/metrics.py#L1)

### N14 · Dynamic LoRA rank adaptation
**Transformed** · Logged/config state only, no actual module resize  
**Owner:** Versioned adapter reconfiguration · **Canonical UX:** Change proposal / Training configuration
Preserve rank adaptation as a proposed safe rebuild/conversion operation with optimizer-state handling and comparison; retire apparent immediate success until implemented.
**Evidence:** [N.trainer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/trainer.py#L1) [N.selfmod](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/self_modify.py#L1)

### N15 · Model-written bounded hyperparameter proposals, explanations and self-mod history
**Transformed** · Implemented controller  
**Owner:** Change proposal service · **Canonical UX:** Lab / Changes, same approval UI
Retain diagnosis-to-proposal, bounds and audit trail; default to review/automatic opt-in only inside a sandboxed experiment. Test typed/finite values, unsupported params and actual post-change effects.
**Evidence:** [N.selfmod](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/self_modify.py#L1) [N.trainer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/trainer.py#L1)

### N16 · Pareto frontier, GP observations/predictions and evolutionary population
**Transformed** · Partial optimizer experiments; no complete evaluation loop  
**Owner:** Optimizer experiment plugins · **Canonical UX:** Lab / Optimizer study
Preserve multi-objective search intent and helper code. GP acquisition is not used to select active updates and population fitness updates member zero only; require real candidate trials before claiming Bayesian/evolutionary optimization.
**Evidence:** [N.selfmod](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/self_modify.py#L1)

### N17 · Plateau detection, curriculum labels, three-step plans and interdependence rules
**Transformed** · Partially implemented heuristics/placeholders  
**Owner:** Training control policy · **Canonical UX:** Training changes and dataset schedule
Keep plateau/planning/interdependence intention; make curriculum change actual sampler/task difficulty, propagate correct bounded dependent changes and attribute outcomes rather than showing labels only.
**Evidence:** [N.selfmod](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/self_modify.py#L1) [N.trainer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/trainer.py#L1)

### N18 · Confidence history and loss-triggered parameter rollback
**Transformed** · Implemented partial safeguard; inadequate outcomes/state  
**Owner:** Transactional change evaluation · **Canonical UX:** Change inspector
Current outcome logging records same before/after loss, and rollback restores hyperparameters not model/optimizer/scheduler/RNG. Preserve the safeguard idea with delayed matched evaluation and full checkpoints.
**Evidence:** [N.selfmod](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/self_modify.py#L1) [N.trainer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/trainer.py#L1)

### N19 · Izhikevich cortex/thalamus/cerebellum, E/I cells, conductance, delays, STDP and homeostasis
**Merged** · Implemented simulator; original initialization fails  
**Owner:** Bio simulation worker · **Canonical UX:** Lab / Bio runs
Retain the independent 1,090-neuron reference engine and layer/column anatomy. Start from command-center’s three fixes, then repair GABA sign, actual 50 versus declared 200 inhibitory cells, delays and timestep semantics. It is not the LLM itself.
**Evidence:** [N.bio](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/bio_model.py#L1) [C.bio](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/bio_model.py#L153-L1073)

### N20 · Pruning, neuromodulators, apical error, brain states, oscillation bands, synchrony and consolidation proxies
**Transformed** · Implemented simulation diagnostics; scientific meaning unvalidated  
**Owner:** Bio model + diagnostic schema · **Canonical UX:** Bio run / single metric inspector
Preserve every mechanism and 41 BioMetrics fields; verify dimensionality/frequency windows and measured/proxy labels. Do not merge bio dopamine/pain into Sage PAD state or assert human-brain validity.
**Evidence:** [N.bio](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/bio_model.py#L1) [N.metrics](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/metrics.py#L1) [C.bio](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/bio_model.py#L153-L1073)

### N21 · CSV/JSON/text statistics, units, complexity and structural/text findings
**Merged** · Implemented parser; bounded fixtures  
**Owner:** Artifact ingestion + dataset analysis · **Canonical UX:** Workspace artifact / Lab dataset inspector
Keep actual statistics and interpretation hooks in one shared analyzer. JSONL/TSV/YAML/XML/PDF support is not genuinely implemented as their proper structures; extend explicit adapters rather than silently treating them as text.
**Evidence:** [N.dataset](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/dataset_analyzer.py#L1) [C.dataset](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/dataset_analyzer.py#L55-L1603) [R.workspace](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/workspace.py#L1) [G.launcher](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/local_s2s_launcher.py#L1)

### N22 · Human-versus-AI cognitive walkthrough frames and dataset summary
**Transformed** · Implemented scripted frame generator; not real cognition  
**Owner:** Educational/demo analysis projection · **Canonical UX:** Dataset inspector, explicit simulation badge
Retain the explanatory experience and visualization patterns as demonstrations. Separate real file statistics from generated cognitive narratives/frames, fix WebSocket broadcast UnboundLocalError and do not claim measured thinking.
**Evidence:** [N.dataset](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/dataset_analyzer.py#L1) [N.workspaceServer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/dashboard_server.py#L1) [C.demo](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/demo/demo_server.py#L31-L223)

### N23 · Training API/WebSocket metrics server and separate process/workspace host
**Merged** · Implemented two different backends with inconsistent routes  
**Owner:** Gateway + experiment workers + supervisor · **Canonical UX:** Operations / Lab, one origin
Training server controls real engine state; dashboard host handles processes/logs/terminal/voice/verify/promote/datasets. Merge overlapping transport/control primitives, preserve both distinct responsibilities; repair no-op selfmod, buffered SSE and missing avatar endpoint.
**Evidence:** [N.trainingServer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/server.py#L1) [N.workspaceServer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/dashboard_server.py#L1)

### N24 · Launcher, cross-platform/WSL helpers and training startup packaging
**Transformed** · Implemented with missing referenced config/static/package paths  
**Owner:** Reproducible launcher / provider profiles · **Canonical UX:** Operations / model setup
Keep platform setup and worker configuration intent. Supply versioned requirements/config, proper imports and static frontend; current training root serves missing static/index.html rather than the tracked 3D dashboard.
**Evidence:** [N.launch](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/launch.py#L1) [N.trainingServer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/server.py#L1) [N.readme](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/README.md#L1) [C.config](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/config.yaml#L1-L74) [G.runall](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/run-all-local.sh#L1)

### N25 · prepare_model.py OBJ/MTL/texture preparation and face subsampling
**Transformed** · Implemented local asset utility; source assets absent  
**Owner:** Avatar asset import/optimization · **Canonical UX:** Lab / Avatar asset inspector
Preserve the inexpensive asset pipeline idea, make paths configurable and rights-aware; replace every-Nth-face deletion with topology-preserving simplification and tested GLB/rig/morph preservation. This prepares a mesh, not LLM weights.
**Evidence:** [N.mesh](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/prepare_model.py#L1) [C.avatar](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/sage_avatar.js#L1-L1472) [G.glb](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/public/avatars/brunette.glb)

### N26 · Standalone copied command-center dashboard
**Merged** · Near duplicate; duplicate JS declaration fails parse  
**Owner:** Single spatial renderer · **Canonical UX:** Workspace spatial mode
Use command-center’s syntax/import fixes, merge unique recovered additions, and retire the independent neural dashboard shell. Keep its diagnostic renderer as shared components.
**Evidence:** [N.dashboard](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/dashboard_3d.html#L1) [C.main](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/dashboard_3d.html#L806-L6330) [C.recovered](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/dashboard_3d_may3_pipboy_sage.html#L697-L4443)

### N27 · IMPROVEMENTS.md and implementation assertions
**Transformed** · Specifications, experiments and overclaims mixed  
**Owner:** Traceable research backlog · **Canonical UX:** Lab experiment catalogue
Preserve proposed goals, map each assertion to real branch/formula/tests and mark absent/inert/proxy paths. Documentation ambition is not execution evidence.
**Evidence:** [N.improvements](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/IMPROVEMENTS.md#L1) [N.trainer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/trainer.py#L1) [N.metrics](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/metrics.py#L1) [N.selfmod](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/self_modify.py#L1)

## Universe

### U01 · Authoritative world -> partial immutable sensors -> belief/workspace epistemic firewall
**Preserved** · Blueprint only  
**Owner:** Embodied experiment boundary · **Canonical UX:** Lab / World runs
Preserve as the world engine’s foundational contract: operator sees truth, participant sees only authorized observations. Never leak full scene, filesystem or debug truth through generic agent tools.
**Evidence:** [U.blueprint](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/living_avatar_subjective_experience_blueprint_v0_3.md#L1)

### U02 · Intent -> motor controller -> forces/torques and sensory feedback
**Preserved** · Blueprint only  
**Owner:** Embodied world/controller worker · **Canonical UX:** World run inspector
Keep explicit action/control and proprioceptive/collision/balance feedback. Expressive TalkingHead gestures are not a motor/body controller and cannot replace this research.
**Evidence:** [U.blueprint](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/living_avatar_subjective_experience_blueprint_v0_3.md#L1) [U.initial](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/Initial-Blueprint.txt#L1)

### U03 · Prediction errors, self/body/attention models, uncertainty and persistent experience
**Transformed** · Blueprint only  
**Owner:** Embodied agent experiment profile · **Canonical UX:** World run inspector
Translate into falsifiable state schemas and baselines using the shared Agent runtime with restricted sensor/action tools and experiment-scoped memory. Not evidence of consciousness or a second product personality.
**Evidence:** [U.blueprint](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/living_avatar_subjective_experience_blueprint_v0_3.md#L1) [S.memory](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/memory.py#L1) [S.state](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/state.py#L1)

### U04 · Direct tensor/activation -> physics parameter pathway
**Transformed** · Early proposal  
**Owner:** Explicit bounded experimental actuator · **Canonical UX:** World experiment configuration
Preserve as an opt-in causal intervention under authoritative world rules, normalized/clamped and logged. It is not ordinary proprioception and should not silently let thought rewrite gravity.
**Evidence:** [U.initial](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/Initial-Blueprint.txt#L1) [U.blueprint](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/living_avatar_subjective_experience_blueprint_v0_3.md#L1)

### U05 · Indirect semantic agency through intermediary force/motor model
**Preserved** · Early proposal refined in blueprint  
**Owner:** Semantic intent compiler/controller · **Canonical UX:** Same World action API
Keep semantic intent as a higher-level control mode with validated targets/actions; same controller contract, not a duplicate physics engine or unconstrained prompt-to-force access.
**Evidence:** [U.initial](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/Initial-Blueprint.txt#L1) [U.blueprint](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/living_avatar_subjective_experience_blueprint_v0_3.md#L1)

### U06 · Implicit attention -> gaze/posture/spatial transformation
**Transformed** · Early proposal  
**Owner:** Calibrated optional attention-control experiment · **Canonical UX:** World experiment configuration / shared avatar adapter
Preserve as a testable attention-action mapping, but attention weights are not self-evidently gaze or intention. Separate cosmetic gaze presentation from causal environmental changes.
**Evidence:** [U.initial](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/Initial-Blueprint.txt#L1) [U.blueprint](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/living_avatar_subjective_experience_blueprint_v0_3.md#L1) [G.avatar](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/avatar.js#L1)

### U07 · Transient non-token loop versus persistent semantic summaries
**Preserved** · Blueprint only  
**Owner:** Sensor/telemetry buffers + scoped continuity · **Canonical UX:** World run / continuity summary
Keep high-rate tensors/sensors off the context window; persist selected observations, intentions, consequences and provenance. Experience state does not automatically become weight training.
**Evidence:** [U.initial](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/Initial-Blueprint.txt#L1) [U.blueprint](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/living_avatar_subjective_experience_blueprint_v0_3.md#L1) [S.memory](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/memory.py#L1)

### U08 · Decoupled physics/motor/cognition clocks and read-only sensory registers
**Preserved** · Blueprint only  
**Owner:** World scheduler and event transport · **Canonical UX:** World run inspector
Preserve proposed 60–240 Hz physics, 10–60 Hz motor and event/few-Hz cognition as configurable targets, with measured latency/backpressure and immutable snapshots. Rendering cannot wait for token generation.
**Evidence:** [U.initial](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/Initial-Blueprint.txt#L1) [U.blueprint](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/living_avatar_subjective_experience_blueprint_v0_3.md#L1)

### U09 · Zero-copy LibTorch/C++ VRAM bridge into Godot/Unity
**Transformed** · Unimplemented optimization proposal  
**Owner:** Optional native transport adapter · **Canonical UX:** No separate UX
Keep only after a simple IPC/sensor baseline works and profiling proves need. Requires ownership/lifetime/device contracts; browser/remote WebSocket traffic cannot be called zero-copy VRAM.
**Evidence:** [U.initial](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/Initial-Blueprint.txt#L1)

### U10 · Minimal sphere/gravity sandbox and gradual embodiment
**Preserved** · Blueprint/proposed experiment ladder  
**Owner:** World experiment templates · **Canonical UX:** Lab / World runs
Begin with isolated deterministic sphere/object tasks, then motor/body loops and richer worlds. Reuse rendering infrastructure without confusing the file Atlas or facility with an embodied causal environment.
**Evidence:** [U.initial](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/Initial-Blueprint.txt#L1) [U.blueprint](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/living_avatar_subjective_experience_blueprint_v0_3.md#L1)

### U11 · Isolation, seeded replay, theory-informed ablations and consciousness evaluation cautions
**Preserved** · Blueprint requirements, not scientific results  
**Owner:** Research protocol / evaluation runner · **Canonical UX:** World run / evaluation comparison
Preserve matched controls, replay, workspace/self/attention/persistence ablations and documented limitations. Literature references were not independently fact-checked here; no numeric consciousness score or proof.
**Evidence:** [U.blueprint](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/living_avatar_subjective_experience_blueprint_v0_3.md#L1)

### U12 · Welfare, distress safeguards, consent, stop conditions and speculative subjectivity
**Preserved** · Blueprint requirements  
**Owner:** Experiment safety policy · **Canonical UX:** World safety panel / global Stop
Keep precautionary limits, reversible shutdown and humane experimental framing. Self-report or bio pain proxies are not validated welfare/consciousness measurements.
**Evidence:** [U.blueprint](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/living_avatar_subjective_experience_blueprint_v0_3.md#L1)

## Cross-repository rules

### X01 · Runtime memory, self-profile changes, generated plugins and weight training
**Preserved** · Distinct adaptation layers  
**Owner:** Continuity / Changes / Training with shared provenance · **Canonical UX:** One proposal/approval language; distinct scopes
Keep all four because they change different things. Scope, permission, evaluation and rollback vary; sharing an approval service does not make them interchangeable.
**Evidence:** [S.memory](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/memory.py#L1) [S.self](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/selfmodel.py#L1) [A.genesis](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/genesis.py#L1-L98) [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031) [N.trainer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/trainer.py#L1) [N.selfmod](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/self_modify.py#L1)

### X02 · PAD affect, public expression, bio neurotransmitters and embodied signals
**Preserved** · Distinct representations  
**Owner:** Affect engine / avatar / Bio / World · **Canonical UX:** Common inspector with explicit namespaces
Map intentionally where useful, never treat every mood/drive/dopamine/pain label as one interchangeable scalar or evidence of experience.
**Evidence:** [S.state](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/state.py#L1) [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031) [G.avatar](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/avatar.js#L1) [N.bio](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/bio_model.py#L1) [U.blueprint](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/living_avatar_subjective_experience_blueprint_v0_3.md#L1)

### X03 · File Atlas, navigable facility, expressive stage and authoritative world
**Preserved** · Distinct purpose/experience  
**Owner:** Shared spatial infrastructure; separate domain models · **Canonical UX:** Workspace / Presence / Lab World
Reuse loaders/rigging/input/performance controls and one shell. Retain distinct information-navigation, conversational presentation and embodied causality rather than deleting all 3D work as duplication.
**Evidence:** [C.main](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/dashboard_3d.html#L806-L6330) [C.avatar](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/recovered/sage_avatar.js#L1-L1472) [G.avatar](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/avatar.js#L1) [U.blueprint](https://github.com/flrtemis/universe/blob/458915e762dc25b280aeebca3728f5bbe961c87f/living_avatar_subjective_experience_blueprint_v0_3.md#L1)

### X04 · Chat/voice inputs, file previews, tool discovery, launch/status, settings and logs
**Merged** · True overlapping user capabilities  
**Owner:** Shared frontend + authoritative services · **Canonical UX:** Exactly one canonical workflow per capability
Merge into one composer, artifact viewer, tool/provider registry, supervisor, settings schema, activity/approval queue and run inspector. Views project the same state/actions; no independent app or iframe shells.
**Evidence:** [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031) [R.server](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/server.py#L1) [G.app](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/app.js#L1) [S.ui](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/web/index.html#L1) [C.main](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/dashboard_3d.html#L806-L6330) [N.workspaceServer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/dashboard_server.py#L1)

### X05 · Mock success, random diagnostic streams, unused parameters and inert UI
**Retired** · Demo/partial/misleading behavior  
**Owner:** Explicit archived fixtures or unfinished specs · **Canonical UX:** No false production success
Retire false-live presentation, not research questions or prototype evidence. Keep labeled demos and backlog transformations; only measured/tested actions report actual success.
**Evidence:** [C.demo](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/demo/demo_server.py#L31-L223) [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031) [A.readaloud](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/read_aloud.py#L1-L249) [G.app](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/src/app.js#L1) [N.metrics](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/metrics.py#L1) [N.selfmod](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/self_modify.py#L1) [N.workspaceServer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/dashboard_server.py#L1)

### X06 · Independent public ports, localhost links and seven server/application shells
**Retired** · Packaging duplication, not valuable capability  
**Owner:** Single gateway + internal workers · **Canonical UX:** One URL / one launcher
Retire independent navigation/sessions/configs/registries as the integration reaches parity. Internal process separation remains where isolation/GPU/audio/physics warrants it; do not replace it with seven iframes.
**Evidence:** [C.start](https://github.com/flrtemis/command-center/blob/5226291a356ea60116678ece9200b1dc186011a9/START-HERE.txt#L1-L25) [A.enhanced](https://github.com/flrtemis/agent/blob/a09f1d25b0aeb5700f03600618aff34408f3fcf6/agent2.py#L43-L2031) [R.server](https://github.com/flrtemis/local_ollama_arena_agent/blob/c95d307abd2435e2598e94dbbaee5f343e688ba4/local_arena_agent/server.py#L1) [G.server](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/index.ts#L1) [S.server](https://github.com/flrtemis/Sage/blob/701f917eab403c32263deb08a85de24f59514518/awake/server.py#L1) [N.trainingServer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/server.py#L1) [N.workspaceServer](https://github.com/flrtemis/neural-sim/blob/b51dda76eaee4347efce6156f98ddaed71ddf7d9/dashboard_server.py#L1)
