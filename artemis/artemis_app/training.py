"""Managed training/evaluation/checkpoint lifecycle and honest hardware reporting."""
from pathlib import Path
import os,sys,json,subprocess,threading,signal,secrets,hashlib,time,importlib.util,re
from .store import dump
class Training:
    def __init__(self,tools,store,root):self.tools=tools;self.store=store;self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True);self.processes={};self.hardware_cache=None;self.hardware_lock=threading.RLock();self.lease_lock=threading.RLock()
    def hardware(self):
        with self.hardware_lock:
            if self.hardware_cache:return self.hardware_cache
            if not importlib.util.find_spec('torch'):return {'available':False,'cuda':False,'reason':'Install optional training requirements; no fake GPU mode'}
            r=subprocess.run([sys.executable,'-c','import torch,json;print(json.dumps({"available":True,"cuda":torch.cuda.is_available(),"torch":torch.__version__,"devices":torch.cuda.device_count()}))'],capture_output=True,text=True,timeout=20)
            self.hardware_cache=json.loads(r.stdout) if r.returncode==0 else {'available':False,'cuda':False,'reason':r.stderr[-300:]};return self.hardware_cache
    def register_model(self,name,path):
        p=Path(path).expanduser().resolve()
        if not (p/'config.json').is_file() or not list(p.glob('*.safetensors')):raise ValueError('Register an actual local HF safetensors model directory, not GGUF/model-list/mesh placeholders')
        registry=self.store.settings('training_models',{});id=secrets.token_hex(8);registry[id]={'name':name[:80],'path':str(p),'config_sha256':hashlib.sha256((p/'config.json').read_bytes()).hexdigest()};self.store.setting('training_models',registry);return {'id':id,**registry[id]}
    def models(self):return [{'id':id,**v} for id,v in self.store.settings('training_models',{}).items()]
    def start(self,args,producer):
        with self.lease_lock:
            hardware=self.hardware()
            if not hardware['available']:raise ValueError(hardware['reason'])
            if args.get('device','cuda')=='cuda' and not hardware['cuda']:raise ValueError('No CUDA device on this host. Run this same GPU path locally or choose explicit CPU conformance.')
            if any(p.poll() is None for p in self.processes.values()):raise ValueError('A training resource lease is already held; pause/finish the current run')
            data=self.tools.ws.safe_path(args['path'])
            if not data.is_file() or data.stat().st_size>12_000_000:raise ValueError('Select an existing dataset within the workspace limit')
            if not args.get('fixture',False) and not self.store.settings('training_models',{}).get(args.get('model_id')):raise ValueError('Select a registered local model')
            run=self.store.new_run('training','GPU LoRA training' if args.get('device')=='cuda' else 'Explicit CPU training/conformance',state={'parent_proposal':producer})
            root=self.root/run['id'];root.mkdir();control=root/'control.json';control.write_text(dump({'status':'running'}))
            shutil=__import__('shutil');corpus=root/('dataset'+data.suffix);shutil.copy2(data,corpus)
            cfg={**args,'dataset_path':str(corpus),'output_dir':str(root),'control_file':str(control)}
            if not cfg.get('fixture',False):
                model=self.store.settings('training_models',{}).get(cfg.get('model_id'))
                if not model:raise ValueError('Select a registered local training model')
                cfg['model_path']=model['path']
            (root/'config.json').write_text(dump(cfg));(root/'lineage.json').write_text(dump({'dataset_sha256':hashlib.sha256(corpus.read_bytes()).hexdigest(),'source_recipe':'neural-sim trainer SAM/ReplayBuffer + repaired composite objective','parent':producer,'created':time.time(),'configuration':args}))
            env={'PATH':os.environ.get('PATH','/usr/bin'),'HOME':os.environ.get('HOME','/tmp'),'OMP_NUM_THREADS':'1','TOKENIZERS_PARALLELISM':'false','HF_HUB_OFFLINE':'1'}
            p=subprocess.Popen([sys.executable,'-m','artemis_app.training_worker',str(root/'config.json')],stdout=subprocess.PIPE,stderr=(root/'stderr.log').open('wb'),cwd=str(Path(__file__).resolve().parent.parent),env=env,start_new_session=True);self.processes[run['id']]=p;self.store.update_run(run['id'],status='running')
            threading.Thread(target=self.consume,args=(run['id'],p,root),daemon=True).start();return {'ok':True,'training_run_id':run['id'],'device':cfg['device'],'quality':'conformance_fixture' if cfg.get('fixture') else 'actual_local_hf_training','promotion':'No runtime model automatically changed'}
    def consume(self,id,p,root):
        metrics=[];result=None;error=None
        try:
            for raw in p.stdout:
                if len(raw)>100000:raise ValueError('Worker event too large')
                try:m=json.loads(raw)
                except json.JSONDecodeError:continue
                if m.get('type')=='training_step':
                    metrics.append(m);self.store.update_run(id,steps=m['step'],result={'metrics':metrics[-200:],'quality':m['quality'],'device':m['device']});self.store.add_event('training','Training step '+str(m['step']),{'run_id':id,'metrics':m})
                elif m.get('type')=='training_complete':result=m
                elif m.get('type')=='training_error':error=m['error']
            p.wait()
            if self.store.run(id)['status']=='cancelled':return
            if p.returncode or not result:raise ValueError(error or ('Training worker exit '+str(p.returncode)+'; '+(root/'stderr.log').read_text(errors='replace')[-500:]))
            self.store.update_run(id,status='succeeded',result={**result,'metrics':metrics[-200:]});self.store.add_event('training','Training candidate created',{'run_id':id,'steps':len(metrics),'device':result['device']})
        except Exception as e:
            if self.store.run(id)['status']!='cancelled':self.store.update_run(id,status='failed',error=str(e)[:1000])
        finally:self.processes.pop(id,None)
    def control(self,id,status):
        if status not in ['paused','running','cancelled']:raise ValueError('Invalid training control')
        p=self.root/id/'control.json'
        if not re.fullmatch('[a-f0-9]{32}',id) or not p.exists():raise ValueError('Training run not found')
        p.write_text(dump({'status':status}))
        if status=='cancelled':
            proc=self.processes.get(id)
            if proc:
                try:os.killpg(proc.pid,signal.SIGTERM)
                except ProcessLookupError:pass
            self.store.cancel(id)
        self.store.add_event('training','Training '+status,{'run_id':id});return {'ok':True,'control':status}
    def promote(self,args,producer):
        id=args['training_run_id'];r=self.store.run(id)
        if r['kind']!='training' or r['status']!='succeeded' or not r['result']:raise ValueError('Only completed evaluated candidates can be promoted')
        if 'conformance' in r['result']['quality']:raise ValueError('A tiny conformance model cannot be promoted as your production agent')
        result=r['result'];threshold=args.get('max_heldout_ce',10.)
        if result['heldout_ce']>threshold:raise ValueError('Candidate failed the explicit evaluation threshold')
        # This promotes a catalogued adapter candidate, not an implicit GGUF conversion/Ollama swap.
        self.store.setting('promoted_adapter',{'run_id':id,'path':str(self.root/id/'adapter'),'evaluation':{'heldout_ce':result['heldout_ce']},'approved_by':producer})
        return {'ok':True,'adapter_candidate':id,'effect':'Registered approved adapter; serving-model swap requires compatible HF inference adapter/export, not mesh conversion'}
    def close(self):
        pending=list(self.processes.items())
        for id,_ in pending:self.control(id,'cancelled')
        for _,p in pending:
            try:p.wait(timeout=10)
            except subprocess.TimeoutExpired:p.kill();p.wait()
