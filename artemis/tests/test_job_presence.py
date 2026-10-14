"""Canonical work survives transient audio. PCM/STT here are labelled fixtures.

These are runtime/transport/correction contracts, NOT mic, synthesis quality,
Silero/Parakeet/Qwen latency, physical GPU or meaningful-answer-audio benchmarks.
"""
import asyncio
import base64
import copy
import json
import threading
import time

from fastapi.testclient import TestClient
from artemis_app.api import create_app
from artemis_app.speech import RealtimeSession
from tests.test_integration import FixtureProvider, call, unlock, wait, approve


class SocketFixture:
    def __init__(self):
        self.sent = []
        self.closed = False

    async def send_json(self, message):
        self.sent.append(copy.deepcopy(message))

    async def close(self):
        self.closed = True


async def until(condition, timeout=3):
    async with asyncio.timeout(timeout):
        while not condition():
            await asyncio.sleep(.01)


async def fixture_pcm(text):
    # Deliberately silent PCM; transport assertions, never actual TTS proof.
    await asyncio.sleep(.01)
    return {'pcm16': base64.b64encode(b'\0\0' * 2000).decode(), 'sample_rate': 16000,
            'quality': 'SILENT_TEST_PCM_NOT_TTS', 'samples': 2000}


def test_audio_yield_preserves_approval_and_holds_verified_result(tmp_path):
    async def exercise():
        fake = FixtureProvider([{'tool_calls': [call('write_file', {'path': 'result.txt', 'content': 'actual approved artifact'})]},
                                {'content': 'The approved artifact was written.'}])
        app = create_app(tmp_path, 'test-operator-key', fake)
        runtime = app.state.runtime
        service = runtime.extensions.speech
        service.synthesize = fixture_pcm
        thread = app.state.store.new_thread()['id']
        socket = SocketFixture()
        session = RealtimeSession(service, socket, thread)
        session.watcher = asyncio.create_task(session.watch_committed_replies())
        try:
            await session.begin_text('Create a local artifact')
            rid = session.run_id
            await until(lambda: app.state.store.run(rid)['status'] == 'awaiting_approval')
            approval = app.state.store.approvals()[0]
            await session.interrupt()  # EXACT production method used by VAD/response.cancel.
            assert session.run_id == rid
            assert app.state.store.run(rid)['status'] == 'awaiting_approval'
            assert app.state.store.approval(approval['id'])['status'] == 'pending'
            await runtime.decide(approval['id'], True, approval['digest'])
            await until(lambda: app.state.store.run(rid)['status'] == 'succeeded')
            assert (app.state.tools.ws.root / 'result.txt').read_text() == 'actual approved artifact'
            await asyncio.sleep(.1)
            assert not any(m['type'] == 'response.output_audio.delta' for m in socket.sent)
            assert not any(m['type'] == 'response.done' and m['response']['status'] == 'completed' for m in socket.sent)
            await session.resume_audio()
            await until(lambda: any(m['type'] == 'response.done' and m['response']['status'] == 'completed' for m in socket.sent))
            assert [m['role'] for m in app.state.store.messages(thread)] == ['user', 'assistant']
            assert len(app.state.store.runs()) == 1
            assert any(m['type'] == 'artemis.audio.yielded' and m['work_continues'] for m in socket.sent)
        finally:
            await session.close()
            await runtime.extensions.close()
            await runtime.shutdown()
            app.state.store.close()
    asyncio.run(exercise())


