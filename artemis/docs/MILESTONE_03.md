# Milestone 03 — hot capabilities and an honest front door

**ARTEMIS — A Reality That Enhances My Integrated Services**

Branch: `arena/b4094b40-artemis` · base: `b39062b589b4a953e826b2e6042397198df967ef`.
This is an additive continuation of the substantial partial milestone-02 host,
not a replacement/rebrand or a finished twelve-source product.

**OWNER ACTION REQUIRED:** only you enable Pages. In `flrtemis/artemis` →
**Settings → Pages → Build and deployment → Source: Deploy from a branch →
select the branch containing `docs/index.html` → folder `/docs` → Save**.
After deployment, check **https://flrtemis.github.io/artemis/** and report a
failure. After a *later reviewed merge*, use `main` + `/docs`. Do not merge just
to publish. This agent does not enable Pages, merge, or claim the site live.

## 1. Current inventory and genuine gap

The full [current twelve-source matrix](CURRENT_CAPABILITIES.md) has pinned
branches/commits, owners, destinations, source paths, evidence tiers, costs,
risks and license limits in Markdown/JSON/CSV. It supersedes neither the
September audit nor its historical test results. Fifteen remote heads and all
PR queries were inspected before implementation; active non-main Phone,
Atrium and Speech-to-Speech code was not mistaken for sparse main branches.

Original Agent's dynamic `create_tool`/`load_tools()` lifecycle was missing from
ARTEMIS's existing static selected tools. Its original handlers also wrote and
registered before separately testing, allowed unsafe path/name input and let
names containing `scrape` affect networking. Preserve the original sources;
adapt the useful lifecycle, not those unsafe policies.

## 2. Implemented integration

`create_tool` now belongs to the SAME canonical model loop, thread, durable job,
registry, approvals, Store and execution service:

1. Missing capability proposal → exact operator code/schema/test approval.
2. Strict bounded contract → immutable staged version.
3. Real Bubblewrap namespace/seccomp test (no user files/private memory/egress).
4. Passing result activates/hot-registers the schema without host restart.
5. Separate exact version-bound invocation approval → real isolated result.
6. The original run consumes result/error and commits its original answer.

A browser-captured run computes median **7.5/count 4** from `[12,3,9,6]` and
stores just the original request + one final answer. Model decisions are
explicitly **SCRIPTED_TEST_PROVIDER_NO_LLM**; the API/runtime/store/sandbox are
real. This is not proof your installed Ollama model authors valid code.
Creation failure, repair feedback, cancellation, restart, concurrent versions,
rollback, resource/schema/network/path boundaries and scoped export have tests.
No trusted gateway import or irreversible replay is introduced.

[`EXTENSIONS.md`](EXTENSIONS.md) defines `artemis.capability/v1` and the CC0
model-free example. Rich file/network/native/device capabilities and production
multi-tenant boundaries remain future contracts.

Audio is presentation, not the durable work owner: yield/barge-in cancels stale
STT/TTS/playback and holds delivery; approvals/jobs survive. Explicit cancel is
separate. Revisioned same-job corrections reject stale model calls/proposals
without replaying completed effects. Busy-model follow-ups are held for
explicit reconciliation, not answered by another agent/history. A new explicit
turn suppresses automatic playback of older held replies; explicit read-aloud
still uses saved text. Silent-PCM tests do not prove speech quality or latency.

Offline launch skips installation and admits only loopback/private-literal
configured model/audio endpoints, without DNS; a fixed non-loopback WSL/LAN IP
still needs explicit consent. It is not a host firewall or blanket offline
promise for separately configured engines. No weights are downloaded here.

## 3. Pages-ready guide

Root `docs/index.html`, local styles/script/font/mark/captioned real screenshot,
code-approval capture and sanitized six-phase trace. This is a consumer guide
and **static evidence replay**, never a mock backend, chat widget or localhost
connector. Daily-value paths, ownership/cost requirements, category comparisons,
accessibility and current/planned claims point to source/test evidence.

