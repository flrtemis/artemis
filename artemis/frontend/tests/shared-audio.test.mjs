// The real coordinator bundled with controlled transport stubs; no microphone/model/device proof.
import test from 'node:test';
import assert from 'node:assert/strict';
import {build} from 'esbuild';
const built=await build({entryPoints:['src/shared-audio.ts'],bundle:true,write:false,platform:'node',format:'esm',target:'es2021',plugins:[{
 name:'controlled-transports',setup(b){
  b.onResolve({filter:/^\.\/client$/},()=>({path:'client',namespace:'fixture'}));
  b.onResolve({filter:/^\.\/s2s-client\.js$/},()=>({path:'s2s',namespace:'fixture'}));
  b.onLoad({filter:/.*/,namespace:'fixture'},args=>({contents:args.path==='client'?
   `export async function post(path,args){globalThis.__audioTest.posts.push({path,args});return {path:'/api/speech/ws?ticket=fixture'};}`:
   `export class S2sWsRealtimeClient extends EventTarget {constructor(options){super();this.options=options;this.closed=0;globalThis.__audioTest.clients.push(this);}connect(){return new Promise(resolve=>{this.resolve=resolve;});}async close(){this.closed++;}bindOutput(){}cancelUnifiedTurn(){this.cancelled=true;}resumeAudio(){this.resumed=true;}sendUserText(){}requestResponse(){}speakMessage(){}}`,loader:'js'}));
 }}]});
const source='data:text/javascript;base64,'+Buffer.from(built.outputFiles[0].text).toString('base64');
const flush=()=>new Promise(r=>setImmediate(r));
const local={voiceURI:'local',localService:true,lang:'en-GB',name:'Fixture device'};
const prefs={voiceURI:'local',rate:1,skipCode:true};
async function fresh(){
 globalThis.__audioTest={posts:[],clients:[],utterances:[],cancels:0,contexts:0,stages:[]};
 globalThis.window={speechSynthesis:{getVoices:()=>[local],speak:u=>{globalThis.__audioTest.utterances.push(u);u.onstart?.();},cancel:()=>globalThis.__audioTest.cancels++},SpeechSynthesisUtterance:class{constructor(text){this.text=text;}}};
 globalThis.location={href:'http://test.invalid/',protocol:'http:'};
 globalThis.AudioContext=class{constructor(){globalThis.__audioTest.contexts++;this.state='running';this.destination={};}resume(){return Promise.resolve();}};
 Object.defineProperty(globalThis,'navigator',{value:{mediaDevices:{getUserMedia:()=>{throw Error('Unexpected microphone');}}},configurable:true});
 const module=await import(source+'#instance-'+Math.random());return {audio:module.sharedAudio,stats:globalThis.__audioTest};
}
const message={id:'saved',role:'assistant',content:'Saved user-facing answer.',meta:{run_id:'run'}};

test('explicit device mode uses no backend/model/mic/second AudioContext and reads only committed messages',async()=>{
 const {audio,stats}=await fresh();audio.enableDevice('thread',[],prefs);audio.observeSaved('thread',[message]);assert.equal(audio.mode,'device');assert.equal(stats.posts.length,0);assert.equal(stats.contexts,0);assert.equal(stats.utterances.length,1);assert.equal(stats.utterances[0].text,message.content);await audio.stopVoice();assert.equal(audio.mode,'off');
});
test('late configured connect/status after device switch cannot steal ownership or reset device state',async()=>{
 const {audio,stats}=await fresh();const starting=audio.start('thread',false);await flush();const old=stats.clients[0];assert.equal(old.options.acquireMic,undefined);
 audio.enableDevice('thread',[],prefs);assert.equal(old.closed,1);old.dispatchEvent(new CustomEvent('status',{detail:'ai-speaking'}));assert.equal(audio.status,'device-ready');old.resolve();assert.equal(await starting,null);assert.equal(audio.mode,'device');assert.equal(audio.status,'device-ready');assert.ok(stats.posts.every(p=>p.path==='/speech/session'));
});
test('stop/off/hold invoke presentation controls, never Runtime cancellation or extra model work',async()=>{
 const {audio,stats}=await fresh();audio.enableDevice('thread',[],prefs);audio.observeSaved('thread',[message]);audio.holdForInput();assert.equal(audio.status,'device-held');audio.resumeAudio();audio.cancel();assert.equal(audio.status,'device-held');await audio.stopVoice();assert.equal(audio.status,'off');assert.equal(stats.posts.length,0);
});
test('configured PCM may drive speaking, but device speech does not invent avatar PCM/lip-sync',async()=>{
 const {audio,stats}=await fresh();const ctx=audio.context();audio.adoptStage({audioCtx:ctx,voiceSink:{},setConversationState:state=>stats.stages.push(state)});
 const starting=audio.start('thread',false);await flush();const client=stats.clients[0];client.resolve();await starting;client.dispatchEvent(new CustomEvent('status',{detail:'ai-speaking'}));assert.equal(stats.stages.at(-1),'speaking');
 audio.readDeviceMessage('thread',message,prefs);assert.equal(audio.mode,'device');assert.equal(stats.stages.at(-1),'idle');assert.equal(stats.contexts,1);await audio.stopVoice();
});
test('invalid remote/missing device voice fails before disrupting an active configured owner',async()=>{
 const {audio,stats}=await fresh();const starting=audio.start('thread',false);await flush();const client=stats.clients[0];client.resolve();await starting;assert.throws(()=>audio.enableDevice('thread',[],{...prefs,voiceURI:'remote'}),/local/);assert.equal(audio.mode,'configured');assert.equal(client.closed,0);await audio.stopVoice();
});
