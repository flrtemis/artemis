# Sage helper 02 — explicit answer reading, one audio owner

2026-10-14 · additive to [Sage helper 01](SAGE_HELPER_01.md), milestone 03 and
[ONGOING_WORK.md](ONGOING_WORK.md). Branch `arena/b4094b40-artemis`.

**ARTEMIS — A Reality That Enhances My Integrated Services.**

## Continued work, not a new replacement

The 58-file read-only inbox is unchanged from its reviewed manifest. No upload
was executed, edited, copied into the product/site or converted into instructions
to change hardware/networking. This slice advances SAGE-02 accessibility while
keeping original engine, vision, phone, scope/privacy and native-worker work active.

## Implemented

### Deliberate speech-source choice

In Sage, expand **Voice & reading options**. The default remains the existing
**Configured ARTEMIS engine**. If it is not ready, no other provider is silently
selected.

A separate **Device voice** option is now available only by explicit user choice:

1. Choose that speech source.
2. Choose an available voice the OS/browser **reports as local**. Remote-reported
   voices are not offered, missing/revoked voices fail closed, and name/gender
   heuristics do not choose a substitute.
3. Set **0.5–2.0× speed** and optional **skip fenced code in speech only**.
4. Use **Read replies** to enable automatic reading of new saved answers in the
   selected canonical conversation, or use **Read saved reply** for manual replay.

Source/voice/speed/code preferences exist only in this page, not cookies or hidden
persistent settings. Opening Sage, looking at voices or visiting another view
never starts speech or a model request.

**Local-service is a device report, not an independently verified offline or
privacy guarantee.** Browser/OS implementations remain external software. No
remote voice, API, asset/model download or microphone is used as a fallback.

### Complete, stable answer presentation

`device-reader.ts` consumes committed user-facing assistant messages—not DOM
mutations, text-length guesses, thinking, tool traces or acknowledgements.

- Thread/message IDs drive deduplication; identical text in different messages is
  not incorrectly suppressed.
- Existing history is baselined, not automatically replayed on enable/reconnect.
- Sequential bounded chunks concatenate exactly and include short final tails;
  Unicode surrogate pairs are not split.
- Only selected fenced code is omitted. Warnings, emphasis, actions, names, math,
  quotes and canonical stored text are not globally stripped or rewritten.
- The 20,000-character answer / 16-reply presentation budgets fail visibly;
  complete text stays saved rather than silently truncated.
- Input holds output; stop/late-event epochs fence stale callbacks. A new explicit
  turn suppresses older held/late automatic audio, but keeps saved replies manually
  readable. Confirmed canonical run IDs release the appropriate new answer.
- Browser permission/voice-loss failures retain text/work and expose a recovery
  gesture, not a hidden retry/fallback loop.

### One coordinator, not a second assistant/audio loop

`SharedAudio` coordinates configured realtime PCM, recorded narration and explicit
device reading. Switching sources releases the old presentation transport without
cancelling a Runtime job or starting another model/history.

Configured connection setup/status callbacks are generation-fenced: an older
socket cannot finish connecting after a device switch and steal ownership.
Device speech has **no PCM/visemes**, so the avatar is not made to appear lip-synced
based merely on a browser API flag. Configured PCM/stage behavior remains intact.

The full conversation and helper use the same reader and saved messages. Old
thread-message requests are fenced before applying results; one thread's delayed
projection cannot become another thread's auto-read context.

**Stop speech only**, **Turn audio off**, and closing Sage do not call durable job
cancellation. **Cancel job** remains the separate exact-run action.

### Reconnect correctness discovered during verification

A pre-existing configured-voice cleanup race intermittently rejected a legitimate
reconnect with WebSocket code 1008. A session could remain in the ownership map
when cancellable cleanup was interrupted; simultaneous handshakes also checked
ownership before an await without reserving it.

The Speech service now reserves a thread **before handshake awaits** and releases
that exact reservation **before cancellable cleanup**. Identity checking prevents
late old cleanup from removing a new owner. Ticket expiry, one-use grants,
thread scope and duplicate-active-session rejection remain unchanged. Three new
deterministic admission/cancellation/slow-cleanup tests accompany the existing
real WebSocket job-preservation tests. No Runtime cancellation was added.

### Static visual ground

The shared-component `/docs/sage-preview.html` now exposes the same explicit
reading controls for **synthetic design answers**, not a model/backend. The fixed
introduction uses the same bounded reader rather than competing with it. The
page still declares no model/API/local-service connectivity, no tracking state,
no raw inbox assets and no microphone.

## Verification

Fresh command/case details and limitations are recorded in
`verification-sage-02.json`; earlier verification files stay historical.

