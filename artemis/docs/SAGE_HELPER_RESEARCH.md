# Sage helper — read-only inspiration review and design

Research date: **2026-10-14**. Additive to ARTEMIS milestone 03, not a replacement for its runtime or pending integrations. Read with [ONGOING_WORK.md](ONGOING_WORK.md).

## Inbox provenance and handling

The owner supplied seven files plus a purpose README on `arena/b4094b40-artemis`, at owner commit `f3388e47eeb8538e7a0b0a5bbf6c58b979260cab`. They were read through GitHub blob reads, **without materializing, editing, deleting, executing, or staging the inbox**. Full byte identities are recorded in `ideas-reviewed-2026-10-14.json`.

No uploaded source is imported as production code. No captured authentication values, personal discussion, raw transcript, saved HTML, or userscript is copied into this report or the website. A public repository's branch is not private; a temporary inbox is not a secret store. The capture contains session/reservation/routing identifiers and must not be replayed.

## What the files actually contribute

| Owner file | Read/analysis finding | Sage application | Do not copy blindly |
|---|---|---|---|
| `auto-tts.js` | AI Studio userscript using Web Speech, voice discovery, sentence/length chunks, floating toggle/stop and mouse drag | Native answer-audio controls; explicit voice/rate preference and low-friction activation | Broad DOM selectors, one global character offset, unfenced stale chunks, unflushed short final text, mouse-only positioning, voice-name/gender assumptions and default auto-speech |
| `Google AI Studio auto-TTS.js` | Same implementation as `auto-tts.js` after CRLF/trailing-newline normalization; not an independent second solution | Preserve both owner uploads, review once as one implementation family | Do not delete/merge duplicate inbox files; line-ending differences are not feature differences |
| `perchance-ai-tts.user.js` | Mobile-friendly reader panel, manual replay, auto toggle, rate controls, optional code skipping, capped text/hash history, heuristic assistant selection and 2.5s settling | Make answer replay and stop prominent, keep short/plain spoken presentation, expose settings | Hash-only deduplication is not message identity; DOM quiet is not generation completion; selector guesses can include user/hidden/tool text; truncation can silently omit important content |
| `CRUSHON_AI_remove_all_actions_in_responses.js` | Attempts spoken-only presentation by hiding emphasis and rewriting text nodes throughout the page | Optional **speech-only** presentation policy, separate from the canonical answer | Global `<em>` suppression and regex deletion can remove warnings, names, math, code and meaningful answer text. Never mutate stored history or the entire UI to clean speech |
| `ai_studio_code.py` | Google GenAI SDK example, environment API-key lookup, a hosted Gemma model identifier, streamed parts, code-execution tool, JSON response schema and several disabled safety thresholds | Typed separation of final answer/tool/error/audio data; explicit engine/provider configuration | Do not import/execute it, add a mandatory Google dependency, choose/replace the user's local model from a hosted identifier, infer resource requirements from its name, copy disabled safeguards, or speak/store sample reasoning as the final answer |
| Saved Perchance editor HTML | Entire 637,272-byte page parsed inertly. Contains editor/helper controls and a recorded read/write/test/download/speech/reconnect interaction; 39 script tags have no executable bodies in the saved snapshot | Accessible helper beside ongoing work, visible tool/result trail, explicit files/attachments, reversible artifact proposals and recovery feedback | Snapshot is one session, not a complete backend specification. Recorded `speaking: true` is browser state, not proof of audible output. Do not execute captured `page_eval`/worker code in ARTEMIS's privileged UI |
| Saved Perchance agent text | Entire network note read with credential/identifier redaction for inspection. Shows session reservation, tab ownership, typed tool-result exchange, preview source readout and a downloadable-file result | Explicit operation IDs, ownership, bounded attachments, typed tool responses and first-class artifact download links | Never reuse captured tokens/routing/session IDs or POST to captured endpoints. The note is not a supported public Perchance API contract |
| Inbox `README.md` | Owner-only upload space for analysis/inspiration | Standing inbox workflow in the cumulative plan | Not a directory for agent-generated reports |