def test_no_playback_over_capture_or_transcription_and_stale_pcm_discarded(tmp_path):
    async def exercise():
        app = create_app(tmp_path, 'test-operator-key')
        service = app.state.runtime.extensions.speech
        socket = SocketFixture()
        thread = app.state.store.new_thread()['id']
        session = RealtimeSession(service, socket, thread)
        started = asyncio.Event()
        release = asyncio.Event()

        async def slow_pcm(text):
            started.set()
            try:
                await release.wait()
            except asyncio.CancelledError:
                # A configured engine may finish even after cancellation: epoch still wins.
                await release.wait()
            return await fixture_pcm(text)
        service.synthesize = slow_pcm
        session.watcher = asyncio.create_task(session.watch_committed_replies())
        try:
            session.speaking = True
            session.playback_held = True
            message = app.state.store.message(thread, 'assistant', 'A saved verified reply.', {'run_id': 'synthetic_finished_reference'})
            await asyncio.sleep(.1)
            assert not socket.sent and message['id'] not in session.seen
            session.speaking = False
            session.transcribing = True
            await session.resume_audio()
            assert session.playback_held
            session.transcribing = False
            await session.resume_audio()
            await started.wait()
            old = session.task
            await session.interrupt()
            release.set()
            await old
            assert not any(m['type'] == 'response.output_audio.delta' for m in socket.sent)
        finally:
            await session.close()
            await app.state.runtime.extensions.close()
            await app.state.runtime.shutdown()
            app.state.store.close()
    asyncio.run(exercise())


def configure_fixture_voice(app, client):
    # Configure a loopback adapter, then replace TTS with a SILENT transport fixture.
    # No request ever reaches this dummy URL and no model asset is downloaded.
    r = client.put('/api/speech', json={'stt_backend': 'http', 'tts_backend': 'http',
                                      'stt_url': 'http://127.0.0.1:9999/stt', 'tts_url': 'http://127.0.0.1:9999/tts'})
    assert r.status_code == 200
    app.state.runtime.extensions.speech.synthesize = fixture_pcm


def receive_type(ws, typ, limit=30):
    for _ in range(limit):
        message = ws.receive_json()
        if message['type'] == typ:
            return message
    raise AssertionError('Expected event ' + typ)


def test_real_websocket_disconnect_reconnect_yield_and_explicit_cancel(tmp_path):
    provider = FixtureProvider([{'tool_calls': [call('write_file', {'path': 'never-written.txt', 'content': 'not yet approved'})]}])
    app = create_app(tmp_path, 'test-operator-key', provider)
    with TestClient(app) as c:
        unlock(c)
        configure_fixture_voice(app, c)
        thread = c.post('/api/threads', json={}).json()['id']
        other = c.post('/api/threads', json={}).json()['id']
        grant = c.post('/api/speech/session', json={'thread_id': thread}).json()
        with c.websocket_connect(grant['path']) as ws:
            assert ws.receive_json()['type'] == 'session.created'
            ws.send_json({'type': 'conversation.item.create', 'item': {'role': 'user', 'content': [{'type': 'input_text', 'text': 'Create an artifact'}]}})
            ws.send_json({'type': 'response.create'})
            created = receive_type(ws, 'response.created')
            rid = created['response']['run_id']
            wait(c, rid, 'awaiting_approval')
            ws.send_json({'type': 'response.cancel'})
            yielded = receive_type(ws, 'artemis.audio.yielded')
            assert yielded['run_id'] == rid and yielded['work_continues']
        assert c.get('/api/runs/' + rid).json()['status'] == 'awaiting_approval'
        assert len(c.get('/api/state').json()['approvals']) == 1
        other_grant = c.post('/api/speech/session', json={'thread_id': other}).json()
        with c.websocket_connect(other_grant['path']) as ws:
            ws.receive_json()
            ws.send_json({'type': 'artemis.job.cancel', 'run_id': rid})
            assert 'another thread' in receive_type(ws, 'error')['error']['message']
        reconnect = c.post('/api/speech/session', json={'thread_id': thread}).json()
        with c.websocket_connect(reconnect['path']) as ws:
            hello = ws.receive_json()
            assert hello['session']['artemis']['run_id'] == rid
            ws.send_json({'type': 'artemis.job.cancel', 'run_id': rid})
            assert receive_type(ws, 'artemis.job.cancelled')['run_id'] == rid
        assert c.get('/api/runs/' + rid).json()['status'] == 'cancelled'
        assert not c.get('/api/state').json()['approvals']
        assert not (app.state.tools.ws.root / 'never-written.txt').exists()