The exact founder expansion, approved brief, stylized `𝘧𝘳𝘦𝘦` sentence and plain
accessibility equivalent are retained. [Attribution](../../docs/ATTRIBUTION.md)
identifies original work and Ready Player Me's source-declared CC BY-NC avatar;
public source/screenshot does not grant blanket commercial redistribution.
There is no CDN, analytics, cloud sign-in or publishing Action.

## 4. Verification

Final exact fresh commands/results and honest skips are in
[`verification-03.json`](verification-03.json). Historical milestone-02
Godot/Torch/voice results are not relabelled as fresh. Test output/screenshots
live in ignored `.cache/`; selected sanitized public evidence lives in `docs/`.
The original bundle checksums describe the historical ZIP, not this changed
branch. The source verifier handles 505 byte-identical blobs and two LFS
pointer/runtime-payload mappings separately.

### Fresh results (2026-10-13)

| Check | Actual result / limits |
|---|---|
| Full backend suite | **88 passed, 11 skipped**: 5 Godot, 3 Torch, 3 optional speech configurations; 1 Starlette/httpx warning |
| Hot lifecycle / presence / offline-source groups | **36 / 7 / 4 passed**, included in the full suite; real kernel scratch/readonly and older-reply/new-turn regressions |
| Actual built-app hot-tool Chromium | **9/9**; labelled scripted provider, real namespace/seccomp/test/use, 7.5 in the original job/thread |
| Static Pages Chromium | **9/9**; `/artemis/`, 320/390/768/1440px, keyboard, reduced motion, no-JS, 34 links; desktop/mobile automated axe **0 violations** (not certification) |
| Broader file/dataset/Atlas/memory/avatar UI | **11/11**; actual new dataset run and unique synthetic memory, no model or microphone |
| Facility/wrist/shared audio graph UI | **7 passed, 1 real-Godot skip**; optional full-page captures disabled after software-WebGL screenshot timeout |
| Real model-free CLI/export/import workflow | **5 checks passed**; creation/use approvals separate, export refuses overwrite, fresh isolated import; no inference |
| Original pinned Phone / Atrium / S2S tests | **119 / 23 (166 assertions) / 5 passed**; focused implementation/fixture evidence, not devices/engines |
| Frontend typecheck / production build / npm audit | **Pass / pass / 0 vulnerabilities**; existing runtime-font resolution and optional >500KB presence-chunk warnings visible |
| Retained source verifier | **505 exact blobs + 2 separately verified LFS pointer/payload mappings = 507**, 0 failures; all 46 cited source paths exist at 12 pinned commits |
| Launcher/host syntax / existing-env offline setup | **Pass**, no weights downloaded |

Earlier failed test assumptions/selector/capture attempts are recorded honestly
in the machine record rather than erased or counted as passing. No real model,
physical device, complete native engine or live deployment claim follows.

## 5. What to try locally

In WSL2/Linux, from the cloned repository root:

```bash
cd artemis
bash start.sh
# Initial Internet installs Python dependencies; included UI needs no Node build.
```

Open `http://localhost:8000`, unlock with the printed local operator key.
Workspace → New artifact → `notes.md` → submit, review Activity and approve.
Open the real file. Continuity → Keep a memory → approve; restart with the same
data directory and inspect it. These paths do not need a model.

For a real isolated calculation without any model, install working
Bubblewrap/libseccomp and follow [`EXTENSIONS.md`](EXTENSIONS.md)'s
`extension_cli.py propose/use/status/export` example. Each creation/use is
approved separately. Do not import unknown code casually.

For the model path, select the **actual installed tag** and the **existing WSL
Ollama fixed IP** in Operations. Obtain WSL's own configuration; Windows shell
environment does not configure WSL. Do not start another Windows Ollama server,
replace the requested model, download another resident model or raise WSL memory
to 24 GB. Ask the median question and review both approvals. Then observe
errors/results and same-thread delivery on that actual machine.

```bash
bash start.sh --offline    # installed environment/cached assets only; no installs
```

