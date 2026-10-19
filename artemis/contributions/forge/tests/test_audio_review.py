"""Real libsndfile/NumPy I/O; Torch conversion facade, NOT live Torch/XTTS training.

The same candidate module is exercised with real Torch by verify_forge.py on
Bob's existing environment. No recordings, model weights, network or GPU needed here.
"""
from __future__ import annotations
import importlib.util
import io
from pathlib import Path
import sys
import types

import numpy as np
import pytest
import soundfile as sf

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def compat(monkeypatch):
    calls = []
    def original(*args, **kwargs):
        calls.append((args, kwargs))
        return 'ORIGINAL_NON_WAV_LOADER'
    torch = types.ModuleType('torch')
    torch.from_numpy = lambda array: array  # explicitly a facade: no actual tensor claim
    ta = types.ModuleType('torchaudio')
    ta.load = original
    ta.__version__ = '2.9.0'
    monkeypatch.setitem(sys.modules, 'torch', torch)
    monkeypatch.setitem(sys.modules, 'torchaudio', ta)
    spec = importlib.util.spec_from_file_location('review_audio_compat', ROOT / 'audio_compat.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.install()
    return module, ta, calls


@pytest.mark.parametrize('channels', [1, 2])
@pytest.mark.parametrize('subtype', ['PCM_U8', 'PCM_16', 'PCM_24', 'PCM_32', 'FLOAT'])
def test_real_wav_shapes_values_dtype_rate(compat, tmp_path, channels, subtype):
    _, ta, calls = compat
    samples = np.sin(np.arange(4096, dtype=np.float32) * 0.03) * 0.4
    source = samples[:, None] if channels == 1 else np.stack((samples, -samples), axis=1)
    path = tmp_path / 'sample.WAV'
    sf.write(path, source, 22050, subtype=subtype)
    expected, sr = sf.read(path, dtype='float32', always_2d=True)
    loaded, actual_sr = ta.load(path)
    assert loaded.shape == (channels, 4096) and loaded.dtype == np.float32
    assert loaded.flags.c_contiguous and actual_sr == sr == 22050
    np.testing.assert_array_equal(loaded, expected.T)
    assert calls == []


def test_frame_offset_count_positional_and_channels_last_are_not_silently_ignored(compat, tmp_path):
    _, ta, _ = compat
    path = tmp_path / 'window.wav'
    values = np.stack((np.linspace(-0.5, 0.5, 1000), np.linspace(0.2, -0.2, 1000)), axis=1)
    sf.write(path, values, 44100, subtype='FLOAT')
    result, sr = ta.load(path, 100, 37, channels_first=False)
    assert result.shape == (37, 2) and sr == 44100
    np.testing.assert_allclose(result, values[100:137].astype(np.float32), rtol=0, atol=0)
    empty, _ = ta.load(path, frame_offset=1000, num_frames=0)
    assert empty.shape == (2, 0)


def test_non_wav_dispatch_unchanged_and_install_is_idempotent(compat):
    module, ta, calls = compat
    once = ta.load
    assert module.install() is once and ta.load is once
    assert ta.load('sample.flac', 5, 9, channels_first=False) == 'ORIGINAL_NON_WAV_LOADER'
    assert calls == [(('sample.flac', 5, 9), {'channels_first': False})]


def test_file_like_explicit_wav_preserves_caller_file_object(compat):
    _, ta, _ = compat
    stream = io.BytesIO()
    sf.write(stream, np.ones(400, dtype=np.float32) * 0.1, 16000, format='WAV', subtype='FLOAT')
    stream.seek(0)
    result, sr = ta.load(stream, format='wav', frame_offset=11, num_frames=13)
    assert result.shape == (1, 13) and sr == 16000
    assert not stream.closed


@pytest.mark.parametrize('options', [{'frame_offset': -1}, {'frame_offset': True}, {'num_frames': -2}, {'channels_first': 'no'}, {'normalize': 'yes'}, {'format': 'mp3'}])
def test_invalid_options_fail_explicitly(compat, tmp_path, options):
    _, ta, _ = compat
    p = tmp_path / 'valid.wav'
    sf.write(p, np.ones(64) * 0.2, 22050)
    with pytest.raises((TypeError, ValueError)):
        ta.load(p, **options)


def test_corrupt_mislabeled_and_out_of_range_wav_do_not_fallback_to_codec(compat, tmp_path):
    _, ta, calls = compat
    bad = tmp_path / 'bad.wav'
    bad.write_bytes(b'not an audio container')
    with pytest.raises(Exception):
        ta.load(bad)
    sf.write(bad, np.ones(64) * 0.2, 22050, format='FLAC')
    with pytest.raises(ValueError, match='actual WAV'):
        ta.load(bad)
    sf.write(bad, np.ones(64) * 0.2, 22050, format='WAV')
    with pytest.raises(ValueError, match='exceeds'):
        ta.load(bad, frame_offset=65)
    assert calls == []


def test_legacy_normalize_false_is_not_misrepresented(compat, tmp_path):
    _, ta, _ = compat
    p = tmp_path / 'normal.wav'
    sf.write(p, np.ones(64) * 0.2, 22050)
    assert ta.load(p, normalize=False)[0].dtype == np.float32  # torchaudio>=2.9 contract
    ta.__version__ = '2.8.0'
    with pytest.raises(NotImplementedError, match='integer semantics'):
        ta.load(p, normalize=False)


def test_inference_wav_write_uses_real_soundfile_not_torchaudio_save(compat, tmp_path):
    module, ta, _ = compat
    ta.save = lambda *a, **kw: (_ for _ in ()).throw(RuntimeError('Could not load libtorchcodec'))
    p = tmp_path / 'out.wav'
    data = np.sin(np.arange(2400) * 0.04).astype(np.float32) * 0.4
    assert module.write_wav(p, data, 24000) == str(p)
    actual, sr = sf.read(p, dtype='float32')
    assert sr == 24000 and actual.shape == data.shape and sf.info(p).subtype == 'PCM_16'
    np.testing.assert_allclose(actual, data, rtol=0, atol=1/32768)
    for invalid in [[], [float('nan')], [float('inf')], [1.2]]:
        with pytest.raises(ValueError):
            module.write_wav(p, invalid, 24000)


def test_original_shim_default_works_but_window_request_reproduces_contract_gap(monkeypatch, tmp_path):
    original = Path(__file__).resolve().parents[4] / '.cache/forge-review/source/forge/__init__.py'
    if not original.exists():
        pytest.skip('Original read-only Drive snapshot not cached; candidate contracts still run')
    fake_torch = types.ModuleType('torch')
    fake_torch.from_numpy = lambda data: data
    fake_ta = types.ModuleType('torchaudio')
    fake_ta.load = lambda *a, **kw: (_ for _ in ()).throw(RuntimeError('Could not load libtorchcodec'))
    monkeypatch.setitem(sys.modules, 'torch', fake_torch)
    monkeypatch.setitem(sys.modules, 'torchaudio', fake_ta)
    spec = importlib.util.spec_from_file_location('original_forge_audio_shim', original)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    p = tmp_path / 'original.wav'
    sf.write(p, np.ones(100) * 0.1, 22050)
    loaded, _ = fake_ta.load(p)
    assert loaded.shape == (1, 100)  # original default use really decodes WAV via soundfile
    window, _ = fake_ta.load(p, frame_offset=10, num_frames=20, channels_first=False)
    assert window.shape == (1, 100)  # proves original ignores all these arguments
