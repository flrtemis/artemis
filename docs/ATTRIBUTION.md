# Site evidence, provenance and license limits

This static ARTEMIS front door was added on `arena/b4094b40-artemis`, continuing
from `b39062b589b4a953e826b2e6042397198df967ef`. It is a guide, **not a hosted model**.
No Pages publication or physical-PC validation is claimed by this session.

## Actual captures, not generated/mock product output

- `assets/workspace.webp` and `assets/creation-approval.webp`: screenshots of the
  actual newly built ARTEMIS frontend and authenticated backend in Chromium.
  Fresh disposable state, synthetic numbers, and an explicitly labelled
  **SCRIPTED_TEST_PROVIDER_NO_LLM** make model decisions reproducible.
- `assets/hot-tool-trace.json`: sanitized selected records from that actual
  durable run, approvals, live capability schema and final messages. Real
  Bubblewrap namespaces/seccomp execute the generated code; no substitute
  subprocess-only sandbox, model inference, physical voice or GPU result is
  implied. No operator key, bearer token, Sage private state or transcripts
  belonging to the founder are exported.
- Reproduce with `artemis/tests/demo_host.py --confirm-fixture-provider` and
  `artemis/frontend/tests/browser.03.integration.mjs`. Ordinary launch never
  substitutes this test provider for a missing model.
- The browser walkthrough replays these static records. It does not fabricate
  a fresh answer, connect to your localhost or host ARTEMIS's Python/Ollama stack.

## Preserve authorship and terms

The source/provenance map lives in
[`CURRENT_CAPABILITIES.md`](https://github.com/flrtemis/artemis/blob/arena/b4094b40-artemis/artemis/docs/CURRENT_CAPABILITIES.md)
and its JSON/CSV companions. Founder's original projects and other contributors'
work are not reattributed to this site. Byte-identical retained source stays
under `artemis/vendor_sources/`; new adapters are separate.

The existing avatar capture uses Gemma Avatar's retained Ready Player Me
`brunette.glb`, **declared by that source as CC BY-NC 4.0 (non-commercial)**.
See the [pinned original declaration](https://github.com/flrtemis/gemma-avatar/blob/c4becc81781fc59d0cf6d7ff52f6099f9943f7b8/README.md).
TalkingHead and HeadAudio are original libraries with their own terms.
No blanket commercial redistribution permission is inferred from public source
or a screenshot. Model and source/component license obligations remain.

The site mark, CSS, layout and static interaction code are new project work. The exact founder-symbol wordmark is vector typography drawn from Noto Sans Math, Noto Sans and Noto Sans Coptic glyphs, so it renders even when a browser has no mathematical/Coptic fonts installed. A three-character, renamed **ARTEMIS Math Accent** WOFF2 subset renders the exact stylized `𝘧𝘳𝘦𝘦` in the ownership sentence. The original Noto copyright/OFL 1.1 texts and pinned font/license blob identities are preserved in [`assets/OFL-Wordmark-Sources.txt`](assets/OFL-Wordmark-Sources.txt). No new license for source projects is implied.
The self-hosted **Instrument Serif** font is from `@fontsource/instrument-serif`
**5.2.5**, under SIL Open Font License 1.1; the exact packaged copyright/license
is preserved in [`assets/OFL-InstrumentSerif.txt`](assets/OFL-InstrumentSerif.txt).
The upstream Instrument Serif authors/copyright and reserved-name notice are also preserved in [`assets/OFL-InstrumentSerif-upstream.txt`](assets/OFL-InstrumentSerif-upstream.txt) (Google Fonts `ofl/instrumentserif/OFL.txt`, blob `669ce7917bec662fcf7244d37f49c4277f6fbd73`). No font CDN is contacted. The local extension example alone explicitly declares
CC0-1.0; that is not a new license for the rest of ARTEMIS or its source projects.

Familiar-category comparisons identify everyday jobs, not endorsement, product
parity, unlimited performance or a free replacement for managed services.
Hardware, setup, energy, optional connectivity, privacy configuration and
unfinished integrations are deliberately visible.
