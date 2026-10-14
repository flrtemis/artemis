"""Scripted model decisions; REAL namespace/seccomp test + hot invocation.

No LLM weights, device, GPU, microphone or model-quality proof is implied.
These contracts exercise production Store/Runtime/approval/Execution, not a mock
sandbox, subprocess substitute, second registry owner or renamed API endpoint.
"""
import copy
import json
import os
import threading
import time

import pytest
from fastapi.testclient import TestClient
from artemis_app.api import create_app
from artemis_app.capability_contract import CONTRACT, SOURCE
from tests.test_integration import FixtureProvider, call, unlock, proposal, approve, wait

MEDIAN_CODE = '''def execute(**kwargs):
    values = sorted(kwargs['values'])
    n = len(values)
    median = values[n // 2] if n % 2 else (values[n // 2 - 1] + values[n // 2]) / 2
    return {'median': median, 'count': n}
'''


def median_proposal(**changes):
    return {'name': 'median_values', 'description': 'Compute the median of a bounded list of numbers.',
            'parameters': {'values': {'type': 'array', 'items': {'type': 'number', 'minimum': -1e6, 'maximum': 1e6}, 'minItems': 1, 'maxItems': 128}},
            'required_args': ['values'], 'python_code': MEDIAN_CODE,
            'test_arguments': {'values': [1, 7, 3]}, 'expected_result': {'median': 3, 'count': 3}, **changes}


class HotToolProvider(FixtureProvider):
    """Chooses calls deterministically, but final content uses the REAL tool result."""
    def __init__(self):
        super().__init__([{'tool_calls': [call('create_tool', median_proposal())]},
                          {'tool_calls': [call('median_values', {'values': [12, 3, 9, 6]})]}])

    async def chat(self, messages, schemas, *, config=None):
        if self.responses:
            return await super().chat(messages, schemas, config=config)
        self.requests.append({'messages': copy.deepcopy(messages), 'schemas': copy.deepcopy(schemas), 'config': config})
        output = json.loads(next(m['content'] for m in reversed(messages) if m['role'] == 'tool' and m['name'] == 'median_values'))
        assert output['ok']
        return {'content': f"The median is {output['result']['median']} across {output['result']['count']} values. Scripted test-provider answer using a real isolated result."}


@pytest.fixture
def hot_host(tmp_path):
    app = create_app(tmp_path, 'test-operator-key')
    with TestClient(app) as client:
        unlock(client)
        if not app.state.runtime.extensions.generated.sandbox.available()['available']:
            pytest.skip('REAL Bubblewrap+seccomp / Docker profile is not available; no soft fallback')
        yield app, client


def install(client, arguments=None):
    rid, a = proposal(client, 'create_tool', arguments or median_proposal())
    response = approve(client, a)
    assert response.status_code == 200, response.text
    result = wait(client, rid)['result']
    assert result['registered'] and result['test']['ok'], result
    return result


def test_hot_create_test_register_use_answer_in_one_durable_thread(tmp_path):
    provider = HotToolProvider()
    app = create_app(tmp_path, 'test-operator-key', provider)
    with TestClient(app) as c:
        unlock(c)
        if not app.state.runtime.extensions.generated.sandbox.available()['available']:
            pytest.skip('Real isolation unavailable')
        t = c.post('/api/threads', json={}).json()['id']
        original = 'Find the median of [12, 3, 9, 6]. Create a needed capability if it is missing.'
        rid = c.post('/api/chat', json={'thread_id': t, 'text': original}).json()['run_id']
        wait(c, rid, 'awaiting_approval')
        assert not app.state.tools.registry.get('median_values')
        a = next(x for x in c.get('/api/state').json()['approvals'] if x['run_id'] == rid)
        created = approve(c, a).json()['result']
        assert created['registered'] and created['test']['result'] == {'median': 3, 'count': 3}, created
        assert created['test']['sandbox']['backend'] in ['bubblewrap', 'docker']
        assert app.state.tools.registry.get('median_values')  # SAME host; no restart.
        wait(c, rid, 'awaiting_approval')
        b = next(x for x in c.get('/api/state').json()['approvals'] if x['run_id'] == rid)
        assert b['tool'] == 'median_values'
        used = approve(c, b).json()['result']
        assert used['result'] == {'median': 7.5, 'count': 4}
        assert wait(c, rid)['result']['reply'].startswith('The median is 7.5')
        assert approve(c, b).status_code == 400  # No second action on replay.
        messages = c.get('/api/threads/' + t + '/messages').json()['messages']
        assert [m['role'] for m in messages] == ['user', 'assistant']
        assert messages[0]['content'] == original and {m['meta']['run_id'] for m in messages} == {rid}
        state = app.state.store.run(rid)['state']
        assert [m['name'] for m in state['messages'] if m['role'] == 'tool'] == ['create_tool', 'median_values']
        assert any(s['function']['name'] == 'median_values' for s in provider.requests[1]['schemas'])
        events = c.get('/api/events').json()['events']
        assert {e['meta'].get('phase') for e in events} >= {'staged', 'registered'}
        assert not [f for f in app.state.tools.inventory() if not f['is_dir']]  # No code copied into user's workspace.


