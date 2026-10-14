// Production app/Store/Runtime with an explicitly scripted provider and mocked DEVICE speech.
// Physical audibility, voice quality, native-engine compatibility and latency are not tested.
import {chromium} from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
const key=process.argv[2],base=(process.argv[3]||'http://localhost:8040').replace(/\/$/,'');
if(!key)throw Error('Use a temporary disposable scripted-host key, not private Sage state.');
const root=new URL('../../../',import.meta.url).pathname,output=path.join(root,'.cache/sage-reading-browser');await fs.mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:process.env.ARTEMIS_CHROMIUM_BIN||undefined,args:['--no-sandbox']});
const context=await browser.newContext({viewport:{width:1440,height:1000}});
await context.addInitScript(()=>{
 const local={voiceURI:'fixture-local',name:'Fixture local voice',lang:'en-GB',localService:true},remote={voiceURI:'fixture-remote',name:'Fixture remote voice',lang:'en-US',localService:false};
 const synth=new EventTarget();window.__reading={utterances:[],cancelled:0,microphones:0,voices:[remote,local]};
 synth.getVoices=()=>window.__reading.voices;synth.speak=u=>{window.__reading.utterances.push(u);u.onstart?.();};synth.cancel=()=>window.__reading.cancelled++;
 Object.defineProperty(window,'speechSynthesis',{value:synth,configurable:true});window.SpeechSynthesisUtterance=class{constructor(text){this.text=text;}};
 window.__finishReading=()=>window.__reading.utterances.at(-1)?.onend?.();
 navigator.mediaDevices.getUserMedia=()=>{window.__reading.microphones++;throw Error('No microphone allowed in reading tests');};
});
const page=await context.newPage();page.setDefaultTimeout(15000);page.setDefaultNavigationTimeout(20000);
const records=[],errors=[],requests=[];const pass=name=>{records.push({name,result:'pass'});console.log('PASS',name);};
page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>requests.push({url:r.url(),method:r.method()}));
const d=()=>page.getByRole('dialog',{name:'Sage',exact:true});
const api=async route=>page.evaluate(async route=>{const r=await fetch('/api'+route,{headers:{'X-Artemis-Session':sessionStorage.getItem('artemis-session')}});if(!r.ok)throw Error(route+' '+r.status);return r.json();},route);
const wait=async(route,predicate)=>{for(let n=0;n<150;n++){const data=await api(route);if(predicate(data))return data;await page.waitForTimeout(100);}throw Error('Unsettled canonical state '+route);};
const finishAll=async()=>{for(let n=0;n<150;n++){if(await d().getByText(/Ready for the next committed answer|Saved-answer reading finished/).count())return;await page.evaluate(()=>window.__finishReading());await page.waitForTimeout(20);}throw Error('Final speech tail did not complete');};
try{
 await page.goto(base);await page.getByPlaceholder('Operator key').fill(key);await page.getByRole('button',{name:'Enter workspace',exact:true}).click();await page.getByRole('heading',{name:'Conversation',exact:true}).waitFor();
 await page.getByRole('button',{name:/Open Sage helper/}).click();await d().waitFor();
 if(!await d().getByRole('button',{name:'Read replies',exact:true}).isDisabled())throw Error('Unconfigured engine secretly substituted');
 if(await page.evaluate(()=>window.__reading.utterances.length))throw Error('Automatic reading before choice');
 pass('No voice is active by default; missing configured TTS never silently switches providers');
 await d().locator('.sage-reading-settings').getByText('Voice & reading options',{exact:false}).click();
 await d().getByLabel('Speech source', {exact:true}).selectOption('device');
 const voices=d().getByLabel('Device-reported local voice',{exact:true});
 if(await voices.locator('option[value="fixture-remote"]').count())throw Error('Remote voice selectable');
 if(!await d().getByRole('button',{name:'Read replies',exact:true}).isDisabled())throw Error('Voice auto-selected');
 await voices.selectOption('fixture-local');await d().getByRole('slider',{name:'Device reading speed'}).focus();await page.keyboard.press('Home');for(let n=0;n<3;n++)await page.keyboard.press('ArrowRight');
 await d().getByRole('button',{name:'Read replies',exact:true}).click();
 await d().getByText('Automatic device reading enabled',{exact:false}).waitFor();
 if(requests.some(r=>r.url.endsWith('/api/speech/session')))throw Error('Device option opened configured speech session');
 pass('Explicit local-reported voice, rate and reading gesture enable presentation with no mic/engine/model download');
 await d().getByRole('textbox',{name:'Message Sage',exact:true}).fill('Make the scripted note using the real canonical approval, then give the saved test answer.');await d().getByRole('button',{name:'Send to Sage',exact:true}).click();
 const s=await wait('/state',s=>s.runs.some(r=>r.kind==='chat'&&r.status==='awaiting_approval'));const run=s.runs.find(r=>r.kind==='chat'&&r.status==='awaiting_approval');
 if(await page.evaluate(()=>window.__reading.utterances.length))throw Error('Read an acknowledgement/tool log before final answer');
 await page.keyboard.press('Escape');if((await api('/runs/'+run.id)).status!=='awaiting_approval')throw Error('Closing panel stopped durable work');
 await page.getByRole('button',{name:/Open Sage helper/}).click();await d().getByRole('tab',{name:/Work & decisions/}).click();await d().getByRole('button',{name:'Approve & execute',exact:true}).click();
 await wait('/runs/'+run.id,r=>r.status==='succeeded');await d().getByRole('tab',{name:'Ask Sage',exact:true}).click();
 await page.waitForFunction(()=>window.__reading.utterances.length>0);
 const saved=(await api('/threads/'+run.thread_id+'/messages')).messages;assertSaved(saved,run.id);
 await finishAll();
 const spoken=await page.evaluate(()=>window.__reading.utterances.map(u=>({text:u.text,rate:u.rate,voice:u.voice?.voiceURI,local:u.voice?.localService})));
 const joined=spoken.map(u=>u.text).join('');
 if(!joined.includes('Last short answer tail.')||!joined.includes('**Important: approval is still your decision.**')||joined.includes('CODE_NOT_FOR_SPEECH'))throw Error('Final tail/warning/code presentation corrupted');
 if(!spoken.every(u=>u.voice==='fixture-local'&&u.local&&u.rate===0.8))throw Error('Wrong voice/rate');
 await page.waitForTimeout(1800);if(await page.evaluate(()=>window.__reading.utterances.length)!==spoken.length)throw Error('Polling duplicated read-aloud');
 pass('Actual approved run commits one complete answer; stable ID reader serializes all chunks/tail, preserves warnings, skips only chosen code, no duplicate polling audio');
 const before=(await api('/state')).runs.length;const beforeRequests=requests.filter(r=>r.url.endsWith('/api/chat')&&r.method==='POST').length;
 await d().getByRole('button',{name:'Read saved reply',exact:true}).click();await page.waitForFunction(n=>window.__reading.utterances.length>n,spoken.length);
 await d().getByRole('button',{name:'Stop speech only',exact:true}).click();const stopped=await page.evaluate(()=>window.__reading.utterances.length);
 await page.evaluate(()=>{const u=window.__reading.utterances.at(-1);u.onstart?.();u.onend?.();});await page.waitForTimeout(100);
 if(await page.evaluate(()=>window.__reading.utterances.length)!==stopped)throw Error('Stale callback restarted speech');
 if((await api('/state')).runs.length!==before||requests.filter(r=>r.url.endsWith('/api/chat')&&r.method==='POST').length!==beforeRequests)throw Error('Replay created model/tool work');
 pass('Saved replay/stop touch presentation only; delayed callbacks fenced and no model/tool/run replay');
 await d().getByRole('textbox',{name:'Message Sage',exact:true}).fill('Create another pending proposal for the exact cancellation test.');await d().getByRole('button',{name:'Send to Sage',exact:true}).click();
 const pending=await wait('/state',s=>s.runs.some(r=>r.kind==='chat'&&r.status==='awaiting_approval'));const next=pending.runs.find(r=>r.kind==='chat'&&r.status==='awaiting_approval');
 await d().getByRole('button',{name:'Stop speech only',exact:true}).click();await d().getByRole('button',{name:'Turn audio off',exact:true}).click();
 if((await api('/runs/'+next.id)).status!=='awaiting_approval')throw Error('Audio controls cancelled job');
 await d().getByRole('tab',{name:/Work & decisions/}).click();await d().locator('[data-run-id="'+next.id+'"]').getByRole('button',{name:'Cancel job',exact:true}).click();await wait('/runs/'+next.id,r=>r.status==='cancelled');
 pass('Stop/off retain awaiting approval; separate Cancel job cancels only the explicitly selected durable run');
 await d().getByRole('tab',{name:'Ask Sage',exact:true}).click();await d().locator('.sage-reading-settings').getByText('Voice & reading options',{exact:false}).click();
 const desktop=await new AxeBuilder({page}).include('#sage-helper-dialog').withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze();await fs.writeFile(path.join(output,'axe-desktop.json'),JSON.stringify(desktop.violations,null,2));if(desktop.violations.length)throw Error('Reading-control accessibility '+JSON.stringify(desktop.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))));
 await page.screenshot({path:path.join(output,'reading-controls-desktop.png'),timeout:20000});
 for(const width of [320,390,768,1440]){await page.setViewportSize({width,height:844});if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('Overflow '+width);if(await d().evaluate(el=>el.getBoundingClientRect().bottom>innerHeight+1||el.getBoundingClientRect().right>innerWidth+1))throw Error('Reading panel outside viewport');}
 await page.setViewportSize({width:390,height:844});const mobile=await new AxeBuilder({page}).include('#sage-helper-dialog').withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze();if(mobile.violations.length)throw Error('Mobile reading-control axe '+JSON.stringify(mobile.violations.map(v=>v.id)));
 await page.screenshot({path:path.join(output,'reading-controls-mobile.png'),timeout:20000});
 pass('Voice/source/speed/code controls stay keyboard-accessible and 320–1440px safe; scoped automated axe checks pass, not certification');
 await page.evaluate(()=>{window.__reading.voices=window.__reading.voices.filter(v=>!v.localService);window.speechSynthesis.dispatchEvent(new Event('voiceschanged'));});
 if(!await d().getByRole('button',{name:'Read replies',exact:true}).isDisabled())throw Error('Revoked voice silently replaced');
 if(await page.evaluate(()=>window.__reading.microphones)!==0||requests.some(r=>!r.url.startsWith(base+'/'))||errors.length)throw Error('Mic/external/browser error '+JSON.stringify(errors));
 pass('Voice loss is explicit; no microphone, third-party request, extra model or uncaught error in exercised paths');
}catch(error){records.push({name:'Sage reading suite did not complete',result:'fail',error:String(error)});throw error;}finally{
 await fs.writeFile(path.join(output,'results.json'),JSON.stringify({scope:'Real canonical app/API/files/approvals/jobs with explicit scripted provider. Device speech events mocked: no physical audible voice, native engine, GPU, owner PC or model-quality proof.',records,errors,requests:requests.map(r=>({path:new URL(r.url).pathname,method:r.method}))},null,2));await browser.close();
}
console.log(JSON.stringify(records,null,2));
function assertSaved(messages,id){if(messages.length!==2||messages.some(m=>m.meta.run_id!==id)||!messages.find(m=>m.role==='assistant').content.includes('CODE_NOT_FOR_SPEECH'))throw Error('Canonical answer/history was modified or duplicated');}