def test_correction_discards_inflight_stale_model_calls_without_replay(tmp_path):
    class SlowFirst(FixtureProvider):
        def __init__(self):
            super().__init__([{'tool_calls': [call('write_file', {'path': 'stale.txt', 'content': 'must never run'})]},
                              {'tool_calls': [call('write_file', {'path': 'correct.txt', 'content': 'new instruction'})]},
                              {'content': 'The corrected artifact is ready.'}])
            self.started = threading.Event()

        async def chat(self, messages, schemas, *, config=None):
            if not self.started.is_set():
                self.started.set()
                await asyncio.sleep(.25)
            return await super().chat(messages, schemas, config=config)
    fake = SlowFirst()
    app = create_app(tmp_path, 'test-operator-key', fake)
    with TestClient(app) as c:
        unlock(c)
        thread = c.post('/api/threads', json={}).json()['id']
        rid = c.post('/api/chat', json={'thread_id': thread, 'text': 'Create a file'}).json()['run_id']
        assert fake.started.wait(2)
        correction = c.post('/api/runs/' + rid + '/correct', json={'text': 'Actually use correct.txt, not stale.txt'})
        assert correction.status_code == 200 and correction.json()['revision'] == 1
        wait(c, rid, 'awaiting_approval')
        a = c.get('/api/state').json()['approvals'][0]
        assert a['args']['path'] == 'correct.txt'
        approve(c, a)
        assert wait(c, rid)['result']['reply'] == 'The corrected artifact is ready.'
        assert not (app.state.tools.ws.root / 'stale.txt').exists()
        assert (app.state.tools.ws.root / 'correct.txt').read_text() == 'new instruction'
        messages = c.get('/api/threads/' + thread + '/messages').json()['messages']
        assert [m['role'] for m in messages] == ['user', 'user', 'assistant']
        assert messages[1]['meta']['correction_for'] == rid and messages[-1]['meta']['revision'] == 1
        assert len(app.state.store.runs()) == 1
        assert any('Stale model response discarded' in e['content'] for e in c.get('/api/events').json()['events'])
        assert c.post('/api/runs/' + rid + '/correct', json={'text': 'too late'}).status_code == 400


def test_correction_supersedes_pending_batch_approval_and_keeps_same_history(tmp_path):
    fake = FixtureProvider([{'tool_calls': [call('write_file', {'path': 'old-a.txt', 'content': 'old'}),
                                          call('write_file', {'path': 'old-b.txt', 'content': 'old'})]},
                            {'content': 'No file changes were made after the correction.'}])
    app = create_app(tmp_path, 'test-operator-key', fake)
    with TestClient(app) as c:
        unlock(c)
        thread = c.post('/api/threads', json={}).json()['id']
        rid = c.post('/api/chat', json={'thread_id': thread, 'text': 'Write two files'}).json()['run_id']
        wait(c, rid, 'awaiting_approval')
        old = c.get('/api/state').json()['approvals'][0]
        r = c.post('/api/runs/' + rid + '/correct', json={'text': 'Do not write any files; just explain'})
        assert r.status_code == 200 and r.json()['superseded_approvals'] == 1
        assert wait(c, rid)
        assert approve(c, old).status_code == 400
        assert not [f for f in app.state.tools.inventory() if not f['is_dir']]
        results = [json.loads(m['content']) for m in app.state.store.run(rid)['state']['messages'] if m['role'] == 'tool']
        assert len(results) == 2 and all(r['blocked'] for r in results)
        assert app.state.store.approval(old['id'])['status'] == 'superseded'


