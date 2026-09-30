"""One authenticated gateway for the integrated application. No legacy servers launched."""
from __future__ import annotations
import asyncio,base64,dataclasses,hashlib,hmac,json,math,mimetypes,os,secrets,time,threading,uuid
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlparse
import numpy as np
from fastapi import FastAPI,Depends,HTTPException,Header,UploadFile,File,Request
from fastapi.responses import FileResponse,StreamingResponse,JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel,Field,ConfigDict
from .store import Store,uid
from .continuity import Continuity
from .tools import Tools,MAX_UPLOAD,clean
from .runtime import Runtime
from .extensions import Extensions
from .bio_engine import IzhikevichNetwork,NEURONS_PER_COLUMN

PROJECT=Path(__file__).resolve().parent.parent
class Body(BaseModel):model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
class Login(Body):key:str=Field(min_length=1,max_length=250)
class NewThread(Body):title:str=Field(default='New conversation',min_length=1,max_length=100)
class Chat(Body):thread_id:str;text:str=Field(min_length=1,max_length=20000);attachments:list[str]=Field(default_factory=list,max_length=10)
class Proposal(Body):tool:str=Field(max_length=100);arguments:dict
class Decision(Body):approved:bool;digest:str=Field(min_length=64,max_length=64)
class Provider(Body):base_url:str=Field(min_length=1,max_length=500);model:str=Field(max_length=200);allow_remote_context:bool=False
class BioRequest(Body):steps:int=Field(default=5,ge=1,le=20);seed:int=Field(default=17,ge=0,le=2**31-1)

