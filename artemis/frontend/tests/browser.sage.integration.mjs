// Disposable normal + explicit scripted UI hosts only. Never test against personal Sage state.
import {chromium} from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
const key=process.argv[2],base=(process.argv[3]||'http://localhost:8000').replace(/\/$/,''),mode=process.argv[4]||'normal';
if(!key)throw Error('A temporary disposable-host key is required. Never commit it.');
const root=new URL('../../../',import.meta.url).pathname,output=path.join(root,'.cache/sage-browser-'+mode);
await fs.mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:process.env.ARTEMIS_CHROMIUM_BIN||undefined,args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader']});
const context=await browser.newContext({viewport:{width:1440,height:1000}});
await context.addInitScript(()=>{window.__sageMicRequests=0;navigator.mediaDevices.getUserMedia=()=>{window.__sageMicRequests++;throw Error('No physical microphone is part of this test');};});
const page=await context.newPage();page.setDefaultTimeout(15000);page.setDefaultNavigationTimeout(20000);
const records=[],errors=[],chatRequests=[];
const pass=(name,detail)=>{records.push({name,result:'pass',...(detail?{detail}:{})});console.log('PASS',name);};
page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(r.url().endsWith('/api/chat'))chatRequests.push(r.url());});
const dialog=()=>page.getByRole('dialog',{name:'Sage',exact:true});
const open=async()=>{await page.getByRole('button',{name:/Open Sage helper/}).click();await dialog().waitFor();};
const close=async()=>{await dialog().getByRole('button',{name:'Close Sage helper',exact:true}).click();};
const api=async(route,body)=>page.evaluate(async({route,body})=>{const headers={'X-Artemis-Session':sessionStorage.getItem('artemis-session'),'Content-Type':'application/json'};const r=await fetch('/api'+route,{headers,...(body!==undefined?{method:'POST',body:JSON.stringify(body)}:{})});if(!r.ok)throw Error('API '+route+' '+r.status);return r.json();},{route,body});
const waitAPI=async(route,predicate)=>{for(let attempt=0;attempt<150;attempt++){const data=await api(route);if(predicate(data))return data;await page.waitForTimeout(100);}throw Error('Canonical state did not settle: '+route);};
try{
 await page.goto(base);await page.getByPlaceholder('Operator key').fill(key);await page.getByRole('button',{name:'Enter workspace',exact:true}).click();await page.getByRole('heading',{name:'Conversation',exact:true}).waitFor();
 for(const name of ['Workspace','Continuity','Laboratory','Operations','Conversation']){
  await page.getByRole('navigation').getByRole('button',{name,exact:true}).click();await open();await dialog().getByText('Right here in '+name+'.',{exact:false}).waitFor();await close();
 }
 if(chatRequests.length)throw Error('Opening helper/navigation requested an answer');
 pass('Sage is available across all five views; open/close/navigation create no chat or second model owner');
 await open();await dialog().getByRole('textbox',{name:'Message Sage',exact:true}).fill('Synthetic draft kept while the panel closes');await page.keyboard.press('Escape');
 await page.waitForFunction(()=>document.activeElement?.getAttribute('aria-label')?.startsWith('Open Sage helper'));
 await open();if(await dialog().getByRole('textbox',{name:'Message Sage',exact:true}).inputValue()!=='Synthetic draft kept while the panel closes')throw Error('Draft lost');
 await dialog().getByRole('textbox',{name:'Message Sage',exact:true}).fill('');
 const closeButton=dialog().getByRole('button',{name:'Close Sage helper',exact:true});await closeButton.focus();await page.keyboard.press('Shift+Tab');
 if(!await dialog().evaluate(el=>el.contains(document.activeElement)))throw Error('Focus escaped dialog');
 await dialog().getByRole('tab',{name:'Ask Sage',exact:true}).focus();await page.keyboard.press('ArrowRight');
 if(!await dialog().getByRole('tab',{name:'Capabilities',exact:true}).evaluate(el=>el===document.activeElement&&el.getAttribute('aria-selected')==='true'))throw Error('Arrow tab navigation failed');
 pass('Draft persists; Escape returns focus; focus stays contained; tabs support keyboard navigation');
 const caps=(await api('/state')).capabilities;
 await dialog().getByRole('textbox',{name:'Find a capability'}).fill('');
 for(const c of caps){const card=dialog().locator('.sage-capability').filter({has:page.locator('strong',{hasText:c.name.replaceAll('_',' ')})});await card.first().waitFor();}
 const blocked=caps.find(c=>!c.available);if(blocked&&!await dialog().locator('.sage-capability').filter({has:page.locator('strong',{hasText:blocked.name.replaceAll('_',' ')})}).first().isDisabled())throw Error('Unavailable capability enabled');
 pass('Actual canonical registry is discoverable, including disabled capabilities/reasons—not invented parity');
 await dialog().getByRole('textbox',{name:'Find a capability'}).fill('write_file');
 await dialog().locator('.sage-capability').filter({has:page.locator('strong',{hasText:'write file'})}).click();
 await page.getByRole('heading',{name:'Make something happen.'}).waitFor();
 const note='sage-helper-'+Date.now()+'.md';await page.getByLabel('path',{exact:false}).fill(note);await page.getByLabel('content',{exact:false}).fill('# Real scoped file\nCreated only after explicit approval.\n');await page.getByRole('button',{name:'Create proposal',exact:true}).click();
 let snapshot=await api('/state');if(snapshot.files.some(f=>f.path===note))throw Error('Unapproved file write');const a=snapshot.approvals.find(a=>a.args.path===note);if(!a)throw Error('No real approval');
 await open();await dialog().getByRole('tab',{name:/Work & decisions/}).click();await dialog().getByRole('button',{name:'Approve & execute',exact:true}).click();
 await waitAPI('/state',s=>s.files.some(f=>f.path===note));
 snapshot=await api('/state');if(snapshot.approvals.some(x=>x.id===a.id))throw Error('Duplicate unresolved approval');
 pass('Helper proposes through existing tool UI and renders the same exact approval; actual file writes only after decision');
 await dialog().getByRole('tab',{name:'Files',exact:true}).click();await dialog().getByRole('textbox',{name:'Find an artifact'}).fill(note);
 const download=page.waitForEvent('download');await dialog().getByRole('button',{name:'Download '+note,exact:true}).click();const dl=await download;
 await dl.saveAs(path.join(output,note));if(!(await fs.readFile(path.join(output,note),'utf8')).includes('Created only after explicit approval'))throw Error('Wrong artifact content');
 await dialog().locator('.sage-artifact').getByRole('button').first().click();await page.getByRole('heading',{name:'Workspace',exact:true}).waitFor();await page.getByRole('heading',{name:note,exact:true}).waitFor();
 pass('Open/download use the actual authenticated workspace artifact; no raw inbox or unrelated project imported');
 await open();await dialog().getByRole('tab',{name:'Ask Sage',exact:true}).click();
 if(mode==='normal'){
  if(!await dialog().getByRole('button',{name:'Send to Sage',exact:true}).isDisabled())throw Error('Disconnected chat enabled');
  if(!await dialog().getByRole('button',{name:'Read replies',exact:true}).isDisabled())throw Error('Unconfigured voice enabled');
  if(chatRequests.length)throw Error('Unexpected assistant request on disconnected host');
  pass('Missing model/TTS are explicit, no fabricated reply or silent browser/hosted voice fallback');
 }else{
  const previousChats=(await api('/state')).runs.filter(r=>r.kind==='chat').length;
  await dialog().getByRole('textbox',{name:'Message Sage',exact:true}).fill('Write the synthetic scripted note using the real canonical approval.');await dialog().getByRole('button',{name:'Send to Sage',exact:true}).click();
  await waitAPI('/state',s=>s.runs.some(r=>r.kind==='chat'&&r.status==='awaiting_approval'));
  let s=await api('/state');const run=s.runs.find(r=>r.kind==='chat'&&r.status==='awaiting_approval');if(s.runs.filter(r=>r.kind==='chat').length!==previousChats+1)throw Error('Expected one new canonical chat, observed '+s.runs.filter(r=>r.kind==='chat').length);
  if(!await page.getByRole('heading',{name:'Workspace',exact:true}).isVisible())throw Error('Helper jumped away from workspace');
  await dialog().getByRole('tab',{name:/Work & decisions/}).click();await dialog().getByRole('button',{name:'Approve & execute',exact:true}).click();
  await waitAPI('/runs/'+run.id,r=>r.status==='succeeded');
  const saved=(await api('/threads/'+run.thread_id+'/messages')).messages;if(saved.length!==2||saved.some(m=>m.meta.run_id!==run.id))throw Error('Different message/run ownership');
  await dialog().getByRole('tab',{name:'Ask Sage',exact:true}).click();await dialog().getByText('Scripted UI test answer.',{exact:false}).waitFor();
  await dialog().getByRole('button',{name:'Open full conversation',exact:true}).click();await page.getByRole('heading',{name:'Conversation',exact:true}).waitFor();await page.locator('.message-content').filter({hasText:'Scripted UI test answer.'}).waitFor();
  pass('Scripted decision / REAL runtime: helper stays in view, approval/result/answer share one original run/thread and full history');
  await open();await dialog().getByRole('textbox',{name:'Message Sage',exact:true}).fill('Create another synthetic approval, then test explicit durable cancellation.');await dialog().getByRole('button',{name:'Send to Sage',exact:true}).click();
  await waitAPI('/state',s=>s.runs.some(r=>r.kind==='chat'&&r.status==='awaiting_approval'));
  s=await api('/state');const cancelRun=s.runs.find(r=>r.kind==='chat'&&r.status==='awaiting_approval');
  await close();if((await api('/runs/'+cancelRun.id)).status!=='awaiting_approval')throw Error('Closing helper cancelled work');
  await open();await dialog().getByRole('tab',{name:/Work & decisions/}).click();await dialog().locator('[data-run-id="'+cancelRun.id+'"]').getByRole('button',{name:'Cancel job',exact:true}).click();
  await waitAPI('/runs/'+cancelRun.id,r=>r.status==='cancelled');
  pass('Closing helper preserves pending durable job; explicit Cancel job cancels that exact job only');
 }
 const allTabs=[];
 for(const name of ['Ask Sage','Capabilities','Work & decisions','Files']){
  await dialog().getByRole('tab',{name,exact:true}).click();
  const checked=await new AxeBuilder({page}).include('#sage-helper-dialog').withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze();
  allTabs.push({name,violations:checked.violations});
 }
 await fs.writeFile(path.join(output,'axe-all-tabs.json'),JSON.stringify(allTabs,null,2));
 if(allTabs.some(t=>t.violations.length))throw Error('Accessibility in helper sections '+JSON.stringify(allTabs.filter(t=>t.violations.length).map(t=>({name:t.name,ids:t.violations.map(v=>v.id)}))));
 pass('All four helper sections have zero scoped automated axe violations, including real work/results and file lists');
 await dialog().getByRole('tab',{name:'Ask Sage',exact:true}).click();
 const axe=await new AxeBuilder({page}).include('#sage-helper-dialog').withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze();
 await fs.writeFile(path.join(output,'axe-desktop.json'),JSON.stringify(axe.violations,null,2));if(axe.violations.length)throw Error('Helper accessibility '+JSON.stringify(axe.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>n.target)}))));
 await page.screenshot({path:path.join(output,'sage-desktop.png'),fullPage:false,timeout:20000});
 for(const width of [320,390,768]){
  await page.setViewportSize({width,height:844});if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('Overflow '+width);
  if(await dialog().evaluate(el=>el.getBoundingClientRect().right>innerWidth+1||el.getBoundingClientRect().bottom>innerHeight+1))throw Error('Dialog outside viewport '+width);
 }
 const mobile=await new AxeBuilder({page}).include('#sage-helper-dialog').withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze();await fs.writeFile(path.join(output,'axe-mobile.json'),JSON.stringify(mobile.violations,null,2));if(mobile.violations.length)throw Error('Mobile helper accessibility '+JSON.stringify(mobile.violations.map(v=>v.id)));
 await page.screenshot({path:path.join(output,'sage-mobile.png'),fullPage:false,timeout:20000});
 pass('Helper keyboard/1440-320px layout and scoped desktop/mobile automated axe checks pass; not certification');
 if(await page.evaluate(()=>window.__sageMicRequests)!==0)throw Error('A helper path requested microphone');if(errors.length)throw Error('Browser errors '+JSON.stringify(errors));
 pass('No microphone request, external model call or uncaught browser exception in exercised helper paths');
}catch(error){records.push({name:'Sage UI suite did not complete',result:'fail',error:String(error)});throw error;}finally{
 await fs.writeFile(path.join(output,'results.json'),JSON.stringify({scope:'Actual production frontend/API/Store/Runtime. '+(mode==='normal'?'Unconfigured real host, no model.':'Explicit scripted provider, no inference. Real file approvals, durable run/thread. No physical speech or model-quality proof.'),records,errors,chatRequests:chatRequests.length},null,2));await browser.close();
}
console.log(JSON.stringify(records,null,2));