### Model identity: deliberately limited claim

The owner identifies the helper as **Muse Spark**, and the saved helper self-identifies that way. The public client also contains Muse-related provider/recovery strings and a custom model-choice path. This is evidence of the observed label/client implementation, **not** independent verification of exact weights, model version, licensing, deployment topology, or every provider used by Perchance.

Do not conflate Perchance's editor helper with Meta's separately marketed Muse/Muse Code products, or assume all features of those products are present in Perchance. Sage remains the ARTEMIS assistant on the owner's selected local engine. Similar interaction design does not promise identical reasoning, speed, privacy or results. No Muse/Google API dependency is added.

## Independent public research

Read-only primary source: `https://perchance.org/lib/aiAgentClient.js`, retrieved October 14. Relevant inspected source sections include the architecture header, error taxonomy, file-worker calls/recovery, execution-result deduplication, editor synchronization, source ownership/rename handoff and attachment preflight. The source is publicly served, but that is **not a license grant** to copy it. Its server implementation was not obtained or tested.

The publicly served client describes:

- Lazy loading of helper code and later server-session creation, rather than loading every worker/model with the initial page.
- A server-owned agent loop and SSE tool relay, with browser OPFS file tools in a module worker. Browser files are its workspace authority; **ARTEMIS's Store/workspace remains our authority**, not a new OPFS assistant history.
- Read/write/edit/patch/glob/grep file operations; explicit preview reload/evaluation; isolated-worker JS computation; copy-line operations.
- Separate in-flight/settled execution tracking so a repeated delivery can join or return the original result rather than blindly re-executing an effect.
- Distinguishing retry-safe reads from uncertain mutation completion; stale generation fences, owner handoff, bounded backoff, storage/quota failure messages, and preserving user edits during repair.
- Downloaded-tool/storage failure handling, source files versus ephemeral scratch, and visible recovery/loss notices.
- Client diagnostics/telemetry hooks. Those are **not** carried into ARTEMIS: useful robustness patterns do not justify adding tracking.

The owner snapshot directly shows **Send**, **then do this** (a queue button labelled up to three), **Stop**, **files**, **undo**, **redo**, **attach files/folder**, **new chat**, draft options, console/helper switching, and a background-worker iframe. It includes tool rows for `read`, `write`, `execute_js`, `page_eval`, `page_refresh`, and `attach_file`. A visible control or source branch is code/recorded-session evidence, not a fresh end-to-end test of each feature.

