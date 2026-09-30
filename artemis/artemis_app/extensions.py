"""Milestone 02 mounts six subsystems on the SAME authenticated host/runtime."""
import asyncio,json,time,secrets,io,wave,base64,os
from pathlib import Path
from fastapi import Depends,WebSocket,HTTPException
from pydantic import Field
from vendor_sources.local_ollama_arena_agent.local_arena_agent.tools.base import Tool
from .autonomy import Autonomy
from .execution import Execution
from .speech import Speech
from .training import Training
from .world import World

class Extensions:
    def __init__(self,runtime,data):
        self.runtime=runtime;self.tools=runtime.tools;self.store=runtime.store
        self.autonomy=Autonomy(runtime,data/'sage');self.execution=Execution(self.tools,data/'execution');self.speech=Speech(runtime,data/'speech');self.training=Training(self.tools,self.store,data/'training');self.world=World(self.store)
        self.participants={};runtime.extensions=self;runtime.autonomy=self.autonomy
        t=self.tools;t.execution=self.execution;t.async_methods={};t.local_context=__import__('threading').local()
        def add(name,desc,props,required,fn,approval=True,category='execution'):
            t.registry.add(Tool(name,desc,{'type':'object','properties':props,'required':required},fn,approval,category));t.unavailable.pop(name,None)
        if self.execution.available()['available']:
            add('run_bash','Run an approved command in mandatory kernel/container isolation on a job copy. No host/network access; changed files require separate promotion.',{'command':{'type':'string','minLength':1,'maxLength':8000},'timeout':{'type':'integer','minimum':1,'maximum':120}},['command'],lambda a:self.execution.execute(a,getattr(t.local_context,'producer','operator'),'bash'))
            add('run_python','Execute approved Python in the same mandatory isolated job-copy boundary.',{'code':{'type':'string','minLength':1,'maxLength':8000},'timeout':{'type':'integer','minimum':1,'maximum':120}},['code'],lambda a:self.execution.execute(a,getattr(t.local_context,'producer','operator'),'python'))
        add('promote_execution_changes','Promote the exact reviewed isolated job diff; stale original revisions block the whole change set.',{'job_id':{'type':'string','pattern':'^[a-f0-9]{32}$'}},['job_id'],lambda a:self.execution.promote(a,getattr(t.local_context,'producer','operator')))
        train_props={'path':{'type':'string'},'device':{'type':'string','enum':['cpu','cuda']},'fixture':{'type':'boolean'},'model_id':{'type':'string'},'steps':{'type':'integer','minimum':1,'maximum':1000},'rank':{'type':'integer','minimum':1,'maximum':64},'sequence_length':{'type':'integer','minimum':8,'maximum':2048},'learning_rate':{'type':'number','minimum':1e-7,'maximum':.1},'sam':{'type':'boolean'},'pcgrad':{'type':'boolean'},'meta_learning':{'type':'boolean'},'distill_weight':{'type':'number','minimum':0,'maximum':1},'ewc_lambda':{'type':'number','minimum':0,'maximum':10},'token_weighting':{'type':'boolean'},'quantize_nf4':{'type':'boolean'},'activation_checkpointing':{'type':'boolean'}}
        add('start_training','Start an actual local HF/PEFT candidate run under a training lease. CPU fixture is explicitly conformance-only, not fake GPU training.',train_props,['path','device','fixture','steps'],lambda a:self.training.start(a,getattr(t.local_context,'producer','operator')),category='training')
        add('promote_training_adapter','Register an evaluated candidate adapter with explicit consent; no automatic Ollama/GGUF swap.',{'training_run_id':{'type':'string'},'max_heldout_ce':{'type':'number','minimum':0,'maximum':100}},['training_run_id','max_heldout_ce'],lambda a:self.training.promote(a,getattr(t.local_context,'producer','operator')),category='training')
        # Presence choreography changes presentation only; no continuity/weight mutation.
        for name,prop,options in [('set_mood','mood',['neutral','happy','angry','sad','fear','disgust','love','sleep']),('make_hand_gesture','gesture',['handup','index','ok','thumbup','thumbdown','side','shrug']),('make_facial_expression','emoji',['😊','😢','😠','😮','❤️'])]:
            def fn(a,name=name):self.store.add_event('presence','Avatar choreography',{'tool':name,'arguments':a});return {'ok':True,'projection':'expressive_avatar','tool':name}
            add(name,'Gemma’s original avatar choreography, projected onto the same actor.',{prop:{'type':'string','enum':options}},[prop],fn,False,'presence')
        # Real speech generation/transcription are runtime-dispatched async callbacks.
        add('generate_speech','Synthesize through the configured real speech worker; save an actual WAV artifact.',{'text':{'type':'string','minLength':1,'maxLength':4000},'path':{'type':'string'}},['text','path'],lambda a:None,True,'media')
        add('transcribe_audio','Transcribe a contained PCM16 mono 16k WAV through real configured STT.',{'path':{'type':'string'}},['path'],lambda a:None,False,'media')
        t.async_methods.update(generate_speech=self.speech_artifact,transcribe_audio=self.transcribe_artifact)
        self.sync_availability()
    def sync_availability(self):
        s=self.speech.status()
        for name,ready in [('generate_speech',s['tts_ready']),('transcribe_audio',s['stt_ready'])]:
            if ready:self.tools.unavailable.pop(name,None)
            else:self.tools.unavailable[name]='Configure a real local speech model or compatible engine endpoint in Operations.'
    async def speech_artifact(self,args,producer):
        pre=self.tools.fingerprint('generate_speech',args);result=await self.speech.synthesize(args['text']);pcm=base64.b64decode(result['pcm16'])
        with self.tools.lock:
            if self.tools.fingerprint('generate_speech',args)!=pre:raise ValueError('Speech output destination changed during synthesis')
            p=self.tools.ws.safe_path(args['path']);p.parent.mkdir(parents=True,exist_ok=True);self.tools.capture(args['path'],producer)
            with wave.open(str(p),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(16000);w.writeframes(pcm)
            self.tools.capture(args['path'],producer)
        return {'ok':True,'path':args['path'],'meta':self.tools.ws.meta(p),'quality':result['quality']}
    async def transcribe_artifact(self,args,producer):
        p=self.tools.ws.safe_path(args['path'])
        with wave.open(str(p),'rb') as w:
            if w.getnchannels()!=1 or w.getsampwidth()!=2 or w.getframerate()!=16000:raise ValueError('Use PCM16 mono 16k WAV for this contained transcription route')
            pcm=w.readframes(16000*30)
        return {'ok':True,**await self.speech.transcribe(pcm)}
    async def start(self):self.autonomy.start()
    async def close(self):
        await self.autonomy.close();await self.speech.close();await asyncio.to_thread(self.training.close);await asyncio.to_thread(self.world.close)
        for producer in list(self.execution.running):self.execution.cancel(producer)

    def mount(self,app,auth,Body):
        e=self
        class AutonomyConfig(Body):enabled:bool;interval_s:int=Field(default=600,ge=60,le=10800);user_name:str=Field(default='Operator',max_length=80);thread_id:str|None=None;allow_memory:bool=True;allow_goals:bool=True;allow_messages:bool=True;allow_affect:bool=True
        class Letter(Body):text:str=Field(min_length=1,max_length=16000)
        class SpeechConfig(Body):stt_backend:str='local';tts_backend:str='local';whisper_model:str='';piper_model:str='';device:str='cpu';language:str='en';stt_url:str='';tts_url:str='';voice:str='sage';allow_remote_audio:bool=False;vad_threshold:float=.012;silence_ms:int=600
        class VoiceGrant(Body):thread_id:str
        class ModelRegistration(Body):name:str=Field(max_length=80);path:str=Field(max_length=2000)
        class TrainingControl(Body):status:str
        class WorldStart(Body):seed:int=Field(default=17,ge=0,le=2147483647)
        class WorldAdvance(Body):frames:int=Field(default=1,ge=1,le=600)
        class WorldPlay(Body):running:bool
        class Intent(Body):move_x:float=Field(default=0,ge=-1,le=1);move_z:float=Field(default=0,ge=-1,le=1);look_delta:float=Field(default=0,ge=-.5,le=.5);expected_revision:int|None=None
        class ActorStep(Body):goal:str=Field(min_length=1,max_length=1000)
        @app.get('/api/subsystems',dependencies=[Depends(auth)])
        async def subsystems():return {'autonomy':e.autonomy.status(),'speech':e.speech.status(),'execution':e.execution.available(),'training':await asyncio.to_thread(e.training.hardware),'training_models':e.training.models(),'world':e.world.status()}
        @app.put('/api/autonomy',dependencies=[Depends(auth)])
        async def autonomous(body:AutonomyConfig):return e.autonomy.configure(body.model_dump())
        @app.post('/api/autonomy/wake',dependencies=[Depends(auth)])
        async def wake():return await e.autonomy.wake('operator_poke')
        @app.post('/api/continuity/letters',dependencies=[Depends(auth)])
        async def letter(body:Letter):return e.autonomy.add_letter(body.text)
        @app.put('/api/speech',dependencies=[Depends(auth)])
        async def speech(body:SpeechConfig):result=await e.speech.configure(body.model_dump());e.sync_availability();return result
        @app.post('/api/speech/session',dependencies=[Depends(auth)])
        async def voice(body:VoiceGrant):
            ticket=e.speech.grant(body.thread_id)
            return {'ticket':ticket,'path':'/api/speech/realtime?ticket='+ticket,'ttl_s':30,'thread_id':body.thread_id}
        @app.websocket('/api/speech/realtime')
        async def realtime(ws:WebSocket,ticket:str):
            # Reject cross-origin WebSocket upgrades even with an otherwise-valid ticket.
            from urllib.parse import urlparse
            origin=ws.headers.get('origin')
            if origin and urlparse(origin).netloc!=ws.headers.get('host'):await ws.close(code=1008);return
            await e.speech.accept(ws,ticket)
        @app.post('/api/training/models',dependencies=[Depends(auth)])
        async def model(body:ModelRegistration):return e.training.register_model(body.name,body.path)
        @app.post('/api/training/{id}/control',dependencies=[Depends(auth)])
        async def traincontrol(id:str,body:TrainingControl):return e.training.control(id,body.status)
        @app.post('/api/world/start',dependencies=[Depends(auth)])
        async def worldstart(body:WorldStart):return await asyncio.to_thread(e.world.start,body.seed)
        @app.get('/api/world/truth',dependencies=[Depends(auth)])
        async def truth():return await asyncio.to_thread(e.world.request,'truth')
        @app.get('/api/world/sensors',dependencies=[Depends(auth)])
        async def sensors():return await asyncio.to_thread(e.world.sensors)
        @app.post('/api/world/intent',dependencies=[Depends(auth)])
        async def intent(body:Intent):return await asyncio.to_thread(e.world.intent,**body.model_dump())
        @app.post('/api/world/advance',dependencies=[Depends(auth)])
        async def advance(body:WorldAdvance):return await asyncio.to_thread(e.world.request,'advance',frames=body.frames)
        @app.post('/api/world/play',dependencies=[Depends(auth)])
        async def play(body:WorldPlay):return await asyncio.to_thread(e.world.request,'play',running=body.running)
        @app.post('/api/world/replay',dependencies=[Depends(auth)])
        async def replay():return await asyncio.to_thread(e.world.replay)
        @app.post('/api/world/participant',dependencies=[Depends(auth)])
        async def participant():
            if not e.world.status()['running']:raise ValueError('Start a World episode first')
            token=secrets.token_urlsafe(32);e.participants[token]={'episode':e.world.episode,'expires':time.time()+3600};return {'token':token,'scope':['sensors','intent'],'episode':e.world.episode}
        async def restricted(authorization:str|None=None):
            # Intentionally distinct from operator auth; cannot access ANY host endpoint.
            from fastapi import Header
        def check_participant(request):
            token=request.headers.get('x-artemis-session') or request.headers.get('authorization','').removeprefix('Bearer ');p=e.participants.get(token)
            if not p or p['expires']<time.time() or p['episode']!=e.world.episode:raise HTTPException(401,'Invalid scoped participant token')
        from fastapi import Request
        @app.get('/api/participant/sensors')
        async def participant_sensors(request:Request):check_participant(request);return await asyncio.to_thread(e.world.sensors)
        @app.post('/api/participant/intent')
        async def participant_intent(request:Request,body:Intent):check_participant(request);return await asyncio.to_thread(e.world.intent,**body.model_dump())
        @app.post('/api/world/actor-step',dependencies=[Depends(auth)])
        async def actor_step(body:ActorStep):
            frame=await asyncio.to_thread(e.world.sensors)
            # Restricted policy: no tool registry, self history, private memory or operator truth.
            messages=[{'role':'system','content':'You control an embodied participant. You only know supplied partial sensors. Return JSON {"move_x":-1..1,"move_z":-1..1,"look_delta":-.5...5,"prediction":"brief expected sensory consequence"}. No tools, filesystem, scene truth or host APIs are available.'},{'role':'user','content':json.dumps({'goal':body.goal,'sensors':frame})}]
            msg=await e.runtime.provider.chat(messages,[],config=e.runtime.provider.config())
            from vendor_sources.sage.awake.mind import parse_response
            text=msg.get('content','');obj=json.loads(text[text.index('{'):text.rindex('}')+1]);intent_=Intent(move_x=obj.get('move_x',0),move_z=obj.get('move_z',0),look_delta=obj.get('look_delta',0),expected_revision=frame['revision'])
            accepted=await asyncio.to_thread(e.world.intent,**intent_.model_dump());prediction=str(obj.get('prediction',''))[:500]
            e.store.add_event('world','Restricted actor intent accepted',{'episode':frame['episode'],'sensor_tick':frame['tick'],'prediction':prediction,'intent':intent_.model_dump()})
            return {'accepted':accepted,'prediction':prediction,'input_contract':'partial sensors only; tools=[]','sensors_before':frame}
