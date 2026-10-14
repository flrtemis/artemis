# Sage helper 01 — accessible, cumulative, and on the existing runtime

2026-10-14 · `arena/b4094b40-artemis` · additive to milestone 03.
Owner upload history preserved through `1c61efc66fcded617b3bbfa0c5b7cb4b4af8456c`.

**ARTEMIS — A Reality That Enhances My Integrated Services.**

## What was read and retained

- Original seven Perchance/AI Studio/TTS/response-formatting files and the owner README.
- The subsequent owner batch: **58 inbox files total**, including full inert reads of the saved HTML, network note and clipboard/reference dump. Duplicate AI Studio scripts are the same after EOL normalization; both owner originals remain untouched.
- Existing milestone-03 handoff/verification, founder brief and the pinned twelve-repository ownership/capability matrix. A separately named original `handoff.md` is not present; no claim it was reread.
- Public Perchance client implementation sections and selected direct source visits discovered in the new bookmarks. Other public links remain an explicit research queue; signed/personal/account/credential links are not replayed.

See [research](SAGE_HELPER_RESEARCH.md), [metadata-only inbox manifest](ideas-reviewed-2026-10-14.json), and [cumulative work](ONGOING_WORK.md). Those reports are outside `ideas/`. No raw upload, personal transcript, token, captured page, or script was imported into the runtime or website.

## Real local Sage surface

`frontend/src/SageHelper.tsx` and `sage-helper.css` add a persistent launcher across
Conversation, Workspace, Continuity, Laboratory and Operations.

- **Ask Sage:** the existing App draft, selected canonical thread, messages, attachments and send/correction handler. Open/close/navigation create no model call. First send can stay in the current workspace view.
- **Capabilities:** the actual live registry, including unavailable reasons. Buttons open the existing scoped capability form; approved code/testing/versioning remains milestone-03 behavior.
- **Work & decisions:** existing runs/results and the same exact approval cards. Close does not cancel work; explicit **Cancel job** is separate from **Stop speech only**.
- **Files:** existing scoped workspace catalogue, actual authenticated content downloads and artifact inspector; no separate filesystem or inbox import.
- **Audio:** configured TTS/read-saved-message and SharedAudio, including a no-microphone read-replies gesture, yield/resume/off. No hosted/browser voice is silently substituted when TTS is unconfigured.
- Keyboard Escape/focus containment/return, arrow/Home/End tabs, focusable scrolling, readable answer text, explicit labels, mobile layout and reduced-motion rules. The underlying narrow-phone page actions were corrected to wrap rather than overflow at 320 px.

This is one projection of one runtime, **not another chatbot/backend**. No original source repository, model/tag, private Sage data, camera, carrier/device, remote networking or trained weights are changed.

## Pages interaction lab

Root `docs/sage-preview.html` reuses **the same helper component** with explicit
static/synthetic props, no runtime/model, and `connect-src 'none'`.

The lab lets you explore the drawer, draft retention, labelled design response,
readiness examples and a synthetic browser-generated download. Capability buttons
never execute real work. Optional introduction narration is a user gesture using
a voice the device reports as local; it is not the ARTEMIS audio pipeline or
physical speech proof.

There are no API keys, Perchance/Muse/Google/localhost calls, raw inbox assets,
tracking storage, microphone or camera requests. The guide has an **Explore Sage**
link. All assets/fonts are self-hosted and original licensing notices retained.

The existing Pages deployment is independently confirmed built from **main + `/`**,
serving the older README. This new guide/lab is **not claimed deployed**. Owner-only
instructions: [PAGES_SETUP.md](../../docs/PAGES_SETUP.md). Select the feature branch
+ **`/docs`**, not its root, to preview without a merge.

## Fresh checks — not the historical milestone-03 totals

| Check | Current actual result |
|---|---|
| Production frontend typecheck / application build / lab build | Pass; no new framework or model dependency |
| Normal, unconfigured host helper browser | **9/9**: five views, no model calls on opening/navigation, draft/focus, real scoped proposal/approval/write/download, missing model/TTS honesty, all-section automated axe, 320–1440 px, no mic/error |
| Explicit scripted-provider helper browser | **10/10**: real canonical runtime/file effect/approval, one new original chat run/thread and saved answer/full history; close retains pending work, explicit exact-job cancel |
| Static shared-component lab browser | **8/8**: prefix, labelled non-AI interaction, synthetic download, fixture-local voice dispatch/stop, automated axe/mobile/reduced motion, no inbox/backend exposure or external/credential/tracking traffic |
| Existing file/dataset/Atlas/memory/avatar browser | **11/11**; actual new dataset mean/memory/GLB paths, no mic; prior work not replaced |
| Existing static guide browser | **9/9**; 36 local/fragment/evidence anchors, mobile/keyboard/no-JS/reduced-motion, zero automated desktop/mobile axe violations |
| Backend foundation/presence/offline-source subset | **43 passed**, included in the full run below |
| Full backend in the restored current environment | **50 passed, 49 skipped**, 1 Starlette/httpx warning. **35 hot-isolation + 3 other execution + 11 native/optional-engine cases skip** because Bubblewrap/Docker/Godot/Torch/voice assets are not installed/permitted here |
| Source preservation | **505 exact blobs + 2 separately verified LFS pointer/payload mappings = 507**, zero failures |
| npm audit | **0 vulnerabilities**; existing optional large-presence-chunk/runtime-font Vite warnings remain visible |

