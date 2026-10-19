# Rowan ↔ ARTEMIS: FORGE verification handoff

**2026-10-19. Candidate review, not a successful live training run.**

Shared source: Bob's public FORGE Drive folder, 17 files. All read and fingerprinted
in `source-manifest.json`; original Drive files remain unchanged. No recordings,
weights, personal datasets, credentials, model downloads or remote training were
used here. New review artifacts belong in a separate Drive review folder, never
as an overwrite of Rowan's source.

## Current result, without conflating evidence

- **28 CPU contract checks passed** using actual libsndfile/SoundFile/NumPy:
  WAV bit depths, mono/stereo, rate/value/layout, bounded reads, paths/file objects,
  invalid/corrupt files, non-WAV dispatch, idempotence, actual WAV output, source
  governor logic and real ZIP relocation.
- The Torch conversion in those checks is an **explicit NumPy facade**, not a real
  Torch tensor or XTTS optimizer. Source governor tests use scripted percentages,
  not Windows native memory sampling or a proven hard RAM cap.
- Original supplied shim's default WAV route really decoded generated fixtures.
  Its ignored `frame_offset`, `num_frames`, `channels_first` behavior was reproduced.
- Applying the candidate to a **scratch copy** passed source fingerprint checks,
  created source-only backups, and was idempotent. Drift protection refused a
  synthetic Rowan edit without overwriting it.
- The verifier was run in this sandbox and reported **failed / ModuleNotFoundError
  (torch), live training NOT RUN**. It does not substitute a random model or claim
  a GPU result. Full native training is still the immediate shared verification job.

**Please run the real Torch contract first on Bob's existing venv, then the small
live smoke. Return `verification.json` after checking paths/errors for private
information. Do not upload recordings, checkpoint/model files, voice embeddings,
provider credentials or caches.**

## What the code review found

### Immediate path: audio → checkpoint → inference

1. `forge/__init__.py` runs before FORGE imports the training modules, so the WAV
   monkeypatch should reach normal later `torchaudio.load` calls. It currently
   catches all import errors silently and ignores every WAV argument beyond URI.
   Reloading that original module can also make the captured original loader
   self-referential on non-WAV paths.
2. `forge/synth.py` still uses **`torchaudio.save`**. Decoder bypass alone does not
   remove a possible TorchCodec/encoder failure at the final WAV output stage.
3. Exported `voice.json` contains **absolute paths**, contradicting portability
   after moving/extracting a ZIP. The candidate writes relative artifact paths
   and resolves both new relative and legacy absolute packages when loading.
4. `train_voice` can return a directory where an actual checkpoint file is
   expected. The candidate fails visibly if the expected best checkpoint is
   absent instead of calling export successful.
5. The candidate adds explicit existing-base-directory / `allow_download=False`
   options for verification. It never reinstalls Torch, changes Bob's chosen
   CUDA build, downloads a model, enables a provider, or changes WSL settings.

### RAM governor / safety

- `num_loader_workers=0` is real code, but reduction/peak RAM/VRAM must be measured
  on the actual workload. Do not claim a fixed saving or a guaranteed-safe PC.
- The existing preflight gate occurs after model initialization. Candidate adds
  the same >90% gate **before** base/model initialization; thresholds are unchanged.
- The monitor checks Windows **system RAM**, not process allocation or a hard
  limit. Missing API readings return `None` and are skipped; CUDA allocator-cache
  cleanup is not proof of sufficient RAM/VRAM.
- `os._exit(42)` kills the whole FORGE/Gradio process. A stop before the first
  save, or during a checkpoint write, cannot guarantee a safe checkpoint. Candidate
  log/batch text removes that guarantee. It does not remove the guard or invent
  graceful resume.
- A hard stop may leave no final verifier report. **Absence of a completed report
  is not success.** Keep terminal exit code/log, inspect an actual checkpoint and
  do not auto-replay/resume the run blindly.
- The normal local UI does not pass `resume_from`; a printed instruction to restart
  is not itself a resume test. The Roam resume path also needs separate verification
  of the exact trainer checkpoint argument semantics.

