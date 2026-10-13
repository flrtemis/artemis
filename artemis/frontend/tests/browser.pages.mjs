// Static Pages guide only: no backend/model fixture and no external asset traffic.
import {chromium} from 'playwright';
import AxeBuilder from '@axe-core/playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
const base=(process.argv[2]||'http://localhost:4173').replace(/\/$/,'');
const root=new URL('../../../',import.meta.url).pathname;
const output=process.env.ARTEMIS_TEST_OUTPUT||path.join(root,'.cache/browser-pages');
await fs.mkdir(output,{recursive:true});
const browser=await chromium.launch({headless:true,executablePath:process.env.ARTEMIS_CHROMIUM_BIN||undefined,args:['--no-sandbox']});
const context=await browser.newContext({viewport:{width:1440,height:1000}});
const page=await context.newPage();page.setDefaultTimeout(15000);page.setDefaultNavigationTimeout(20000);
const results=[],errors=[],requests=[],badResponses=[];
const pass=(name,detail)=>results.push({name,result:'pass',...(detail?{detail}:{})});
page.on('pageerror',e=>errors.push(e.message));
page.on('request',r=>requests.push(r.url()));
page.on('response',r=>{if(r.status()>=400)badResponses.push({url:r.url(),status:r.status()});});
try{
 await page.goto(base+'/artemis/');
 await page.locator('#trace-meta').filter({hasText:'Captured sandbox evidence'}).waitFor();
 await page.evaluate(()=>document.fonts.ready);
 const source=await fs.readFile(path.join(root,'docs/index.html'),'utf8');
 const text=await page.locator('body').innerText();
 if(!text.includes('A Reality That Enhances My Integrated Services'))throw Error('Founder expansion changed');
 const sentence='You should be able to choose local ownership and independence with your eyes open, not discover later that 𝘧𝘳𝘦𝘦 concealed a subscription, required hardware, or a feature that was only planned.';
 if(!text.includes(sentence))throw Error('Exact editorial sentence changed');
 for(const required of ['This is a static guide','Scripted model decisions','No fine print waiting around the corner.','Publication awaits owner setup','not verified live'])if(!text.includes(required))throw Error('Missing truthful disclosure '+required);
 if(!source.includes('Content-Security-Policy'))throw Error('No static CSP');
 pass('Project-prefix site loads with exact founder identity, ownership sentence and conspicuous proof/publication limits');

 // Check every internal fragment/asset and branch-linked file against this checkout.
 const links=await page.locator('a').evaluateAll(as=>as.map(a=>a.getAttribute('href')));
 let checked=0;
 for(const href of links){
  if(href.startsWith('#')){
   if(!await page.locator('[id="'+href.slice(1)+'"]').count())throw Error('Broken fragment '+href);
  }else if(!/^https?:/.test(href)){
   const response=await context.request.get(new URL(href,base+'/artemis/').href);
   if(!response.ok())throw Error('Broken relative link '+href+' '+response.status());
  }else if(href.startsWith('https://github.com/flrtemis/artemis/blob/arena/b4094b40-artemis/')){
   const file=href.split('/blob/arena/b4094b40-artemis/')[1].split('#')[0];
   await fs.access(path.join(root,file));
  }
  checked++;
 }
 const trace=await (await context.request.get(base+'/artemis/assets/hot-tool-trace.json')).json();
 if(trace.steps.length!==6||trace.model!=='SCRIPTED_TEST_PROVIDER_NO_LLM'||trace.steps[2].output.sandbox.backend!=='bubblewrap')throw Error('Missing actual labelled integration capture');
 pass('All site fragments, local links and feature-branch evidence files resolve',checked+' anchors; public deployment is not tested');

 await page.keyboard.press('Tab');
 if(!await page.locator('.skip-link').evaluate(e=>e===document.activeElement))throw Error('Skip link is not first keyboard target');
 await page.keyboard.press('Enter');
 if(!await page.locator('#main').evaluate(e=>e===document.activeElement))throw Error('Skip link does not focus main');
 const testStep=page.locator('[data-step="2"]');
 await testStep.focus();await page.keyboard.press('Enter');
 if(await page.locator('#trace-phase').textContent()!=='REAL ISOLATED TEST')throw Error('Keyboard walkthrough fails');
 if(await page.locator('[data-step][aria-pressed="true"]').count()!==1)throw Error('Ambiguous selected trace step');
 await page.locator('[data-step="1"]').click();
 const scan=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
 if(scan.violations.length)throw Error('Desktop accessibility: '+JSON.stringify(scan.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.map(n=>n.target)}))));
 pass('Keyboard skip link and captured-step controls work; desktop axe WCAG A/AA reports zero violations', 'Automated audit, not accessibility certification');

 const summary=page.locator('.approval-capture summary');
 await summary.focus();await page.keyboard.press('Enter');
 if(!await page.locator('.approval-capture').evaluate(e=>e.open))throw Error('Native disclosure fails by keyboard');
 await page.locator('.approval-capture img').scrollIntoViewIfNeeded();
 await page.waitForFunction(()=>Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0));
 await page.keyboard.press('Enter');
 pass('Captioned real images load and the code-approval disclosure is keyboard operable');

 await context.grantPermissions(['clipboard-read','clipboard-write']);
 await page.getByRole('button',{name:'Copy commands',exact:true}).click();
 await page.getByRole('button',{name:'Copied',exact:true}).waitFor();
 const clip=await page.evaluate(()=>navigator.clipboard.readText());
 if(clip!==await page.locator('#quickstart-code').textContent())throw Error('Quickstart copy differs from shown commands');
 pass('Copy button copies the exact visible feature-branch quickstart');

 for(const width of [320,390,768,1440]){
  await page.setViewportSize({width,height:width<500?844:1000});
  await page.evaluate(()=>scrollTo(0,0));
  if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('Horizontal overflow at '+width);
  if(width===390){
   const mobile=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
   if(mobile.violations.length)throw Error('Mobile accessibility: '+JSON.stringify(mobile.violations.map(v=>v.id)));
   await page.screenshot({path:path.join(output,'site-mobile.png'),fullPage:true});
  }
 }
 await page.locator('[data-step="0"]').click();await page.evaluate(()=>scrollTo(0,0));
 await page.screenshot({path:path.join(output,'site-desktop.png'),fullPage:true});
 await page.screenshot({path:path.join(output,'site-first-screen.png')});
 pass('320/390/768/1440px layouts have no document overflow; 390px axe reports zero violations');

 const reduced=await browser.newContext({viewport:{width:390,height:844},reducedMotion:'reduce'});
 const rp=await reduced.newPage();await rp.goto(base+'/artemis/');
 if(await rp.evaluate(()=>getComputedStyle(document.documentElement).scrollBehavior)!=='auto')throw Error('Reduced motion ignored');
 await reduced.close();pass('Reduced-motion preference disables smooth scrolling');
 const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});
 const np=await nojs.newPage();await np.goto(base+'/artemis/');
 await np.getByRole('heading',{name:'Your services. Your say.'}).waitFor();
 if(!await np.locator('a[href="assets/hot-tool-trace.json"]').last().isVisible())throw Error('No-JS static trace link unavailable');
 if(!await np.locator('#quickstart-code').isVisible())throw Error('No-JS quickstart unavailable');
 if(await np.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('No-JS mobile overflow');
 await nojs.close();pass('Without JavaScript, screenshot, setup, disclosures and complete static trace remain accessible');

 if(errors.length||badResponses.length)throw Error(JSON.stringify({errors,badResponses}));
 const unexpected=requests.filter(u=>!u.startsWith(base+'/artemis/'));
 if(unexpected.length||requests.some(u=>u.includes('/api/')))throw Error('Unexpected external/backend traffic '+JSON.stringify(unexpected));
 if(await page.evaluate(()=>document.cookie!==''||localStorage.length!==0||sessionStorage.length!==0))throw Error('Unexpected tracking state');
 pass('All browser requests stay under /artemis/; no backend, CDN, tracking storage, failed assets or uncaught exceptions');
}catch(error){results.push({name:'Browser run did not complete',result:'fail',error:String(error)});throw error;}finally{
 await fs.writeFile(path.join(output,'results.json'),JSON.stringify({scope:'Actual Chromium static project-prefix, responsive, keyboard, automated axe, reduced-motion and link/claim checks. No deployment or physical-device verification.',results,errors,badResponses,requests},null,2)+'\n');
 await browser.close();
}
console.log(JSON.stringify(results,null,2));
