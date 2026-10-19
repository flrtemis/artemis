# FORGE contribution review — local voice training

Start with [HANDOFF.md](HANDOFF.md). This is a source-pinned **candidate and
verification harness**, not a registered ARTEMIS training engine, model download,
new UI, or proof of a successful live XTTS training run.

Source manifest: 17 Bob/Rowan files from the authorized shared Drive table.
Current local evidence: 28 real SoundFile/NumPy contracts with explicitly simulated
Torch conversion; native Torch/XTTS/checkpoint/inference remains NOT RUN here.
Real native gates must run in Bob's existing environment with cached weights,
owned/consented voice and reviewed local output. No changes to Drive originals.

```bash
python -m pytest artemis/contributions/forge/tests -q -rs
# soundfile/numpy/pytest test dependencies only; no model or training stack needed
```

Source-specific tests skip if the fingerprinted scratch snapshot is absent.
`verify_forge.py` instead uses actual Torch and FORGE in the existing target venv;
it never installs dependencies, downloads models or turns a missing engine into
an imitation success. Read the evidence boundaries and commands in the handoff.

`candidate.patch` preserves supplied Coqui/MPL adaptation headers. Other source,
base-model/output terms and voice permissions remain distinct. No blanket license
or commercial-use grant is added by this review directory.