### Separate follow-up, not enabled by this bundle

- `LocalProvider.stop` only logs; it does not stop its training thread.
- Roam can auto-select a credentialed Kaggle provider and upload voice data. That
  requires explicit data/engine/provider consent before an ARTEMIS integration.
  A private cloud dataset is not equivalent to local-only processing.
- Start failures bypass the loop's final failover-count check; candidate work here
  does not claim all provider/failover/retry behavior is robust.
- `latest_checkpoint` only recognizes two basenames; check actual Coqui checkpoint
  naming/completeness before trusting failover. Provider fetch/done markers must
  not imply a validated artifact after a failed fetch.
- Non-WAV upload formats still depend on decoder support; this is a narrow local
  WAV workaround, not a full FFmpeg/MP3/M4A claim.
- Export overwrite/SameFile behavior, active UI concurrency, dataset split minimums,
  crash-safe checkpoint writes, resource leases and serving-model cache eviction
  are additional gates. Do not delay the first controlled WAV/live pass by
  silently implementing a different system.

## Candidate contents

- `audio_compat.py`: idempotent WAV load profile + finite PCM16 WAV writer.
- `candidate.patch`: inspectable unified diff for the pinned source.
- `candidate-files.json`: source-fingerprinted overlay payload (source code only).
- `apply_candidate.py`: defaults to read-only check; apply requires explicit flag,
  stopped FORGE acknowledgement, exact source hashes and source-only backups.
- `verify_forge.py`: real-Torch local audio checks; optional small cached-CUDA smoke.
- `tests/`: CPU contracts with evidence limitations stated in the code.

MPL-2.0 adaptation notices in the supplied training code are retained. The source
snapshot has no blanket top-level license grant. **XTTS v2 model terms are
separate from MPL code and voice consent**: the published model license is CPML
1.0.0, non-commercial model/output use, with notices required for derivatives and
outputs. Personal ownership of a recording does not erase model/output terms:
https://huggingface.co/coqui/XTTS-v2/blob/main/LICENSE.txt . Candidate voice manifests
include the model license URL; do not advertise unrestricted commercial voices.

TorchAudio documents the >=2.9 float32/TorchCodec load behavior and ignored
normalize/backend/buffer compatibility arguments here:
https://docs.pytorch.org/audio/stable/generated/torchaudio.load.html . Candidate
refuses unsupported legacy normalize=False integer semantics rather than faking it.

## Run it on Bob's existing environment

Do **not** run setup-forge.bat or pip-install/reinstall the stack for this test.
First stop FORGE normally. Put this review bundle anywhere outside private model
folders, e.g. `C:\FORGE-review`. Substitute actual local source and output paths.

Read-only source check (Windows shell, NOT an instruction to configure Ollama):

```bat
C:\FORGE\.venv\Scripts\python.exe C:\FORGE-review\apply_candidate.py --forge-root C:\FORGE
```

Inspect the diff. If source matches and you accept the candidate:

```bat
C:\FORGE\.venv\Scripts\python.exe C:\FORGE-review\apply_candidate.py --forge-root C:\FORGE --apply --i-stopped-forge
```

If it refuses because Rowan has newer edits: **do not force it**. Put the changed
source on our shared Drive table and we'll rebase the candidate against that source.
The backup path is printed; no dataset/checkpoint/model is replaced by the overlay.

### Gate A — real Torch audio only

```bat
C:\FORGE\.venv\Scripts\python.exe C:\FORGE-review\verify_forge.py --source C:\FORGE --out C:\FORGE-verify-audio-001
```

The output directory must be new. It tests generated WAV fixtures and imports the
actual selected FORGE package, not another installed copy. It records exact module
versions and source digests. **`audio_passed_training_NOT_RUN` does not mean training
passed.** An error such as missing packages, wrong shim, unsupported function or
wrong shapes is a real failed gate; return the JSON, not a claim of success.

### Gate B — bounded local train/reload/export/inference

