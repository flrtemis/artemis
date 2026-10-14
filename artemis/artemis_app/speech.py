"""One realtime speech session feeds the same task runtime/history/approvals.
OpenAI GA-compatible PCM events reuse Gemma's client/worklets. Epochs reject stale audio.
"""
from __future__ import annotations
import asyncio,base64,json,os,secrets,time,re,math,struct,io,wave,importlib.util
from pathlib import Path
import httpx
DEFAULT={'stt_backend':'local','tts_backend':'local','whisper_model':'','piper_model':'','device':'cpu','language':'en','stt_url':'','tts_url':'','voice':'sage','allow_remote_audio':False,'vad_threshold':.012,'silence_ms':600}
from .offline import admit_endpoint,enabled as offline_enabled,local_endpoint
class Speech:
    def __init__(self,runtime,root):self.runtime=runtime;self.store=runtime.store;self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True);self.worker=None;self.lock=asyncio.Lock();self.counter=0;self.tickets={};self.sessions={}
    def config(self):return {**DEFAULT,**self.store.settings('speech',{})}
    def status(self):
        c=self.config();stt=(bool(c['stt_url']) if c['stt_backend']=='http' else bool(c['whisper_model'] and Path(c['whisper_model'],'model.bin').exists() and Path(c['whisper_model'],'vocabulary.txt').exists() and importlib.util.find_spec('faster_whisper')));tts=(bool(c['tts_url']) if c['tts_backend']=='http' else bool(c['piper_model'] and Path(c['piper_model']).is_file() and importlib.util.find_spec('piper')))
        if offline_enabled():
            if c['stt_backend']=='http' and not local_endpoint(c['stt_url']):stt=False
            if c['tts_backend']=='http' and not local_endpoint(c['tts_url']):tts=False
        return {'stt_ready':stt,'tts_ready':tts,'ready':stt and tts,'config':c,'sessions':len(self.sessions),'transport':'same-origin authenticated WebSocket, PCM16 16kHz','conversation_owner':'canonical ARTEMIS Runtime, never a second speech LLM','vad':'energy threshold + bounded silence, explicitly not Silero','limits':'Local model paths or compatible STT/TTS HTTP adapters must be configured'}
    async def configure(self,cfg):
        c={**self.config(),**cfg}
        from urllib.parse import urlparse
        for key in ['stt_url','tts_url']:
            if c[key]:
                admit_endpoint(c[key])
                p=urlparse(c[key])
                if p.scheme not in ['http','https'] or p.username or p.password:raise ValueError('Use a valid speech endpoint without URL credentials')
                if p.hostname not in ['localhost','127.0.0.1','::1'] and not c['allow_remote_audio']:raise ValueError('Explicit remote audio consent required')
        if not .001<=float(c['vad_threshold'])<=.2 or not 200<=int(c['silence_ms'])<=2000:raise ValueError('VAD values outside safe bounds')
        await self.stop_worker();self.store.setting('speech',c);return self.status()
    async def start_worker(self):
        if self.worker and self.worker.returncode is None:return
        cfg=self.root/'worker.json';cfg.write_text(json.dumps(self.config()))
        import sys
        self.worker=await asyncio.create_subprocess_exec(sys.executable,'-m','artemis_app.speech_worker',str(cfg),stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.PIPE,stderr=(self.root/'worker.log').open('ab'),env={'PATH':os.environ.get('PATH','/usr/bin'),'HOME':os.environ.get('HOME','/tmp'),'OMP_NUM_THREADS':'1','HF_HUB_OFFLINE':'1'},limit=3_000_000)
    async def local(self,typ,**kwargs):
        async with self.lock:
            await self.start_worker();self.counter+=1;id=self.counter
            self.worker.stdin.write((json.dumps({'id':id,'type':typ,**kwargs})+'\n').encode());await self.worker.stdin.drain()
            try:line=await asyncio.wait_for(self.worker.stdout.readline(),60)
            except BaseException:await self.stop_worker();raise
            if not line:raise ValueError('Speech worker exited; inspect authenticated Operations diagnostics')
            result=json.loads(line)
            if result.get('error'):raise ValueError(result['error'])
            if result['id']!=id:raise ValueError('Speech request epoch mismatch')
            return result['result']
    async def transcribe(self,pcm):
        if len(pcm)>960000 or len(pcm)%2:raise ValueError('Utterance limit: 30 seconds PCM16')
        if not self.status()['stt_ready']:raise ValueError('Configure a real STT model/provider')
        c=self.config()
        if c['stt_backend']=='local':return await self.local('stt',pcm16=base64.b64encode(pcm).decode())
        buf=io.BytesIO()
        with wave.open(buf,'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(16000);w.writeframes(pcm)
        async with httpx.AsyncClient(timeout=60,trust_env=False,follow_redirects=False) as client:
            r=await client.post(c['stt_url'],files={'file':('utterance.wav',buf.getvalue(),'audio/wav')},data={'model':c.get('stt_model','whisper-1')});r.raise_for_status();return {'text':r.json()['text'],'quality':'actual_configured_http_stt'}
    async def synthesize(self,text):
        if not isinstance(text,str) or not 1<=len(text)<=4000:raise ValueError('Speech text length outside bounds')
        if not self.status()['tts_ready']:raise ValueError('Configure a real TTS model/provider')
        c=self.config()
        if c['tts_backend']=='local':return await self.local('tts',text=text)
        async with httpx.AsyncClient(timeout=60,trust_env=False,follow_redirects=False) as client:
            r=await client.post(c['tts_url'],json={'input':text,'voice':c['voice'],'model':c.get('tts_model','tts-1'),'response_format':'pcm'});r.raise_for_status()
        # Compatible adapter must deliver PCM16 mono @16k; not guessing engine format.
        return {'pcm16':base64.b64encode(r.content).decode(),'sample_rate':16000,'samples':len(r.content)//2,'quality':'actual_configured_http_tts'}
    def grant(self,thread_id):
        self.store.thread(thread_id)
        if not self.status()['tts_ready']:raise ValueError('Configure real TTS before starting a voice session')
        ticket=secrets.token_urlsafe(32);self.tickets[ticket]={'thread_id':thread_id,'expires':time.time()+30};return ticket
    async def accept(self,ws,ticket):
        grant=self.tickets.pop(ticket,None)
        if not grant or grant['expires']<time.time():await ws.close(code=1008);return
        # One audio owner for a thread, not two microphones/speakers fighting.
        thread=grant['thread_id']
        if thread in self.sessions:await ws.close(code=1008);return
        # Reserve before the first await: two simultaneous handshakes cannot both own a thread.
        session=RealtimeSession(self,ws,thread);self.sessions[thread]=session
        try:
            await ws.accept()
            await session.serve()
        finally:
            # Release synchronously before cancellable cleanup. A disconnected socket's
            # cleanup may be interrupted or slow, but must never strand ownership or
            # later remove a newly admitted session for the same canonical thread.
            if self.sessions.get(thread) is session:self.sessions.pop(thread,None)
            await session.close()
    async def stop_worker(self):
        if self.worker and self.worker.returncode is None:self.worker.terminate();await self.worker.wait()
        self.worker=None
    async def close(self):
        for s in list(self.sessions.values()):await s.close()
        await self.stop_worker()
class RealtimeSession:
    """An audio surface over durable work, NEVER the owner of that work.

    response.cancel / VAD barge-in yield audio only. Explicit artemis.job.cancel
    or the authenticated HTTP cancel route cancels a job. Corrections are
    explicit and tied to the canonical run ID. The committed-reply watcher is
    a projection, not another LLM/history loop. Disconnection releases audio;
    it does not discard a pending approval or invent completion.
    """
    def __init__(self, service, ws, thread):
        self.service, self.ws, self.thread = service, ws, thread
        self.epoch = 0
        self.response = None
        active = self.active_run()
        self.run_id = active['id'] if active else None
        self.task = None  # transient STT, playback or reply waiter only
        self.watcher = None
        self.audio = bytearray()
        self.speaking = False
        self.transcribing = False
        self.playback_held = False
        self.silent_ms = 0
        self.pending_text = ''
        self.closed = False
        self.send_lock = asyncio.Lock()
        # Reconnection never automatically replays old, already-committed work.
        # It is still visible/readable through the canonical message UI.
        self.seen = {m['id'] for m in service.store.messages(thread)}

    def active_run(self):
        return self.service.store.active_chat(self.thread)

    def gate_closed(self):
        return self.playback_held or self.speaking or self.transcribing

    async def send(self, type, **data):
        if self.closed:
            return
        async with self.send_lock:
            await self.ws.send_json({'type': type, **data})

    async def interrupt(self, hold=True):
        """Invalidate stale audio/STT, retaining the durable job and approvals."""
        self.epoch += 1
        old, self.task = self.task, None
        if old and old is not asyncio.current_task() and not old.done():
            old.cancel()
        self.transcribing = False
        self.playback_held = hold
        response, self.response = self.response, None
        if response:
            await self.send('response.done', response={'id': response, 'status': 'cancelled'})
        if hold:
            active = self.active_run()
            if active:
                self.run_id = active['id']
            await self.send('artemis.audio.yielded', run_id=self.run_id,
                            work_continues=bool(active), playback='held_until_resume_or_new_turn')

    async def resume_audio(self):
        if self.speaking or self.transcribing:
            await self.send('error', error={'message': 'Audio remains held while your input is being captured/transcribed'})
            return
        self.playback_held = False
        await self.send('artemis.audio.resumed', run_id=self.run_id)

    async def watch_committed_replies(self):
        try:
            while not self.closed:
                active = self.active_run()
                if active:
                    self.run_id = active['id']
                for m in self.service.store.messages(self.thread):
                    if m['id'] in self.seen:
                        continue
                    if m['role'] != 'assistant':
                        self.seen.add(m['id'])
                        continue
                    # Do NOT mark a result seen merely because audio is busy/held.
                    if self.response is None and not self.gate_closed():
                        await self.begin_speech(m['content'], m['id'], m['meta'].get('run_id'))
                        break
                await asyncio.sleep(.05)
        except asyncio.CancelledError:
            pass
        except Exception:
            # Socket failure does not change job status. accept() owns cleanup.
            pass

    def bound_job(self, run_id):
        if not run_id:
            raise ValueError('A canonical run_id is required')
        run = self.service.store.run(run_id)
        if run['thread_id'] != self.thread or run['kind'] != 'chat':
            raise ValueError('Voice grant cannot control another thread or non-chat job')
        return run

    async def serve(self):
        self.watcher = asyncio.create_task(self.watch_committed_replies())
        await self.send('session.created', session={'id': self.thread, 'input_audio_format': 'pcm16',
                        'output_audio_format': 'pcm16', 'sample_rate': 16000,
                        'artemis': {'run_id': self.run_id, 'response_cancel': 'audio_yield_only',
                                    'parallel_model_answer': 'not promised'}})
        while not self.closed:
            try:
                m = await self.ws.receive_json()
            except Exception:
                break
            if len(json.dumps(m)) > 100000:
                raise ValueError('Realtime event size exceeded')
            typ = m.get('type')
            try:
                if typ == 'session.update':
                    await self.send('session.updated', session={'id': self.thread})
                elif typ == 'input_audio_buffer.append':
                    pcm = base64.b64decode(m.get('audio', ''), validate=True)
                    if len(pcm) > 3200 or len(pcm) % 2:
                        raise ValueError('Audio frame must be bounded PCM16')
                    values = struct.unpack('<' + 'h' * (len(pcm) // 2), pcm) if pcm else []
                    rms = math.sqrt(sum(x*x for x in values) / max(1, len(values))) / 32768
                    cfg = self.service.config()
                    milliseconds = len(pcm) / 32
                    if rms > cfg['vad_threshold']:
                        if not self.speaking:
                            await self.interrupt()
                            self.speaking = True
                            self.audio.clear()
                            await self.send('input_audio_buffer.speech_started', item_id=secrets.token_hex(8))
                        self.silent_ms = 0
                    elif self.speaking:
                        self.silent_ms += milliseconds
                    if self.speaking:
                        self.audio.extend(pcm)
                    if len(self.audio) > 960000 or (self.speaking and self.silent_ms >= cfg['silence_ms']):
                        await self.commit_audio()
                elif typ == 'input_audio_buffer.commit':
                    await self.commit_audio()
                elif typ == 'input_audio_buffer.clear':
                    self.audio.clear()
                    self.speaking = False
                    # Clearing captured audio alone does not grant playback permission.
                elif typ == 'conversation.item.create':
                    item = m.get('item', {})
                    if item.get('role') != 'user':
                        raise ValueError('Client cannot forge assistant or tool history')
                    parts = item.get('content', [])
                    if any(p.get('type') not in ['input_text', 'text'] for p in parts):
                        raise ValueError('Use canonical authenticated upload/attachment UI for media')
                    self.pending_text = ' '.join(str(p.get('text', '')) for p in parts)[:20000]
                elif typ == 'response.create':
                    if self.pending_text:
                        text, self.pending_text = self.pending_text, ''
                        await self.begin_text(text)
                elif typ in ('response.cancel', 'artemis.audio.yield'):
                    await self.interrupt()
                elif typ == 'artemis.audio.resume':
                    await self.resume_audio()
                elif typ == 'artemis.job.cancel':
                    run = self.bound_job(m.get('run_id'))
                    await self.service.runtime.cancel(run['id'])
                    await self.interrupt()
                    await self.send('artemis.job.cancelled', run_id=run['id'])
                elif typ == 'artemis.job.correct':
                    run = self.bound_job(m.get('run_id'))
                    result = await self.service.runtime.correct(run['id'], m.get('text', ''))
                    await self.interrupt(hold=False)
                    await self.send('artemis.job.corrected', **result)
                elif typ == 'artemis.speak':
                    # Read actual persisted text, never client-supplied claimed model output.
                    message = next((x for x in self.service.store.messages(self.thread)
                                    if x['id'] == m.get('message_id') and x['role'] == 'assistant'), None)
                    if message:
                        if self.speaking or self.transcribing:
                            raise ValueError('Finish your input before requesting read-aloud')
                        await self.begin_speech(message['content'], message['id'], message['meta'].get('run_id'))
                else:
                    raise ValueError('Unsupported realtime message')
            except (ValueError, KeyError) as e:
                await self.send('error', error={'message': str(e)})

    async def commit_audio(self):
        if not self.audio:
            return
        pcm = bytes(self.audio[:960000])
        self.audio.clear()
        self.speaking = False
        self.silent_ms = 0
        self.transcribing = True
        await self.send('input_audio_buffer.speech_stopped')
        epoch = self.epoch

        async def transcribe():
            try:
                result = await self.service.transcribe(pcm)
                if epoch != self.epoch:
                    return
                self.transcribing = False
                text = result['text']
                await self.send('conversation.item.input_audio_transcription.completed', transcript=text,
                                item_id=secrets.token_hex(8), content_index=0)
                if text:
                    await self.begin_text(text)
            except asyncio.CancelledError:
                pass
            except Exception as e:
                if epoch == self.epoch:
                    self.transcribing = False
                    await self.send('error', error={'message': str(e)})
        self.task = asyncio.create_task(transcribe())

    async def begin_text(self, text):
        active = self.active_run()
        if active:
            await self.interrupt()
            self.run_id = active['id']
            held = self.service.runtime.hold_input(active['id'], text)
            await self.send('artemis.job.active', run_id=active['id'], message_id=held['id'], text=text,
                            disposition='held: explicitly correct the active job, or send a new turn after it finishes',
                            parallel_answer='unavailable: one canonical active job, not a second LLM loop')
            return
        # A new explicit turn supersedes automatic playback of older saved replies;
        # their text/read-aloud remains available. No stale result is replayed into it.
        self.seen.update(m['id'] for m in self.service.store.messages(self.thread) if m['role']=='assistant')
        await self.interrupt(hold=False)
        epoch = self.epoch
        self.run_id = await self.service.runtime.begin_chat(self.thread, text)
        job_id = self.run_id
        self.response = secrets.token_hex(16)
        rid = self.response
        await self.send('response.created', response={'id': rid, 'status': 'in_progress', 'run_id': job_id})

        async def wait_for_reply():
            approval_sent = False
            try:
                while epoch == self.epoch:
                    run = self.service.store.run(job_id)
                    if run['status'] == 'succeeded':
                        if self.gate_closed():
                            await asyncio.sleep(.05)
                            continue
                        message = next((m for m in reversed(self.service.store.messages(self.thread))
                                        if m['role'] == 'assistant' and m['meta'].get('run_id') == job_id), None)
                        if message:
                            self.seen.add(message['id'])
                            await self.stream_speech(message['content'], rid, epoch)
                        break
                    if run['status'] in ('failed', 'cancelled', 'interrupted'):
                        await self.send('error', error={'message': run['error'] or run['status']})
                        await self.send('response.done', response={'id': rid, 'status': 'failed'})
                        if epoch == self.epoch:
                            self.response = None
                        break
                    if run['status'] == 'awaiting_approval' and not approval_sent:
                        await self.send('artemis.approval', run_id=job_id)
                        approval_sent = True
                    await asyncio.sleep(.05)
            except asyncio.CancelledError:
                pass
            except Exception as e:
                if epoch == self.epoch:
                    await self.send('error', error={'message': str(e)})
        self.task = asyncio.create_task(wait_for_reply())

    async def begin_speech(self, text, message_id=None, run_id=None):
        await self.interrupt(hold=False)
        if message_id:
            self.seen.add(message_id)
        if run_id:
            self.run_id = run_id
        epoch = self.epoch
        self.response = secrets.token_hex(16)
        rid = self.response
        await self.send('response.created', response={'id': rid, 'message_id': message_id, 'run_id': run_id})
        self.task = asyncio.create_task(self.stream_speech(text, rid, epoch))

    async def stream_speech(self, text, rid, epoch):
        try:
            for chunk in re.split(r'(?<=[.!?])\s+', text):
                if not chunk.strip():
                    continue
                for start in range(0, len(chunk), 1000):
                    segment = chunk[start:start+1000]
                    result = await self.service.synthesize(segment)
                    if epoch != self.epoch or self.gate_closed():
                        return
                    await self.send('response.output_audio_transcript.delta', response_id=rid, delta=segment+' ')
                    pcm = base64.b64decode(result['pcm16'])
                    for offset in range(0, len(pcm), 1280):
                        if epoch != self.epoch or self.gate_closed():
                            return
                        await self.send('response.output_audio.delta', response_id=rid,
                                        delta=base64.b64encode(pcm[offset:offset+1280]).decode())
                        await asyncio.sleep(.005)
            if epoch != self.epoch or self.gate_closed():
                return
            await self.send('response.output_audio_transcript.done', response_id=rid, transcript=text)
            await self.send('response.output_audio.done', response_id=rid)
            await self.send('response.done', response={'id': rid, 'status': 'completed',
                            'output': [{'type': 'message', 'content': [{'type': 'audio', 'transcript': text}]}]})
            if epoch == self.epoch:
                self.response = None
                active = self.active_run()
                self.run_id = active['id'] if active else None
        except asyncio.CancelledError:
            pass
        except Exception as e:
            if epoch == self.epoch:
                await self.send('error', error={'message': str(e)})
                await self.send('response.done', response={'id': rid, 'status': 'failed'})
                self.response = None

    async def close(self):
        if self.closed:
            return
        self.closed = True
        self.epoch += 1
        tasks = [t for t in (self.watcher, self.task) if t and t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        # No runtime.cancel here. Jobs/approvals survive a voice disconnect.
        try:
            await self.ws.close()
        except Exception:
            pass
