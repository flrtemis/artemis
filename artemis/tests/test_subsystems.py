"""Milestone 02 tests: actual namespace/Godot/Torch/speech where installed; labelled fixtures for LLM."""
import json,asyncio,time,os,sys,base64,threading,hashlib
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from artemis_app.api import create_app
from artemis_app.store import Store
from artemis_app.world import World
from artemis_app.training_worker import train
from tests.test_integration import unlock,proposal,approve,wait,FixtureProvider
PIPER=Path(__file__).resolve().parents[2]/'.cache/speech-models/piper/en_US-lessac-low.onnx'
WHISPER=Path(__file__).resolve().parents[2]/'.cache/speech-models/whisper-tiny'

def host(tmp_path,provider=None):return create_app(tmp_path,'test-operator-key',provider)
def speech_config():return {'piper_model':str(PIPER),'whisper_model':str(WHISPER),'device':'cpu'}

def test_autonomous_wake_real_sage_parser_private_projection(tmp_path):
    private='WAKE_PRIVATE_NEVER_PUBLIC';payload={'actions':[{'text':private,'type':'private'},{'type':'remember','text':'Synthetic autonomous kept memory','importance':4},{'type':'want','text':'Synthetic autonomous goal'},{'type':'message_user','text':'Synthetic pending message'},{'type':'set_next_wake','minutes':.001}],'thought':private}
    fake=FixtureProvider([{'role':'assistant','content':json.dumps(payload)}]);app=host(tmp_path,fake)
    with TestClient(app) as c:
        unlock(c);r=c.post('/api/autonomy/wake');assert r.status_code==200,r.text
        assert r.json()['status']=='succeeded';s=c.get('/api/state').json();assert s['continuity']['autonomy']['wake_count']==1
        assert s['continuity']['private_count']==2 and private not in json.dumps(s) and private not in c.get('/api/events').text
        assert s['continuity']['memories'][0]['text']=='Synthetic autonomous kept memory';assert s['continuity']['goals'][0]['text']=='Synthetic autonomous goal'
        assert app.state.continuity.state.get('next_wake_ts')>=time.time()+58
        assert 'Sage' in fake.requests[0]['messages'][0]['content'] and fake.requests[0]['schemas']==[]

def test_garbled_wake_retries_once_no_mutations(tmp_path):
    fake=FixtureProvider([{'content':''},{'content':'repeated repeated repeated repeated repeated repeated'}]);app=host(tmp_path,fake)
    with TestClient(app) as c:
        unlock(c);r=c.post('/api/autonomy/wake').json();assert r['status']=='failed';assert not c.get('/api/state').json()['continuity']['memories'];assert len(fake.requests)==2

def test_nonfinite_wake_action_rejected_before_commit(tmp_path):
    fake=FixtureProvider([{'content':'{"thought":"secret reflection","actions":[{"type":"remember","text":"must not commit"},{"type":"set_next_wake","minutes":"nonnumeric"}]}'}]);app=host(tmp_path,fake)
    with TestClient(app) as c:
        unlock(c);assert c.post('/api/autonomy/wake').json()['status']=='failed';s=c.get('/api/state').json();assert not s['continuity']['memories'] and s['continuity']['private_count']==0

def test_autonomy_bound_schedule_and_letters_opaque(tmp_path):
    app=host(tmp_path)
    with TestClient(app) as c:
        unlock(c);assert c.put('/api/autonomy',json={'enabled':True,'interval_s':1}).status_code==422
        r=c.post('/api/continuity/letters',json={'text':'Synthetic letter'}).json();id=r['id'];assert app.state.runtime.extensions.autonomy.read_letter(id)=='Synthetic letter'
        with pytest.raises(ValueError):app.state.runtime.extensions.autonomy.read_letter('../../outside')
        (app.state.runtime.extensions.autonomy.letters/'legacy-name.txt').write_text('Legacy synthetic letter')
        entries=app.state.runtime.extensions.autonomy.list_letters();legacy=next(x for x in entries if x['name']=='legacy-name.txt');assert app.state.runtime.extensions.autonomy.read_letter(legacy['id'])=='Legacy synthetic letter'

