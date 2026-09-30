"""Canonical registry reuses Arena tools and selected Agent/Neural/Sage implementations.
Unsafe/external adapters are preserved but unavailable until their safe workers are connected.
Schema checks, approvals and revisions are host-enforced, never model-controlled.
"""
from __future__ import annotations
import base64,dataclasses,hashlib,json,math,mimetypes,re,threading,os
from pathlib import Path
from urllib.parse import quote
from jsonschema import Draft202012Validator
from vendor_sources.local_ollama_arena_agent.local_arena_agent.workspace import Workspace
from vendor_sources.local_ollama_arena_agent.local_arena_agent.tools import build_registry
from vendor_sources.local_ollama_arena_agent.local_arena_agent.tools.base import Tool
from vendor_sources.local_ollama_arena_agent.local_arena_agent.config import DEFAULT_CONFIG,deep_merge
from vendor_sources.agent.tools.calculator import execute as calculator
from vendor_sources.agent.tools.current_time import execute as legacy_time
from vendor_sources.agent.tools.directory_manager import execute as legacy_directory
from vendor_sources.neural_sim.dataset_analyzer import parse_dataset
from .store import dump

MAX_UPLOAD=12_000_000
SUPPORTED_DATASETS={'.csv','.json','.txt','.md','.rst'}
def digest(x):return hashlib.sha256(dump(x).encode()).hexdigest()
def clean(x):
    if dataclasses.is_dataclass(x):return clean(dataclasses.asdict(x))
    if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(v) for v in x]
    if isinstance(x,float) and not math.isfinite(x):return None
    if hasattr(x,'item'):
        try:return clean(x.item())
        except (ValueError,TypeError):pass
    if hasattr(x,'tolist'):return clean(x.tolist())
    return x

