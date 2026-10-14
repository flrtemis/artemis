// Production reader with a deterministic speech adapter. No audible voice/model/PC proof.
import test from 'node:test';
import assert from 'node:assert/strict';
import {build} from 'esbuild';
const bundle=await build({entryPoints:['src/device-reader.ts'],bundle:true,write:false,format:'esm',platform:'node',target:'es2021'});
const {DeviceReplyReader,speechChunks,speechPresentation}=await import('data:text/javascript;base64,'+Buffer.from(bundle.outputFiles[0].text).toString('base64'));
const local={voiceURI:'fixture-local',name:'Fixture local voice',lang:'en-GB',localService:true};
const remote={voiceURI:'fixture-remote',name:'Fixture remote voice',lang:'en-US',localService:false};
const options={voiceURI:local.voiceURI,rate:1,skipCode:true};
const reply=(id,content='Saved answer.',run='run-a')=>({id,role:'assistant',content,meta:{run_id:run}});
const flush=()=>new Promise(resolve=>setImmediate(resolve));
function setup(){const spoken=[],states=[];let cancels=0;let voices=[local,remote];
 const adapter={voices:()=>voices,utterance:text=>({text,voice:null,rate:1,lang:'',onstart:null,onend:null,onerror:null}),speak:u=>{spoken.push(u);u.onstart?.();},cancel:()=>{cancels++;}};
 const r=new DeviceReplyReader(s=>states.push(s),adapter);
 return {r,spoken,states,get cancels(){return cancels;},setVoices:v=>{voices=v;},finish:async()=>{spoken.at(-1)?.onend?.();await flush();}};
}

