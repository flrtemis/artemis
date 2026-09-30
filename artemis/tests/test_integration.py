"""Real integration contracts with deterministic provider fixtures, not real LLM/GPU claims."""
import asyncio,json,time,zipfile,hashlib,sqlite3
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from artemis_app.api import create_app
from artemis_app.runtime import OllamaGateway
from artemis_app.bio_engine import IzhikevichNetwork
import numpy as np

class FixtureProvider:
    def __init__(self,messages):self.responses=list(messages);self.requests=[]
    def config(self):return {'base_url':'http://127.0.0.1:11434','model':'fixture-model','allow_remote_context':False}
    async def health(self):return {'connected':True,'models':['fixture-model'],'configured_model':'fixture-model','model_ready':True,'base_url':'http://127.0.0.1:11434'}
    async def chat(self,messages,schemas,*,config=None):
        self.requests.append({'messages':json.loads(json.dumps(messages)),'schemas':schemas,'config':config})
        return self.responses.pop(0)

def call(name,args):return {'function':{'name':name,'arguments':args}}
def unlock(client):
    r=client.post('/api/auth',json={'key':'test-operator-key'});assert r.status_code==200
    client.headers['Authorization']='Bearer '+r.json()['token'];return client

def wait(client,id,status='succeeded'):
    for _ in range(300):
        r=client.get('/api/runs/'+id).json()
        if r['status']==status:return r
        if r['status']=='failed' and status!='failed':pytest.fail(r.get('error'))
        time.sleep(.01)
    pytest.fail('Timed out waiting for '+status+': '+str(r))

def proposal(client,tool,args):
    r=client.post('/api/tools/propose',json={'tool':tool,'arguments':args});assert r.status_code==200,r.text
    s=client.get('/api/state').json();a=next(a for a in s['approvals'] if a['run_id']==r.json()['run_id']);return r.json()['run_id'],a

def approve(client,a,yes=True):return client.post('/api/approvals/'+a['id'],json={'approved':yes,'digest':a['digest']})
@pytest.fixture
def host(tmp_path):
    app=create_app(tmp_path,'test-operator-key')
    with TestClient(app) as c:yield app,unlock(c)

def test_requires_auth_and_wrong_key(tmp_path):
    with TestClient(create_app(tmp_path,'test-operator-key')) as c:
        assert c.get('/api/state').status_code==401
        assert c.post('/api/auth',json={'key':'wrong'}).status_code==401
        assert c.get('/healthz').json()['ok']

def test_origin_mutation_guard(host):
    app,c=host
    assert c.post('/api/threads',json={},headers={'Origin':'https://untrusted.example'}).status_code==403

def test_schema_required_and_unknown_fields(host):
    app,c=host
    assert c.post('/api/tools/propose',json={'tool':'write_file','arguments':{'path':'empty.txt'}}).status_code==400
    assert c.post('/api/tools/propose',json={'tool':'write_file','arguments':{'path':'empty.txt','content':'x','host_override':'/tmp'}}).status_code==400
    assert not (app.state.tools.ws.root/'empty.txt').exists()
    assert not c.get('/api/state').json()['approvals']

def test_approved_write_and_no_duplicate_replay(host):
    app,c=host;id,a=proposal(c,'write_file',{'path':'notes/test.txt','content':'actual integration'})
    assert not (app.state.tools.ws.root/'notes/test.txt').exists()
    assert approve(c,a).status_code==200
    assert (app.state.tools.ws.root/'notes/test.txt').read_text()=='actual integration'
    assert wait(c,id)['result']['ok']
    assert approve(c,a).status_code==400
    assert c.get('/api/files/content',params={'path':'notes/test.txt'}).content==b'actual integration'

def test_denial_has_no_mutation(host):
    app,c=host;id,a=proposal(c,'write_file',{'path':'denied.txt','content':'no'})
    assert approve(c,a,False).status_code==200
    assert not (app.state.tools.ws.root/'denied.txt').exists()
    assert c.get('/api/runs/'+id).json()['status']=='failed'

def test_proposal_digest_tamper(host):
    app,c=host;id,a=proposal(c,'write_file',{'path':'tamper.txt','content':'safe'})
    assert c.post('/api/approvals/'+a['id'],json={'approved':True,'digest':'f'*64}).status_code==400
    assert not (app.state.tools.ws.root/'tamper.txt').exists()

def test_revision_drift_blocks_approval(host):
    app,c=host;p=app.state.tools.ws.root/'drift.txt';p.write_text('before')
    id,a=proposal(c,'write_file',{'path':'drift.txt','content':'proposed'})
    p.write_text('external change');r=approve(c,a).json()
    assert not r['result']['ok'] and 'changed since proposal' in r['result']['error']
    assert p.read_text()=='external change'

