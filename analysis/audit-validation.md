# Audit method, evidence and validation

**Audit date:** 2026-09-29. **Scope:** the exact seven public snapshots listed below, all tracked file trees, first-party implementation/contracts, tests, assets/configuration, public history, and the embedded Gemma history. This is a source-grounded design audit, not an implemented unified application, security certification, GPU benchmark or consciousness assessment.

## Snapshot census

| Repository | Commit | Tracked files | Public commits |
|---|---|---:|---:|
| command-center | `5226291a356ea60116678ece9200b1dc186011a9` | 387 | 1 |
| agent | `a09f1d25b0aeb5700f03600618aff34408f3fcf6` | 32 | 1 |
| local_ollama_arena_agent | `c95d307abd2435e2598e94dbbaee5f343e688ba4` | 2,710 | 7 |
| gemma-avatar | `c4becc81781fc59d0cf6d7ff52f6099f9943f7b8` | 1,785 | 76 |
| Sage | `701f917eab403c32263deb08a85de24f59514518` | 27 | 21 |
| neural-sim | `b51dda76eaee4347efce6156f98ddaed71ddf7d9` | 14 | 16 |
| universe | `458915e762dc25b280aeebca3728f5bbe961c87f` | 3 | 3 |

**Total:** 4,958 tracked files and 125 public commits, plus the embedded 12-commit history. Every tracked file appears in file-manifest.csv (hash/size/category/commit/source URL) and file-disposition-map.csv (review treatment and decision IDs). All 79 project-level implementation files, four tests and the exact agent.txt duplicate are mapped to explicit decisions. Dependency distributions, venv/cache/bytecode files and vendor source are classified and provenance-checked, **not claimed as a line-by-line audit of thousands of upstream files**.

The review included call sites, route wiring, schemas, formulas, UI branches, tool dispatch, launch scripts, tests, archived dashboard/mobile/avatar code, embedded HTML/JavaScript, deleted-file history, structured galaxy/catalogue schemas, audio/GLB headers, and hash-manifest comparison. README statements were checked against implementation. Source labels in the design/ledger link to commit-pinned files and lines; the machine-readable index is source-evidence-index.csv.

## Executed checks and limits

| Check family | Result | What this does / does not establish |
|---|---|---|
| Python AST parsing | 61 first-party/test Python files parse | Syntax only, not import/dependency/runtime/model correctness. |
| Authored/embedded JS and shell syntax | 18 of 19 checks pass | Neural dashboard duplicate logSelfModify declaration fails; other syntax passes are not browser runtime tests. |
| Existing Sage scripts | Exit 0; 40 + 9 + 11 = 60 checks reported | Bounded continuity/look-back/fake-Ollama cases. One echo-exclusion assertion contains or True and proves nothing. Not privacy certification. |
| New bounded source harness | 38 records: 17 pass, 13 observations, 8 reproduced defects | Exact-method/pure-module fixtures and real Arena host loop with synthetic model replies. Exit 0 means harness completed, not every system passed. |
| Codec / AudioWorklet fixtures | 7 of 7 pass | Synthetic samples and minimal browser API objects, not real microphone/playback/GLB/lip-sync/realtime backend integration. |
| Gemma SHA manifest | 17 match; 14 mismatch, of 31 entries | Stale artifact checks, including self-entry problem; not a model/asset supply-chain attestation. |
| GLB / recorded WAV structural checks | Headers/schema inspected | GLB rig/morph counts and recording durations, not rendered-animation or listening validation. |

## Reproduced defects

1. Arena dispatch accepts write_file without required content and creates an empty file: registry schema is not enforced.
2. Arena real loop processes one of two native tool calls, losing the second (synthetic provider response fixture).
3. Neural dataset WebSocket broadcast raises UnboundLocalError even with an empty client set (exact function, not full server startup).
4. Neural Bio constructor raises AttributeError for missing _delay_buffer_len before simulation (actual BioMetrics dataclass injected to avoid missing package/torch dependency).
5. Command Center Bio negative inhibitory weight creates zero GABA conductance after clipping (exact-method fixture).
6. Agent registration writes a traversal-named tool outside tools/ and accepts syntactically invalid Python (fresh temporary parent; generated code never executed).
7. Sage _scrub redacts type-before-text private JSON but leaks the same synthetic sentinel with text-before-type (no real private entry exposed).
8. Sage exact _letter_text method reads a synthetic .md file outside the letters directory using ../../outside (fresh temporary parent, no personal file access).

## Positive findings that must not be misrepresented

- Arena exact/fuzzy editing works. The smoke output is gamma without a trailing newline; that is a newline policy observation, **not a failed edit**.
- Arena relative traversal and symlink escapes are rejected by its file-path layer; uploads normalize basenames and avoid name collisions. This does not prove arbitrary shell execution is confined.
- Minimal DOCX/XLSX/PPTX containers, simple PDF/CSV output and printf through bounded shell pass. No Microsoft Office or PDF viewer rendering was validated.
- Approval fixture pauses before a write and resumes after approval. No real model, concurrent session, denial/failure/restart or durable approval integration was tested.
- Command Center Bio initializes 1,090 neurons and runs five finite steps with the source’s actual dataclass. Five steps do not validate stability or neuroscience.
- Recomputed E/I helper uses **column-local indexes modulo 100**: 50 inhibitory cortical cells, not the invalid earlier global-index count of 5, and not the declared 200.

## Source-only findings and unavailable integration

Trainer gradient composition, detached distillation, unused token weights, log-only rank adaptation, GP/population/curriculum/rollback deficiencies, Bio delay/time/FFT semantics, unsafe shell routes, absent authentication, missing static/config/package paths, Piper fallback branching and inert UI wiring are source-derived unless explicitly reproduced above. They should be fixed and tested, not treated as benchmark results.

No models were downloaded, no real Ollama/audio/vision/LLM engines were run, no torch/transformers/peft/Bun/GPU integration was available, no apps or real browsers/audio devices were launched, no live search/media providers were invoked, and no generated arbitrary code or Genesis mutation was executed. A small fake-Ollama HTTP provider was used by the existing Sage test; no real provider was contacted by these fixtures.

## Privacy, rights and reproducibility

Personal continuity contents are deliberately absent from this package. Only schemas/aggregate existence and synthetic sentinels were used in findings. The temporary research copy of the committed Sage database was deleted after inspection; original repositories were not changed. Do not ship their user DB/history/letters as default data.

No repository-level licenses were declared in GitHub metadata. Public visibility does not imply unrestricted redistribution. Preserve upstream dependency notices and the avatar’s declared CC BY-NC 4.0 attribution/limits; review voice/model/mesh/data rights before distribution. Scientific citations in Universe were read as part of the proposal, not independently fact-checked.

Raw test results are supplied as validation-results.json; harness source is retained under research/. To rerun, clone the exact commits in the census, restore the indicated tool/runtime dependencies, then run the bounded research scripts. The original clones are in the workspace cache, not embedded in the deliverable ZIP. Package outputs contain no private diary/database contents.