test('formatter preserves emphasis, warnings, actions, math, quotes and original text',()=>{
 const original='**WARNING: do not delete files.**\nSage: "Keep this."\n*waves* a < b, 2*3*4, literal_underscore\n';
 assert.equal(speechPresentation(original,true),original);assert.equal(speechPresentation(original,false),original);
});
test('only selected fenced code is skipped, supporting tilde/backtick fences and complete tail',()=>{
 const original='Answer first.\n```python\nprint("not spoken")\n```\nTail that must be spoken';
 const spoken=speechPresentation(original,true);assert.match(spoken,/Answer first/);assert.match(spoken,/Code block omitted/);assert.match(spoken,/Tail that must be spoken/);assert.doesNotMatch(spoken,/print/);assert.equal(speechPresentation(original,false),original);
 assert.match(speechPresentation('~~~js\nconst x=1;\n~~~\nFinal.',true),/Final\./);
});
test('chunks concatenate exactly, include short punctuation-free tails and never split surrogate pairs',()=>{
 for(let n=1;n<100;n++){const text='First sentence. '+('A long Unicode answer 😀 with spaces '.repeat(n))+'LAST SHORT TAIL';const chunks=speechChunks(text);assert.equal(chunks.join(''),text);assert.ok(chunks.every(c=>c.length<=240));assert.ok(chunks.every(c=>!/[\uD800-\uDBFF]$/.test(c)));}
 assert.throws(()=>speechChunks('x',0));
});
test('reader is off by default; observing alone cannot speak or create a model call',()=>{
 const {r,spoken}=setup();r.observe('thread',[reply('one')]);assert.equal(spoken.length,0);assert.equal(r.snapshot().enabled,false);
});
test('only explicit device-reported local voices can be configured, no name/gender/remote fallback',()=>{
 const {r}=setup();assert.throws(()=>r.enable('thread',[],{...options,voiceURI:remote.voiceURI}),/local/);assert.throws(()=>r.enable('thread',[],{...options,voiceURI:'missing'}),/local/);assert.throws(()=>r.configure({...options,rate:3}),/speed/);assert.throws(()=>r.configure({...options,rate:NaN}),/speed/);
});
test('enable baselines saved history; new committed assistant IDs read once, not user/tool/system data',async()=>{
 const {r,spoken,finish}=setup();r.enable('thread',[reply('old')],options);
 const messages=[reply('old'),{id:'user',role:'user',content:'Private input'},{id:'tool',role:'tool',content:'Tool output'},{id:'sys',role:'system',content:'System text'},reply('new')];
 r.observe('thread',messages);assert.equal(spoken.length,1);assert.equal(spoken[0].text,'Saved answer.');await finish();r.observe('thread',messages);assert.equal(spoken.length,1);
});
test('identical answer text in distinct message IDs is not incorrectly deduplicated by text hash',async()=>{
 const {r,spoken,finish}=setup();r.enable('thread',[],options);r.observe('thread',[reply('a'),reply('b')]);await finish();assert.equal(spoken.length,2);await finish();r.observe('thread',[reply('a'),reply('b')]);assert.equal(spoken.length,2);
});
test('same ID content edit does not replay; another thread cannot speak',()=>{
 const {r,spoken}=setup();r.enable('thread',[],options);r.observe('other',[reply('outside')]);assert.equal(spoken.length,0);r.observe('thread',[reply('same')]);r.observe('thread',[reply('same','Edited')]);assert.equal(spoken.length,1);
});
test('long answer serializes utterances at selected language/rate and finishes its entire tail',async()=>{
 const {r,spoken,finish}=setup();r.enable('thread',[],{...options,rate:0.75});const text=('A sufficiently long reply sentence. '.repeat(20))+'tiny tail';r.observe('thread',[reply('a',text)]);
 assert.equal(spoken.length,1);while(r.snapshot().queued){await finish();}
 assert.equal(spoken.map(u=>u.text).join(''),text);assert.ok(spoken.every(u=>u.voice.localService&&u.lang==='en-GB'&&u.rate===0.75));
});
test('new results hold while input is active, then resume once without changing saved text',async()=>{
 const {r,spoken,finish}=setup();r.enable('thread',[],options);r.hold();r.observe('thread',[reply('a')]);assert.equal(spoken.length,0);assert.equal(r.snapshot().held,true);r.resume();assert.equal(spoken.length,1);await finish();r.resume();assert.equal(spoken.length,1);
});
test('stop speech fences delayed start/end callbacks and never auto-restarts the cut reply',async()=>{
 const {r,spoken,finish}=setup();r.enable('thread',[],options);r.observe('thread',[reply('a','Sentence. '.repeat(100))]);const old=spoken[0];r.stopSpeech();old.onstart?.();old.onend?.();await flush();assert.equal(spoken.length,1);assert.equal(r.snapshot().status,'device-held');r.resume();assert.equal(spoken.length,1);r.readSaved('thread',reply('a','A saved replay.'),options);assert.equal(spoken.length,2);await finish();
});
test('barge-in hold discards the interrupted playback but preserves later queued replies for explicit resume',async()=>{
 const {r,spoken}=setup();r.enable('thread',[],options);r.observe('thread',[reply('a','Old. '.repeat(80))]);r.hold();r.observe('thread',[reply('a'),reply('b','New held answer.')]);assert.equal(spoken.length,1);r.resume();assert.equal(spoken.length,2);assert.equal(spoken[1].text,'New held answer.');
});
test('new turn suppresses older held/late automatic results; only confirmed run can release audio',()=>{
 const {r,spoken}=setup();r.enable('thread',[],options);r.hold();r.observe('thread',[reply('old')]);r.beginTurn('thread');r.observe('thread',[reply('old'),reply('late','Late old result','run-a'),reply('new','New result','run-b')]);r.resume();assert.equal(spoken.length,0);r.expectReply('run-b');assert.equal(spoken.length,1);assert.equal(spoken[0].text,'New result');
});
test('old saved answer remains manually replayable after new turn, without tool/model invocation',()=>{
 const {r,spoken}=setup();r.enable('thread',[reply('old')],options);r.beginTurn('thread');r.expectReply('new-run');r.readSaved('thread',reply('old','Original stored answer'),options);assert.equal(spoken[0].text,'Original stored answer');assert.equal(r.snapshot().automatic,true);
});
test('voice revocation fails closed; no remote/default voice or repeated retry',async()=>{
 const {r,spoken,setVoices,finish}=setup();r.enable('thread',[],options);r.observe('thread',[reply('a','Long answer. '.repeat(60))]);setVoices([remote]);await finish();assert.equal(spoken.length,1);assert.equal(r.snapshot().status,'device-error');assert.equal(r.snapshot().held,true);
});
test('browser permission error preserves work/text and requires a gesture; stale errors are fenced',()=>{
 const {r,spoken}=setup();r.enable('thread',[],options);r.observe('thread',[reply('a')]);spoken[0].onerror?.({error:'not-allowed'});assert.equal(r.snapshot().status,'device-error');assert.match(r.snapshot().detail,/blocked/);r.disable();spoken[0].onerror?.({error:'not-allowed'});assert.equal(r.snapshot().status,'off');
});
test('oversize answer fails rather than silently truncating; queue remains bounded',()=>{
 const {r,spoken}=setup();r.enable('thread',[],options);r.observe('thread',[reply('big','x'.repeat(20001))]);assert.equal(spoken.length,0);assert.throws(()=>r.readSaved('thread',reply('big','x'.repeat(20001)),options),/exceeds/);r.hold();r.observe('thread',Array.from({length:40},(_,n)=>reply('m-'+n)));assert.ok(r.snapshot().queued<=16);
});
test('large baseline history does not cause an eviction/re-read loop on repeated snapshots',async()=>{
 const {r,spoken}=setup();const history=Array.from({length:1500},(_,n)=>reply('h-'+n));r.enable('thread',history,options);for(let n=0;n<3;n++)r.observe('thread',history);assert.equal(spoken.length,0);
});
test('disabling drops only presentation; one-off read is not automatic reader enable',async()=>{
 const {r,spoken,finish}=setup();r.readSaved('thread',reply('manual'),options);assert.equal(r.snapshot().automatic,false);await finish();r.observe('thread',[reply('future')]);assert.equal(spoken.length,1);r.disable();assert.equal(r.snapshot().enabled,false);r.observe('thread',[reply('another')]);assert.equal(spoken.length,1);
});
test('failed turn releases the pending-run fence but holds uncertain outcomes for explicit inspection',()=>{
 const {r}=setup();r.enable('thread',[],options);r.beginTurn('thread');r.turnFailed();assert.equal(r.snapshot().held,true);assert.equal(r.snapshot().status,'device-error');assert.match(r.snapshot().detail,/not confirmed/);
});