def test_paths_and_symlinks_blocked(host,tmp_path):
    app,c=host
    for path in ['../escape.txt','/etc/passwd','C:\\outside.txt']:
        assert c.post('/api/tools/propose',json={'tool':'write_file','arguments':{'path':path,'content':'bad'}}).status_code==400
    outside=tmp_path/'outside.txt';outside.write_text('synthetic private sentinel')
    (app.state.tools.ws.root/'escape').symlink_to(outside)
    assert c.get('/api/files/preview',params={'path':'escape'}).status_code==400
    assert c.post('/api/tools/propose',json={'tool':'delete_file','arguments':{'path':'.'}}).status_code==400

def test_safe_upload_collision_and_utf8_download(host):
    app,c=host
    a=c.post('/api/files/upload',files={'file':('../sample.txt',b'one')}).json()
    b=c.post('/api/files/upload',files={'file':('../sample.txt',b'two')}).json()
    assert a['name']=='sample.txt' and b['name']=='sample-2.txt'
    f=c.post('/api/files/upload',files={'file':('日本語.txt','hello'.encode())}).json()
    r=c.get('/api/files/content',params={'path':f['path']});assert r.status_code==200 and r.content==b'hello'

def test_shell_and_external_workers_cannot_bypass(host):
    app,c=host
    for name,args in [('fetch_page',{'url':'http://127.0.0.1/secret'}),('generate_image',{'prompt':'test'})]:
        assert c.post('/api/tools/propose',json={'tool':name,'arguments':args}).status_code==400
    schemas=app.state.tools.schemas()
    if app.state.runtime.extensions.execution.available()['available']:
        id,a=proposal(c,'run_bash',{'command':'echo x'});assert c.get('/api/runs/'+id).json()['status']=='awaiting_approval'
    else:assert all(s['function']['name']!='run_bash' for s in schemas)

def test_current_time_and_original_calculator(host):
    app,c=host
    r=c.post('/api/tools/propose',json={'tool':'calculator','arguments':{'operation':'multiply','numbers':[6,7]}}).json();result=wait(c,r['run_id'])['result'];assert result['result']==42
    r=c.post('/api/tools/propose',json={'tool':'current_time','arguments':{}}).json();assert wait(c,r['run_id'])['result']['timezone']=='America/New_York'

def test_actual_dataset_analysis_no_cognitive_demo(host):
    app,c=host
    f=c.post('/api/files/upload',files={'file':('sample.csv',b'age,city\n21,A\n30,B\n,A\n')}).json()
    r=c.post('/api/lab/dataset',json={'tool':'analyze_dataset','arguments':{'path':f['path']}}).json();d=wait(c,r['run_id'])['result']
    assert d['shape']==[3,2] and len(d['columns'])==2 and d['file_type']=='csv'
    assert d['columns'][0]['mean']==25.5 and d['quality']=='computed_statistics_with_heuristic_findings'
    assert 'not emitted' in d['cognitive_frames']

def test_unsupported_format_honest_failure(host):
    app,c=host;f=c.post('/api/files/upload',files={'file':('data.yaml',b'age: 21')}).json()
    r=c.post('/api/lab/dataset',json={'tool':'analyze_dataset','arguments':{'path':f['path']}}).json()
    result=wait(c,r['run_id'],'failed');assert 'explicitly supports' in result['error']

@pytest.mark.parametrize('name,args,ext',[('create_docx',{'path':'output/a.docx','title':'Integration','paragraphs':['real output']},'.docx'),('create_xlsx',{'path':'output/a.xlsx','sheets':[{'name':'Test','rows':[['a','b'],[1,2]]}]},'.xlsx'),('create_pptx',{'path':'output/a.pptx','title':'Integration','slides':[{'title':'One','bullets':['two']}]},'.pptx'),('create_pdf',{'path':'output/a.pdf','title':'Integration','lines':['one']},'.pdf'),('create_csv',{'path':'output/a.csv','rows':[['a','b'],[1,2]]},'.csv')])
def test_actual_document_tools(host,name,args,ext):
    app,c=host;id,a=proposal(c,name,args);assert approve(c,a).status_code==200
    r=wait(c,id);assert r['result']['ok'];p=app.state.tools.ws.safe_path(args['path']);assert p.stat().st_size>0
    if ext in ['.docx','.xlsx','.pptx']:
        with zipfile.ZipFile(p) as z:assert z.testzip() is None and '[Content_Types].xml' in z.namelist()
    if ext=='.pdf':assert p.read_bytes().startswith(b'%PDF')

