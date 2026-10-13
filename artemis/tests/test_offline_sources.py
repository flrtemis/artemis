"""Offline engine admission and provenance checks; no private machine evidence."""
import copy
import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient
from artemis_app.api import create_app
from artemis_app.offline import local_endpoint
from scripts.verify_sources import verify
from tests.test_integration import unlock


def test_offline_blocks_public_provider_and_audio_but_admits_explicit_fixed_wsl_ip(tmp_path, monkeypatch):
    monkeypatch.setenv('ARTEMIS_OFFLINE', '1')
    app = create_app(tmp_path, 'test-operator-key')
    with TestClient(app) as c:
        unlock(c)
        assert c.get('/healthz').json()['offline']
        for url in ['https://example.com', 'http://8.8.8.8', 'http://provider.internal']:
            assert c.put('/api/provider', json={'base_url': url, 'model': '', 'allow_remote_context': True}).status_code == 400
            assert c.put('/api/speech', json={'tts_backend': 'http', 'tts_url': url + '/tts', 'allow_remote_audio': True}).status_code == 400
        # A private fixed IP is local-configured, but still requires explicit context consent.
        assert c.put('/api/provider', json={'base_url': 'http://192.168.4.20:11434', 'model': '', 'allow_remote_context': False}).status_code == 400
        # Do NOT actually connect to some invented local IP; endpoint policy is pure.
        assert local_endpoint('http://192.168.4.20:11434')
        assert local_endpoint('http://172.20.1.2:11434')
        assert local_endpoint('http://127.0.0.1:11434')
        assert not local_endpoint('http://172.1.1.2:11434')
        assert not local_endpoint('https://models.example')
        assert not c.get('/api/state').json()['provider']['model']
        assert not app.state.runtime.extensions.autonomy.config()['enabled']
        assert app.state.runtime.extensions.generated.sandbox.available()['network'] == 'none'


def test_existing_remote_config_is_unready_when_offline_without_http_request(tmp_path, monkeypatch):
    monkeypatch.setenv('ARTEMIS_OFFLINE', '1')
    app = create_app(tmp_path, 'test-operator-key')
    app.state.store.setting('provider', {'base_url': 'https://example.com', 'model': 'not-a-real-installed-model', 'allow_remote_context': True})
    app.state.store.setting('speech', {**app.state.runtime.extensions.speech.config(), 'tts_backend': 'http', 'tts_url': 'https://example.com/tts', 'allow_remote_audio': True})
    with TestClient(app) as c:
        unlock(c)
        health = c.get('/api/provider/health').json()
        assert not health['connected'] and 'Offline mode' in health['error']
        assert not app.state.runtime.extensions.speech.status()['tts_ready']


def test_retained_source_blobs_and_explicit_lfs_payload_verification():
    root = Path(__file__).resolve().parents[1]
    result = verify(root)
    assert result['total'] == 507 and not result['failures']
    assert result['byte_identical_blobs'] + result['lfs_pointers_with_verified_runtime_payloads'] == 507


def test_lfs_pointer_never_bypasses_pinned_payload_or_size(tmp_path):
    payload = b'non-personal binary fixture'
    sha = hashlib.sha256(payload).hexdigest()
    path = 'vendor_sources/gemma_avatar/public/avatars/brunette.glb'
    pointer = tmp_path / path
    pointer.parent.mkdir(parents=True)
    pointer.write_text(f'version https://git-lfs.github.com/spec/v1\noid sha256:{sha}\nsize {len(payload)}\n')
    (tmp_path / 'SOURCE_MAP.json').write_text(json.dumps({'files': [{'bundled_path': path, 'sha256': sha, 'bytes': len(payload)}]}))
    assert verify(tmp_path)['failures']  # Pointer alone is never sufficient.
    runtime = tmp_path / 'web/avatars/brunette.glb'
    runtime.parent.mkdir(parents=True)
    runtime.write_bytes(payload)
    assert not verify(tmp_path)['failures']
    pointer.write_text(f'version https://git-lfs.github.com/spec/v1\noid sha256:{sha}\nsize 1\n')
    assert verify(tmp_path)['failures']
    runtime.write_bytes(b'changed')
    assert verify(tmp_path)['failures']