@pytest.mark.parametrize('name', ['../escape', '/tmp/tool', 'a/b', 'a\\b', 'BadName', 'x', 'create_tool', 'calculator', 'run_python', 'remember', '__import__'])
def test_invalid_names_and_core_override_rejected_before_staging(hot_host, name):
    app, c = hot_host
    r = c.post('/api/tools/propose', json={'tool': 'create_tool', 'arguments': median_proposal(name=name)})
    assert r.status_code == 400, r.text
    assert not app.state.store.extension_versions() and not c.get('/api/state').json()['approvals']


@pytest.mark.parametrize('changes', [
    {'parameters': {'value': {'type': 'bogus'}}, 'required_args': ['value']},
    {'parameters': {'value': {'$ref': 'https://example.com/schema'}}, 'required_args': ['value']},
    {'parameters': {'value': {'type': 'object', 'additionalProperties': True}}, 'required_args': ['value']},
    {'parameters': {'value': {'type': 'string', 'maxLength': 100000}}, 'required_args': ['value']},
    {'parameters': {'value': {'type': 'array', 'items': {'type': 'number'}, 'maxItems': 10000}}, 'required_args': ['value']},
    {'required_args': ['not_declared']}, {'required_args': ['values', 'values']},
    {'test_arguments': {'values': []}}, {'test_arguments': {'values': [1], 'extra': True}},
    {'python_code': 'this is not valid Python !!'}, {'python_code': 'print("no execute")'},
    {'python_code': 'async def execute(**kwargs):\n    return 1'},
    {'python_code': 'def execute(value):\n    return value'},
    {'provenance': {'repository': 'forged-source'}},
])
def test_schema_code_test_and_provenance_contract_rejection(hot_host, changes):
    app, c = hot_host
    r = c.post('/api/tools/propose', json={'tool': 'create_tool', 'arguments': median_proposal(**changes)})
    assert r.status_code == 400, r.text
    assert not app.state.store.extension_versions()


def test_denied_creation_has_no_stage_no_registration_and_feedback(hot_host):
    app, c = hot_host
    rid, a = proposal(c, 'create_tool', median_proposal())
    assert approve(c, a, False).json()['result']['rejected_by_user']
    assert wait(c, rid, 'failed')['result']['blocked']
    assert not app.state.store.extension_versions() and not app.state.tools.registry.get('median_values')


def test_test_failure_retry_versions_and_approved_rollback(hot_host):
    app, c = hot_host
    rid, a = proposal(c, 'create_tool', median_proposal(expected_result={'median': 100, 'count': 3}))
    failed = approve(c, a).json()['result']
    assert not failed['ok'] and not failed['registered']
    assert failed['test']['result'] == {'median': 3, 'count': 3}
    assert wait(c, rid, 'failed') and not app.state.tools.registry.get('median_values')
    first = install(c)
    assert first['version'] == 2  # Failed stage retained as immutable version 1.
    newer = install(c, median_proposal(python_code="def execute(**kwargs):\n    return {'median': 42, 'count': len(kwargs['values'])}\n",
                                      expected_result={'median': 42, 'count': 3}, replace_version=2))
    assert newer['version'] == 3
    rid, a = proposal(c, 'rollback_tool', {'name': 'median_values', 'version': 2, 'expected_version': 3})
    result = approve(c, a).json()['result']
    assert result['version'] == 2 and not result['replayed_actions']
    rid, a = proposal(c, 'median_values', {'values': [4, 6]})
    assert approve(c, a).json()['result']['result']['median'] == 5
    assert wait(c, rid)
    assert c.post('/api/tools/propose', json={'tool': 'rollback_tool', 'arguments': {'name': 'median_values', 'version': 1, 'expected_version': 2}}).status_code == 400