Use existing prepared metadata and existing cached XTTS base files. Only owned or
explicitly consented voice audio. Candidate selects up to four train/two eval,
disjoint 3–11.5 second mono 22050 Hz clips into a new local output directory.
It does not retranscribe or test the raw-recording/Whisper dataset-build stage.

```bat
C:\FORGE\.venv\Scripts\python.exe C:\FORGE-review\verify_forge.py --source C:\FORGE --out C:\FORGE-verify-live-001 --live-smoke --own-or-consented-voice --train-csv C:\FORGE-WORK\dataset\metadata_train.csv --eval-csv C:\FORGE-WORK\dataset\metadata_eval.csv --base-model-dir C:\FORGE-WORK\run\training\XTTS_v2.0_original_model_files
```

Requires the actual configured CUDA stack and five cached base files. Network is
blocked within this verifier process; no provider/Internet/model fallback.
One epoch, batch 1, accumulation 1. Existing RAM guard remains active. The verifier
requires a real checkpoint with positive training step and finite recorded loss,
loads that freshly generated trusted checkpoint (never an arbitrary downloaded
pickle), moves a new voice package, synthesizes a WAV from the moved package, and
checks actual finite/non-silent 24000 Hz waveform output.

A clean pass is a real smoke, **not full-data convergence, audible identity/quality,
latency, resource-peak, resume or long-run safety proof**. Listen locally and record
that observation separately. If the checkpoint schema differs, it must fail and
be adjusted to the real schema; do not remove assertions just to get a green label.

The full voice-quality run, crash/resume check and original raw-audio dataset-build
verification come after those gates. Keep the existing model, existing WSL fixed
IP/configuration and current RAM limits; no 24 GB recommendation or extra resident
model is introduced.

## ARTEMIS: one system, not a launcher

FORGE contributes an **optional voice-training worker**, not a new assistant or a
second canonical job store. Stage integration after the live source is verified:

| FORGE contribution | ARTEMIS authority / required contract |
|---|---|
| Prepared voice data | Workspace-owned opaque artifact IDs, hashes, consent and license provenance; no private recording in Git/Pages |
| Start/stop/resource gate | Exact approval and canonical durable run ID, separate worker attempt IDs, resource lease/admission; training must not silently consume the interactive voice/model budget |
| Training progress/error/guard stop | Versioned JSON events, finite metrics, explicit failed/interrupted/guard-stopped states; no fabricated progress or success |
| Checkpoint/export | Candidate artifact catalogue, atomic completeness manifest, source/model/dataset lineage and fingerprints; resume only validated compatible checkpoints |
| Voice inference | Engine-only adapter over existing Speech/SharedAudio, no second history/LLM/audio owner. XTTS 24k output requires a tested conversion to current canonical 16k PCM transport |
| Serving voice promotion | Separate explicit approved candidate selection; do not auto-replace Sage's current voice/model during training |
| Roam | Separate per-provider/data-egress consent, budget and trust contract; **local-only by default**, no automatic Kaggle/Colab upload |
| UI | Existing Sage/Laboratory/Work/Files projections and approvals, not an iframe around the FORGE Gradio app |

All previous speech, perception, phone/mobile, spatial/lab/world, privacy and Pages
work remains in the cumulative plan. Pages is static/public; it does not run this
GPU worker or host private voice data. Existing Pages publication was separately
blocked by integration permissions; do not claim this handoff publishes the site.

## Return notes to the shared Drive table

Please leave a NEW small file/report in this review folder with Gate A/B result,
exact command, source hash/version information and whether local listening worked.
Do not overwrite source or earlier reports. Review logs for personal paths/content
before sharing. We can iterate from a failing gate with evidence rather than
loading Bob's full dataset into an unverified loop.

### Bundle revision note

Use **FORGE-candidate-and-verifier-2026-10-19-v2.zip**. The first review ZIP was
superseded because its source manifest accidentally included a generated test
bytecode cache entry. v2 contains exactly the original 17 source fingerprints,
adds a regression for that boundary and reports 28 checks. No original source,
recording or model content changed. Earlier review artifacts remain traceable.
