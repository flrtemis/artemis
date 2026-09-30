"""One realtime speech session feeds the same task runtime/history/approvals.
OpenAI GA-compatible PCM events reuse Gemma's client/worklets. Epochs reject stale audio.
"""
from __future__ import annotations
import asyncio,base64,json,os,secrets,time,re,math,struct,io,wave,importlib.util
from pathlib import Path
import httpx
DEFAULT={'stt_backend':'local','tts_backend':'local','whisper_model':'','piper_model':'','device':'cpu','language':'en','stt_url':'','tts_url':'','voice':'sage','allow_remote_audio':False,'vad_threshold':.012,'silence_ms':600}
class Speech:
    def __init__(self,runtime,root):self.runtime=runtime;self.store=runtime.store;self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True);self.worker=None;self.lock=asyncio.Lock();self.counter=0;self.tickets={};self.sessions={}
    def config(self):return {**DEFAULT,**self.store.settings('speech',{})}
    def status(self):
        c=self.config();stt=(bool(c['stt_url']) if c['stt_backend']=='http' else bool(c['whisper_model'] and Path(c['whisper_model'],'model.bin').exists() and Path(c['whisper_model'],'vocabulary.txt').exists() and importlib.util.find_spec('faster_whisper')));tts=(bool(c['tts_url']) if c['tts_backend']=='http' else bool(c['piper_model'] and Path(c['piper_model']).is_file() and importlib.util.find_spec('piper')))
        return {'stt_ready':stt,'tts_ready':tts,'ready':stt and tts,'config':c,'sessions':len(self.sessions),'transport':'same-origin authenticated WebSocket, PCM16 16kHz','conversation_owner':'canonical ARTEMIS Runtime, never a second speech LLM','vad':'energy threshold + bounded silence, explicitly not Silero','limits':'Local model paths or compatible STT/TTS HTTP adapters must be configured'}
    async def configure(self,cfg):
        c={**self.config(),**cfg}
        from urllib.parse import urlparse
        for key in ['stt_url','tts_url']:
            if c[key]:
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
        await ws.accept();session=RealtimeSession(self,ws,thread);self.sessions[thread]=session
        try:await session.serve()
        finally:await session.close();self.sessions.pop(thread,None)
    async def stop_worker(self):
        if self.worker and self.worker.returncode is None:self.worker.terminate();await self.worker.wait()
        self.worker=None
    async def close(self):
        for s in list(self.sessions.values()):await s.close()
        await self.stop_worker()