def test_revision_change_blocks_stale_tool_invocation_approval(hot_host):
    app, c = hot_host
    install(c)
    rid, old_approval = proposal(c, 'median_values', {'values': [4, 8]})
    install(c, median_proposal(replace_version=1))
    result = approve(c, old_approval).json()['result']
    assert not result['ok'] and result['blocked']
    assert wait(c, rid, 'failed')


def test_generated_code_cannot_see_user_files_network_env_or_spawn(hot_host, tmp_path, monkeypatch):
    app, c = hot_host
    secret = tmp_path / 'private-continuity-sentinel'
    secret.write_text('PRIVATE_NEVER_SHARE')
    (app.state.tools.ws.root / 'user-file.txt').write_text('PRIVATE_WORKSPACE_SENTINEL')
    monkeypatch.setenv('ARTEMIS_SECRET_SENTINEL', 'DO_NOT_INHERIT')
    code = f'''def execute(**kwargs):
    import os, socket, subprocess
    checks = {{'private': os.path.exists({str(secret)!r}), 'workspace': os.path.exists('/workspace/user-file.txt'), 'env': 'ARTEMIS_SECRET_SENTINEL' in os.environ}}
    try:
        s = socket.socket()
        s.connect(('127.0.0.1', 8000))
        checks['network'] = True
    except OSError:
        checks['network'] = False
    try:
        subprocess.run(['/usr/bin/true'], check=True)
        checks['spawn'] = True
    except OSError:
        checks['spawn'] = False
    open('discarded.txt', 'w').write('only disposable scratch')
    return checks
'''
    result = install(c, median_proposal(name='scrape_private_test', parameters={}, required_args=[],
                                       python_code=code, test_arguments={},
                                       expected_result={'private': False, 'workspace': False, 'env': False, 'network': False, 'spawn': False}))
    assert result['test']['sandbox']['network'] == 'none'  # 'scrape' never grants network.
    job_id = result['test']['sandbox']['job_id']
    assert c.post('/api/tools/propose', json={'tool': 'promote_execution_changes', 'arguments': {'job_id': job_id}}).status_code == 400
    assert not (app.state.tools.ws.root / 'discarded.txt').exists()


def test_runtime_error_and_nonserializable_result_return_to_owner(hot_host):
    app, c = hot_host
    code = "def execute(**kwargs):\n    if kwargs['values'][0] == 0: raise ValueError('fixture tool failed')\n    return {'median': 3, 'count': 3}\n"
    install(c, median_proposal(python_code=code))
    rid, a = proposal(c, 'median_values', {'values': [0]})
    failed = approve(c, a).json()['result']
    assert not failed['ok'] and 'fixture tool failed' in failed['error']
    assert wait(c, rid, 'failed')
    rid, a = proposal(c, 'create_tool', median_proposal(name='non_json_result', python_code="def execute(**kwargs):\n    return {1,2,3}\n"))
    assert not approve(c, a).json()['result']['registered']
    assert wait(c, rid, 'failed')


def test_cancel_during_test_prevents_late_registration(hot_host):
    app, c = hot_host
    rid, a = proposal(c, 'create_tool', median_proposal(python_code="def execute(**kwargs):\n    import time\n    time.sleep(3)\n    return {'median': 3, 'count': 3}\n"))
    reply = {}
    thread = threading.Thread(target=lambda: reply.update(approve(c, a).json()))
    thread.start()
    for _ in range(200):
        if rid in app.state.runtime.extensions.execution.running:
            break
        time.sleep(.01)
    assert c.post('/api/runs/' + rid + '/cancel').status_code == 200
    thread.join(5)
    assert not thread.is_alive()
    assert c.get('/api/runs/' + rid).json()['status'] == 'cancelled'
    assert not app.state.tools.registry.get('median_values')