class UnifiedWorkspace(Workspace):
    def safe_path(self,user_path,*,base='workspace'):
        raw=str(user_path or '.').replace('\\','/')
        if raw.startswith('/') or re.match(r'^[A-Za-z]:',raw):raise ValueError('Use a relative workspace path, not a host path')
        return super().safe_path(raw,base=base)
    def meta(self,path):
        path.resolve().relative_to(self.root)
        m=super().meta(path);m['preview_url']='/api/files/content?path='+quote(m['path'],safe='')
        if not path.is_dir():m['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        return m
    def save_upload(self,filename,data_base64):
        name=str(filename).replace('\\','/').split('/')[-1]
        if not name or name in ['.','..']:raise ValueError('Invalid filename')
        data=base64.b64decode(data_base64,validate=True)
        if len(data)>MAX_UPLOAD:raise ValueError('Upload exceeds 12 MB')
        return super().save_upload(name,base64.b64encode(data).decode())

class Tools:
    def __init__(self,root:Path,revision_root:Path,store,continuity):
        self.store=store;self.continuity=continuity;self.revision_root=revision_root;revision_root.mkdir(parents=True,exist_ok=True)
        self.ws=UnifiedWorkspace(root,root/'outputs');self.lock=threading.RLock()
        self.registry=build_registry(self.ws,deep_merge(DEFAULT_CONFIG,{'auto_approve':False,'sandbox':{'backend':'disabled'}}))
        self.registry.get('list_files').function=self.safe_listing
        self.unavailable={
            'run_bash':'Mandatory isolated execution worker is not yet connected. Unsafe soft execution is disabled.',
            'fetch_page':'Egress/SSRF worker is not yet connected.',
            'web_search':'Retrieval provider and egress policy are not yet connected.',
            'image_search':'Image-search provider and egress policy are not yet connected.',
            'generate_image':'Image provider worker is not yet connected.',
            'generate_video':'Video provider worker is not yet connected.',
            'generate_speech':'Speech provider worker is not yet connected.',
            'transcribe_audio':'Speech recognition worker is not yet connected.'}
        self.registry.add(Tool('make_directory','Create a scoped workspace directory using the original Agent directory capability.',{'type':'object','properties':{'path':{'type':'string','minLength':1},'recursive':{'type':'boolean'}},'required':['path']},self.make_directory,True,'files'))
        self.registry.add(Tool('calculator','Perform bounded arithmetic using the existing Agent calculator.',{'type':'object','properties':{'operation':{'type':'string','enum':['add','subtract','multiply','divide']},'numbers':{'type':'array','items':{'type':'number','minimum':-1e12,'maximum':1e12},'minItems':1,'maxItems':128}},'required':['operation','numbers']},self.calculate,category='utilities'))
        self.registry.add(Tool('current_time','Read the shared timezone-aware local clock.',{'type':'object','properties':{}},lambda a:{'ok':True,'text':legacy_time(),'local_time':self.continuity.clock.fmt(seconds=True),'timezone':self.continuity.clock.tz_name},category='continuity'))
        self.registry.add(Tool('analyze_dataset','Analyze actual CSV, JSON or text statistics. Not a simulated cognitive walkthrough.',{'type':'object','properties':{'path':{'type':'string','minLength':1}},'required':['path']},self.analyze,category='lab'))
        self.registry.add(Tool('remember','Persist an explicit salient memory in Sage.',{'type':'object','properties':{'text':{'type':'string','minLength':1,'maxLength':4000},'importance':{'type':'integer','minimum':1,'maximum':5}},'required':['text']},self.remember,True,'continuity'))
        self.registry.add(Tool('recall','Use Sage’s weighted relevance/importance/recency recall.',{'type':'object','properties':{'query':{'type':'string','maxLength':4000},'limit':{'type':'integer','minimum':1,'maximum':20}},'required':['query']},lambda a:{'ok':True,'memories':self.store.recall(a['query'],a.get('limit',6))},category='continuity'))
        self.registry.add(Tool('add_goal','Persist a goal in Sage’s wants table.',{'type':'object','properties':{'text':{'type':'string','minLength':1,'maxLength':4000}},'required':['text']},lambda a:{'ok':True,'goal':self.store.add_want(a['text'])},True,'continuity'))
        self.registry.add(Tool('update_self_profile','Propose a bounded versioned self-profile edit.',{'type':'object','properties':{'text':{'type':'string','minLength':40,'maxLength':4000},'reason':{'type':'string','maxLength':120}},'required':['text']},self.update_self,True,'continuity'))
    def make_directory(self,args):
        path=self.ws.safe_path(args['path'])
        result=legacy_directory(action='create',path=str(path),recursive=args.get('recursive',True))
        if isinstance(result,str) and result.startswith('Error:'):return {'ok':False,'error':result}
        return {'ok':True,'path':self.ws.rel(path),'meta':self.ws.meta(path)}
    def safe_listing(self,args):
        # Adapt Arena's walk/depth algorithm; outside symlinks cannot leak metadata.
        path=self.ws.safe_path(args.get('path','.'));depth=int(args.get('max_depth',2));hidden=args.get('include_hidden',False)
        if not path.exists():return {'ok':False,'error':'Path not found'}
        if path.is_file():return {'ok':True,'entries':[self.ws.meta(path)]}
        entries=[]
        for root,dirs,files in os.walk(path,followlinks=False):
            base=Path(root)
            dirs[:]=[d for d in dirs if (hidden or not d.startswith('.')) and not (base/d).is_symlink()]
            if len(base.parts)-len(path.parts)>=depth:dirs[:]=[]
            for name in sorted(dirs)+sorted(files):
                if not hidden and name.startswith('.'):continue
                child=base/name
                try:child.resolve().relative_to(self.ws.root)
                except ValueError:continue
                entries.append(self.ws.meta(child))
                if len(entries)>=2000:return {'ok':True,'entries':entries,'truncated':True}
        return {'ok':True,'entries':entries,'truncated':False}
    def calculate(self,args):
        result=calculator(**args)
        if isinstance(result,dict) and isinstance(result.get('result'),float) and not math.isfinite(result['result']):return {'ok':False,'error':'Arithmetic result exceeds finite numeric range'}
        return {'ok':True,**result} if isinstance(result,dict) else {'ok':False,'error':result}
    def remember(self,args):
        m=self.store.add_memory(args['text'],args.get('importance',3));self.store.add_event('memory',args['text'],{'memory_id':m['id']});return {'ok':True,'memory':m}
    def update_self(self,args):
        accepted,why=self.continuity.profile.propose(args['text'],args.get('reason','Operator-approved change'))
        if accepted:self.store.add_event('self_edit',args.get('reason','Profile updated'))
        return {'ok':accepted,'message':why,'versions':self.continuity.profile.versions()}
    def manifest(self):
        rows=[]
        for t in self.registry._tools.values():
            schema=self.schema(t.name)
            rows.append({'name':t.name,'description':t.description,'category':t.category,'requires_approval':t.requires_approval,'available':t.name not in self.unavailable,'unavailable_reason':self.unavailable.get(t.name),'parameters':schema})
        return rows
    def schemas(self):
        return [{'type':'function','function':{'name':t.name,'description':t.description,'parameters':self.schema(t.name)}} for t in self.registry._tools.values() if t.name not in self.unavailable]
    def schema(self,name):
        t=self.registry.get(name)
        if not t:raise ValueError('Unknown tool')
        schema=json.loads(json.dumps(t.parameters));schema['additionalProperties']=False
        for k,v in schema.get('properties',{}).items():
            if v.get('type')=='string':v.setdefault('maxLength',250000 if k in ['content','new_text','old_text'] else 4000)
            if k=='max_bytes':v.update(minimum=1,maximum=250000)
            if k=='max_depth':v.update(minimum=1,maximum=6)
        return schema
    def validate(self,name,args):
        t=self.registry.get(name)
        if not t:raise ValueError('Unknown tool: '+name)
        if name in self.unavailable:raise ValueError(self.unavailable[name])
        errors=list(Draft202012Validator(self.schema(name)).iter_errors(args))
        if errors:raise ValueError('Invalid tool arguments: '+errors[0].message)
        dump(args) # also rejects NaN/infinity
        for key,value in args.items():
            if key in ['path','source','destination','source_path','destination_path','output_path'] and isinstance(value,str):self.ws.safe_path(value)
        if name in ['delete_file','move_file']:
            p=args.get('path') or args.get('source') or args.get('source_path')
            if p and self.ws.safe_path(p)==self.ws.root:raise ValueError('Cannot delete/move the workspace root')
        return t
    def fingerprint(self,name,args):
        result={}
        if name=='promote_execution_changes' and hasattr(self,'execution'):return self.execution.promotion_precondition(args['job_id'])
        if name in ['run_bash','run_python'] and hasattr(self,'execution'):return {'workspace':self.execution.scan(self.ws.root)}
        for key,value in args.items():
            if key not in ['path','source','destination','source_path','destination_path','output_path'] or not isinstance(value,str):continue
            p=self.ws.safe_path(value)
            if p.is_file():result[value]={'kind':'file','sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
            elif p.is_dir():result[value]={'kind':'directory','listing':digest(sorted(str(x.relative_to(p)) for x in p.rglob('*')))}
            else:result[value]={'kind':'absent'}
        if name=='update_self_profile':result['self_profile']={'sha256':hashlib.sha256(self.continuity.profile.read().encode()).hexdigest()}
        return result
    def proposal(self,name,args):
        self.validate(name,args)
        pre=self.fingerprint(name,args);return pre,digest({'tool':name,'arguments':args,'precondition':pre})
    def capture(self,path,producer):
        p=self.ws.safe_path(path)
        if not p.is_file():return
        data=p.read_bytes();sha=hashlib.sha256(data).hexdigest();target=self.revision_root/sha
        if not target.exists():target.write_bytes(data)
        previous=self.store.revisions(path)
        if not previous or previous[0]['sha256']!=sha:self.store.revision(path,sha,producer)
        self.store.artifact(path,sha,len(data),mimetypes.guess_type(p.name)[0] or 'application/octet-stream',producer)
    def inventory(self):
        result=self.registry.dispatch('list_files',{'path':'.','max_depth':6});entries=result.get('entries',[])
        for e in entries:
            if not e['is_dir']:
                self.store.artifact(e['path'],e['sha256'],e['size'],e['mime'])
        return entries
    def dispatch(self,name,args,producer):
        self.validate(name,args)
        if hasattr(self,'local_context'):self.local_context.producer=producer
        if name in ['run_bash','run_python','start_training']:
            result=clean(self.registry.dispatch(name,args));dump(result);return result
        with self.lock:
            t=self.registry.get(name)
            if t.requires_approval:
                for k in ['path','source','source_path']:
                    if k in args:self.capture(args[k],producer)
            result=clean(self.registry.dispatch(name,args))
            # Normalize legacy preview URLs and record actual new outputs.
            for k in (['path','output_path','destination','destination_path'] if t.requires_approval else []):
                if k in args:
                    p=self.ws.safe_path(args[k])
                    if p.is_file():self.capture(self.ws.rel(p),producer)
            if t.requires_approval and isinstance(result.get('meta'),dict) and not result['meta'].get('is_dir'):self.capture(result['meta']['path'],producer)
            if t.requires_approval and isinstance(result.get('file'),dict) and not result['file'].get('is_dir'):self.capture(result['file']['path'],producer)
            dump(result)
            return result
    def analyze(self,args):
        p=self.ws.safe_path(args['path'])
        if not p.is_file():raise ValueError('Dataset file not found')
        if p.suffix.lower() not in SUPPORTED_DATASETS:raise ValueError('This milestone explicitly supports CSV, JSON and text; other format adapters are not connected')
        if p.stat().st_size>MAX_UPLOAD:raise ValueError('Dataset exceeds limit')
        raw=p.read_bytes()
        if p.suffix.lower()=='.json':json.loads(raw) # no malformed JSON mislabeled success
        ds=parse_dataset(raw,p.name)
        cols=[{k:clean(getattr(c,k)) for k in ['name','dtype','n_unique','missing_frac','mean','std','is_date']} for c in ds.csv_columns]
        return clean({'ok':True,'quality':'computed_statistics_with_heuristic_findings','path':args['path'],'file_type':ds.file_type,'bytes':ds.raw_size,'shape':ds.shape,'logical_units':ds.n_logical_units,'complexity_score':ds.complexity_score,'complexity_quality':'heuristic','findings':ds.key_findings,'columns':cols,'source':'neural-sim/dataset_analyzer.py (shared duplicate consolidated)','cognitive_frames':'not emitted: those are scripted demonstrations, not measurements'})
