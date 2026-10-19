"""FORGE candidate WAV compatibility layer; no FFmpeg/TorchCodec for local WAV I/O.

New integration work for Bob/Rowan's FORGE source snapshot (2026-10-19).
Defaults match FORGE's float32 torchaudio>=2.9 use. No resampling or model load.
This is a candidate overlay, not a claim of live XTTS/Windows verification.
"""
from __future__ import annotations
import os
import re

PROFILE = 'forge.soundfile-wav/v1'


def _wav_request(uri, format=None):
    if format is not None and str(format).lower() in ('wav', 'wave'):
        return True
    try:
        return os.fsdecode(os.fspath(uri)).lower().endswith('.wav')
    except TypeError:
        return False  # file-like inputs require explicit format='wav'; otherwise preserve original dispatch


def install():
    """Idempotently patch one API, keeping the actual original non-WAV loader."""
    import soundfile as sf
    import torch
    import torchaudio

    current = torchaudio.load
    if getattr(current, '_forge_wav_profile', None) == PROFILE:
        return current
    # Migrate the supplied first shim without preserving its reload recursion bug.
    original = getattr(current, '_forge_original_load', current)
    if getattr(original, '__name__', '') == '_forge_audio_load':
        module = __import__('sys').modules.get(getattr(original, '__module__', ''))
        saved = getattr(module, '_orig_ta_load', None) if module else None
        if saved is original:
            raise RuntimeError('Existing FORGE shim recursively references itself; restart the process before applying the candidate')
        if callable(saved):
            original = saved

    def read_wav(uri, frame_offset=0, num_frames=-1, normalize=True,
                 channels_first=True, format=None, buffer_size=4096, backend=None):
        if isinstance(frame_offset, bool) or not isinstance(frame_offset, int) or frame_offset < 0:
            raise ValueError('frame_offset must be a non-negative integer')
        if isinstance(num_frames, bool) or not isinstance(num_frames, int) or num_frames < -1:
            raise ValueError('num_frames must be -1 or a non-negative integer')
        if not isinstance(channels_first, bool) or not isinstance(normalize, bool):
            raise TypeError('normalize and channels_first must be booleans')
        if format is not None and str(format).lower() not in ('wav', 'wave'):
            raise ValueError('A WAV path cannot be decoded with a conflicting format hint')
        # torchaudio 2.9+ documents normalize/backend/buffer_size as compatibility
        # arguments and always returns float32. Do not silently claim old integer semantics.
        version = re.match(r'^(\d+)\.(\d+)', str(getattr(torchaudio, '__version__', '')))
        if not normalize and (not version or tuple(map(int, version.groups())) < (2, 9)):
            raise NotImplementedError('normalize=False integer semantics before torchaudio 2.9 are not part of this FORGE profile')
        source = os.fspath(uri) if isinstance(uri, (str, bytes, os.PathLike)) else uri
        if isinstance(source, (str, bytes)):
            source = os.fsdecode(source)
        # SoundFile handles frames/channel layout without materializing the entire
        # recording for a bounded read. Preserve the caller-owned file object.
        with sf.SoundFile(source, mode='r') as audio:
            if not audio.format.startswith('WAV'):
                raise ValueError('The WAV compatibility path requires an actual WAV container')
            if frame_offset > len(audio):
                raise ValueError('frame_offset exceeds the WAV frame count')
            audio.seek(frame_offset)
            data = audio.read(frames=num_frames, dtype='float32', always_2d=True)
            sr = int(audio.samplerate)
        array = data.T.copy() if channels_first else data.copy()
        return torch.from_numpy(array), sr

    def load(uri, *args, **kwargs):
        if _wav_request(uri, kwargs.get('format')):
            return read_wav(uri, *args, **kwargs)
        return original(uri, *args, **kwargs)

    load._forge_wav_profile = PROFILE
    load._forge_original_load = original
    load.__name__ = 'forge_soundfile_wav_load'
    torchaudio.load = load
    return load


def write_wav(path, samples, sample_rate):
    """Write finite inference samples to actual PCM16 WAV without torchaudio.save.

    XTTS returns a one-dimensional waveform. A 2-D channels-first tensor is also
    accepted explicitly. No silent transposition guessing or automatic resampling.
    """
    import numpy as np
    import soundfile as sf
    if isinstance(sample_rate, bool) or not isinstance(sample_rate, int) or sample_rate <= 0:
        raise ValueError('sample_rate must be a positive integer')
    if hasattr(samples, 'detach'):
        samples = samples.detach().cpu().numpy()
    data = np.asarray(samples, dtype=np.float32)
    if data.ndim == 2:
        data = data.T
    elif data.ndim != 1:
        raise ValueError('Waveform must be samples or channels-by-samples')
    if not data.size or not np.isfinite(data).all():
        raise ValueError('Waveform must be non-empty and finite')
    if np.abs(data).max() > 1:
        raise ValueError('Waveform exceeds [-1, 1]; no silent clipping of invalid inference output')
    sf.write(os.fspath(path), data, sample_rate, format='WAV', subtype='PCM_16')
    return os.fspath(path)