def test_interactive_preempts_stale_wake(tmp_path):
    class Delayed(FixtureProvider):
        async def chat(self,messages,schemas,*,config=None):
            if messages[0]['content'].startswith('You are Sage. You are not an assistant'):
                await asyncio.sleep(.4);return {'content':'{"actions":[{"type":"remember","text":"stale must not commit"}]}'}
            return {'content':'Interactive fixture response'}
    app=host(tmp_path,Delayed([]))
    with TestClient(app) as c:
        unlock(c);result={}
        def wake():result.update(c.post('/api/autonomy/wake').json())
        thread=threading.Thread(target=wake);thread.start();time.sleep(.12)
        t=c.post('/api/threads',json={}).json()['id'];r=c.post('/api/chat',json={'thread_id':t,'text':'User has priority'}).json();wait(c,r['run_id']);thread.join(3)
        assert result['status']=='cancelled';assert not c.get('/api/state').json()['continuity']['memories']

def test_actual_bwrap_host_files_and_network_inaccessible(tmp_path):
    app=host(tmp_path)
    with TestClient(app) as c:
        unlock(c);execution=app.state.runtime.extensions.execution
        if not execution.available()['available']:pytest.skip('No permitted kernel/container backend')
        secret=tmp_path/'host-secret';secret.write_text('DO_NOT_READ_HOST')
        code=f"import os,socket,json\nchecks={{'host_path_visible':os.path.exists({str(secret)!r}),'home':os.listdir('/home')}}\ntry:\n s=socket.create_connection(('127.0.0.1',8000),.2);checks['host_network']=True\nexcept OSError:checks['host_network']=False\nopen('isolated-output.txt','w').write('from isolated worker')\nprint(json.dumps(checks))"
        id,a=proposal(c,'run_python',{'code':code,'timeout':8});assert approve(c,a).status_code==200;r=wait(c,id)['result'];assert r['ok'],r
        checks=json.loads(r['stdout']);assert not checks['host_path_visible'] and not checks['host_network'];assert not (app.state.tools.ws.root/'isolated-output.txt').exists()
        p,a=proposal(c,'promote_execution_changes',{'job_id':r['job_id']});assert approve(c,a).status_code==200;assert wait(c,p)['result']['ok'];assert (app.state.tools.ws.root/'isolated-output.txt').read_text()=='from isolated worker'

def test_execution_promotion_revision_drift_blocked(tmp_path):
    app=host(tmp_path)
    with TestClient(app) as c:
        unlock(c)
        if not app.state.runtime.extensions.execution.available()['available']:pytest.skip('Isolation unavailable')
        file=app.state.tools.ws.root/'a.txt';file.write_text('before')
        id,a=proposal(c,'run_bash',{'command':"printf 'new' > a.txt"});approve(c,a);r=wait(c,id)['result'];file.write_text('concurrent human change')
        id,a=proposal(c,'promote_execution_changes',{'job_id':r['job_id']});approve(c,a);result=wait(c,id,'failed');assert 'changed' in result['result']['error'];assert file.read_text()=='concurrent human change'

def test_execution_timeout_and_symlink_fail_closed(tmp_path):
    app=host(tmp_path)
    with TestClient(app) as c:
        unlock(c)
        if not app.state.runtime.extensions.execution.available()['available']:pytest.skip('Isolation unavailable')
        id,a=proposal(c,'run_bash',{'command':'sleep 10','timeout':1});approve(c,a);result=wait(c,id,'failed')['result'];assert result['error']=='Execution timeout'
        id,a=proposal(c,'run_bash',{'command':'ln -s /usr a-link'});approve(c,a);r=wait(c,id,'failed');assert 'Symlink' in r['result']['error']

@pytest.fixture
def world(tmp_path):
    s=Store(tmp_path/'world.sqlite3');w=World(s)
    if not w.binary():s.close();pytest.skip('Godot not configured')
    w.start(17)
    try:yield w
    finally:w.close();s.close()

def test_native_physics_ground_and_collision(world):
    f=world.request('advance',frames=60);assert f['proprioception']['grounded'];assert .8<f['proprioception']['position'][1]<.9
    world.intent(0,1);world.request('advance',frames=180);f=world.sensors();assert f['proprioception']['position'][2]>-.45,'Body should collide with native occluder, not pass through'

