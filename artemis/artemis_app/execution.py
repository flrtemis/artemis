"""Mandatory kernel/container isolation, job-copy filesystem and reviewed promotion.
Never substitutes subprocess/regex/rlimits alone for an isolation boundary.
"""
from __future__ import annotations
import os,sys,subprocess,signal,resource,hashlib,json,shutil,time,threading,re
from pathlib import Path
from .store import uid,dump

MAX_FILES=2000;MAX_TOTAL=64_000_000;MAX_FILE=12_000_000
class Execution:
    def __init__(self,tools,root:Path):self.tools=tools;self.root=root;root.mkdir(parents=True,exist_ok=True);self.running={};self._availability=None
    def available(self):
        if self._availability is not None:return self._availability
        if shutil.which('bwrap'):
            try:
                r=subprocess.run(self.base_bwrap()+['/usr/bin/true'],capture_output=True,timeout=5)
                if r.returncode==0:self._availability={'available':True,'backend':'bubblewrap','boundary':'user/pid/mount/network/ipc namespaces'};return self._availability
            except (OSError,subprocess.TimeoutExpired):pass
        if shutil.which('docker'):
            try:
                if subprocess.run(['docker','info'],capture_output=True,timeout=5).returncode==0:self._availability={'available':True,'backend':'docker','boundary':'container, no network, unprivileged user, read-only root'};return self._availability
            except (OSError,subprocess.TimeoutExpired):pass
        self._availability={'available':False,'backend':None,'reason':'Working bubblewrap namespaces or a Docker daemon are required. No soft sandbox fallback.'};return self._availability
    def base_bwrap(self):
        return ['bwrap','--unshare-all','--die-with-parent','--new-session','--ro-bind','/usr','/usr','--symlink','usr/bin','/bin','--symlink','usr/lib','/lib','--symlink','usr/lib64','/lib64','--proc','/proc','--dev','/dev','--tmpfs','/tmp','--dir','/home/worker','--clearenv','--setenv','PATH','/usr/local/bin:/usr/bin:/bin','--setenv','HOME','/home/worker','--setenv','PYTHONDONTWRITEBYTECODE','1','--setenv','OPENBLAS_NUM_THREADS','1','--setenv','OMP_NUM_THREADS','1']
    @staticmethod
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU,(20,21));resource.setrlimit(resource.RLIMIT_AS,(768_000_000,768_000_000));resource.setrlimit(resource.RLIMIT_FSIZE,(MAX_FILE,MAX_FILE));resource.setrlimit(resource.RLIMIT_NOFILE,(128,128));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    def scan(self,root):
        found={};total=0
        for p in sorted(root.rglob('*')):
            if p.is_symlink():raise ValueError('Symlink outputs cannot be promoted')
            if p.is_file():
                rel=str(p.relative_to(root));size=p.stat().st_size;total+=size
                if size>MAX_FILE or total>MAX_TOTAL or len(found)>=MAX_FILES:raise ValueError('Execution workspace output quota exceeded')
                found[rel]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':size}
        return found
    def execute(self,args,producer,language='bash'):
        state=self.available()
        if not state['available']:raise ValueError(state['reason'])
        timeout=max(1,min(120,int(args.get('timeout',20))))
        id=uid();job=self.root/id;work=job/'workspace';work.mkdir(parents=True)
        with self.tools.lock:
            before=self.scan(self.tools.ws.root)
            expected=getattr(self.tools.local_context,'expected_precondition',None)
            if expected and expected.get('workspace')!=before:raise ValueError('Workspace changed before isolated job snapshot; approval no longer applies')
            for rel in before:
                src=self.tools.ws.safe_path(rel);target=work/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,target)
        (job/'before.json').write_text(dump(before));(job/'meta.json').write_text(dump({'producer':producer,'language':language,'created':time.time(),'status':'running'}))
        if language=='python':command=['/usr/local/bin/python3' if Path('/usr/local/bin/python3').exists() else '/usr/bin/python3','-c',args['code']]
        else:command=['/bin/bash','-lc',args['command']]
        if state['backend']=='bubblewrap':cmd=self.base_bwrap()+['--bind',str(work),'/workspace','--chdir','/workspace']+command
        else:
            # Prebuilt worker image must exist; do not silently pull/build during an approved action.
            name='artemis-'+id
            cmd=['docker','run','--rm','--name',name,'--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--pids-limit','32','--memory','768m','--cpus','1','--user',str(os.getuid())+':'+str(os.getgid()),'--tmpfs','/tmp:rw,noexec,nosuid,size=32m','--mount','type=bind,src='+str(work)+',dst=/workspace','-w','/workspace','artemis-worker:local']+(command if language=='bash' else ['python','-c',args['code']])
        started=time.monotonic();reason=None
        with (job/'stdout').open('wb') as out,(job/'stderr').open('wb') as err:
            p=subprocess.Popen(cmd,stdout=out,stderr=err,stdin=subprocess.DEVNULL,start_new_session=True,env={'PATH':os.environ.get('PATH','/usr/bin:/bin')},preexec_fn=self.limits if state['backend']=='bubblewrap' else None)
            self.running[producer]=(p,id)
            try:
                while p.poll() is None:
                    if time.monotonic()-started>timeout:reason='Execution timeout';break
                    if (job/'stdout').stat().st_size+(job/'stderr').stat().st_size>300000:reason='Output limit';break
                    try:self.scan(work)
                    except ValueError as e:reason=str(e);break
                    time.sleep(.08)
                if reason:self.kill(p,id,state['backend'])
                p.wait(timeout=5)
            finally:
                self.running.pop(producer,None)
                if p.poll() is None:self.kill(p,id,state['backend'])
        after=self.scan(work)
        changes=[{'path':path,'before':before.get(path),'after':after.get(path),'operation':'delete' if path not in after else 'create' if path not in before else 'modify'} for path in sorted(set(before)|set(after)) if before.get(path)!=after.get(path)]
        (job/'changes.json').write_text(dump(changes));(job/'meta.json').write_text(dump({'producer':producer,'language':language,'status':'finished','returncode':p.returncode}))
        return {'ok':p.returncode==0 and reason is None,'job_id':id,'backend':state['backend'],'returncode':p.returncode,'stdout':(job/'stdout').read_text(errors='replace')[:100000],'stderr':(job/'stderr').read_text(errors='replace')[:100000],'error':reason,'changes':changes,'promotion':'No job changes touch your real workspace until a second explicit approval','elapsed_s':round(time.monotonic()-started,3)}
    def kill(self,p,id,backend):
        if backend=='docker':subprocess.run(['docker','kill','artemis-'+id],capture_output=True,timeout=5)
        try:os.killpg(p.pid,signal.SIGKILL)
        except ProcessLookupError:pass
    def cancel(self,producer):
        item=self.running.get(producer)
        if item:self.kill(item[0],item[1],self.available()['backend'])
    def job(self,id):
        if not re.fullmatch('[a-f0-9]{32}',str(id)):raise ValueError('Invalid execution job ID')
        p=self.root/id
        if not (p/'changes.json').exists():raise ValueError('Finished execution job not found')
        return p,json.loads((p/'changes.json').read_text())
    def promotion_precondition(self,id):
        p,changes=self.job(id);return {'job_manifest':hashlib.sha256((p/'changes.json').read_bytes()).hexdigest(),'workspace':{x['path']:self.fingerprint(x['path']) for x in changes}}
    def fingerprint(self,path):
        p=self.tools.ws.safe_path(path)
        return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size} if p.is_file() else None
    def promote(self,args,producer):
        p,changes=self.job(args['job_id']);before=json.loads((p/'before.json').read_text())
        # Entire change set is validated before the first filesystem mutation.
        for x in changes:
            target=self.tools.ws.safe_path(x['path']);source=(p/'workspace'/x['path']).resolve();source.relative_to((p/'workspace').resolve())
            if self.fingerprint(x['path'])!=before.get(x['path']):raise ValueError('Original workspace changed during the execution job; promotion blocked')
            if x['after'] and (source.is_symlink() or not source.is_file() or self.fingerprint_job(source)!=x['after']):raise ValueError('Job output changed; promotion blocked')
        with self.tools.lock:
            for x in changes:
                target=self.tools.ws.safe_path(x['path']);self.tools.capture(x['path'],producer)
                if x['operation']=='delete':target.unlink(missing_ok=True)
                else:target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p/'workspace'/x['path'],target);self.tools.capture(x['path'],producer)
        return {'ok':True,'job_id':args['job_id'],'promoted':changes}
    @staticmethod
    def fingerprint_job(p):return {'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size}