class RealtimeSession:
    def __init__(self,service,ws,thread):self.service=service;self.ws=ws;self.thread=thread;self.epoch=0;self.response=None;self.run_id=None;self.task=None;self.audio=bytearray();self.speaking=False;self.silent_ms=0;self.pending_text='';self.closed=False;self.send_lock=asyncio.Lock();self.watcher=None;self.seen={m['id'] for m in service.store.messages(thread)}
    async def send(self,type,**data):
        if self.closed:return
        async with self.send_lock:await self.ws.send_json({'type':type,**data})
    async def interrupt(self):
        self.epoch+=1
        if self.task and self.task is not asyncio.current_task() and not self.task.done():self.task.cancel()
        if self.run_id:
            try:await self.service.runtime.cancel(self.run_id)
            except KeyError:pass
        if self.response:await self.send('response.done',response={'id':self.response,'status':'cancelled'})
        self.run_id=None;self.response=None
    async def watch_committed_replies(self):
        try:
            while not self.closed:
                for m in self.service.store.messages(self.thread):
                    if m['id'] in self.seen:continue
                    self.seen.add(m['id'])
                    if m['role']=='assistant' and self.response is None:await self.begin_speech(m['content'])
                await asyncio.sleep(.25)
        except asyncio.CancelledError:pass
    async def serve(self):
        self.watcher=asyncio.create_task(self.watch_committed_replies())
        await self.send('session.created',session={'id':self.thread,'input_audio_format':'pcm16','output_audio_format':'pcm16','sample_rate':16000})
        while not self.closed:
            try:m=await self.ws.receive_json()
            except Exception:break
            if len(json.dumps(m))>100000:raise ValueError('Realtime event size exceeded')
            typ=m.get('type')
            if typ=='session.update':await self.send('session.updated',session={'id':self.thread});continue
            if typ=='input_audio_buffer.append':
                pcm=base64.b64decode(m.get('audio',''),validate=True)
                if len(pcm)>3200 or len(pcm)%2:raise ValueError('Audio frame must be bounded PCM16')
                values=struct.unpack('<'+'h'*(len(pcm)//2),pcm) if pcm else [];rms=math.sqrt(sum(x*x for x in values)/max(1,len(values)))/32768
                cfg=self.service.config();milliseconds=len(pcm)/32
                if rms>cfg['vad_threshold']:
                    if not self.speaking:await self.interrupt();self.speaking=True;self.audio.clear();await self.send('input_audio_buffer.speech_started',item_id=secrets.token_hex(8))
                    self.silent_ms=0
                elif self.speaking:self.silent_ms+=milliseconds
                if self.speaking:self.audio.extend(pcm)
                if len(self.audio)>960000:await self.commit_audio()
                elif self.speaking and self.silent_ms>=cfg['silence_ms']:await self.commit_audio()
            elif typ=='input_audio_buffer.commit':await self.commit_audio()
            elif typ=='input_audio_buffer.clear':self.audio.clear();self.speaking=False
            elif typ=='conversation.item.create':
                item=m.get('item',{})
                if item.get('role')!='user':raise ValueError('Client cannot forge assistant or tool history')
                parts=item.get('content',[]);self.pending_text=' '.join(str(p.get('text','')) for p in parts if p.get('type') in ['input_text','text'])[:20000]
                if any(p.get('type') not in ['input_text','text'] for p in parts):await self.send('error',error={'message':'Use the canonical authenticated upload/attachment UI for media; do not bypass file policy'})
            elif typ=='response.create':
                if self.pending_text:await self.begin_text(self.pending_text);self.pending_text=''
            elif typ=='response.cancel':await self.interrupt()
            elif typ=='artemis.speak':
                # Read an actual persisted assistant message, not arbitrary claimed model output.
                id=m.get('message_id');message=next((x for x in self.service.store.messages(self.thread) if x['id']==id and x['role']=='assistant'),None)
                if message:await self.begin_speech(message['content'])
            else:await self.send('error',error={'message':'Unsupported realtime message'})
    async def commit_audio(self):
        if not self.audio:return
        pcm=bytes(self.audio[:960000]);self.audio.clear();self.speaking=False;self.silent_ms=0;await self.send('input_audio_buffer.speech_stopped')
        epoch=self.epoch
        async def transcribe():
            try:
                result=await self.service.transcribe(pcm)
                if epoch!=self.epoch:return
                text=result['text'];await self.send('conversation.item.input_audio_transcription.completed',transcript=text,item_id=secrets.token_hex(8),content_index=0)
                if text:await self.begin_text(text)
            except Exception as e:await self.send('error',error={'message':str(e)})
        self.task=asyncio.create_task(transcribe())
    async def begin_text(self,text):
        await self.interrupt();epoch=self.epoch;self.response=secrets.token_hex(16);rid=self.response;await self.send('response.created',response={'id':rid,'status':'in_progress'})
        self.run_id=await self.service.runtime.begin_chat(self.thread,text)
        async def wait():
            try:
                while epoch==self.epoch:
                    run=self.service.store.run(self.run_id)
                    if run['status']=='succeeded':await self.stream_speech(run['result']['reply'],rid,epoch);break
                    if run['status'] in ['failed','cancelled','interrupted']:await self.send('error',error={'message':run['error'] or run['status']});await self.send('response.done',response={'id':rid,'status':'failed'});break
                    if run['status']=='awaiting_approval':await self.send('artemis.approval',run_id=run['id'])
                    await asyncio.sleep(.2)
            except asyncio.CancelledError:pass
            except Exception as e:await self.send('error',error={'message':str(e)})
        self.task=asyncio.create_task(wait())
    async def begin_speech(self,text):
        await self.interrupt();epoch=self.epoch;self.response=secrets.token_hex(16);rid=self.response;await self.send('response.created',response={'id':rid});self.task=asyncio.create_task(self.stream_speech(text,rid,epoch))
    async def stream_speech(self,text,rid,epoch):
        try:
            # Sentence-boundary chunks keep synthesis/playback latency bounded. No invented streaming.
            chunks=re.split(r'(?<=[.!?])\s+',text)
            for chunk in chunks:
                if not chunk.strip():continue
                for start in range(0,len(chunk),1000):
                    segment=chunk[start:start+1000];result=await self.service.synthesize(segment)
                    if epoch!=self.epoch:return
                    await self.send('response.output_audio_transcript.delta',response_id=rid,delta=segment+' ')
                    pcm=base64.b64decode(result['pcm16'])
                    for offset in range(0,len(pcm),1280):
                        if epoch!=self.epoch:return
                        await self.send('response.output_audio.delta',response_id=rid,delta=base64.b64encode(pcm[offset:offset+1280]).decode());await asyncio.sleep(.005)
            await self.send('response.output_audio_transcript.done',response_id=rid,transcript=text);await self.send('response.output_audio.done',response_id=rid);await self.send('response.done',response={'id':rid,'status':'completed','output':[{'type':'message','content':[{'type':'audio','transcript':text}]}]})
            if epoch==self.epoch:self.response=None;self.run_id=None
        except asyncio.CancelledError:pass
        except Exception as e:await self.send('error',error={'message':str(e)});await self.send('response.done',response={'id':rid,'status':'failed'})
    async def close(self):
        if self.closed:return
        if self.watcher:self.watcher.cancel()
        await self.interrupt();self.closed=True
        try:await self.ws.close()
        except Exception:pass
