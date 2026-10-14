"""JSON-only extension profile of ARTEMIS's canonical Execution owner.

Real namespaces + seccomp (or a constrained Docker container), not AST/regex
pretending to be isolation. No user workspace, continuity, tokens, host home,
network or promotion path is mounted. Generated code has only read-only runtime
files and a disposable scratch directory. Test and invocation use the SAME
profile. This is defense in depth, not a kernel security certification.
"""
from __future__ import annotations

import ctypes
import errno
import json
import os
import resource
import subprocess
import tempfile
import time
from pathlib import Path

from .store import dump, uid

LIMITS = {'wall_seconds': 5, 'cpu_seconds': 4, 'memory_bytes': 256_000_000,
          'output_bytes': 80_000, 'scratch_bytes': 12_000_000, 'processes': 1}
# v1 is stdlib computation, not a subprocess/network/plugin installer.
DENIED_SYSCALLS = ('clone', 'clone3', 'fork', 'vfork', 'socket', 'socketpair',
                  'unshare', 'setns', 'mount', 'umount2', 'ptrace',
                  'process_vm_readv', 'process_vm_writev', 'pidfd_getfd',
                  'bpf', 'perf_event_open', 'keyctl', 'add_key', 'request_key',
                  'open_by_handle_at', 'io_uring_setup', 'reboot',
                  'kexec_load', 'kexec_file_load')