def test_memory_private_projection_and_profile_persistence(tmp_path):
    app=create_app(tmp_path,'test-operator-key')
    with TestClient(app) as c:
        unlock(c);id,a=proposal(c,'remember',{'text':'Synthetic test memory: preserve useful work','importance':5});assert approve(c,a).status_code==200
        app.state.store.add_private('NEVER_PUBLIC_SENTINEL');app.state.store.add_event('wake','NEVER_PUBLIC_SENTINEL',{'raw':'NEVER_PUBLIC_SENTINEL'})
        snapshot=c.get('/api/state').text;events=c.get('/api/events').text
        assert 'NEVER_PUBLIC_SENTINEL' not in snapshot+events
        assert c.get('/api/state').json()['continuity']['private_count']==1
    with TestClient(create_app(tmp_path,'test-operator-key')) as c:
        unlock(c);data=c.get('/api/state').json();assert any('Synthetic test memory' in m['text'] for m in data['continuity']['memories']);assert data['continuity']['versions']

def test_approval_survives_restart_without_auto_execution(tmp_path):
    app=create_app(tmp_path,'test-operator-key')
    with TestClient(app) as c:
        unlock(c);id,a=proposal(c,'write_file',{'path':'restart.txt','content':'once'})
    app2=create_app(tmp_path,'test-operator-key')
    with TestClient(app2) as c:
        unlock(c);assert not (app2.state.tools.ws.root/'restart.txt').exists();assert any(x['id']==a['id'] for x in c.get('/api/state').json()['approvals']);assert approve(c,a).status_code==200
        assert (app2.state.tools.ws.root/'restart.txt').read_text()=='once'

def test_ambiguous_side_effect_never_replayed(tmp_path):
    app=create_app(tmp_path,'test-operator-key')
    with TestClient(app) as c:
        unlock(c);id,a=proposal(c,'append_file',{'path':'once.txt','content':'once'})
        app.state.store.claim_approval(a['id']);(app.state.tools.ws.root/'once.txt').write_text('once')
    app2=create_app(tmp_path,'test-operator-key')
    with TestClient(app2) as c:
        unlock(c);assert c.get('/api/runs/'+id).json()['status']=='interrupted';assert approve(c,a).status_code==400;assert (app2.state.tools.ws.root/'once.txt').read_text()=='once'

def test_all_batched_read_calls_and_thread_isolation(tmp_path):
    fake=FixtureProvider([{'role':'assistant','content':'','tool_calls':[call('read_file',{'path':'one.txt'}),call('read_file',{'path':'two.txt'})]},{'role':'assistant','content':'Fixture completed both reads.'}]);app=create_app(tmp_path,'test-operator-key',fake)
    for name,content in [('one.txt','first'),('two.txt','second')]: (app.state.tools.ws.root/name).write_text(content)
    with TestClient(app) as c:
        unlock(c);t=c.post('/api/threads',json={}).json()['id'];other=c.post('/api/threads',json={}).json()['id']
        id=c.post('/api/chat',json={'thread_id':t,'text':'Read both files'}).json()['run_id'];wait(c,id)
        tool_results=[m for m in fake.requests[1]['messages'] if m['role']=='tool'];assert len(tool_results)==2
        assert [json.loads(m['content'])['text'] for m in tool_results]==['first','second']
        assert len(c.get('/api/threads/'+t+'/messages').json()['messages'])==2
        assert c.get('/api/threads/'+other+'/messages').json()['messages']==[]
        assert fake.requests[0]['config']['model']=='fixture-model'

def test_batched_mutations_resumed_one_by_one(tmp_path):
    fake=FixtureProvider([{'role':'assistant','content':'','tool_calls':[call('write_file',{'path':'one.txt','content':'one'}),call('write_file',{'path':'two.txt','content':'two'})]},{'role':'assistant','content':'Fixture completed the writes.'}]);app=create_app(tmp_path,'test-operator-key',fake)
    with TestClient(app) as c:
        unlock(c);t=c.post('/api/threads',json={}).json()['id'];id=c.post('/api/chat',json={'thread_id':t,'text':'Write two files'}).json()['run_id'];wait(c,id,'awaiting_approval')
        assert c.post('/api/chat',json={'thread_id':t,'text':'Another concurrent turn'}).status_code==409
        a=c.get('/api/state').json()['approvals'][0];assert a['args']['path']=='one.txt';assert approve(c,a).status_code==200
        wait(c,id,'awaiting_approval');a2=c.get('/api/state').json()['approvals'][0];assert a2['args']['path']=='two.txt';assert approve(c,a2).status_code==200
        r=wait(c,id);assert r['steps']==2
        assert len([m for m in fake.requests[-1]['messages'] if m['role']=='tool'])==2
        assert (app.state.tools.ws.root/'one.txt').read_text()=='one' and (app.state.tools.ws.root/'two.txt').read_text()=='two'