def create_app(data_dir:Path|None=None,operator_key:str|None=None,provider=None):
    data=Path(data_dir or os.environ.get('ARTEMIS_DATA_DIR',PROJECT/'.runtime')).resolve();data.mkdir(parents=True,exist_ok=True)
    key=operator_key or os.environ.get('ARTEMIS_OPERATOR_KEY') or secrets.token_urlsafe(24)
    sessions={};store=Store(data/'sage/awake.sqlite3');store.recover()
    if (data/'sage/.imported').exists() and not store.threads():
        # Project old public user/reply events into one canonical imported thread;
        # references preserve provenance, and private/wake/letter payloads stay out.
        old=store.recent_events(limit=100000,kinds=('user','reply'))[::-1]
        if old:
            t=store.new_thread('Imported Sage conversation');context=[]
            for e in old:
                role='user' if e['kind']=='user' else 'assistant'
                store.message(t['id'],role,e['content'],{'source_event_id':e['id'],'imported':True})
                context.append({'role':role,'content':e['content']})
            store.context(t['id'],context[-40:])
    continuity=Continuity(data/'sage',store);tools=Tools(data/'workspace',data/'revisions',store,continuity)
    runtime=Runtime(store,tools,continuity,provider)
    extensions=Extensions(runtime,data)
    if os.getenv('ARTEMIS_OLLAMA_URL') or os.getenv('ARTEMIS_OLLAMA_MODEL'):
        cfg=store.settings('provider',{'base_url':'http://127.0.0.1:11434','model':'','allow_remote_context':False})
        cfg.update({k:v for k,v in {'base_url':os.getenv('ARTEMIS_OLLAMA_URL'),'model':os.getenv('ARTEMIS_OLLAMA_MODEL')}.items() if v});store.setting('provider',cfg)
    bio_lock=threading.Lock()
    @asynccontextmanager
    async def lifespan(app):
        store.add_event('host','Unified host started',{'milestone':'integration-02','recovery':'No ambiguous side effects automatically replayed'})
        await extensions.start()
        yield
        await extensions.close();await runtime.shutdown();store.close()
    app=FastAPI(title='ARTEMIS unified host',version='0.2.0',lifespan=lifespan,docs_url=None,redoc_url=None)
    app.state.operator_key=key;app.state.store=store;app.state.runtime=runtime;app.state.tools=tools;app.state.continuity=continuity
    async def auth(authorization:str|None=Header(default=None),x_artemis_session:str|None=Header(default=None)):
        token=x_artemis_session or (authorization or '').removeprefix('Bearer ')
        expiry=sessions.get(token)
        if not expiry or expiry<time.time():raise HTTPException(401,'Unlock this local workspace with the operator key printed by the launcher')
        return 'operator'
    @app.middleware('http')
    async def headers(request,call_next):
        # Bearer sessions + non-simple content types prevent cross-site form mutations.
        if request.method in ['POST','PUT','DELETE','PATCH']:
            origin=request.headers.get('origin');host=request.headers.get('host','')
            if origin and urlparse(origin).netloc!=host:return JSONResponse({'detail':'Cross-origin mutation blocked'},403)
        response=await call_next(request)
        response.headers['X-Content-Type-Options']='nosniff';response.headers['Referrer-Policy']='no-referrer'
        if request.url.path.startswith('/api/'):response.headers['Cache-Control']='no-store'
        return response
    @app.exception_handler(ValueError)
    async def value_error(request,e):return JSONResponse({'detail':str(e)},400)
    @app.exception_handler(KeyError)
    async def key_error(request,e):return JSONResponse({'detail':str(e)},404)
    @app.exception_handler(sqlite_integrity_error())
    async def integrity_error(request,e):return JSONResponse({'detail':'This conversation already has an active run. Resolve or cancel it first.'},409)
    @app.get('/healthz')
    async def health():return {'ok':True,'milestone':'integration-02'}
    login_attempts={}
    @app.post('/api/auth')
    async def login(body:Login,request:Request):
        remote=request.client.host if request.client else 'unknown';now=time.time();attempts=[t for t in login_attempts.get(remote,[]) if now-t<60]
        if len(attempts)>=20:raise HTTPException(429,'Too many login attempts')
        if not hmac.compare_digest(body.key,key):login_attempts[remote]=attempts+[now];raise HTTPException(401,'Incorrect operator key')
        token=secrets.token_urlsafe(32);sessions[token]=now+12*3600
        return {'token':token,'role':'operator','expires_at':sessions[token]}
    @app.get('/api/state',dependencies=[Depends(auth)])
    async def state():
        return {'threads':store.threads(),'runs':store.runs(),'approvals':store.approvals(),'continuity':continuity.snapshot(),'provider':runtime.provider.config(),'capabilities':tools.manifest(),'files':await asyncio.to_thread(tools.inventory),'milestone':'integration-02'}
    @app.get('/api/provider/health',dependencies=[Depends(auth)])
    async def model_health():return await runtime.provider.health()
    @app.put('/api/provider',dependencies=[Depends(auth)])
    async def configure(body:Provider):
        parsed=urlparse(body.base_url)
        if parsed.scheme not in ['http','https'] or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:raise ValueError('Use an http(s) provider origin without credentials/query/fragment')
        if parsed.path not in ['','/']:raise ValueError('Use the Ollama origin, e.g. http://127.0.0.1:11434, without /api/chat or /v1')
        if parsed.hostname not in ['127.0.0.1','localhost','::1'] and not body.allow_remote_context:raise ValueError('Explicitly authorize selected Sage/task context before using a non-loopback provider')
        cfg=body.model_dump();cfg['base_url']=cfg['base_url'].rstrip('/');store.setting('provider',cfg)
        store.add_event('host','Model connection configuration changed',{'model':cfg['model'],'remote_context_consent':cfg['allow_remote_context']})
        return await runtime.provider.health()
    @app.post('/api/threads',dependencies=[Depends(auth)])
    async def new_thread(body:NewThread):return store.new_thread(body.title)
    @app.get('/api/threads/{id}/messages',dependencies=[Depends(auth)])
    async def messages(id:str):return {'messages':store.messages(id)}
    @app.post('/api/chat',dependencies=[Depends(auth)])
    async def chat(body:Chat):return {'run_id':await runtime.begin_chat(body.thread_id,body.text,body.attachments)}
    @app.post('/api/tools/propose',dependencies=[Depends(auth)])
    async def tool(body:Proposal):return {'run_id':await runtime.begin_tool(body.tool,body.arguments)}
    @app.post('/api/approvals/{id}',dependencies=[Depends(auth)])
    async def decide(id:str,body:Decision):return await runtime.decide(id,body.approved,body.digest)
    @app.post('/api/runs/{id}/cancel',dependencies=[Depends(auth)])
    async def cancel(id:str):return await runtime.cancel(id)
    @app.get('/api/runs/{id}',dependencies=[Depends(auth)])
    async def get_run(id:str):return {k:v for k,v in store.run(id).items() if k!='state'}
    @app.get('/api/files',dependencies=[Depends(auth)])
    async def files():return {'files':await asyncio.to_thread(tools.inventory)}
    @app.post('/api/files/upload',dependencies=[Depends(auth)])
    async def upload(file:UploadFile=File(...)):
        raw=await file.read(MAX_UPLOAD+1)
        if len(raw)>MAX_UPLOAD:raise ValueError('Upload exceeds 12 MB')
        with tools.lock:
            meta=tools.ws.save_upload(file.filename or 'upload.bin',base64.b64encode(raw).decode());tools.capture(meta['path'],'operator-upload')
        store.add_event('file','File uploaded',{'path':meta['path'],'size':len(raw)})
        return meta
    @app.get('/api/files/preview',dependencies=[Depends(auth)])
    async def preview(path:str):
        p=tools.ws.safe_path(path)
        if not p.is_file():raise KeyError('File not found')
        return tools.dispatch('read_file',{'path':path,'max_bytes':200000},'operator-preview')
    @app.get('/api/files/content',dependencies=[Depends(auth)])
    async def content(path:str):
        p=tools.ws.safe_path(path)
        if not p.is_file():raise KeyError('File not found')
        return FileResponse(p,filename=p.name,media_type='application/octet-stream')
    @app.get('/api/files/revisions',dependencies=[Depends(auth)])
    async def revisions(path:str):tools.ws.safe_path(path);return {'revisions':store.revisions(path)}
    @app.get('/api/continuity',dependencies=[Depends(auth)])
    async def continuity_state():return continuity.snapshot()
    @app.get('/api/events',dependencies=[Depends(auth)])
    async def events(after:int=0):return {'events':store.public_events(after=after)}
    @app.get('/api/events/stream',dependencies=[Depends(auth)])
    async def stream(request:Request,after:int=0):
        async def rows():
            cursor=max(0,after);last_ping=time.monotonic()
            while not await request.is_disconnected():
                events=store.public_events(after=cursor)
                for e in events:cursor=e['id'];yield 'id: '+str(cursor)+'\ndata: '+json.dumps(e,ensure_ascii=False)+'\n\n'
                if time.monotonic()-last_ping>15:yield ': keepalive\n\n';last_ping=time.monotonic()
                await asyncio.sleep(.4)
        return StreamingResponse(rows(),media_type='text/event-stream',headers={'Cache-Control':'no-store','X-Accel-Buffering':'no'})
    @app.post('/api/lab/dataset',dependencies=[Depends(auth)])
    async def dataset(body:Proposal):
        if body.tool!='analyze_dataset':raise ValueError('Dataset route only accepts analyze_dataset')
        return {'run_id':await runtime.begin_tool(body.tool,body.arguments,'dataset')}
    @app.post('/api/lab/bio',dependencies=[Depends(auth)])
    async def bio(body:BioRequest):
        run=store.new_run('bio','Numerical simulator probe',state=body.model_dump())
        def probe():
            with bio_lock:
                np.random.seed(body.seed);network=IzhikevichNetwork({})
                metrics=[]
                for _ in range(body.steps):m=network.simulate_step();metrics.append({'step':m.step,'mean_firing_rate':m.mean_firing_rate,'active_fraction':m.active_fraction,'synaptic_weight':m.synaptic_weight})
                inh=sum(not network._is_excitatory(i%NEURONS_PER_COLUMN) for i in range(network.n_cortical))
                return clean({'quality':'experimental_numerical_probe_not_scientifically_validated','neurons':network.n,'steps':body.steps,'finite_voltage_state':bool(np.isfinite(network.v).all()),'actual_cortical_inhibitory':inh,'declared_cortical_inhibitory':network.n_inh,'metrics':metrics,'last':dataclasses.asdict(m),'known_issues':['E/I declaration and diagnostic masks remain inconsistent','Delay-slot ownership/clearing and physical-time units require repair','Band/state and cognitive labels are proxies, not neuroscience/welfare evidence'],'repairs_active':['Command-center constructor/array-shape/import repairs','GABA sign/clamp repair','BioMetrics factored out of torch dependency']})
        async def job():
            try:
                store.update_run(run['id'],status='running');result=await asyncio.to_thread(probe)
                if not runtime.cancelled(run['id']):store.update_run(run['id'],status='succeeded',result=result);runtime.emit('run','Experimental Bio probe completed',run['id'],quality=result['quality'])
            except Exception as e:
                if not runtime.cancelled(run['id']):store.update_run(run['id'],status='failed',error=str(e))
        runtime.start_task(run['id'],job);return {'run_id':run['id']}
    @app.get('/api/integrations',dependencies=[Depends(auth)])
    async def integrations():
        manifest=json.loads((PROJECT/'SOURCE_MAP.json').read_text())
        stages={
            'command-center':('spatial_connected','Original Atlas and 26 facility builders/nine rooms, recovered wrist geometry, touch-look/joystick, narration and shared canonical actions are connected. Illustrative brain shapes are not scientific measurements.'),
            'agent':('partially_connected','Original calculator and time plugins connect to the canonical registry. Plugin generation/Genesis/debug/delegation are retained but not activated.'),
            'local_ollama_arena_agent':('connected_foundation','Original workspace, eight file tools, document tools and registry schemas reused. Durable batched task/approval loop replaces volatile first-call-only loop. Kernel-isolated job execution is connected; external retrieval/media adapters still require configured workers.'),
            'gemma-avatar':('realtime_connected','Original realtime client/worklets, host-owned audio graph, PCM16 bridge, barge-in epochs, real STT/TTS workers, avatar and same conversation owner are connected. Engine/model configuration is explicit.'),
            'Sage':('autonomy_connected','Original moment/system/parser, opt-in bounded wakes/reviews, lookup/letters, private reflection and continuity share the host. User turns preempt stale wakes; profile changes remain approved proposals.'),
            'neural-sim':('training_connected','Actual HF/PEFT training worker with repaired composite SAM/replay/PCGrad/meta/distillation/EWC/token objectives and candidate evaluation, plus dataset/Bio paths. CUDA execution depends on hardware; advanced controller/rank and biology repairs remain explicit.'),
            'universe':('native_engine_connected','A new authoritative Godot World implements the blueprint baseline: native physics, partial ray-tested sensors, restricted participant intents and replay. Not a complete articulated humanoid or consciousness proof.')}
        return {'milestone':'integration-02','repositories':[{'name':r['name'],'commit':r['head'],'state':stages[r['name']][0],'detail':stages[r['name']][1],'files_preserved':sum(x['repository']==r['name'] for x in manifest['files'])} for r in manifest['snapshots']]}
    @app.get('/api/specifications/world',dependencies=[Depends(auth)])
    async def world_spec():return {'status':'specification_not_engine','text':(PROJECT/'vendor_sources/universe/living_avatar_subjective_experience_blueprint_v0_3.md').read_text()}
    extensions.mount(app,auth,Body)
    # Built UI and original avatar/worklet/font assets. These contain no private state.
    if (PROJECT/'web/assets').exists():app.mount('/assets',StaticFiles(directory=PROJECT/'web/assets'),name='assets')
    app.mount('/worklets',StaticFiles(directory=PROJECT/'web/worklets'),name='worklets');app.mount('/narration',StaticFiles(directory=PROJECT/'web/narration'),name='narration')
    app.mount('/vendor',StaticFiles(directory=PROJECT/'web/vendor'),name='vendor');app.mount('/avatars',StaticFiles(directory=PROJECT/'web/avatars'),name='avatars')
    @app.get('/')
    async def index():
        p=PROJECT/'web/index.html'
        if not p.exists():return JSONResponse({'detail':'Build the frontend: cd frontend && npm ci && npm run build'},503)
        return FileResponse(p)
    return app

def sqlite_integrity_error():
    import sqlite3
    return sqlite3.IntegrityError
