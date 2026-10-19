# ARTEMIS
**A Reality That Enhances My Integrated Services**

Your assistant, remembered context, approved tools and files in one locally
owned workspace. A substantial **partial integration**, not a finished
all-project ecosystem or twelve apps behind a launcher.

**[Website / first-run guide](https://flrtemis.github.io/artemis/)** ·
[Pages-ready local site](docs/index.html) · [Current twelve-source evidence](artemis/docs/CURRENT_CAPABILITIES.md)

**Pages is live:** October 14 read-only verification shows `main` + `/`, serving the older README. The newer guide and **[Sage interaction lab](docs/sage-preview.html)** are on this feature branch. [Owner-controlled preview publication](docs/PAGES_SETUP.md) uses this branch + `/docs`, never the branch root/inbox. No merge or publishing-setting change is made by the agent.

## The self-building core is the real build

ARTEMIS's target is **useful existing abilities AND autonomous growth of new
capabilities**—not an inventory or launcher. It must eventually notice gaps,
build/test/repair candidates, integrate verified abilities and reuse them without
human steering of each routine step, within owner-defined authority and budgets.

**That unattended core is not finished today.** Current hot tools, durable runs,
isolation and continuity are prerequisites; approval-driven tool creation is not
presented as full autonomy. [Founder-corrected spec and concrete completion test](artemis/docs/SELF_BUILDING_CORE.md).

## Sage — accessible alongside the work

The new helper is an additive projection of the existing conversation, live
capability registry, approvals, work and files. Open **Sage** from any main view;
no second assistant history/model/audio owner is introduced. Configured answer
audio stays explicit; stopping speech and cancelling a job remain different.
Voice & reading options now offers a deliberately selected device-local-reported
voice, speed and fenced-code speech policy, without silently replacing configured TTS.

[Current answer-reading slice and exact checks](artemis/docs/SAGE_HELPER_02.md) ·
[Original helper surface](artemis/docs/SAGE_HELPER_01.md) ·
[Perchance/inbox research](artemis/docs/SAGE_HELPER_RESEARCH.md) ·
[Cumulative work — new ideas do not replace earlier goals](artemis/docs/ONGOING_WORK.md)

`ideas/` is owner-uploaded, **read-only and branch-only**. Do not merge this
shared branch directly or publish its root; review/promote implementation changes
without inbox commits/files. Raw captures are not website assets.

## Try a real first task (WSL2/Linux)

```bash
git clone --branch arena/b4094b40-artemis https://github.com/flrtemis/artemis.git
cd artemis/artemis
bash start.sh
```

Initial Internet access installs Python dependencies. Open **http://localhost:8000**
and use the operator key printed in your **local** terminal. The built UI is
included; no Node build or model weights are needed for the first task.

**Workspace → New artifact:** create `notes.md`, submit the proposal, review
Activity and approve. Open the real saved file. **Continuity → Keep a memory:**
approve it, restart using the same data directory and inspect it again.
These paths work without a language model.

**Then connect your existing Ollama inside WSL** using its already-configured
fixed IP and an actual installed tool-capable tag in Operations. Non-loopback
context export needs explicit consent. Don't start another Windows Ollama
server, silently replace/download a model or raise WSL RAM to 24 GB.
Once installed, `bash start.sh --offline` skips installation and blocks
public/DNS model/audio endpoints; separately configured engines still have
their own offline requirements. No mandatory subscription for the local core
is **not** a promise of zero hardware, electricity, setup or optional-service cost.

## What's new in integration milestone 03

- Agent's hot `create_tool` lifecycle now uses the **same running canonical
  run/thread/model loop**: exact approval, immutable staging, **real isolated
  test**, hot schema registration, separate invocation approval, result/error
  feedback and the original answer. Versioning, rollback and opt-in export.
- Barge-in/audio yield keeps durable work alive; explicit job cancellation and
  same-job corrections are distinct. Busy follow-ups are held, not answered by
  a second competing agent. Saved replies stay in canonical history.
- Versioned local capability contract and a [model-free contributor example](artemis/docs/EXTENSIONS.md).
- Pages-ready guide with real captioned **scripted-provider** UI/sandbox
  evidence, honest costs/status/comparisons and owner-only publishing steps.

[Full implementation, tests, local checks and remaining scope](artemis/docs/MILESTONE_03.md) ·
[Historical milestone-03 verification](artemis/docs/verification-03.json) ·
[Founder-approved project brief](artemis/docs/PROJECT_BRIEF.md) ·
[Full setup / historical milestone-02 details](artemis/README.md)

**Fresh evidence is not real model/device proof.** Scripted model decisions test
actual Store/Runtime/UI/Bubblewrap namespaces/seccomp. Real Ollama, GPU,
physical audio/camera/PC, native Godot, Docker, carriers remain
unverified in this environment. The existing Pages deployment is verified, but
the new Sage preview is not claimed deployed. See the exact results/skips in the verification
record, separate from historical tests.

## Repository and preservation

- `artemis/`: authoritative host, adapters, built local UI, retained source,
  contracts, examples, tests and current commit-pinned census/evidence matrix.
- `docs/`: static consumer site only; no Python/Ollama backend, private state,
  CDN, tracking or localhost API calls.
- `analysis/`, `BUNDLE_README.md`, `BUNDLE_SHA256.txt`: **historical milestone-02
  seven-origin audit / ZIP handoff**, not a complete current census or checksum
  for this changed branch. Their original records are retained.

Original repositories, existing agent branches and retained source stay
unchanged. Private Sage databases/transcripts, credentials, weights, caches,
installed environments and native binaries are excluded. Public source does
not grant new rights: the original Ready Player Me avatar is declared
**CC BY-NC 4.0**; model/component terms still apply.
[Site attribution and license limits](docs/ATTRIBUTION.md).

## Founder's original repository note (preserved)

> https://arena.ai/agent can be fully credited for consolidating nearly all of my GitHub repositories because were it not for them, none of this would've been possible! Thank You https://arena.ai/agent Any references in here about a "ZIP" file, is strictly due to https://arena.ai/agent compiling all the work it did there, into a "ZIP" file for me when asked to. So, basically just ignore that part, since I've already extracted that same "ZIP" file before uploading its contents here. All my repositories are a result of either personal work of mine, or work that other had done but I felt needed a personal touch to them. As for what you see here, this is just the beginning...