def test_namespace_profile_timeout_is_real_and_fails_closed(hot_host):
    app, c = hot_host
    rid, a = proposal(c, 'create_tool', median_proposal(python_code="def execute(**kwargs):\n    import time\n    time.sleep(30)\n    return {'median': 3, 'count': 3}\n"))
    result = approve(c, a).json()['result']
    assert not result['ok'] and 'timeout' in result['error'].lower()
    assert wait(c, rid, 'failed')


def test_persisted_version_reload_export_and_strict_source_boundary(tmp_path):
    app = create_app(tmp_path, 'test-operator-key')
    with TestClient(app) as c:
        unlock(c)
        if not app.state.runtime.extensions.generated.sandbox.available()['available']:
            pytest.skip('Real isolation unavailable')
        install(c)
        app.state.store.add_private('DO_NOT_EXPORT_SAGE')
        export = c.get('/api/extensions/median_values/export')
        assert export.status_code == 200 and 'DO_NOT_EXPORT_SAGE' not in export.text
        assert export.json()['manifest']['provenance']['mechanism'] == SOURCE
        assert export.json()['manifest']['provenance']['license'] == 'LicenseRef-Unspecified'
        assert export.json()['contract'] == CONTRACT
    with TestClient(create_app(tmp_path, 'test-operator-key')) as c:
        assert c.get('/api/extensions').status_code == 401
        assert c.get('/api/extensions/median_values/export').status_code == 401
        unlock(c)
        cap = next(t for t in c.get('/api/state').json()['capabilities'] if t['name'] == 'median_values')
        assert cap['available'] and cap['requires_approval'] and not cap['extension']['permissions']['continuity']
        rid, a = proposal(c, 'median_values', {'values': [2, 6]})
        assert approve(c, a).json()['result']['result']['median'] == 4
        assert wait(c, rid)


def test_missing_real_backend_never_exposes_generated_execution(tmp_path):
    app = create_app(tmp_path, 'test-operator-key')
    execution = app.state.runtime.extensions.execution
    execution._availability = {'available': False, 'backend': None, 'reason': 'Deliberately unavailable test backend'}
    app.state.runtime.extensions.generated.sync_availability()
    with TestClient(app) as c:
        unlock(c)
        assert all(s['function']['name'] != 'create_tool' for s in app.state.tools.schemas())
        assert c.post('/api/tools/propose', json={'tool': 'create_tool', 'arguments': median_proposal()}).status_code == 400
        assert not app.state.store.extension_versions()


def test_kernel_scratch_quota_and_readonly_non_scratch_paths(hot_host):
    app, c = hot_host
    if app.state.runtime.extensions.generated.sandbox.available()['backend'] != 'bubblewrap':
        pytest.skip('Kernel shared scratch/temporary-mount assertions require Bubblewrap')
    code = '''def execute(**kwargs):
    import os
    denied = []
    for path in ['/outside-scratch', '/home/worker/file', '/dev/file']:
        try:
            with open(path, 'w') as f:
                f.write('not allowed')
        except OSError:
            denied.append(path)
    with open('/scratch/allowed', 'w') as f:
        f.write('temporary only')
    with open('/tmp/allowed') as f:
        shared = f.read() == 'temporary only'
    return {'denied': len(denied), 'shared': shared}
'''
    expected = {'denied': 3, 'shared': True}
    rid, a = proposal(c, 'create_tool', median_proposal(python_code=code, expected_result=expected))
    assert approve(c, a).json()['result']['test']['result'] == expected
    assert wait(c, rid)['result']['registered']

    quota_code = '''def execute(**kwargs):
    # Both files are below RLIMIT_FSIZE; their combined, actually allocated
    # pages exceed the one shared 12 MB tmpfs. The kernel, not a poll, refuses.
    for path in ['/scratch/a.bin', '/tmp/b.bin']:
        with open(path, 'wb') as f:
            f.write(b'x' * 6500000)
    return {'unexpected': 'quota evaded'}
'''
    rid, a = proposal(c, 'create_tool', median_proposal(name='scratch_quota_check', python_code=quota_code,
                                                      expected_result={'unexpected': 'quota evaded'}))
    result = approve(c, a).json()['result']
    assert not result['registered'] and not result['test']['ok']
    assert 'No space left on device' in result['test']['error']
    assert wait(c, rid, 'failed')['result']['registered'] is False
    assert not app.state.tools.registry.get('scratch_quota_check')
