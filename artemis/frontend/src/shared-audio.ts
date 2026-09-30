import {post} from './client';
import {S2sWsRealtimeClient} from './s2s-client.js';
class SharedAudio extends EventTarget{
 ctx:AudioContext|null=null;stage:any=null;client:any=null;thread:string|null=null;tour:AudioBufferSourceNode|null=null;status='off';
 context(){if(!this.ctx||this.ctx.state==='closed')this.ctx=new AudioContext({latencyHint:'interactive'});return this.ctx;}
 adoptStage(stage:any){this.stage=stage;if(stage){if(stage.audioCtx!==this.context())throw new Error('Avatar and speech must share the same AudioContext');this.client?.bindOutput(stage.voiceSink);}}
 emit(status:string){this.status=status;this.dispatchEvent(new CustomEvent('status',{detail:status}));if(this.stage)this.stage.setConversationState(status==='ai-speaking'?'speaking':status==='user-speaking'?'listening':status==='processing'?'processing':'idle');}
 async start(thread:string,microphone=true){
  const ctx=this.context();ctx.resume(); // synchronous gesture unlock before any awaits
  await this.stopVoice();this.stopTour();const grant=await post('/speech/session',{thread_id:thread});const url=new URL(grant.path,location.href);url.protocol=location.protocol==='https:'?'wss:':'ws:';
  const client=new S2sWsRealtimeClient({directUrl:url.href,voice:'sage',instructions:'Host-controlled canonical conversation',audioContext:ctx,outputNode:this.stage?.voiceSink||ctx.destination,workletBaseUrl:'/worklets/',acquireMic:microphone?()=>navigator.mediaDevices.getUserMedia({audio:{echoCancellation:true,noiseSuppression:true,autoGainControl:true}}):undefined,tools:[],noiseGate:{enabled:true,thresholdDb:-45}});
  this.client=client;this.thread=thread;client.addEventListener('status',(e:any)=>this.emit(typeof e.detail==='string'?e.detail:e.detail?.status||'connected'));client.addEventListener('transcript',(e:any)=>this.dispatchEvent(new CustomEvent('transcript',{detail:e.detail})));client.addEventListener('error',(e:any)=>this.dispatchEvent(new CustomEvent('error',{detail:e.detail})));await client.connect();this.emit('connected');return client;
 }
 async stopVoice(){if(this.client){const old=this.client;this.client=null;await old.close();}this.thread=null;this.emit('off');}
 cancel(){this.client?.cancelUnifiedTurn();this.stopTour();this.stage?.setConversationState('idle');}
 sendText(text:string){if(!this.client)throw new Error('Start a real speech session first');this.client.sendUserText(text);this.client.requestResponse();}
 speakMessage(id:string){this.client?.speakMessage(id);}
 async playTour(url:string){const ctx=this.context();await ctx.resume();this.cancel();const r=await fetch(url);if(!r.ok)throw new Error('Recorded narration not found');const buffer=await ctx.decodeAudioData(await r.arrayBuffer());const source=ctx.createBufferSource();source.buffer=buffer;source.connect(this.stage?.voiceSink||ctx.destination);source.onended=()=>{this.tour=null;this.dispatchEvent(new Event('tour-ended'));};this.tour=source;source.start();}
 stopTour(){if(this.tour){try{this.tour.stop();this.tour.disconnect();}catch{}this.tour=null;}}
 stopAll(){this.cancel();}
}
export const sharedAudio=new SharedAudio();