def test_cancelled_pending_mutation_does_not_execute(host):
    app,c=host;id,a=proposal(c,'write_file',{'path':'cancel.txt','content':'not now'})
    assert c.post('/api/runs/'+id+'/cancel').status_code==200
    assert approve(c,a).status_code==400 and not (app.state.tools.ws.root/'cancel.txt').exists()

def test_bio_gaba_repair_and_probe_contract(host):
    app,c=host;network=IzhikevichNetwork({});network.W_cortical[:]=0;network.W_cortical[0,6]=-.5;fired=np.zeros(network.n,dtype=bool);fired[0]=True;network._update_synaptic_conductances(fired)
    assert network._g_gaba[6]<0
    id=c.post('/api/lab/bio',json={'steps':5,'seed':17}).json()['run_id'];r=wait(c,id)['result'];assert r['finite_voltage_state'] and r['neurons']==1090 and r['actual_cortical_inhibitory']==50 and r['declared_cortical_inhibitory']==200
    assert 'not_scientifically_validated' in r['quality'] and r['known_issues']

def test_seven_sources_and_no_world_engine_claim(host):
    app,c=host;data=c.get('/api/integrations').json();assert len(data['repositories'])==7
    u=next(r for r in data['repositories'] if r['name']=='universe');assert u['state'] in ['specification_preserved','native_engine_connected']
    assert c.get('/api/specifications/world').json()['status']=='specification_not_engine'

def test_remote_context_requires_explicit_consent(host):
    app,c=host;r=c.put('/api/provider',json={'base_url':'https://example.com','model':'x','allow_remote_context':False});assert r.status_code==400

def test_sage_backup_import_includes_wal(tmp_path):
    from scripts.import_sage import import_sage
    source=tmp_path/'original';source.mkdir();db=sqlite3.connect(source/'awake.sqlite3');db.execute('PRAGMA journal_mode=WAL');db.execute('CREATE TABLE test(value TEXT)');db.execute("INSERT INTO test VALUES('synthetic')");db.commit();(source/'self.md').write_text('# Imported identity')
    target=tmp_path/'new';import_sage(source,target)
    copied=sqlite3.connect(target/'awake.sqlite3');assert copied.execute('SELECT value FROM test').fetchone()[0]=='synthetic';copied.close()
    assert (target/'self.md').read_text()=='# Imported identity';assert db.execute('SELECT value FROM test').fetchone()[0]=='synthetic';db.close()
    with pytest.raises(ValueError):import_sage(source,target)

def test_original_directory_creation_is_scoped_and_approved(host):
    app,c=host;id,a=proposal(c,'make_directory',{'path':'nested/directory','recursive':True});assert not (app.state.tools.ws.root/'nested/directory').exists();assert approve(c,a).status_code==200
    assert wait(c,id)['result']['ok'] and (app.state.tools.ws.root/'nested/directory').is_dir()

def test_listing_does_not_leak_outside_symlink_metadata(host,tmp_path):
    app,c=host;outside=tmp_path/'secret-outside.txt';outside.write_text('synthetic')
    (app.state.tools.ws.root/'escape-link').symlink_to(outside)
    rows=c.get('/api/files').json()['files'];assert not any('secret-outside' in r['path'] for r in rows)

def test_profile_snapshots_are_unique_within_same_second(host):
    app,c=host;p=app.state.continuity.profile;p._snapshot('synthetic profile 1','same reason');p._snapshot('synthetic profile 2','same reason')
    paths=[x for x in p.history_dir.iterdir() if 'same-reason' in x.name];assert len(paths)==2

def test_imported_sage_dialogue_projects_into_one_thread(tmp_path):
    from vendor_sources.sage.awake.memory import Memory
    from scripts.import_sage import import_sage
    source=tmp_path/'original';source.mkdir();old=Memory(source/'awake.sqlite3');u=old.add_event('user','Synthetic old question');a=old.add_event('reply','Synthetic old answer');old.add_private('OLD_PRIVATE_SENTINEL');old.close();(source/'self.md').write_text('# Original Sage\n\nA synthetic imported identity fixture, not personal data.\n')
    dest=tmp_path/'runtime';import_sage(source,dest/'sage')
    with TestClient(create_app(dest,'test-operator-key')) as c:
        unlock(c);s=c.get('/api/state').json();assert len(s['threads'])==1 and s['threads'][0]['title']=='Imported Sage conversation'
        m=c.get('/api/threads/'+s['threads'][0]['id']+'/messages').json()['messages'];assert [x['role'] for x in m]==['user','assistant'];assert m[0]['meta']['source_event_id']==u['id'];assert 'OLD_PRIVATE_SENTINEL' not in c.get('/api/state').text