def test_busy_voice_followup_is_held_not_a_second_chat_loop(tmp_path):
    async def exercise():
        provider = FixtureProvider([{'tool_calls': [call('write_file', {'path': 'a.txt', 'content': 'pending'})]}])
        app = create_app(tmp_path, 'test-operator-key', provider)
        thread = app.state.store.new_thread()['id']
        session = RealtimeSession(app.state.runtime.extensions.speech, SocketFixture(), thread)
        try:
            await session.begin_text('Start this job')
            rid = session.run_id
            await until(lambda: app.state.store.run(rid)['status'] == 'awaiting_approval')
            await session.begin_text('An unrelated question while you are busy')
            held = next(m for m in session.ws.sent if m['type'] == 'artemis.job.active')
            assert held['run_id'] == rid and 'unavailable' in held['parallel_answer']
            assert len(app.state.store.runs()) == 1 and len(provider.requests) == 1
            messages = app.state.store.messages(thread)
            assert messages[-1]['meta']['held_input_for'] == rid
            assert session.playback_held
            assert app.state.store.run(rid)['status'] == 'awaiting_approval'
        finally:
            await session.close()
            await app.state.runtime.extensions.close()
            await app.state.runtime.shutdown()
            app.state.store.close()
    asyncio.run(exercise())


def test_new_turn_suppresses_older_held_reply_without_replaying_work(tmp_path):
    """Silent PCM only: automatic playback belongs to the current explicit turn."""
    async def exercise():
        old_text = 'The earlier completed result stays saved.'
        new_text = 'This is the answer to the new question.'
        provider = FixtureProvider([{'content': old_text}, {'content': new_text}])
        app = create_app(tmp_path, 'test-operator-key', provider)
        service = app.state.runtime.extensions.speech
        synthesized = []

        async def tracked_silent_pcm(text):
            synthesized.append(text)
            return await fixture_pcm(text)

        service.synthesize = tracked_silent_pcm
        thread = app.state.store.new_thread()['id']
        socket = SocketFixture()
        session = RealtimeSession(service, socket, thread)
        session.watcher = asyncio.create_task(session.watch_committed_replies())
        try:
            await session.begin_text('First question')
            old_run = session.run_id
            await session.interrupt()
            await until(lambda: app.state.store.run(old_run)['status'] == 'succeeded')
            old_message = app.state.store.messages(thread)[-1]
            await asyncio.sleep(.1)
            assert session.playback_held and old_message['id'] not in session.seen
            assert not synthesized

            await session.begin_text('A new, separate question')
            new_run = session.run_id
            assert new_run != old_run and old_message['id'] in session.seen
            await until(lambda: any(m['type'] == 'response.done' and
                                   m['response']['status'] == 'completed' for m in socket.sent))
            await asyncio.sleep(.1)
            assert synthesized == [new_text]
            transcripts = [m['transcript'] for m in socket.sent
                           if m['type'] == 'response.output_audio_transcript.done']
            assert transcripts == [new_text]
            assert len(provider.requests) == 2 and len(app.state.store.runs()) == 2
            messages = app.state.store.messages(thread)
            assert [m['role'] for m in messages] == ['user', 'assistant', 'user', 'assistant']
            assert messages[1]['meta']['run_id'] == old_run
            assert messages[3]['meta']['run_id'] == new_run
            assert app.state.store.run(old_run)['status'] == 'succeeded'

            # Explicit read-aloud of persisted older text is still available.
            await session.begin_speech(old_message['content'], old_message['id'], old_run)
            await until(lambda: len([m for m in socket.sent if m['type'] ==
                                    'response.output_audio_transcript.done']) == 2)
            assert synthesized == [new_text, old_text]
            assert len(provider.requests) == 2  # No model/tools/effects replayed.
        finally:
            await session.close()
            await app.state.runtime.extensions.close()
            await app.state.runtime.shutdown()
            app.state.store.close()
    asyncio.run(exercise())
