// Actual built ARTEMIS UI + HTTP + isolated execution. Test-provider host ONLY.
import {chromium} from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
const key=process.argv[2];
const base=process.argv[3]||'http://localhost:8030';
if(!key)throw Error('Pass the TEMPORARY test-host operator key; it is never written to artifacts');
const output=process.env.ARTEMIS_TEST_OUTPUT||new URL('../../../.cache/browser-03/',import.meta.url).pathname;
await fs.mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:process.env.ARTEMIS_CHROMIUM_BIN||undefined,args:['--no-sandbox','--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--autoplay-policy=no-user-gesture-required']});
const context=await browser.newContext({viewport:{width:1440,height:1000}});
const page=await context.newPage();page.setDefaultTimeout(15000);page.setDefaultNavigationTimeout(20000);
const errors=[],results=[];
page.on('pageerror',e=>errors.push(e.message));
await page.addInitScript(()=>{window.__micRequests=0;const original=navigator.mediaDevices?.getUserMedia;if(original)navigator.mediaDevices.getUserMedia=async()=>{window.__micRequests++;throw Error('No mic expected in this text/3D flow');};});
const pass=name=>results.push({name,result:'pass'});
const original='Find the median of [12, 3, 9, 6]. Create a needed capability if it is missing.';
try{
 await page.goto(base);await page.getByPlaceholder('Operator key').fill(key);await page.getByRole('button',{name:'Enter workspace',exact:true}).click();await page.waitForSelector('.app-shell');
 await page.getByText('SCRIPTED_TEST_PROVIDER_NO_LLM',{exact:true}).waitFor();
 const token=await page.evaluate(()=>sessionStorage.getItem('artemis-session'));
 const api=async(route,body)=>{const r=await fetch(base+'/api'+route,{method:body===undefined?'GET':'POST',headers:{'X-Artemis-Session':token,'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body)});if(!r.ok)throw Error(route+': '+await r.text());return r.json();};
 pass('Built UI authenticates against the labelled scripted test provider; no real model claimed');
 await page.getByRole('button',{name:'Enable 3D presence',exact:true}).click();await page.waitForTimeout(4500);
 if(await page.locator('.presence-error').count())throw Error(await page.locator('.presence-error').textContent());
 await page.locator('.presence-stage canvas').waitFor();pass('Actual Gemma stage/GLB/HeadAudio assets render in Chromium without microphone');
 await page.getByRole('textbox',{name:'Message Sage',exact:true}).fill(original);await page.getByRole('button',{name:'Send message',exact:true}).click();
 await page.getByRole('button',{name:'Activity',exact:true}).click();await page.locator('.approval-card').waitFor();
 let state=await api('/state');const first=state.approvals.find(a=>a.tool==='create_tool');if(!first)throw Error('Expected canonical creation approval');const runId=first.run_id;
 if(state.capabilities.some(c=>c.name==='median_values'))throw Error('Registered before approval');pass('Missing tool is proposed inside the actual durable chat run, not pre-registered');
 await page.screenshot({path:path.join(output,'creation-approval.png')});
 const createdResponse=page.waitForResponse(r=>r.url().includes('/api/approvals/'+first.id)&&r.request().method()==='POST');
 await page.getByRole('button',{name:'Approve & execute',exact:true}).click();const created=(await (await createdResponse).json()).result;
 if(!created.registered||created.test.sandbox.backend!=='bubblewrap')throw Error('No actual tested Bubblewrap registration: '+JSON.stringify(created));
 await page.locator('.approval-card strong').filter({hasText:'median values'}).waitFor();
 state=await api('/state');const second=state.approvals.find(a=>a.tool==='median_values');if(!second||second.run_id!==runId)throw Error('Invocation left the original run');
 const cap=state.capabilities.find(c=>c.name==='median_values');if(!cap?.available||!cap.requires_approval)throw Error('No live approved dynamic schema');pass('Real namespace/seccomp test hot-registers its live schema in this same host');
 const usedResponse=page.waitForResponse(r=>r.url().includes('/api/approvals/'+second.id)&&r.request().method()==='POST');
 await page.getByRole('button',{name:'Approve & execute',exact:true}).click();const used=(await (await usedResponse).json()).result;
 if(used.result.median!==7.5||used.result.count!==4)throw Error('Incorrect real isolated result');
 await page.locator('.message.assistant .message-content').filter({hasText:'The median is 7.5'}).waitFor();
 const final=await api('/runs/'+runId);if(final.status!=='succeeded')throw Error('Not committed');
 const messages=(await api('/threads/'+final.thread_id+'/messages')).messages;
 if(messages.length!==2||messages[0].content!==original||messages.some(m=>m.meta.run_id!==runId))throw Error('Duplicate/divergent canonical history');
 pass('Approved generated invocation produces 7.5; answer and original input share one stored run/thread');
 await page.locator('.activity-heading .icon-button').click();
 await page.screenshot({path:path.join(output,'workspace.png')});
 const trace={format:'artemis.recorded-integration/v1',captured_at:'2026-10-13',scope:'Actual UI/API/runtime/namespace/seccomp execution with SCRIPTED TEST PROVIDER decisions and synthetic data. Not real Ollama, physical PC, microphone, TTS or latency proof.',run_id:runId,thread_id:final.thread_id,model:'SCRIPTED_TEST_PROVIDER_NO_LLM',steps:[
  {phase:'CANONICAL USER REQUEST',title:'The original question stays present.',explanation:'One thread and one durable ARTEMIS run own every step. The scripted test provider requests a previously absent tool.',output:messages[0].content,meta:'run '+runId.slice(0,10)+' · thread '+final.thread_id.slice(0,10)},
  {phase:'EXACT OPERATOR PROPOSAL',title:'Review code, arguments and the test.',explanation:'The original Agent execute(**kwargs) contract is adapted, not imported into the gateway. No registration or execution before approval.',output:first.args,meta:'create_tool · code/schema/test approval'},
  {phase:'REAL ISOLATED TEST',title:'The staged code actually runs.',explanation:'Bubblewrap namespaces and a seccomp profile run the code with a JSON test vector. No user files, private continuity, network or subprocess grant.',output:created.test,meta:'real '+created.test.sandbox.backend+' test · JSON-only v1'},
  {phase:'LIVE CANONICAL CATALOGUE',title:'No runtime restart. No second agent.',explanation:'Only a passing tested version is activated. The next model round can discover its schema through the same registry.',output:{name:cap.name,version:cap.extension.version,contract:cap.extension.contract,available:cap.available,requires_approval:cap.requires_approval,parameters:cap.parameters},meta:'same runtime instance · same original run'},
  {phase:'SEPARATE INVOCATION APPROVAL',title:'Use the tool on the original numbers.',explanation:'Approving creation is not approving every future use. This exact invocation receives its own single-use, version-bound approval.',output:{arguments:second.args,result:used},meta:'real isolated result, not a model guess'},
  {phase:'COMMITTED CANONICAL ANSWER',title:'The same job answers from the result.',explanation:'The scripted provider reads the actual sandbox result. ARTEMIS commits one answer into the original conversation. The real embodied/speech client can read that stored text when configured.',output:{status:final.status,reply:messages[1].content,message_count:messages.length},meta:'one final assistant message · no real inference/audio claim'}
 ]};
 await fs.writeFile(path.join(output,'hot-tool-trace.json'),JSON.stringify(trace,null,2)+'\n');
 const before=await api('/state');if(before.runs.filter(r=>r.kind==='chat').length!==1)throw Error('Competing chat store');
 if(await page.evaluate(()=>window.__micRequests)!==0)throw Error('Unexpected mic acquisition');pass('Text, generated-tool and avatar flows request no mic; no competing chat job/history');
 await page.getByRole('button',{name:'Operations',exact:true}).click();await page.locator('.integration-row').nth(11).waitFor();
 if(await page.locator('.integration-row').count()!==12)throw Error('Current source census not represented');pass('Operations distinguishes twelve current sources from actual integration status');
 await page.setViewportSize({width:390,height:844});await page.getByRole('button',{name:'Conversation',exact:true}).click();await page.screenshot({path:path.join(output,'mobile-app.png')});
 if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+2))throw Error('Mobile horizontal overflow');pass('Narrow-screen canonical conversation remains usable');
 if(errors.length)throw Error(errors.join('; '));pass('No uncaught browser exceptions');
}catch(error){results.push({name:'Browser run did not complete',result:'fail',error:String(error)});throw error;}finally{await fs.writeFile(path.join(output,'results.json'),JSON.stringify({scope:'Actual Chromium built UI/API/namespace execution; scripted provider. No PC/audio/model proof.',results,errors},null,2));await browser.close();}
console.log(JSON.stringify(results,null,2));
