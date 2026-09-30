export type FileEntry={path:string;name:string;size:number;mime:string;is_dir:boolean;sha256?:string};
export type Run={id:string;thread_id:string|null;kind:string;status:string;input:string;result:any;error:string|null;created:number;updated:number;steps:number};
export type Approval={id:string;run_id:string;tool:string;args:Record<string,any>;digest:string;precondition:any;created:number;status:string};
export type Capability={name:string;category:string;description:string;available:boolean;requires_approval:boolean;unavailable_reason:string|null;parameters:any};
export type Snapshot={threads:{id:string;title:string;created:number}[];runs:Run[];approvals:Approval[];continuity:any;provider:any;capabilities:Capability[];files:FileEntry[];milestone:string};
export type Message={id:string;role:string;content:string;meta:any;ts:number};
let token='';
export function getToken(){return token;}
export function setToken(t:string){token=t;try{sessionStorage.setItem('artemis-session',t);}catch{}}
export function restoreToken(){try{token=sessionStorage.getItem('artemis-session')||'';}catch{}return token;}
export function forgetToken(){token='';try{sessionStorage.removeItem('artemis-session');}catch{}}
export async function request(path:string,options:RequestInit={}){
 const headers=new Headers(options.headers);if(token){headers.set('Authorization','Bearer '+token);headers.set('X-Artemis-Session',token);}
 if(options.body&&!(options.body instanceof FormData))headers.set('Content-Type','application/json');
 const r=await fetch('/api'+path,{...options,headers});
 if(!r.ok){let detail:any;try{detail=(await r.json()).detail;}catch{};if(r.status===401)forgetToken();throw new Error(typeof detail==='string'?detail:JSON.stringify(detail)||'Request failed');}
 return r.json();
}
export async function login(key:string){const x=await request('/auth',{method:'POST',body:JSON.stringify({key})});setToken(x.token);return x;}
export function post(path:string,body:any){return request(path,{method:'POST',body:JSON.stringify(body)});}
export async function download(path:string){const r=await fetch('/api/files/content?path='+encodeURIComponent(path),{headers:{Authorization:'Bearer '+token,'X-Artemis-Session':token}});if(!r.ok)throw new Error('Download failed');const url=URL.createObjectURL(await r.blob());const a=document.createElement('a');a.href=url;a.download=path.split('/').pop()||'artifact';a.click();setTimeout(()=>URL.revokeObjectURL(url),10000);}
export function bytes(n:number){if(n<1024)return n+' B';if(n<1048576)return (n/1024).toFixed(1)+' KB';return (n/1048576).toFixed(1)+' MB';}
export function when(ts:number){return new Date(ts*1000).toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'});}
export const active=(status:string)=>['queued','running','awaiting_approval','cancelling'].includes(status);
