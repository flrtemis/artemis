// Shared-component static preview. Fake browser speech proves dispatch/control only, NEVER audible TTS.
import {chromium} from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
const base=(process.argv[2]||'http://localhost:4173').replace(/\/$/,''),root=new URL('../../../',import.meta.url).pathname,output=path.join(root,'.cache/sage-static-browser');
await fs.mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:process.env.ARTEMIS_CHROMIUM_BIN||undefined,args:['--no-sandbox']});
const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
await context.addInitScript(()=>{
 const synth=new EventTarget();window.__sageSpeech={spoken:[],cancelled:0};
 synth.getVoices=()=>[{voiceURI:'fixture-remote',name:'Fixture remote voice',localService:false,lang:'en-US'},{voiceURI:'fixture-local',name:'Fixture local voice',localService:true,lang:'en-US'}];
 synth.speak=u=>{window.__sageSpeech.spoken.push({text:u.text,localService:u.voice?.localService});u.onstart?.();u.onend?.();};synth.cancel=()=>window.__sageSpeech.cancelled++;
 Object.defineProperty(window,'speechSynthesis',{value:synth,configurable:true});window.SpeechSynthesisUtterance=class{constructor(text){this.text=text;}};
});
const page=await context.newPage();page.setDefaultTimeout(15000);page.setDefaultNavigationTimeout(20000);
const records=[],requests=[],errors=[],badResponses=[];const pass=name=>{records.push({name,result:'pass'});console.log('PASS',name);};
page.on('request',r=>requests.push(r.url()));page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.status()>=400)badResponses.push({url:r.url(),status:r.status()});});
const dialog=()=>page.getByRole('dialog',{name:'Sage',exact:true});
try{
 await page.goto(base+'/artemis/sage-preview.html');await page.getByRole('heading',{name:'A little help. A lot more continuity.'}).waitFor();
 await page.getByText('Static design preview. No AI model or backend.',{exact:true}).waitFor();
 pass('Project-prefix preview loads with explicit static/no-model/no-backend evidence boundary and preserved ARTEMIS name');
 await page.getByRole('button',{name:'Explore Sage',exact:true}).click();await dialog().waitFor();
 await dialog().getByRole('textbox',{name:'Message Sage',exact:true}).fill('A synthetic design question, not sent to a model.');await page.keyboard.press('Escape');
 await page.waitForFunction(()=>document.activeElement?.getAttribute('aria-label')?.startsWith('Open Sage helper'));
 await page.getByRole('button',{name:'Open Sage helper',exact:true}).click();
 if(await dialog().getByRole('textbox',{name:'Message Sage',exact:true}).inputValue()!=='A synthetic design question, not sent to a model.')throw Error('Static draft lost');
 await dialog().getByRole('button',{name:'Send to Sage',exact:true}).click();await dialog().getByText('Design example—not an AI answer.',{exact:false}).waitFor();
 pass('Actual shared helper component supports keyboard close/focus, draft retention and clearly labelled non-AI design response');
 await dialog().getByRole('tab',{name:'Capabilities',exact:true}).click();const unavailable=dialog().locator('.sage-capability').filter({hasText:'camera observation'});if(!await unavailable.isDisabled())throw Error('Planned perception enabled');
 await dialog().locator('.sage-capability').filter({has:page.locator('strong',{hasText:'write file'})}).click();await page.getByRole('region',{name:'Design-only capability proposal'}).waitFor();
 await page.getByText('DESIGN EXAMPLE — NOTHING EXECUTED',{exact:true}).waitFor();
 pass('Example capability/approval interactions stay synthetic and planned capabilities stay disabled');
 await page.getByRole('button',{name:'Open Sage helper',exact:true}).click();await dialog().getByRole('tab',{name:'Files',exact:true}).click();
 const download=page.waitForEvent('download');await dialog().getByRole('button',{name:'Download examples/notebook.md',exact:true}).click();const dl=await download;await dl.saveAs(path.join(output,'synthetic-notebook.md'));
 if(!(await fs.readFile(path.join(output,'synthetic-notebook.md'),'utf8')).includes('synthetic design example'))throw Error('Wrong local example');
 await dialog().getByRole('button',{name:'Close Sage helper',exact:true}).click();
 pass('Download generates only the labelled synthetic browser file, never a backend or private artifact request');
 await page.getByRole('button',{name:'Read introduction',exact:true}).click();const speech=await page.evaluate(()=>window.__sageSpeech);
 if(!speech.spoken.length||!speech.spoken.every(u=>u.localService))throw Error('Undisclosed remote voice');
 await page.getByRole('button',{name:'Stop narration only',exact:true}).click();
 pass('Optional narration requires gesture, selects device-reported local voice and has explicit stop; fixture is NOT physical audio proof');
 const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze();await fs.writeFile(path.join(output,'axe-page.json'),JSON.stringify(axe.violations,null,2));
 if(axe.violations.length)throw Error('Page accessibility '+JSON.stringify(axe.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))));
 await page.getByRole('button',{name:'Open Sage helper',exact:true}).click();await dialog().getByRole('tab',{name:'Ask Sage',exact:true}).click();
 const axed=await new AxeBuilder({page}).include('#sage-helper-dialog').withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze();if(axed.violations.length)throw Error('Dialog accessibility '+JSON.stringify(axed.violations.map(v=>v.id)));
 await page.screenshot({path:path.join(output,'static-sage-desktop.png'),timeout:20000});
 for(const width of [320,390,768,1440]){await page.setViewportSize({width,height:844});if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('Overflow '+width);if(await dialog().evaluate(el=>el.getBoundingClientRect().right>innerWidth+1||el.getBoundingClientRect().bottom>innerHeight+1))throw Error('Outside viewport '+width);}
 await page.setViewportSize({width:390,height:844});const axem=await new AxeBuilder({page}).include('#sage-helper-dialog').withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze();if(axem.violations.length)throw Error('Mobile accessibility '+JSON.stringify(axem.violations.map(v=>v.id)));
 await page.screenshot({path:path.join(output,'static-sage-mobile.png'),timeout:20000});
 if(!await page.evaluate(()=>matchMedia('(prefers-reduced-motion: reduce)').matches&&getComputedStyle(document.querySelector('.sage-panel')).transitionDuration==='0s'))throw Error('Reduced motion not honored');
 pass('Page/dialog automated axe, keyboard, 320-1440px layout and reduced-motion checks pass; not certification');
 await dialog().getByRole('button',{name:'Close Sage helper',exact:true}).click();
 if(!await page.getByRole('link',{name:/Back to the guide/}).isVisible())throw Error('Guide link missing');
 const protectedPaths=['/artemis/ideas/Information%20I%20saved%20while%20using%20perchance%20ai-agent.txt','/artemis/../ideas/README.md','/ideas/README.md','/artemis/api/state'];
 for(const route of protectedPaths){const r=await context.request.get(base+route);if(r.status()!==404)throw Error('Static server exposed non-docs '+route+' '+r.status());}
 pass('Guide link is accessible and static server refuses inbox/backend/out-of-prefix paths');
 if(requests.some(u=>!u.startsWith(base+'/artemis/')))throw Error('Unexpected request '+JSON.stringify(requests));
 if(badResponses.length||errors.length)throw Error('Assets/browser errors '+JSON.stringify({badResponses,errors}));
 const storage=await page.evaluate(()=>({local:localStorage.length,session:sessionStorage.length}));if(storage.local||storage.session||(await context.cookies()).length)throw Error('Unexpected tracking/session storage');
 pass('Only self-hosted /artemis/ assets requested; no model/API/localhost/third-party/credential traffic or tracking storage');
}catch(error){records.push({name:'Static Sage preview suite did not complete',result:'fail',error:String(error)});throw error;}finally{
 await fs.writeFile(path.join(output,'results.json'),JSON.stringify({scope:'Static shared-component visual interaction lab. Synthetic examples, mocked browser speech dispatch, no runtime, model, physical audio or deployment proof.',records,requests,errors,badResponses},null,2));await browser.close();
}
console.log(JSON.stringify(records,null,2));
