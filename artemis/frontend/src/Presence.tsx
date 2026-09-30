import {useEffect,useRef,useState} from 'react';
import {AvatarStage} from './avatar-stage.js';
import {sharedAudio} from './shared-audio';
import {Eye,AudioLines,RotateCcw} from 'lucide-react';
export function Presence({busy,mood,name='Sage'}:{busy:boolean;mood:any;name?:string}){
 const ref=useRef<HTMLDivElement>(null);const stage=useRef<any>(null);const [on,setOn]=useState(false);const [loading,setLoading]=useState(false);const [error,setError]=useState('');
 useEffect(()=>{if(!on||!ref.current)return;let stopped=false;setLoading(true);setError('');const a:any=new AvatarStage(ref.current);stage.current=a;
 a.init({avatarUrl:'/avatars/brunette.glb'}).then(()=>{if(!stopped){a.resume();a.ready=true;sharedAudio.adoptStage(a);setLoading(false);a.setConversationState(busy?'processing':'idle');}}).catch((e:any)=>{if(!stopped){setError('The avatar renderer could not initialize in this browser. Text and tools remain available.');setLoading(false);console.warn('Presence:',e);}});
 return()=>{stopped=true;try{a.head?.stop();a.head?.renderer?.dispose();sharedAudio.adoptStage(null);}catch{}stage.current=null;ref.current?.replaceChildren();};
 },[on]);
 useEffect(()=>{stage.current?.setConversationState(busy?'processing':'idle');if(stage.current?.ready&&stage.current?.head){const m=mood?.word==='bright'?'happy':mood?.word==='low'?'sad':'neutral';stage.current.runTool('set_mood',{mood:m});}},[busy,mood?.word]);
 return <section className="presence-card"><div className="rail-heading"><span>PRESENCE</span><Eye size={14}/></div><div className="presence-stage" ref={ref}/>{!on&&<div className="presence-off"><div className="sage-seal"><AudioLines size={36} strokeWidth={1.3}/></div><h3>{name}</h3><p>One identity.<br/>A continuous workspace.</p><button className="presence-enable" onClick={()=>setOn(true)}><Eye size={14}/> Enable 3D presence</button></div>}{loading&&<div className="presence-loading">Loading the original avatar…</div>}{error&&<div className="presence-error">{error}<button onClick={()=>{setOn(false);setTimeout(()=>setOn(true),0);}}><RotateCcw size={13}/> Retry</button></div>}<div className="presence-footer"><span className={'state-dot '+(busy?'busy':'')}/><span>{busy?'Processing a run':'Available for connected tasks'}</span><span className="tag-mini">{mood?.word||'settled'}</span></div><p className="rail-note">Gemma’s original TalkingHead / HeadAudio stage. No microphone requested. Speech uses the host-owned audio graph when configured.</p></section>;
}
