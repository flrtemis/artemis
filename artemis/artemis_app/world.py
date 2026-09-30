"""Native authoritative World + separate immutable sensor/intent participant contract."""
from __future__ import annotations
import os,shutil,subprocess,socket,time,json,threading,secrets,hashlib,re
from pathlib import Path
PROJECT=Path(__file__).resolve().parent.parent
class World:
    def __init__(self,store):self.store=store;self.process=None;self.sock=None;self.lock=threading.RLock();self.key=secrets.token_urlsafe(32);self.request_id=0;self.episode=None;self.action_log=[];self.error=None
    def binary(self):
        candidates=[os.environ.get('ARTEMIS_GODOT_BIN'),shutil.which('godot4'),shutil.which('godot'),str(PROJECT.parent/'.cache/native-engines/Godot_v4.4.1-stable_linux.x86_64')]
        return next((p for p in candidates if p and Path(p).is_file()),None)
    def status(self):return {'available':bool(self.binary()),'running':bool(self.process and self.process.poll() is None),'engine':'Godot 4 authoritative native physics','episode':self.episode,'error':self.error,'physics_hz':60,'participant':'Only immutable partial sensor frames and bounded motor intents; no host tools or truth API'}
    def start(self,seed=17):
        with self.lock:
            if self.process and self.process.poll() is None:
                self.episode=secrets.token_hex(16);self.action_log=[];return self.request('reset',seed=seed)
            binary=self.binary()
            if not binary:raise ValueError('Install Godot 4 or set ARTEMIS_GODOT_BIN. No fake physics fallback.')
            with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
            self.process=subprocess.Popen([binary,'--headless','--path',str(PROJECT/'engines/world'),'--script','sim.gd','--','--port='+str(port),'--key='+self.key],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,env={'PATH':os.environ.get('PATH','/usr/bin'),'HOME':os.environ.get('HOME','/tmp')},start_new_session=True)
            until=time.monotonic()+10
            while time.monotonic()<until:
                if self.process.poll() is not None:
                    log=self.process.stdout.read().decode(errors='replace');self.error=log[-2500:];raise ValueError('Godot worker failed: '+self.error)
                try:self.sock=socket.create_connection(('127.0.0.1',port),timeout=.15);self.sock.settimeout(15);break
                except OSError:time.sleep(.05)
            else:self.close();raise ValueError('Godot worker did not become ready')
            # Native stdout is drained independently; no pipe backpressure/deadlocks.
            threading.Thread(target=lambda:[None for _ in self.process.stdout],daemon=True).start()
            self.episode=secrets.token_hex(16);self.action_log=[];self.error=None
            result=self.request('reset',seed=seed);self.store.add_event('host','Native World episode started',{'episode':self.episode,'seed':seed});return result
    def request(self,command,**kwargs):
        with self.lock:
            if not self.sock or not self.process or self.process.poll() is not None:raise ValueError('Start a World episode first')
            self.request_id+=1;id=self.request_id;payload={'id':id,'key':self.key,'command':command,**kwargs}
            self.sock.sendall((json.dumps(payload,allow_nan=False)+'\n').encode());buffer=bytearray()
            while b'\n' not in buffer:
                block=self.sock.recv(65536)
                if not block:raise ValueError('Native World connection closed')
                buffer.extend(block)
                if len(buffer)>1_000_000:raise ValueError('Native response exceeded limit')
            response=json.loads(buffer.split(b'\n',1)[0]);result=response['data']
            if isinstance(result,dict) and result.get('error'):raise ValueError(result['error'])
            if command in ['intent','advance','reset']:self.action_log.append({'command':command,'arguments':kwargs,'tick':result.get('tick',0),'sensor_hash':self.hash(result) if command=='advance' else None})
            return result
    @staticmethod
    def hash(frame):return hashlib.sha256(json.dumps(frame,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    def sensors(self):
        frame=self.request('sense');frame['episode']=self.episode;frame['revision']=frame['tick'];return frame
    def intent(self,move_x=0,move_z=0,look_delta=0,expected_revision=None):
        import math
        if not all(math.isfinite(float(x)) for x in [move_x,move_z,look_delta]) or abs(move_x)>1 or abs(move_z)>1 or abs(look_delta)>.5:raise ValueError('Motor intent outside bounded controller contract')
        if expected_revision is not None and self.request('sense')['tick']!=expected_revision:raise ValueError('Stale sensor revision; resample before committing intent')
        return self.request('intent',move_x=move_x,move_z=move_z,look_delta=look_delta)
    def replay(self):
        with self.lock:
            if self.request('truth')['running']:raise ValueError('Pause World before deterministic replay')
            entries=json.loads(json.dumps(self.action_log));seed=next((e['arguments']['seed'] for e in entries if e['command']=='reset'),17)
            self.action_log=[];self.request('reset',seed=seed);comparisons=[]
            for e in entries:
                if e['command']=='reset':continue
                result=self.request(e['command'],**e['arguments'])
                if e['sensor_hash']:comparisons.append({'tick':e['tick'],'matches':self.hash(result)==e['sensor_hash']})
            return {'quality':'native_engine_replay','frames_compared':len(comparisons),'exact_matches':all(x['matches'] for x in comparisons),'comparisons':comparisons,'limits':'Deterministic seed/actions in the tested engine/build. Cross-platform floating-point identity is not guaranteed.'}
    def close(self):
        with self.lock:
            if self.sock:
                try:self.sock.close()
                except OSError:pass
                self.sock=None
            if self.process:
                self.process.terminate()
                try:self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:self.process.kill();self.process.wait()
                self.process=None