If reusing another installed Python environment, set `ARTEMIS_PYTHON` to its
absolute interpreter path explicitly. Keep originals unchanged. Sage import
remains optional into a **fresh** destination; do not publish personal state.

Preview only the static guide from the repository root:

```bash
python3 artemis/scripts/serve_pages.py --port 4173
# http://localhost:4173/artemis/
```

Developers: Python suite `cd artemis && .venv/bin/python -m pytest tests -q -rs`
(or explicitly selected environment), `scripts/verify_sources.py`, and
`cd frontend && npm ci && npm run typecheck && npm run build`. Browser scripts
require an explicitly installed compatible Chromium; `ARTEMIS_CHROMIUM_BIN`
can select it. **All browser suites write/approve synthetic QA artifacts and must use a separate fresh disposable data directory, never personal Sage state.**
`tests/demo_host.py --confirm-fixture-provider` is test-only,
fresh state, never normal launch; stop it after testing.

## 6. What remains unverified

No actual Ollama inference/model/tool-authoring quality, founder's current
physical PC/RAM/VRAM, GPU/CUDA/NF4, native Godot here, physical mic/speaker/camera,
meaningful-answer audio latency/visemes, original Parakeet/Qwen endpoint
compatibility, Docker, carrier/SIP/Android/remote exposure, production security
certification or Pages deployment. No numerical RAM/latency improvement,
parity, “unlimited”, stronger privacy or subjective-experience claim follows.

## 7. Staged next unification

- **Speech engines/turns:** adapt engine-only Parakeet/Qwen workers and
  progressive/speculative perception into `speech.py`/`speech_worker.py` and
  canonical revisions. Test stale partials, long approved work, model-busy
  repair, explicit cancel, physical answer audio and exact current resource
  use. Never run the source's competing chat loop.
- **Vision:** consented local Atrium observations/attachments in the canonical
  multimodal thread; CDN fallback explicitly off. Test camera denied/revoked,
  offline assets, motion throttling, no observation before consent and no
  unsafe model invocation. Physical webcam remains owner-side.
- **Phone/mobile:** opt-in authenticated channel/actor scope and canonical
  durable thread/run delivery, preserving source spool/protocol behavior.
  Test disconnect/reconnect/deduplication/no auto-dial; actual carrier/device
  costs/permissions visible. No host networking change without approval.
- **Spatial/continuity/labs/world:** continue original facility interactions,
  Sage recall/reflection/user boundaries, resource-admitted training and
  actual native engine tests. Review scientific validity; placeholders and
  diagnostic proxies never become invented measurements.
- **Contributors:** richer explicit permission/state contracts, trust review,
  license checks and real multi-user/project isolation before sharing private
  continuity or enabling broad extension capabilities. Guardian policy ideas
  require reviewed device-specific evidence, not automatic host control.

Exact next seams are the existing files named above and in the matrix. Do not
start a second gateway, LLM history or continuity owner to make a contribution
appear connected.

### Exact next files/tests (proposed, not shipped now)

| Next slice | Code seams | Required next contracts |
|---|---|---|
| Original speech engine/turn adapter | Existing `artemis_app/speech.py`, `speech_worker.py`, `runtime.py`, `frontend/src/s2s-client.js`; proposed `tests/test_s2s_engine_bridge.py` | Cached engine-only Parakeet/Qwen calls, partial/reopened turn revisions, resource admission, stale/cancel/error cases; actual owner-side meaningful-answer audio |
| Atrium perception | Proposed `artemis_app/vision.py`; existing `api.py`, `frontend/src/Presence.tsx` and canonical attachments; proposed `tests/test_vision_presence.py` | Explicit camera consent/revocation, bounded frame/artifact ownership, local assets/no CDN, canonical multimodal context and no observation before consent |
| Phone/mobile | Proposed `artemis_app/channels/phone.py`; existing `api.py`, `store.py`, `runtime.py`; proposed `tests/test_phone_channel.py` | Channel actor/thread bindings, idempotent spool IDs, disconnect result delivery, dialing approvals, no second history/model loop or unapproved exposure |
| Scoped contributor/privacy state | Existing `store.py`, `api.py`, `capability_contract.py`; proposed reviewed `artemis_app/privacy/policy.py` and `tests/test_privacy_policy.py` | Real project/user visibility and grants; no cross-user private-memory leakage, name-derived networking, automatic host/device enforcement or unreviewed richer extensions |

