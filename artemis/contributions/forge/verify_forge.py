#!/usr/bin/env python3
"""Verify FORGE in Bob's EXISTING environment, without installs or downloads.

Default: real torch/torchaudio/soundfile WAV contract. Optional explicit local
smoke: <=4 train/2 eval owned clips, cached XTTS, one epoch, checkpoint reload,
relocated package and inference. Reports never claim audible quality or live
training unless those stages actually ran. Never upload audio/checkpoints.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import shutil
import socket
import sys
import tempfile
import time


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def audio_contract(torch, torchaudio, sf):
    import numpy as np
    checks = []
    with tempfile.TemporaryDirectory(prefix='forge-wav-contract-') as tmp:
        root = Path(tmp)
        for channels in [1, 2]:
            values = np.sin(np.arange(4096, dtype=np.float32) * 0.03) * 0.4
            values = values[:, None] if channels == 1 else np.stack((values, -values), axis=1)
            path = root / ('fixture-' + str(channels) + '.WAV')
            sf.write(path, values, 22050, subtype='PCM_16')
            expected, sr = sf.read(path, dtype='float32', always_2d=True)
            loaded, actual_sr = torchaudio.load(path)
            assert isinstance(loaded, torch.Tensor), 'Not an actual Torch tensor'
            assert loaded.dtype == torch.float32 and actual_sr == sr
            assert tuple(loaded.shape) == (channels, 4096)
            np.testing.assert_array_equal(loaded.cpu().numpy(), expected.T)
            checks.append({'case': 'real_torch_wav_default_' + str(channels) + '_channel', 'result': 'pass'})
            loaded, actual_sr = torchaudio.load(path, frame_offset=13, num_frames=31, channels_first=False)
            assert tuple(loaded.shape) == (31, channels), 'Shim ignored frame_offset/num_frames/channels_first'
            np.testing.assert_array_equal(loaded.cpu().numpy(), expected[13:44])
            checks.append({'case': 'real_torch_wav_window_' + str(channels) + '_channel', 'result': 'pass'})
        bad = root / 'corrupt.wav'
        bad.write_bytes(b'not an audio file')
        try:
            torchaudio.load(bad)
        except Exception:
            checks.append({'case': 'corrupt_wav_rejected', 'result': 'pass'})
        else:
            raise AssertionError('Corrupt WAV unexpectedly accepted')
    return checks


def subset(source_csv, destination, limit, sf, used):
    """Select prepared 3–11.5s mono 22050 clips; no Whisper/model/audio downloads."""
    source_csv = Path(source_csv).resolve()
    selected = []
    if source_csv.stat().st_size > 20_000_000:
        raise ValueError('Metadata exceeds verifier budget')
    with source_csv.open(newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f, delimiter='|')
        for row in reader:
            if not all(row.get(k) for k in ['audio_file', 'text', 'speaker_name']):
                continue
            p = Path(row['audio_file'])
            p = p if p.is_absolute() else source_csv.parent / p
            p = p.resolve()
            info = sf.info(p)
            if info.channels != 1 or info.samplerate != 22050 or not 3 <= info.duration <= 11.5:
                continue
            sha = digest(p)
            if sha in used:
                continue
            used.add(sha)
            target = destination / 'wavs' / (sha[:16] + '.wav')
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, target)
            selected.append({'audio_file': 'wavs/' + target.name, 'text': row['text'], 'speaker_name': row['speaker_name']})
            if len(selected) >= limit:
                break
    if not selected:
        raise ValueError('No disjoint prepared mono/22050Hz/3–11.5s clips fit this smoke profile')
    out = destination / ('metadata_train.csv' if limit == 4 else 'metadata_eval.csv')
    with out.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['audio_file', 'text', 'speaker_name'], delimiter='|')
        writer.writeheader(); writer.writerows(selected)
    return out, len(selected)


def smoke(args, root, torch, sf):
    if not args.own_or_consented_voice:
        raise ValueError('--own-or-consented-voice is required for a live smoke')
    if not torch.cuda.is_available():
        raise RuntimeError('This live XTTS smoke requires Bob\'s actual configured CUDA environment; no CPU/model substitute')
    if not all([args.train_csv, args.eval_csv, args.base_model_dir]):
        raise ValueError('--train-csv, --eval-csv and --base-model-dir are required')
    cached = Path(args.base_model_dir).resolve()
    for name in ['dvae.pth', 'mel_stats.pth', 'vocab.json', 'model.pth', 'config.json']:
        if not (cached / name).is_file():
            raise FileNotFoundError('Cached base artifact missing: ' + name)
    data = root / 'smoke_dataset'
    data.mkdir()
    used = set()
    train, count_train = subset(args.train_csv, data, 4, sf, used)
    evaluate, count_eval = subset(args.eval_csv, data, 2, sf, used)
    from forge.train import train_voice
    result = train_voice(args.language, 1, 1, 1, str(train), str(evaluate), str(root / 'smoke_run'),
                         log_fn=lambda m: print(m, flush=True), base_model_dir=str(cached), allow_download=False)
    checkpoint = Path(result['checkpoint'])
    assert checkpoint.is_file(), 'No actual checkpoint file'
    # Only load the trusted checkpoint just produced locally by this explicit run.
    state = torch.load(checkpoint, map_location='cpu', weights_only=False)
    step = state.get('step', state.get('global_step', state.get('total_steps_done', 0)))
    if hasattr(step, 'item'):
        step = step.item()
    assert isinstance(step, (int, float)) and step > 0, 'Checkpoint has no positive optimizer/training step'
    loss = state.get('model_loss', state.get('loss'))
    if hasattr(loss, 'item'):
        loss = loss.item()
    assert isinstance(loss, (int, float)) and math.isfinite(loss), 'Checkpoint loss is missing/non-finite; do not claim a verified update'
    del state
    import gc
    gc.collect()
    torch.cuda.empty_cache()
    from forge.synth import export_voice, synthesize
    voice, archive = export_voice('smoke-voice', result['checkpoint'], result['config'], result['vocab'],
                                  result['speaker_ref'], str(root / 'voices'))
    relocated = root / 'relocated-voice'
    shutil.copytree(voice, relocated)
    manifest = json.loads((relocated / 'voice.json').read_text())
    assert all(not Path(manifest[k]).is_absolute() for k in ['checkpoint', 'config', 'vocab', 'speaker_ref'])
    output = root / 'smoke-inference.wav'
    synthesize('This is a local verification sample from the explicitly approved training run.', str(relocated), str(output), args.language)
    info = sf.info(output)
    samples, sr = sf.read(output, dtype='float32')
    import numpy as np
    assert sr == 24000 and info.frames > 0 and np.isfinite(samples).all()
    assert float(np.square(samples).mean()) > 1e-10, 'Inference waveform is silent'
    return {'training': 'ran_one_real_epoch', 'train_clips': count_train, 'eval_clips': count_eval,
            'checkpoint_reload': 'pass', 'checkpoint_step': step, 'checkpoint_loss': float(loss),
            'relocated_package_inference': 'pass', 'wav_rate': sr, 'wav_frames': info.frames,
            'checkpoint_sha256': digest(checkpoint), 'waveform_sha256': digest(output),
            'audible_voice_quality': 'not verified by this script', 'archive_created': Path(archive).is_file()}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', required=True, help='Existing FORGE source root containing forge/')
    p.add_argument('--out', required=True, help='NEW local verifier output directory; must not exist')
    p.add_argument('--live-smoke', action='store_true')
    p.add_argument('--own-or-consented-voice', action='store_true')
    p.add_argument('--train-csv'); p.add_argument('--eval-csv'); p.add_argument('--base-model-dir')
    p.add_argument('--language', default='en')
    args = p.parse_args(argv)
    source = Path(args.source).expanduser().resolve(); out = Path(args.out).expanduser().resolve()
    if not (source / 'forge/__init__.py').is_file():
        p.error('FORGE source root is missing forge/__init__.py')
    if out.exists():
        p.error('Output already exists; choose a NEW directory. Nothing will be overwritten.')
    out.mkdir(parents=True)
    report = {'schema': 'forge.verification/v1', 'started_at': time.time(), 'status': 'running',
              'live_training_requested': args.live_smoke, 'audio_contract': [], 'live_training': 'NOT RUN',
              'sensitive_audio_weights_or_credentials_to_share': False}
    try:
        os.environ['HF_HUB_OFFLINE'] = '1'; os.environ['TRANSFORMERS_OFFLINE'] = '1'
        # No Internet/model/provider fallback, even from an unexpected library path.
        def deny_connect(*a, **kw):
            raise RuntimeError('Network disabled by explicit offline FORGE verifier')
        socket.socket.connect = deny_connect
        socket.create_connection = deny_connect
        sys.path.insert(0, str(source))
        import torch
        import torchaudio
        import soundfile as sf
        import forge
        assert Path(forge.__file__).resolve() == (source / 'forge/__init__.py').resolve(), 'Wrong forge package imported'
        report['versions'] = {'python': sys.version.split()[0], 'torch': torch.__version__,
                              'torchaudio': torchaudio.__version__, 'soundfile': sf.__version__, 'cuda_available': torch.cuda.is_available()}
        report['source_sha256'] = {name: digest(source / name) for name in ['forge/__init__.py', 'forge/train.py', 'forge/synth.py', 'run-forge.bat']}
        report['active_shim_profile'] = getattr(torchaudio.load, '_forge_wav_profile', 'original/unmarked')
        report['audio_contract'] = audio_contract(torch, torchaudio, sf)
        if args.live_smoke:
            report['live_training'] = smoke(args, out, torch, sf)
        report['status'] = 'passed' if args.live_smoke else 'audio_passed_training_NOT_RUN'
        return_code = 0
    except Exception as e:
        report['status'] = 'failed'
        report['error_type'] = type(e).__name__
        report['error'] = str(e)[:600]
        return_code = 1
    finally:
        report['finished_at'] = time.time()
        with (out / 'verification.json').open('x', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        print(json.dumps({'status': report['status'], 'report': str(out / 'verification.json'),
                          'share_only': 'verification.json after reviewing its paths/error; never recordings, model/checkpoint files or credentials'}, indent=2))
    return return_code


if __name__ == '__main__':
    raise SystemExit(main())
