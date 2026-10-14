import {useEffect, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {ArrowRight, BookOpen, Check, FileText, Layers, ShieldCheck, Wrench} from 'lucide-react';
import {SageHelper} from './SageHelper';
import type {Approval, Capability, Message, Snapshot} from './client';
import './sage-preview.css';

const capability = (name: string, description: string, requires_approval: boolean, category: string, available = true, unavailable_reason: string | null = null): Capability => ({name, description, requires_approval, category, available, unavailable_reason, parameters: {type: 'object', properties: {}}});
const samples: Capability[] = [
  capability('write_file', 'Example: propose an exact change to a workspace file, then review it.', true, 'files'),
  capability('remember', 'Example: explicitly keep selected information in Sage continuity.', true, 'continuity'),
  capability('calculator', 'Example: scoped arithmetic through the canonical tool registry.', false, 'utilities'),
  capability('create_tool', 'Example: stage, approve and test a bounded Python capability.', true, 'generated'),
  capability('transcribe_audio', 'Example: configured speech worker, not a built-in browser assumption.', false, 'speech', false, 'Design example: an actual STT engine and explicit microphone consent are required.'),
  capability('camera_observation', 'Future consented vision contribution.', false, 'perception', false, 'Planned integration, not a working camera in this preview.'),
];
const exampleText = '# Example notebook\n\nThis is a synthetic design example, not a file from your ARTEMIS workspace.\nNo AI model, backend or private inbox content was used.\n';
function Preview() {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [proposal, setProposal] = useState<string | null>(null);
  const [notice, setNotice] = useState('');
  const [voice, setVoice] = useState<SpeechSynthesisVoice | null>(null);
  const [narration, setNarration] = useState('Optional device narration is off.');
  useEffect(() => {
    if (!('speechSynthesis' in window)) {setNarration('This browser has no speech synthesis. The preview stays readable.'); return;}
    const update = () => {setVoice(window.speechSynthesis.getVoices().find(v => v.localService) || null);};
    update(); window.speechSynthesis.addEventListener('voiceschanged', update);
    return () => {window.speechSynthesis.removeEventListener('voiceschanged', update); window.speechSynthesis.cancel();};
  }, []);
  const snapshot: Snapshot = {
    threads: [{id: 'static-design-thread', title: 'Synthetic design conversation', created: 0}],
    runs: [], approvals: [], continuity: {name: 'Sage'},
    provider: {model: 'NO_MODEL_STATIC_PREVIEW'}, milestone: 'Sage surface preview',
    capabilities: samples,
    files: [{path: 'examples/notebook.md', name: 'notebook.md', size: new TextEncoder().encode(exampleText).length, mime: 'text/markdown', is_dir: false}],
  };
  const send = () => {
    if (!draft.trim()) return;
    const text = draft.trim();
    setMessages(old => [...old,
      {id: 'design-user-' + old.length, role: 'user', content: text, meta: {}, ts: Date.now() / 1000},
      {id: 'design-reply-' + old.length, role: 'assistant', content: 'Design example—not an AI answer. In the local app, this same drawer sends your request to the selected model through the canonical ARTEMIS thread. Here, nothing was sent or executed. Explore Capabilities, Work & decisions, or Files to review the interaction.', meta: {design_only: true}, ts: Date.now() / 1000},
    ]);
    setDraft('');
  };
  const downloadExample = () => {
    const url = URL.createObjectURL(new Blob([exampleText], {type: 'text/markdown;charset=utf-8'}));
    const a = document.createElement('a'); a.href = url; a.download = 'sage-design-example.md'; a.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 5000);
    setNotice('Downloaded a synthetic example generated in this tab—not a server artifact.');
  };
  const readIntroduction = () => {
    if (!voice) {setNarration('No device-reported local voice is available. No remote voice was substituted.'); return;}
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance('Welcome to the Sage interaction lab. This is a static design preview, not the AI assistant. Sage is being added to the existing ARTEMIS workspace, with one conversation, explicit approvals, and controllable answer audio.');
    u.voice = voice;
    u.onstart = () => setNarration('Browser reports narration started. This does not verify that a speaker is audible.');
    u.onend = () => setNarration('Browser reports narration ended. Device voice: ' + voice.name + '.');
    u.onerror = () => setNarration('Narration did not complete. Check browser audio permissions; text remains available.');
    window.speechSynthesis.speak(u);
  };
  return <>
    <a className="lab-skip" href="#lab-main">Skip to preview</a>
    <header className="lab-nav"><a href="index.html" className="lab-brand"><img src="assets/mark.svg" width="29" height="29" alt=""/><span>ARTEMIS <small>SAGE INTERACTION LAB</small></span></a><a href="index.html">Back to the guide <ArrowRight size={14}/></a></header>
    <div className="lab-proof-notice" role="note"><ShieldCheck size={17}/><p><strong>Static design preview. No AI model or backend.</strong> Examples stay in this tab. This page cannot operate your computer, contact Ollama, or read your inbox.</p></div>
    <main id="lab-main" tabIndex={-1}>
      <section className="lab-hero"><div><span className="lab-eyebrow">ADDITIVE TO YOUR WORKSPACE · NOT A NEW CHAT SILO</span><h1>A little help.<br/><em>A lot more continuity.</em></h1><p>Sage belongs beside whatever you are doing—not behind another app, another login, or a conversation that starts from scratch.</p><p className="lab-acronym">A Reality That Enhances <strong>My</strong> Integrated Services</p><button className="lab-primary" onClick={() => setOpen(true)}><Layers size={18}/>Explore Sage <ArrowRight size={16}/></button><span className="lab-click-note">The same helper component used by the local ARTEMIS UI.</span></div>
        <aside className="lab-principles" aria-label="Sage design principles"><span className="lab-eyebrow">WHAT STAYS TRUE</span><div><MessageMark/><span><strong>One continuous conversation</strong><small>Your existing history, not a second assistant.</small></span></div><div><ShieldCheck size={20}/><span><strong>Your decisions still matter</strong><small>Proposals and exact approvals remain visible.</small></span></div><div><BookOpen size={20}/><span><strong>New ideas add to the plan</strong><small>Earlier work is not erased by the newest thought.</small></span></div><div><Wrench size={20}/><span><strong>Capabilities, honestly labelled</strong><small>Connected, needs configuration, or still planned.</small></span></div></aside>
      </section>
      <section className="lab-workspace" aria-labelledby="lab-workspace-title"><div className="lab-workspace-bar"><span><FileText size={15}/>SYNTHETIC WORKSPACE</span><span>Design exploration only</span></div><div className="lab-workspace-content"><div><span className="lab-eyebrow">KEEP YOUR PLACE</span><h2 id="lab-workspace-title">Your notebook stays here.</h2><p>Open Sage in the corner, explore the four sections, write a sample request, close and reopen it. Your draft stays while you move around this preview.</p><p>No live tools run here. Capability buttons let you inspect an example action; file download generates a small synthetic file in your browser.</p><button onClick={() => setOpen(true)}>Open the helper <ArrowRight size={14}/></button></div><pre aria-label="Synthetic notebook contents">{exampleText}</pre></div></section>
      {proposal && <section className="lab-proposal" aria-label="Design-only capability proposal"><span className="lab-eyebrow">DESIGN EXAMPLE — NOTHING EXECUTED</span><h2>{proposal.replaceAll('_', ' ')}</h2><p>In the real app this opens the existing scoped capability form and, for mutations, an exact approval. This preview does not write a file, keep a memory, run code, or create a real approval.</p><button onClick={() => {setProposal(null); setNotice('Example dismissed. No actual effect or durable task was created.');}}>Dismiss example <Check size={14}/></button></section>}
      <section className="lab-narration" aria-labelledby="lab-narration-title"><div><h2 id="lab-narration-title">Listen to the introduction</h2><p>Optional browser narration, explicitly started by you. Only a voice the device reports as local is eligible. This is separate from—and not proof of—the configured ARTEMIS speech pipeline or lip-sync.</p><p className="lab-audio-status" role="status">{narration}{!voice && ' No local voice detected yet.'}</p></div><div><button onClick={readIntroduction}>Read introduction</button><button onClick={() => {window.speechSynthesis?.cancel(); setNarration('Narration stopped. No work was cancelled.');}}>Stop narration only</button></div></section>
      <p className="lab-current-limits">Still in scope: real selected-model validation, original speech/vision/phone integration, native workers, accessibility testing on physical devices, and scoped private state. This design does not claim feature or model parity with Perchance/Muse Spark.</p>
      {notice && <p className="lab-notice" role="status">{notice}</p>}
    </main>
    <footer className="lab-footer"><span className="lab-footer-brand"><img src="assets/wordmark.svg" width="158" height="28" alt="⩘Ꝛ𝘛𝕰𝘔𝘐Ⲋ™ — ARTEMIS"/><span>A Reality That Enhances My Integrated Services</span></span><a href="index.html#start">Run the actual local application <ArrowRight size={14}/></a></footer>
    <SageHelper mode="preview" open={open} onOpen={() => setOpen(true)} onClose={() => setOpen(false)} snapshot={snapshot}
      messages={messages} thread="static-design-thread" viewName="a synthetic notebook" draft={draft} onDraft={setDraft} onSend={send}
      canChat working={false} attachments={[]} onAttach={() => {setOpen(false); setNotice('File uploads belong in the authenticated local application. Nothing is uploaded from this preview.');}}
      onRemoveAttachment={() => {}} onAttachSelected={() => {}} onSelectThread={() => {}}
      onOpenConversation={() => {setOpen(false); setNotice('Use the local app for the full canonical conversation. This is only a synthetic design example.');}}
      onCapability={name => {setOpen(false); setProposal(name);}} onOpenFile={() => {setOpen(false); setNotice('The synthetic notebook is displayed on this page; no real workspace was read.');}}
      onDownload={downloadExample} onSettings={() => {setOpen(false); setNotice('Model, speech, and capability connections are configured in the actual local ARTEMIS app, never in this static page.');}}
      onCancel={() => {}} renderApproval={(_a: Approval) => null} speechReady={false} voiceStatus="off" onReadReply={() => {}}
      onEnableReading={() => {}} onStopSpeech={() => {}} onStopReading={() => {}} onResumeAudio={() => {}}/>
  </>;
}
function MessageMark() {return <Layers size={20}/>;}
createRoot(document.getElementById('root')!).render(<Preview/>);