def test_partial_vision_and_revision_contract(world):
    sensors=world.sensors();assert 'seed' not in sensors and 'objects' not in sensors;assert all('position' not in x for x in sensors['vision']['objects'])
    assert len(sensors['vision']['objects'])<len(world.request('truth')['objects'])
    world.request('advance',frames=2)
    with pytest.raises(ValueError,match='Stale'):world.intent(move_x=1,expected_revision=0)

def test_native_replay_reproduces_sensor_hashes(world):
    world.intent(1,0);world.request('advance',frames=20);world.intent(0,1,.2);world.request('advance',frames=30)
    result=world.replay();assert result['frames_compared']==2 and result['exact_matches'],result

def test_participant_token_cannot_access_operator_truth_or_files(tmp_path):
    app=host(tmp_path)
    with TestClient(app) as c:
        unlock(c)
        if not app.state.runtime.extensions.world.binary():pytest.skip('No Godot')
        assert c.post('/api/world/start',json={'seed':17}).status_code==200
        token=c.post('/api/world/participant').json()['token'];headers={'Authorization':'Bearer '+token}
        assert c.get('/api/participant/sensors',headers=headers).status_code==200
        for path in ['/api/world/truth','/api/files','/api/state','/api/subsystems']:assert c.get(path,headers=headers).status_code==401

def test_model_world_step_receives_only_sensors_and_no_tools(tmp_path):
    fake=FixtureProvider([{'content':'{"move_x":0.5,"move_z":0,"look_delta":0,"prediction":"my horizontal position should change"}'}]);app=host(tmp_path,fake)
    with TestClient(app) as c:
        unlock(c)
        if not app.state.runtime.extensions.world.binary():pytest.skip('No Godot')
        c.post('/api/world/start',json={'seed':17});r=c.post('/api/world/actor-step',json={'goal':'Explore'});assert r.status_code==200,r.text
        data=json.loads(fake.requests[0]['messages'][1]['content']);assert set(data)=={'goal','sensors'} and fake.requests[0]['schemas']==[] and 'seed' not in data['sensors']

def test_real_cpu_lora_composite_objectives_and_checkpoint(tmp_path):
    pytest.importorskip('torch');pytest.importorskip('peft')
    corpus=tmp_path/'data.txt';corpus.write_text('An actual differentiable objective preserves replay and distillation. '*15);out=tmp_path/'out';records=[]
    r=train({'fixture':True,'device':'cpu','steps':3,'rank':4,'dataset_path':str(corpus),'output_dir':str(out),'sam':True,'pcgrad':True,'meta_learning':True,'token_weighting':True,'distill_weight':.1,'ewc_lambda':.1},records.append)
    assert r['adapter_delta_l2']>0 and r['trainable_parameters']>0 and list((out/'adapter').glob('*.safetensors'))
    assert r['device']=='cpu' and 'conformance' in r['quality'] and records[1]['replay_size']>=2
    assert all(x['gradient_l2']>0 for x in records if x['type']=='training_step')

def test_cuda_missing_is_not_faked(tmp_path):
    torch=pytest.importorskip('torch')
    if torch.cuda.is_available():pytest.skip('This assertion is for CPU-only hardware')
    with pytest.raises(ValueError,match='CUDA unavailable'):train({'fixture':True,'device':'cuda'})

def test_managed_training_proposal_lifecycle(tmp_path):
    pytest.importorskip('torch');pytest.importorskip('peft');app=host(tmp_path)
    with TestClient(app) as c:
        unlock(c);(app.state.tools.ws.root/'corpus.txt').write_text('Managed training events share the same persistent activity. '*10)
        id,a=proposal(c,'start_training',{'path':'corpus.txt','device':'cpu','fixture':True,'steps':2,'sam':True});approve(c,a);r=wait(c,id);training_id=r['result']['training_run_id']
        # Actual worker cold import can take several seconds on a small machine.
        for _ in range(1000):
            r=c.get('/api/runs/'+training_id).json()
            if r['status'] not in ['queued','running']:break
            time.sleep(.05)
        assert r['status']=='succeeded',r
        id,a=proposal(c,'promote_training_adapter',{'training_run_id':training_id,'max_heldout_ce':10});approve(c,a);r=wait(c,id,'failed');assert 'conformance' in r['result']['error']