The earlier kernel-enabled environment's **88 passed / 11 skipped** and real
Bubblewrap hot-tool capture remain dated historical evidence at commit `94d47e0`.
They are not relabelled as a fresh kernel test here. No soft/host-code execution
fallback was introduced to manufacture a passing sandbox test.

Machine-readable current commands, cases and limitations: `verification-sage-01.json`.
Ignored screenshots/logs: `.cache/sage-*`. Automated axe is not accessibility
certification; browser-speech mocks are not audible meaningful-answer TTS.

Earlier checks caught and corrected focus return, contrast, a non-focusable
conversation scroll region, underlying 320px action overflow and an async-browser
wait test assumption. Failed attempts are not counted as passed cases.

## Try it

In a separate WSL/Linux trial clone, start the existing host normally or installed
cached/offline mode. Open `http://localhost:8000`, use the terminal operator key,
and choose **Sage** from any main view.

Without a model, explore Capabilities → `write file` → propose a test artifact →
open Sage Work & decisions → review/approve → Files → download/open the actual
artifact. Keep a memory through the existing proposal flow. No personal Sage
import is required for this trial.

For chat, select the **actual installed tag** and **existing fixed WSL Ollama
endpoint** in Operations with required context consent. No replacement model,
Windows Ollama server, 24 GB WSL allocation or blind download is prescribed.
For answer audio, explicitly configure existing engine/assets/endpoints; select
a canonical conversation and enable read replies without microphone.

Local static lab, from the repository root:

```bash
python3 artemis/scripts/serve_pages.py --port 4173
# http://localhost:4173/artemis/sage-preview.html
```

Developer builds, from `artemis/frontend`:

```bash
npm ci
npm run typecheck
npm run build
npm run build:sage-preview
```

Browser tests require an installed compatible Chromium, disposable host state,
and temporary keys. `tests/sage_ui_host.py --confirm-scripted-provider` is an
explicit test fixture only, never a production model fallback. Do not use these
scripts against private/real Sage state.

## Work still active

The new [cumulative ledger](ONGOING_WORK.md) preserves hot tools, durable speech,
original engine bridges, Atrium consent/perception, Phone/mobile, privacy scopes,
spatial/lab/world/science and resource/hardware work. New bookmark families add
media, utility/developer/3D/device research; they do not replace those priorities.

This slice does **not** claim all Muse Spark capabilities or equivalent model
quality; exact Perchance server/model internals were not obtained. Real selected
Ollama authoring, meaningful physical answer audio/lip-sync/latency, richer
speech voice/rate/streaming options, Perchance-style queued tasks/universal undo,
web-code preview/promotion contracts, resource performance, camera/carrier/native
engines and production multi-user boundaries remain unverified or pending.

## Non-destructive publication boundary

`ideas/` remains owner-only, read-only and **only on this branch**. Its blob IDs
are unchanged by implementation. The branch contains owner upload commits:
**do not directly merge it into main**. Later promotion must select reviewed
implementation changes without inbox commits/files. No agent merge, force push,
main/source branch write, Pages setting or deployment action is performed.

## Exact implementation changed paths

Inbox/original vendor changes are forbidden; replacement generated hashes are
listed explicitly (Git may display them as renames):

```text
M	README.md
M	artemis/README.md
A	artemis/docs/ONGOING_WORK.md
M	artemis/docs/PROJECT_BRIEF.md
A	artemis/docs/SAGE_HELPER_01.md
A	artemis/docs/SAGE_HELPER_RESEARCH.md
A	artemis/docs/ideas-reviewed-2026-10-14.json
A	artemis/docs/verification-sage-01.json
M	artemis/frontend/package.json
A	artemis/frontend/sage-preview.html
A	artemis/frontend/src/SageHelper.tsx
M	artemis/frontend/src/main.tsx
A	artemis/frontend/src/sage-helper.css
A	artemis/frontend/src/sage-preview.css
A	artemis/frontend/src/sage-preview.tsx
M	artemis/frontend/src/style.css
A	artemis/frontend/tests/browser.sage.integration.mjs
A	artemis/frontend/tests/browser.sage.preview.mjs
A	artemis/frontend/vite.sage-preview.config.ts
A	artemis/tests/sage_ui_host.py
A	artemis/web/assets/index-C-9o9zqo.js
D	artemis/web/assets/index-C-J9G3SF.css
A	artemis/web/assets/index-GPDhAe5D.css
D	artemis/web/assets/index-zqbXvZHZ.js
M	artemis/web/index.html
M	docs/ATTRIBUTION.md
M	docs/PAGES_SETUP.md
A	docs/assets/sage-preview-BV-m0lHX.css
A	docs/assets/sage-preview-BWo3BdX3.woff2
A	docs/assets/sage-preview-CwvVGij3.woff2
A	docs/assets/sage-preview-x6xN3ELT.js
M	docs/index.html
A	docs/sage-preview.html
```
