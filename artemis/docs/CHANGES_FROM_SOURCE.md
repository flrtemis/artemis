# Source reuse and adaptation record

All files indexed as `SOURCE_MAP.json.files` are retained byte-identically under `vendor_sources/`. New host adapters are outside those source trees. User data/models/environments are not silently bundled; originals are unchanged.

## Actual imports/reuse

- `vendor_sources/sage/awake/{memory,clock,state,selfmodel}.py`: persistent storage/recall/wants, wall/timezone clock, PAD decay/state and bounded profile behavior.
- `vendor_sources/local_ollama_arena_agent/local_arena_agent/{workspace,tools/*,agent}.py`: contained workspace, file/document implementations, registered tool schemas, JSON/native tool-call parsers.
- `vendor_sources/agent/tools/{calculator,current_time,directory_manager}.py`: real structured arithmetic, time formatting and scoped directory creation through host wrappers.
- `vendor_sources/neural_sim/dataset_analyzer.py`: real parser/statistic/finding paths; cognitive-frame generator retained but not emitted as observations.
- `frontend/src/avatar-stage.js`: derivative of original Gemma `src/avatar.js`, only vendor import location and ready-state guard added.
- `frontend/src/atlas-source.js`: original Command Center `galMakeStarTex` and `galRemapToSpiral` functions; actual artifact index supplies records.
- `artemis_app/bio_engine.py`: derivative of repaired Command Center Bio, local schema import plus GABA sign repair. Original untouched in source archive.
- `artemis_app/bio_schema.py`: actual Neural Sim BioMetrics dataclass factored out of torch-importing metrics module.
- Universe: blueprint preserved/inspectable; no implemented engine is falsely attributed to it.

## Host changes

- Actor/task runtime follows Arena native/JSON call semantics but uses cancellable async HTTP, durable SQLite state, every batch member/result and explicit pause/resume budgets rather than one volatile first call.
- Tool schemas validate before registration/proposal execution. Default soft Bash/external command workers are never dispatched.
- Workspace subclass rejects absolute host paths, enforces real containment, changes preview URLs to authenticated gateway paths and adds hashes. Listing algorithm adds outside-symlink exclusion.
- Proposal hash includes canonical tool/arguments/precondition. Approval checks current revisions and is single-use. Interrupted ambiguous outcomes require inspection, not automatic replay.
- Sage Store extends the original schema with canonical threads/messages/jobs/approvals/settings/artifacts/revisions; original tables/data remain compatible.
- SelfModel subclass makes snapshot names unique within one second; original max-change/forbidden-pattern validator remains, with higher-level policy still continuation work.
- Imported user/reply events are projected into one conversation with source event references. Original private/wake/raw generated-thought entries are not served by the UI/event projection.
- Provider thinking fields are omitted from persisted/exposed model messages; configuration and context consent bind to the original run.
- Dataset adapters explicitly advertise CSV/JSON/text only; JSONL/TSV/YAML/XML/PDF structural support is not pretended.
- Bio GABA increment now follows the negative-conductance convention used by its current equation. E/I masks/count/time/delay/FFT issues remain visible; no long-run/scientific validity claim.

## Corrected source interpretation

During actual import/integration, the Agent calculator was confirmed to implement structured `add/subtract/multiply/divide` over a numbers list, **not eval-based expression evaluation**. The prior ledger A16 wording was corrected; its transformed disposition now refers to numeric/schema/finite-result/budget validation. The runtime reuses that real arithmetic function.

## Packaging

Local fonts, GLB and HeadAudio assets are self-hosted; no CDN dependency is needed by the built UI. Original libraries/assets remain subject to original terms. `requirements.txt` describes compatible dependencies; `requirements-tested.txt` records the tested Python environment subset. Frontend `package-lock.json` pins the actual installed graph. This is not a claim of fully reproducible GPU/speech model supply chains.