def test_speech_remote_consent_and_one_use_grants(tmp_path):
    app=host(tmp_path)
    with TestClient(app) as c:
        unlock(c);assert c.put('/api/speech',json={'stt_backend':'http','stt_url':'https://example.com/transcribe','allow_remote_audio':False}).status_code==400
        # Native local config existence means capability configured, never synthetic playback.
        if not PIPER.exists():pytest.skip('No optional voice model')
        assert c.put('/api/speech',json=speech_config()).status_code==200
        t=c.post('/api/threads',json={}).json()['id'];grant=c.post('/api/speech/session',json={'thread_id':t}).json()
        with c.websocket_connect(grant['path']) as ws:
            assert ws.receive_json()['type']=='session.created';ws.send_json({'type':'session.update'});assert ws.receive_json()['type']=='session.updated'
        from starlette.websockets import WebSocketDisconnect
        with pytest.raises(WebSocketDisconnect):
            with c.websocket_connect(grant['path']) as ws:ws.receive_json()

def test_native_piper_whisper_roundtrip(tmp_path):
    if not PIPER.exists() or not (WHISPER/'model.bin').exists():pytest.skip('Optional real CPU speech models not installed')
    from artemis_app.speech import Speech
    async def exercise():
        app=host(tmp_path);s=app.state.runtime.extensions.speech
        await s.configure(speech_config())
        try:
            result=await s.synthesize('The unified workspace is ready.');assert result['samples']>4000 and result['quality']=='actual_piper_synthesis'
            transcript=await s.transcribe(base64.b64decode(result['pcm16']));assert 'workspace' in transcript['text'].lower(),transcript
        finally:await s.close();app.state.store.close()
    asyncio.run(exercise())

def test_realtime_websocket_real_tts_same_history_and_cancel_epoch(tmp_path):
    if not PIPER.exists():pytest.skip('Optional Piper model not present')
    fake=FixtureProvider([{'content':'The unified workspace is ready. This is a deterministic language-model fixture.'}]);app=host(tmp_path,fake)
    with TestClient(app) as c:
        unlock(c);assert c.put('/api/speech',json=speech_config()).status_code==200
        t=c.post('/api/threads',json={}).json()['id'];grant=c.post('/api/speech/session',json={'thread_id':t}).json()
        with c.websocket_connect(grant['path']) as ws:
            assert ws.receive_json()['type']=='session.created';ws.send_json({'type':'conversation.item.create','item':{'role':'user','content':[{'type':'input_text','text':'Say hello through the same thread'}]}});ws.send_json({'type':'response.create'})
            audio=bytearray();completed=False
            for _ in range(1000):
                m=ws.receive_json()
                assert m['type']!='error',m
                if m['type']=='response.output_audio.delta':audio.extend(base64.b64decode(m['delta']))
                if m['type']=='response.done':completed=m['response']['status']=='completed';break
            assert completed and len(audio)>10000
            messages=c.get('/api/threads/'+t+'/messages').json()['messages'];assert len(messages)==2 and messages[0]['role']=='user' and messages[1]['role']=='assistant'
            assert messages[1]['content']==fake.responses[0]['content'] if fake.responses else 'deterministic language-model fixture' in messages[1]['content']
            # Replay actual saved assistant text, then cancel; no duplicate stored assistant message.
            ws.send_json({'type':'artemis.speak','message_id':messages[1]['id']});created=ws.receive_json();assert created['type']=='response.created';ws.send_json({'type':'response.cancel'})
            found=False
            for _ in range(100):
                m=ws.receive_json()
                if m['type']=='response.done' and m['response']['status']=='cancelled':found=True;break
            assert found and len(c.get('/api/threads/'+t+'/messages').json()['messages'])==2

def test_proxy_safe_custom_session_header_does_not_bypass_auth(tmp_path):
    with TestClient(host(tmp_path)) as c:
        token=c.post('/api/auth',json={'key':'test-operator-key'}).json()['token']
        assert c.get('/api/state',headers={'Authorization':'Bearer proxy-replaced','X-Artemis-Session':token}).status_code==200
        assert c.get('/api/state',headers={'X-Artemis-Session':'forged'}).status_code==401