class ExtensionSandbox:
    def __init__(self, execution):
        self.execution = execution
        self.worker = Path(__file__).with_name('extension_worker.py')
        self.seccomp = None
        self.seccomp_error = None
        self._probe = None
        try:
            lib = ctypes.CDLL('libseccomp.so.2', use_errno=True)
            lib.seccomp_init.argtypes = [ctypes.c_uint32]
            lib.seccomp_init.restype = ctypes.c_void_p
            lib.seccomp_release.argtypes = [ctypes.c_void_p]
            lib.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
            lib.seccomp_syscall_resolve_name.restype = ctypes.c_int
            lib.seccomp_rule_add.argtypes = [ctypes.c_void_p, ctypes.c_uint32,
                                             ctypes.c_int, ctypes.c_uint]
            lib.seccomp_rule_add.restype = ctypes.c_int
            lib.seccomp_export_bpf.argtypes = [ctypes.c_void_p, ctypes.c_int]
            lib.seccomp_export_bpf.restype = ctypes.c_int
            self.seccomp = lib
            # Probe compilation, not merely library presence.
            with tempfile.TemporaryFile() as f:
                self.write_filter(f)
        except (OSError, RuntimeError) as e:
            self.seccomp = None
            self.seccomp_error = str(e)

    def write_filter(self, file):
        ctx = self.seccomp.seccomp_init(0x7fff0000)  # SCMP_ACT_ALLOW
        if not ctx:
            raise RuntimeError('Cannot initialize seccomp')
        try:
            for name in DENIED_SYSCALLS:
                nr = self.seccomp.seccomp_syscall_resolve_name(name.encode())
                if nr == -1:
                    continue  # Syscall does not exist on this architecture.
                if self.seccomp.seccomp_rule_add(ctx, 0x00050000 | errno.EPERM, nr, 0) < 0:
                    raise RuntimeError('Cannot constrain syscall: ' + name)
            if self.seccomp.seccomp_export_bpf(ctx, file.fileno()) < 0:
                raise RuntimeError('Cannot export seccomp filter')
            file.seek(0)
        finally:
            self.seccomp.seccomp_release(ctx)

    def base_bwrap(self):
        # Keep the canonical namespace owner, but tighten its filesystem for v1.
        # Root, /dev and /proc are read-only. /tmp is an alias of the one sized
        # scratch tmpfs: code cannot evade a host-side scan through another path.
        cmd = self.execution.base_bwrap()
        try:
            at = cmd.index('--tmpfs')
        except ValueError as e:
            raise RuntimeError('Canonical sandbox temporary mount contract changed') from e
        if cmd[at:at + 2] != ['--tmpfs', '/tmp']:
            raise RuntimeError('Canonical sandbox temporary mount contract changed')
        cmd[at:at + 2] = ['--symlink', '/scratch', '/tmp']
        return cmd + ['--unshare-user', '--cap-drop', 'ALL', '--dir', '/extension',
                      '--size', str(LIMITS['scratch_bytes']), '--tmpfs', '/scratch',
                      '--remount-ro', '/dev', '--remount-ro', '/proc', '--remount-ro', '/']

    def available(self):
        state = dict(self.execution.available())
        if state['available'] and state['backend'] == 'bubblewrap' and not self.seccomp:
            state.update(available=False, reason='Generated tools require libseccomp.so.2: ' + str(self.seccomp_error))
        if state['available'] and state['backend'] == 'docker':
            try:
                r = subprocess.run(['docker', 'image', 'inspect', 'artemis-worker:local'],
                                   capture_output=True, timeout=5)
                if r.returncode:
                    state.update(available=False, reason='Build the local artemis-worker:local image first; no automatic pull.')
            except (OSError, subprocess.TimeoutExpired):
                state.update(available=False, reason='Local execution image could not be inspected')
        if state['available'] and state['backend']=='bubblewrap':
            if self._probe is None:
                try:
                    with tempfile.TemporaryFile() as f:
                        self.write_filter(f)
                        cmd=self.base_bwrap()+['--seccomp',str(f.fileno()),'/usr/bin/python3','-I','-S','-c','print("artemis-extension-probe")']
                        r=subprocess.run(cmd,pass_fds=(f.fileno(),),capture_output=True,timeout=5,preexec_fn=self.limits)
                    self._probe=(r.returncode==0 and r.stdout.strip()==b'artemis-extension-probe',r.stderr.decode(errors='replace')[:200])
                except (OSError,RuntimeError,subprocess.TimeoutExpired) as e:self._probe=(False,str(e))
            if not self._probe[0]:state.update(available=False,reason='JSON-only sandbox probe failed: '+self._probe[1])
        state['profile'] = 'json-only-v1'
        state['limits'] = dict(LIMITS)
        state['network'] = 'none'
        state['user_files'] = 'none'
        state['scratch_enforcement'] = 'kernel-sized private tmpfs; no host scratch bind'
        return state

    @staticmethod
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU, (4, 5))
        resource.setrlimit(resource.RLIMIT_AS, (LIMITS['memory_bytes'],) * 2)
        resource.setrlimit(resource.RLIMIT_FSIZE, (LIMITS['scratch_bytes'],) * 2)
        resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        # seccomp denies process creation; this is an additional bound.
        resource.setrlimit(resource.RLIMIT_NPROC, (256, 256))

    def cancelled(self, producer):
        try:
            return self.execution.tools.store.run(producer)['status'] in ('cancelled', 'interrupted')
        except KeyError:
            return False

    def execute(self, code, arguments, producer):
        state = self.available()
        if not state['available']:
            return {'ok': False, 'blocked': True, 'error': state.get('reason', 'Isolation unavailable')}
        if self.cancelled(producer):
            return {'ok': False, 'blocked': True, 'error': 'Run cancelled before extension execution'}
        job_id = uid()
        job = self.execution.root / job_id
        bundle, scratch = job / 'extension', job / 'scratch'
        bundle.mkdir(parents=True)
        scratch.mkdir()
        (bundle / 'tool.py').write_text(code, encoding='utf-8')
        (bundle / 'request.json').write_text(dump(arguments), encoding='utf-8')
        (bundle / 'worker.py').write_bytes(self.worker.read_bytes())
        metadata = {'producer': producer, 'profile': 'json-only-v1', 'status': 'running'}
        (job / 'meta.json').write_text(dump(metadata))
        # Deliberately NO changes.json/before.json: generic promotion cannot use this job.
        bpf = tempfile.TemporaryFile()
        pass_fds = ()
        if state['backend'] == 'bubblewrap':
            self.write_filter(bpf)
            pass_fds = (bpf.fileno(),)
            cmd = self.base_bwrap() + [
                '--seccomp', str(bpf.fileno()), '--ro-bind', str(bundle), '/extension',
                '--chdir', '/scratch', '/usr/bin/python3', '-I', '-S', '/extension/worker.py']
        else:
            cmd = ['docker', 'run', '--rm', '--pull', 'never', '--name', 'artemis-' + job_id,
                   '--network', 'none', '--ipc', 'none', '--read-only', '--cap-drop', 'ALL',
                   '--security-opt', 'no-new-privileges', '--pids-limit', '1',
                   '--memory', str(LIMITS['memory_bytes']), '--memory-swap', str(LIMITS['memory_bytes']),
                   '--cpus', '1', '--user', str(os.getuid()) + ':' + str(os.getgid()),
                   '--env', 'TMPDIR=/scratch', '--env', 'HOME=/scratch',
                   '--tmpfs', '/scratch:rw,noexec,nosuid,mode=1777,size=' + str(LIMITS['scratch_bytes']),
                   '--mount', 'type=bind,src=' + str(bundle) + ',dst=/extension,readonly', '-w', '/scratch',
                   'artemis-worker:local', 'python', '-I', '-S', '/extension/worker.py']
        started = time.monotonic()
        reason = None
        try:
            with (job / 'stdout').open('wb') as out, (job / 'stderr').open('wb') as err:
                p = subprocess.Popen(cmd, stdout=out, stderr=err, stdin=subprocess.DEVNULL,
                                     start_new_session=True, pass_fds=pass_fds,
                                     env={'PATH': os.environ.get('PATH', '/usr/bin:/bin')},
                                     preexec_fn=self.limits if state['backend'] == 'bubblewrap' else None)
                self.execution.running[producer] = (p, job_id)
                try:
                    while p.poll() is None:
                        if self.cancelled(producer):
                            reason = 'Run cancelled during extension execution'
                        elif time.monotonic() - started > LIMITS['wall_seconds']:
                            reason = 'Extension timeout'
                        elif (job / 'stdout').stat().st_size + (job / 'stderr').stat().st_size > LIMITS['output_bytes']:
                            reason = 'Extension output limit'
                        else:
                            try:
                                files = self.execution.scan(scratch)
                                if sum(f['size'] for f in files.values()) > LIMITS['scratch_bytes']:
                                    reason = 'Extension scratch quota exceeded'
                            except ValueError as e:
                                reason = str(e)
                        if reason:
                            self.execution.kill(p, job_id, state['backend'])
                            break
                        time.sleep(.02)
                    p.wait(timeout=5)
                finally:
                    if p.poll() is None:
                        self.execution.kill(p, job_id, state['backend'])
                    if self.execution.running.get(producer, (None, None))[1] == job_id:
                        self.execution.running.pop(producer, None)
            if self.cancelled(producer):
                reason = 'Run cancelled during extension execution'
            # Validate final scratch even if the process exited between polls.
            files = self.execution.scan(scratch)
            if sum(f['size'] for f in files.values()) > LIMITS['scratch_bytes']:
                reason = 'Extension scratch quota exceeded'
            raw = (job / 'stdout').read_bytes()
            if len(raw) > LIMITS['output_bytes']:
                reason = 'Extension output limit'
            if reason or p.returncode:
                result = {'ok': False, 'error': reason or 'Sandbox exited with code ' + str(p.returncode),
                          'stderr': (job / 'stderr').read_text(errors='replace')[:1500]}
            else:
                try:
                    result = json.loads(raw)
                    if not isinstance(result, dict) or type(result.get('ok')) is not bool:
                        raise ValueError('Invalid envelope')
                    dump(result)  # Also rejects non-finite JSON values.
                except (ValueError, TypeError):
                    result = {'ok': False, 'error': 'Sandbox returned an invalid JSON envelope'}
            result['sandbox'] = {'job_id': job_id, 'backend': state['backend'], 'profile': 'json-only-v1',
                                 'network': 'none', 'user_files': 'none',
                                 'scratch_enforcement': 'kernel-sized private tmpfs',
                                 'elapsed_s': round(time.monotonic() - started, 3)}
            metadata.update(status='succeeded' if result['ok'] else 'failed')
            (job / 'meta.json').write_text(dump(metadata))
            return result
        finally:
            bpf.close()