Paths above are relative to the application folder. Proposed files are TODOs,
not empty placeholders presented as completed integration.

## Changed files in this isolated feature branch

`A` added, `M` modified, `D` obsolete compiled asset removed. No original vendor
source/manifest, other repository, main branch, private state or model weights
are changed. Complete staged path list (compiled replacements may appear as
renames in GitHub):

```text
A	.gitattributes
A	.gitignore
M	BUNDLE_README.md
M	README.md
M	artemis/README.md
M	artemis/artemis_app/api.py
A	artemis/artemis_app/capability_contract.py
A	artemis/artemis_app/extension_sandbox.py
A	artemis/artemis_app/extension_worker.py
M	artemis/artemis_app/extensions.py
A	artemis/artemis_app/generated_tools.py
A	artemis/artemis_app/offline.py
M	artemis/artemis_app/runtime.py
M	artemis/artemis_app/speech.py
M	artemis/artemis_app/store.py
M	artemis/artemis_app/tools.py
A	artemis/docs/CURRENT_CAPABILITIES.md
A	artemis/docs/EXTENSIONS.md
A	artemis/docs/MILESTONE_03.md
A	artemis/docs/PROJECT_BRIEF.md
A	artemis/docs/current-capabilities.csv
A	artemis/docs/current-capabilities.json
A	artemis/docs/source-census-2026-10-13.json
A	artemis/docs/verification-03.json
A	artemis/examples/extensions/median_values.json
M	artemis/frontend/package-lock.json
M	artemis/frontend/package.json
M	artemis/frontend/src/main.tsx
M	artemis/frontend/src/s2s-client.js
M	artemis/frontend/src/shared-audio.ts
M	artemis/frontend/src/style.css
M	artemis/frontend/tests/browser.02.integration.mjs
A	artemis/frontend/tests/browser.03.integration.mjs
M	artemis/frontend/tests/browser.integration.mjs
A	artemis/frontend/tests/browser.pages.mjs
M	artemis/run.py
A	artemis/scripts/extension_cli.py
A	artemis/scripts/serve_pages.py
M	artemis/scripts/verify_sources.py
M	artemis/start.sh
A	artemis/tests/demo_host.py
A	artemis/tests/test_hot_tools.py
M	artemis/tests/test_integration.py
A	artemis/tests/test_job_presence.py
A	artemis/tests/test_offline_sources.py
A	artemis/web/assets/index-C-J9G3SF.css
D	artemis/web/assets/index-DzlOMwFq.js
D	artemis/web/assets/index-vYL2zJ0L.css
A	artemis/web/assets/index-zqbXvZHZ.js
A	artemis/web/assets/presence-D3Qh-qT5.js
D	artemis/web/assets/presence-r_Oswgo-.js
M	artemis/web/index.html
A	docs/.nojekyll
A	docs/ATTRIBUTION.md
A	docs/PAGES_SETUP.md
A	docs/assets/OFL-InstrumentSerif-upstream.txt
A	docs/assets/OFL-InstrumentSerif.txt
A	docs/assets/OFL-Wordmark-Sources.txt
A	docs/assets/creation-approval.webp
A	docs/assets/hot-tool-trace.json
A	docs/assets/instrument-serif-latin-italic.woff2
A	docs/assets/instrument-serif-latin.woff2
A	docs/assets/mark.svg
A	docs/assets/math-accent.woff2
A	docs/assets/site.css
A	docs/assets/site.js
A	docs/assets/wordmark.svg
A	docs/assets/workspace.webp
A	docs/index.html
```
