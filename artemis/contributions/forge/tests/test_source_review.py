"""Tests against reviewed cached FORGE candidate modules, no Torch/XTTS/model/GPU claim.

Governance uses scripted percentages (not Windows native sampling); export uses
real files/ZIP relocation plus a controlled XTTS load stub (not inference quality).
"""
import ast
from datetime import datetime
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import threading
import types
import zipfile

import pytest

ROOT = Path(__file__).resolve().parents[4]
CANDIDATE = ROOT / '.cache/forge-review/candidate'


def source(path):
    p = CANDIDATE / path
    if not p.is_file():
        pytest.skip('Reviewed Drive snapshot/candidate is not cached; fetch/pin source before source-specific contracts')
    return p


def guard_class():
    tree = ast.parse(source('forge/train.py').read_text())
    node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == '_ResourceGuard')
    namespace = {'threading': threading, 'gc': types.SimpleNamespace(collect=lambda: None),
                 'json': json, 'datetime': datetime, 'sys': types.SimpleNamespace(stdout=types.SimpleNamespace(flush=lambda: None)),
                 'GUARD_EXIT_CODE': 42}
    exec(compile(ast.Module(body=[node], type_ignores=[]), '<reviewed-guard-class>', 'exec'), namespace)
    return namespace['_ResourceGuard'], namespace


class Event:
    def __init__(self, count):
        self.count = count
    def wait(self, interval):
        self.count -= 1
        return self.count < 0
    def set(self):
        self.count = -1


def test_guard_two_critical_readings_exits_42_and_never_claims_checkpoint_safe(tmp_path):
    cls, ns = guard_class()
    logs, exits = [], []
    ns['_ram_percent'] = lambda: 93
    ns['_ram_gb'] = lambda: 'fixture 93%'
    ns['os'] = types.SimpleNamespace(_exit=lambda code: exits.append(code))
    guard = cls(logs.append, tmp_path / 'guard.json', interval=0)
    guard._stop_event = Event(2)
    guard._tidy = lambda: None
    guard.run()
    assert exits == [42]
    assert json.loads((tmp_path / 'guard.json').read_text())['outcome'] == 'guard_stop'
    assert not any('checkpoint is safe' in line.lower() for line in logs)
    assert any('incomplete' in line.lower() for line in logs)


def test_guard_reset_and_unreadable_samples_do_not_fake_native_enforcement(tmp_path):
    cls, ns = guard_class()
    values = iter([93, 70, 93, None, 70])
    exits = []
    ns['_ram_percent'] = lambda: next(values)
    ns['_ram_gb'] = lambda: 'scripted fixture'
    ns['os'] = types.SimpleNamespace(_exit=lambda code: exits.append(code))
    guard = cls(lambda _: None, tmp_path / 'guard.json', interval=0)
    guard._stop_event = Event(5)
    guard._tidy = lambda: None
    guard._vram = lambda: 'not measured'
    guard.run()
    assert exits == [] and not (tmp_path / 'guard.json').exists()


def test_training_gate_is_before_model_and_downloads_and_offline_cache_gate_exists():
    s = source('forge/train.py').read_text()
    function = ast.parse(s)
    train = next(n for n in function.body if isinstance(n, ast.FunctionDef) and n.name == 'train_voice')
    body = ast.get_source_segment(s, train)
    assert body.index('ram_start = _ram_percent()') < body.index('ModelManager._download_model_files')
    assert body.index('ram_start = _ram_percent()') < body.index('GPTTrainer.init_from_config')
    assert 'missing and not allow_download' in body
    assert 'base_model_dir=None, allow_download=True' in body
    assert '"checkpoint": best,' in body
    assert 'else exp_path' not in body


def test_real_package_relocation_uses_relative_paths_and_never_calls_codec_save(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, 'torch', types.ModuleType('torch'))
    package = types.ModuleType('reviewed_forge')
    package.__path__ = [str(source('forge/synth.py').parent)]
    monkeypatch.setitem(sys.modules, 'reviewed_forge', package)
    spec = importlib.util.spec_from_file_location('reviewed_forge.synth', source('forge/synth.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    base = tmp_path / 'input'
    base.mkdir()
    for name in ['checkpoint.pth', 'config.json', 'vocab.json', 'reference.wav']:
        (base / name).write_bytes(b'synthetic package contract, not a model or recording')
    voice, archive = module.export_voice('case', base / 'checkpoint.pth', base / 'config.json', base / 'vocab.json', base / 'reference.wav', tmp_path / 'voices')
    manifest = json.loads((Path(voice) / 'voice.json').read_text())
    assert all(not Path(manifest[k]).is_absolute() for k in ['checkpoint', 'config', 'vocab', 'speaker_ref'])
    moved = tmp_path / 'moved'
    with zipfile.ZipFile(archive) as z:
        assert not any(n.startswith('/') or '..' in Path(n).parts for n in z.namelist())
        z.extractall(moved)
    shutil.rmtree(tmp_path / 'voices')  # relocation must not depend on the old location
    for key in ['checkpoint', 'config', 'vocab', 'speaker_ref']:
        assert (moved / 'case' / manifest[key]).is_file()
    assert 'torchaudio.save' not in source('forge/synth.py').read_text()
    assert 'write_wav(out_wav' in source('forge/synth.py').read_text()


def test_manifest_counts_only_original_source_not_generated_bytecode():
    manifest = json.loads((Path(__file__).resolve().parents[1] / 'source-manifest.json').read_text())
    assert manifest['count'] == len(manifest['source_files']) == 17
    assert not any('__pycache__' in f['path'] or f['path'].endswith('.pyc') for f in manifest['source_files'])
