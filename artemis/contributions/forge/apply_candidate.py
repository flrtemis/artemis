#!/usr/bin/env python3
"""Review/apply ONLY the pinned FORGE candidate source overlay, with backups.

Default is a read-only --check. Stops on drift, symlinks or existing different
new files before any source change. Does not install, run training, alter memory
settings, enable Roam/networking, remove data, or touch checkpoints/models.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--forge-root', required=True)
    p.add_argument('--apply', action='store_true')
    p.add_argument('--i-stopped-forge', action='store_true')
    args = p.parse_args(argv)
    base = Path(__file__).resolve().parent
    payload = json.loads((base / 'candidate-files.json').read_text(encoding='utf-8'))
    root = Path(args.forge_root).expanduser().resolve()
    if not (root / 'run.py').is_file() or not (root / 'forge/__init__.py').is_file():
        p.error('Select the actual FORGE source root containing run.py and forge/')
    pending = []
    for row in payload['files']:
        relative = Path(row['path'])
        if relative.is_absolute() or '..' in relative.parts:
            raise ValueError('Invalid overlay path')
        destination = root / relative
        if destination.is_symlink() or not destination.resolve().is_relative_to(root):
            raise ValueError('Refusing a source symlink/outside path: ' + str(relative))
        actual = sha(destination.read_bytes()) if destination.is_file() else None
        if actual == row['candidate_sha256']:
            continue  # idempotent, already this exact candidate
        if actual != row['original_sha256']:
            raise ValueError('Source differs from the pinned Drive snapshot; do not overwrite Rowan\'s edits: ' + str(relative))
        content = row['content'].encode('utf-8')
        if sha(content) != row['candidate_sha256']:
            raise ValueError('Candidate payload digest mismatch')
        pending.append((relative, destination, content, row['original_sha256']))
    if not pending:
        print('Exact candidate already present. No changes.'); return 0
    if not args.apply:
        print(json.dumps({'mode': 'read_only_check', 'would_change': [str(row[0]) for row in pending],
                          'next': 'Stop FORGE normally, then rerun with --apply --i-stopped-forge. Read the handoff first.'}, indent=2))
        return 0
    if not args.i_stopped_forge:
        p.error('Stop FORGE normally first and explicitly pass --i-stopped-forge; never patch an active training process')
    # Source-only backup; refuses overwrite. No models/recordings copied into the bundle.
    backup = Path(tempfile.mkdtemp(prefix='artemis-forge-source-backup-', dir=root))
    originals = []
    for relative, destination, content, original in pending:
        if original is not None:
            target = backup / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, target)
        originals.append({'path': str(relative), 'original_sha256': original, 'candidate_sha256': sha(content)})
    (backup / 'overlay-manifest.json').write_text(json.dumps(originals, indent=2), encoding='utf-8')
    # Recheck every source after backup before modifying anything.
    for relative, destination, content, original in pending:
        actual = sha(destination.read_bytes()) if destination.is_file() else None
        if actual != original:
            raise RuntimeError('Source changed during backup; no source overlay written: ' + str(relative))
    for relative, destination, content, original in pending:
        destination.parent.mkdir(parents=True, exist_ok=True)
        # x-mode staging, then replace only the previously fingerprinted source file.
        with tempfile.NamedTemporaryFile(dir=destination.parent, prefix='.forge-overlay-', delete=False) as f:
            f.write(content)
            staged = Path(f.name)
        staged.replace(destination)
    print(json.dumps({'applied': [str(row[0]) for row in pending], 'source_backup': str(backup),
                      'live_training': 'NOT RUN', 'next': 'Run verify_forge.py using the existing FORGE interpreter. No setup/reinstall needed.'}, indent=2))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