A community tutorial corroborates the describe → build → inspect preview → refine → save workflow and describes an accessible editor-side helper: [3](https://perchance.org/ai-helper-tutorial). This community page is not treated as an official storage/recovery contract; stronger claims in it must be checked against current implementation and actual tests.

## Functional translation, not an unsafe clone

| Inspiration | Existing ARTEMIS owner | First helper surface / remaining work |
|---|---|---|
| Helper always within reach | Existing React App and authenticated canonical state | Persistent Sage launcher on every main view; docked desktop/full-height mobile dialog, keyboard/focus controls |
| Contextual conversation | Existing `/chat`, thread messages, Runtime and selected Ollama configuration | Same draft/messages/thread IDs in panel and full conversation. Explicit selected-file attachment, no automatic page/file scraping |
| Tool catalogue and execution | Existing Tools registry, scope checks, approvals and extension sandbox | Browse **all actual registry capabilities**, including disabled reasons; open the existing proposal UI, never execute an unknown capability merely because it was suggested |
| Work trace and control | Existing runs, approvals, event system | Show real stored run status/result/error and the same exact approval cards; explicit job cancel remains distinct from speech stop |
| Files and downloads | Existing workspace catalogue and authenticated content route | Open/download actual scoped artifacts. Attachments are explicit user actions. Never import `ideas/` into the workspace |
| Automatic answer audio | Existing SharedAudio / Speech / realtime thread transport | Read-replies gesture without microphone, saved-message replay, yield/resume/off via the same owner. Configured TTS required; no silent hosted/browser fallback |
| Speech formatting | Existing final answer, separate presentation layer | Keep canonical text intact. Future typed narration/code/voice/rate settings must preserve warnings and support a complete final tail and generation IDs |
| Preview/live testing | Existing isolated execution, staged file diffs, artifact inspection and optional workers | No arbitrary JS evaluation in privileged UI. Future web-artifact previews need a reviewed sandbox/CSP and separate explicit test/promotion |
| Undo/redo/checkpoints | Existing versioned tools, file revisions and exact preconditions | Version-bound rollback is real; universal action undo is **not**. External effects or already completed writes are not silently reversed/replayed |
| Queue / steering / recovery | Existing same-job correction, held inputs, persisted runs and recovery policy | Clearly label correction versus a future queued request. The first surface does not pretend to ship Perchance's entire queue/steer/replay protocol |
| Extensibility beyond coding | Existing twelve-source matrix and optional workers | Speech, perception, phone, continuity, spatial/lab/world capabilities continue contributing to one Sage; preserve their prerequisites/status |

## Interaction and accessibility contract

1. Open Sage without losing the current page, selected artifact or draft. No new model run on open/close/navigation.
2. Four views: **Ask Sage**, **Capabilities**, **Work & decisions**, **Files**. Registry readiness and exact approvals are discoverable even with no model connected.
3. Focus moves into the dialog; Escape closes it; keyboard tabs remain contained and return to the launcher. Tabs support arrow/Home/End navigation. Mobile uses the available viewport rather than a mouse-drag-only panel.
4. Readable answer text, explicit labels, status feedback and large touch controls; no fake progress percentages, fabricated thinking, raw thought transcript or mandatory animation. Do not pull scroll away while the user is reading older answers.
5. Closing the helper, stopping speech and turning voice off are presentation changes. **Cancel job** is the separate durable-work action. Corrections use existing revisioned same-job behavior; no completed effect is replayed.
6. No microphone acquisition for answer reading. Speak only saved user-facing assistant messages. Stable IDs/epochs and explicit generation completion are required for richer streaming speech, not DOM length/hash guesses.
7. Voice availability/autoplay/engine errors must remain visible. A successful API call or headless mock is not a physical audio/latency proof. Browser/OS voices can be remote; any future browser fallback must be separately chosen, disclosed and integrated with the one audio owner.
8. No private diary, captured session, unknown code, raw inbox file, camera, hosted provider or model download is automatically enabled by opening Sage.

## Pages: a real visual ground, not a pretend backend

The owner reports the site live. A **read-only GitHub Pages check on October 14** confirms `status=built`, source **`main` / `/`**. Fetching `https://flrtemis.github.io/artemis/` returns the historical milestone-02 README page, not this feature branch's `/docs` guide or local ARTEMIS backend.

Prepare the additive Sage visual preview under root `docs/`, with a clear static/no-model label, self-hosted assets, synthetic examples and no Perchance/Muse/Google/localhost calls. It must never contain raw inbox content or session data. Preview interaction/optional device speech is not proof of live agent intelligence.

Only the owner changes Pages publication. To review this branch's guide/preview without a merge, the owner can select `arena/b4094b40-artemis` + **`/docs`**. **Do not select the branch root**: it contains the owner's branch-only inbox. No Pages source change, merge or deployment is performed by the agent.

## Test boundary

The new React surface reuses production commands/state; it is not a replacement gateway. Fresh UI/type/build/browser results are recorded separately from the earlier milestone-03 counts. Real model performance, audible physical speech, complete Muse parity, native engines, camera/carrier devices and original code/tool-bridge compatibility remain unverified unless explicitly measured.

## Owner's additional batch — cumulative, not a replacement

During implementation the owner added a second batch and revised the inbox README.
All **58 files** now present at owner commit `1c61efc66fcded617b3bbfa0c5b7cb4b4af8456c`
were read in full, inertly. The original eight-file review above remains intact;
the manifest records both read checkpoints. The 89 KB clipboard dump is mixed
saved code/reference material, not a new system prompt or a production module.
Its raw contents, personal paths, private project links, signed URLs and identifiers
are not republished, replayed, downloaded or executed.

Added inspiration families:

- **Spatial work:** semantic file galaxies, 3D interaction/games, avatar creation.
  Extend canonical artifact IDs/Atlas/facility projections; do not introduce a second
  filesystem or discard the existing Gemma stage. Imported models/assets require license review.
- **Media:** local/optional TTS/STT, voice separation/denoising, images, music and video.
  Admit engines/resources deliberately; show downloads/licenses/provider fees. These
  bookmarks are not permission to launch hosted services or load another large model.
- **Developer tools:** code editors/explainers, web page/app creation, model/ONNX viewing,
  notebook/repository text tools and training references. Reuse approved artifacts,
  isolated testing and explicit promotions; never execute pasted notebook/Python/JS code in the gateway.
- **Utilities:** calculators, Unicode/fonts, Base64/emoji/file conversion and network
  diagnostics. Bounded local JSON operations fit the extension contract. Encoding is
  not encryption; IP/geolocation and cell maps do not prove device/carrier capability.
- **Device/channel ideas:** Termux, ADB, screen mirroring, Shizuku, phone and browser
  developer references. Treat as opt-in, scoped adapters; no root/permission bypass,
  security-setting changes, package installation or remote exposure from an idea file.
- **Media/content/legal references:** keep content rights, asset licenses and actual
  services explicit. No unauthorized stream/APK/premium download is added. Trademark
  and ownership bookmarks are not proof of registration or a new license grant.
- **Recovery/installation notes:** the Rufus/partition material includes destructive
  procedures. Park it as an owner-reference topic, never an instruction to wipe or
  reconfigure hardware. It does not supersede the standing WSL/model constraints.

### Direct visits prompted by the new bookmarks

The updated owner README asks for direct website visits. Current priority visits
were made to the following public pages without logging in, executing user code,
installing extensions, or downloading models:

| Public reference | Observed result / design consequence |
|---|---|
| `https://huggingface.co/spaces/webml-community/semantic-galaxy` | Currently returns a configuration-error page; do not equate that with absence of the idea/source, or pretend a working demo was tested |
| `https://huggingface.co/spaces/webml-community/kokoro-web` | Page offers Kokoro/Transformers.js TTS, an explicit model-loading step and selectable named voices; no model downloaded or audible speech measured. A voice named Sky is not evidence it is the proprietary ChatGPT Sky voice |
| `https://huggingface.co/spaces/ResembleAI/Chatterbox` | Page metadata is refreshing; no working engine/interface test established |
| `https://github.com/ken107/piper-browser-extension` | Source-visible Piper browser extension, MIT source notice and a recorded service-worker callback/recovery limitation; candidate for later review, not silently installed or substituted for the existing audio owner |
| `https://github.com/SillyTavern/Extension-Live2d/` | README describes local model assets and optional Live2D interaction/configuration. Preserve the current avatar; any extra asset/SDK licensing and shared-audio integration need review |
| `https://github.com/Genymobile/scrcpy/blob/master/doc/linux.md` | Public Linux setup/prerequisite documentation is available; no ADB, device, installation or host setting was used |
| `https://www.makehumancommunity.org/` | Visit failed with HTTP 500; further source/license investigation remains pending, not marked unavailable as a product |

**Remaining external links are an explicit research queue, not falsely claimed
visited or verified.** Prioritize the active Sage/audio/spatial contribution work,
then safe public media/developer/device references. Never replay signed URLs,
private cloud/chat/project/transcript links, account pages, or token-bearing
captures; visit public product documentation instead when useful. Link discovery
and a marketing claim do not establish a working local/offline integration.
