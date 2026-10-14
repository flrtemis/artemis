"""Deterministic real Speech-service admission/cleanup gates; fake socket/session transport only.

Tests do not prove physical voice. No durable job is cancelled by disconnect cleanup.
"""
import asyncio
import secrets
import time

from artemis_app.speech import Speech
import artemis_app.speech as speech_module


class Store:
    def thread(self, id):
        return {'id': id}


class Runtime:
    store = Store()


class Socket:
    def __init__(self, accept_gate=None, fail_accept=False):
        self.accept_gate = accept_gate
        self.fail_accept = fail_accept
        self.accepted = asyncio.Event()
        self.serving = asyncio.Event()
        self.stop = asyncio.Event()
        self.cleaning = asyncio.Event()
        self.cleanup_release = asyncio.Event()
        self.closed = []

    async def accept(self):
        self.accepted.set()
        if self.accept_gate:
            await self.accept_gate.wait()
        if self.fail_accept:
            raise RuntimeError('synthetic handshake failure')

    async def close(self, code=1000):
        self.closed.append(code)


class Session:
    def __init__(self, service, socket, thread):
        self.socket = socket
        self.closed = False

    async def serve(self):
        self.socket.serving.set()
        await self.socket.stop.wait()

    async def close(self):
        self.closed = True
        self.socket.cleaning.set()
        await self.socket.cleanup_release.wait()


def ticket(service, thread='thread'):
    id = secrets.token_urlsafe(12)
    service.tickets[id] = {'thread_id': thread, 'expires': time.time() + 30}
    return id


def test_simultaneous_handshake_reserves_one_thread_before_accept_await(tmp_path, monkeypatch):
    monkeypatch.setattr(speech_module, 'RealtimeSession', Session)

    async def scenario():
        service = Speech(Runtime(), tmp_path)
        gate = asyncio.Event()
        first = Socket(gate)
        owner = asyncio.create_task(service.accept(first, ticket(service)))
        await first.accepted.wait()
        assert 'thread' in service.sessions
        second = Socket()
        await service.accept(second, ticket(service))
        assert second.closed == [1008] and not second.accepted.is_set()
        gate.set()
        await first.serving.wait()
        first.stop.set()
        await first.cleaning.wait()
        assert 'thread' not in service.sessions
        first.cleanup_release.set()
        await owner

    asyncio.run(scenario())


def test_slow_old_cleanup_cannot_block_reconnect_or_remove_new_owner(tmp_path, monkeypatch):
    monkeypatch.setattr(speech_module, 'RealtimeSession', Session)

    async def scenario():
        service = Speech(Runtime(), tmp_path)
        old_socket = Socket()
        old = asyncio.create_task(service.accept(old_socket, ticket(service)))
        await old_socket.serving.wait()
        old_socket.stop.set()
        await old_socket.cleaning.wait()
        assert 'thread' not in service.sessions  # old cleanup remains intentionally blocked
        new_socket = Socket()
        new = asyncio.create_task(service.accept(new_socket, ticket(service)))
        await new_socket.serving.wait()
        new_owner = service.sessions['thread']
        old_socket.cleanup_release.set()
        await old
        assert service.sessions['thread'] is new_owner
        new_socket.stop.set()
        new_socket.cleanup_release.set()
        await new
        assert service.sessions == {}

    asyncio.run(scenario())


def test_cancelled_cleanup_and_failed_accept_do_not_leave_ghost_owner(tmp_path, monkeypatch):
    monkeypatch.setattr(speech_module, 'RealtimeSession', Session)

    async def scenario():
        service = Speech(Runtime(), tmp_path)
        socket = Socket()
        running = asyncio.create_task(service.accept(socket, ticket(service)))
        await socket.serving.wait()
        running.cancel()
        await socket.cleaning.wait()
        assert service.sessions == {}
        running.cancel()  # simulate cancellation interrupting the awaited cleanup itself
        try:
            await running
        except asyncio.CancelledError:
            pass
        assert service.sessions == {}
        failed = Socket(fail_accept=True)
        failed.cleanup_release.set()
        try:
            await service.accept(failed, ticket(service))
        except RuntimeError:
            pass
        else:
            raise AssertionError('Handshake should fail')
        assert service.sessions == {}

    asyncio.run(scenario())