| Check | Result |
|---|---|
| Reader/coordinator Node contracts | **25 passed**; controlled speech/socket adapters, not audible/device/model proof |
| New real-app reading browser flow | **7 passed**: explicit source/voice/rate, actual approval/result/history, all final text/tail, code-only speech formatting, replay without new work, stop/off vs exact cancel, voice loss, mobile/keyboard/scoped axe |
| Existing normal-helper / scripted-helper browser | **9 / 10 passed**; current canonical runtime, no inference claim |
| Existing static lab / guide browser | **8 / 9 passed**; static/no-model boundaries retained |
| Speech admission + existing job-presence group | **10 passed**, including three new deterministic admission/cleanup cases |
| Current full backend | **53 passed, 49 skipped**, one Starlette/httpx warning. Isolation/native/optional models absent in this sandbox; no soft fallback |
| TypeScript / application build / static build / npm audit | Pass; **0 vulnerabilities**, existing vendor-font and optional-large-presence-chunk warnings retained |
| Retained originals | **505 exact blobs + 2 separately verified LFS mappings = 507**, zero failures |

An earlier run's reconnect failure was not dismissed as load or counted as a pass:
it was reproduced in isolation, fixed with admission tests, then the full suite
rerun. Initial selector/keyboard focus checks also led to explicit select labels
and modal Escape/Tab handling after a focused Send becomes disabled.

All browser speech events in automated verification are mocked. An utterance
start/end event is **not proof that a speaker was audible**, meaningful-answer
voice quality, physical latency, offline OS behavior or lip-sync. Automated axe
is not accessibility certification. Models/voice engines/weights are not installed
or changed by this slice.

## Try the real UI

Use the existing local WSL/Linux launch with a disposable trial data directory.
Connect only your actual installed model/tag and existing fixed WSL endpoint when
you want inference. No new model or Windows Ollama process is prescribed.

Open **Sage → Voice & reading options → Device voice → choose a local-reported
voice**, set speed, then **Read replies**. Once enabled, new committed answers in
that selected conversation are read automatically. Existing replies can be read
explicitly; changing thread/source/voice releases the prior audio owner.

If no local-reported voice is available, the control explains that and does not
pick a remote voice. You can instead configure your existing ARTEMIS TTS engine.
Device settings do not alter that engine; original engine voice/rate bridging
remains separate pending work.

In the static lab, the same gesture reads **labelled synthetic examples only**.
It does not contact your machine or run a model.

## Publication and remaining seams

Only the owner selects Pages source. Current source remains `main` + `/`; no new
preview deployment is claimed. To review this branch without a merge, select
`arena/b4094b40-artemis` + **`/docs`**, never the branch root/inbox. Do not directly
merge this shared branch: owner inbox commits must remain branch-only.

Physical PC/WSL/model performance, meaningful audible STT/TTS/lip-sync, original
Parakeet/Qwen engine endpoints, microphone/camera/carrier/native devices,
production user/project security and complete Muse parity remain unverified.
Next engine-specific work must retain the same coordinator, context permissions,
resource admission, corrections/held results and no irreversible replay. Device
presentation does not replace those existing tasks or prove them finished.

## Exact implementation changed paths

No owner inbox/original vendor paths are changed. Obsolete compiled entries are
replaced; Git may display them as renames.

```text
M	README.md
M	artemis/README.md
M	artemis/artemis_app/speech.py
M	artemis/docs/ONGOING_WORK.md
A	artemis/docs/SAGE_HELPER_02.md
A	artemis/docs/verification-sage-02.json
M	artemis/frontend/package.json
M	artemis/frontend/src/SageHelper.tsx
A	artemis/frontend/src/SageReadingControls.tsx
A	artemis/frontend/src/device-reader.ts
M	artemis/frontend/src/main.tsx
M	artemis/frontend/src/sage-helper.css
M	artemis/frontend/src/sage-preview.tsx
M	artemis/frontend/src/shared-audio.ts
M	artemis/frontend/tests/browser.sage.preview.mjs
A	artemis/frontend/tests/browser.sage.reading.mjs
A	artemis/frontend/tests/device-reader.test.mjs
A	artemis/frontend/tests/shared-audio.test.mjs
M	artemis/tests/sage_ui_host.py
A	artemis/tests/test_voice_admission.py
A	artemis/web/assets/index-BKyKrW5Q.css
D	artemis/web/assets/index-C-9o9zqo.js
A	artemis/web/assets/index-DViCzjUj.js
D	artemis/web/assets/index-GPDhAe5D.css
M	artemis/web/index.html
M	docs/PAGES_SETUP.md
D	docs/assets/sage-preview-BV-m0lHX.css
A	docs/assets/sage-preview-BmSd6i_-.js
A	docs/assets/sage-preview-Lbk4UVOI.css
D	docs/assets/sage-preview-x6xN3ELT.js
M	docs/sage-preview.html
```
