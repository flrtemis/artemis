import {useEffect, useRef, useState, type ReactNode} from 'react';
import {ArrowDownToLine, ArrowRight, ArrowUp, AudioLines, BookOpen, FileText, Layers, MessageSquare, Paperclip, Search, ShieldCheck, Square, Wrench, X} from 'lucide-react';
import {active, bytes, when, type Approval, type Capability, type FileEntry, type Message, type Run, type Snapshot} from './client';
import {SageReadingControls, type ReadingControlProps} from './SageReadingControls';
import './sage-helper.css';

type Tab = 'ask' | 'capabilities' | 'work' | 'files';
const tabs: {id: Tab; label: string}[] = [
  {id: 'ask', label: 'Ask Sage'}, {id: 'capabilities', label: 'Capabilities'},
  {id: 'work', label: 'Work & decisions'}, {id: 'files', label: 'Files'},
];
type Props = {
  mode?: 'runtime' | 'preview';
  open: boolean; onOpen: () => void; onClose: () => void;
  snapshot: Snapshot; messages: Message[]; thread: string | null; viewName: string;
  draft: string; onDraft: (value: string) => void; onSend: () => void;
  canChat: boolean; working: boolean; selectedFile?: FileEntry; attachments: string[];
  onAttach: () => void; onRemoveAttachment: (path: string) => void; onAttachSelected: () => void;
  onSelectThread: (id: string | null) => void; onOpenConversation: () => void;
  onCapability: (name: string, args?: Record<string, unknown>) => void;
  onOpenFile: (path: string) => void; onDownload: (path: string) => void; onSettings: () => void;
  onCancel: (id: string) => void; renderApproval: (approval: Approval) => ReactNode;
  speechReady: boolean; voiceStatus: string; onReadReply: (id: string) => void;
  onEnableReading: () => void; onStopSpeech: () => void; onStopReading: () => void;
  onResumeAudio: () => void; readingControls?: ReadingControlProps;
};

/** A projection of the existing App state. No second history, model, run owner or audio engine. */
export function SageHelper(p: Props) {
  const [tab, setTab] = useState<Tab>('ask');
  const [query, setQuery] = useState('');
  const [fileQuery, setFileQuery] = useState('');
  const dialog = useRef<HTMLElement>(null);
  const launcher = useRef<HTMLButtonElement>(null);
  const log = useRef<HTMLDivElement>(null);
  const previousCount = useRef(p.messages.length);
  const nearEnd = useRef(true);
  const onClose = useRef(p.onClose); onClose.current = p.onClose;
  const run = p.snapshot.runs.find(r => r.kind === 'chat' && r.thread_id === p.thread && active(r.status));
  const pending = p.snapshot.approvals.length;
  const capabilities = p.snapshot.capabilities.filter(c => `${c.name} ${c.description} ${c.category}`.toLowerCase().includes(query.toLowerCase()));
  const files = p.snapshot.files.filter(f => !f.is_dir && f.path.toLowerCase().includes(fileQuery.toLowerCase()));
  const available = p.snapshot.capabilities.filter(c => c.available).length;
  const status = p.mode === 'preview' ? 'Static design preview · no model or backend' : run ? (run.status === 'awaiting_approval' ? 'Your decision is needed' : 'Working on your request')
    : p.canChat ? 'Your selected model is ready' : 'Local tools ready · model not connected';

  useEffect(() => {
    if (!p.open) return;
    const before = document.activeElement as HTMLElement | null;
    const panel = dialog.current!;
    panel.querySelector<HTMLButtonElement>('[data-sage-close]')?.focus();
    const keydown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') { event.preventDefault(); onClose.current(); return; }
      if (event.key !== 'Tab') return;
      const focusable = [...panel.querySelectorAll<HTMLElement>('button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled), a[href], [tabindex="0"]')]
        .filter(el => el.getClientRects().length > 0);
      if (!focusable.length) { event.preventDefault(); panel.focus(); return; }
      const first = focusable[0], last = focusable[focusable.length - 1];
      if (event.shiftKey && (document.activeElement === first || !panel.contains(document.activeElement))) {
        event.preventDefault(); last.focus();
      } else if (!event.shiftKey && (document.activeElement === last || !panel.contains(document.activeElement))) {
        event.preventDefault(); first.focus();
      }
    };
    // A send can disable the focused button and move focus to body. Keep the
    // modal's Escape/Tab contract even during that transient state.
    document.addEventListener('keydown', keydown);
    return () => {
      document.removeEventListener('keydown', keydown);
      // The launcher is hidden before effects run, so activeElement may already be body.
      // Restore after React makes it visible; do not focus the unfocusable body.
      requestAnimationFrame(() => {if (launcher.current) launcher.current.focus(); else if (before?.isConnected && before !== document.body) before.focus();});
    };
  }, [p.open]);

  useEffect(() => {
    if (p.open && tab === 'ask' && nearEnd.current && p.messages.length !== previousCount.current) {
      log.current?.scrollTo({top: log.current.scrollHeight});
    }
    previousCount.current = p.messages.length;
  }, [p.messages.length, p.open, tab]);

  const chooseCapability = (c: Capability) => {
    if (!c.available) return;
    p.onClose(); p.onCapability(c.name);
  };
  const quickCapability = (name: string, args?: Record<string, unknown>) => {
    if (!p.snapshot.capabilities.some(c => c.name === name && c.available)) return;
    p.onClose(); p.onCapability(name, args);
  };
  const tabKeys = (event: React.KeyboardEvent<HTMLButtonElement>, index: number) => {
    const next = event.key === 'ArrowRight' ? (index + 1) % tabs.length
      : event.key === 'ArrowLeft' ? (index + tabs.length - 1) % tabs.length
      : event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 : -1;
    if (next < 0) return;
    event.preventDefault(); setTab(tabs[next].id);
    dialog.current?.querySelector<HTMLButtonElement>(`#sage-tab-${tabs[next].id}`)?.focus();
  };

  return <>
    <button ref={launcher} className="sage-launcher" onClick={p.onOpen}
      aria-label={pending ? `Open Sage helper, ${pending} decisions waiting` : 'Open Sage helper'}
      aria-haspopup="dialog" aria-expanded={p.open} aria-controls={p.open ? "sage-helper-dialog" : undefined} hidden={p.open}>
      <span className="sage-launcher-symbol" aria-hidden="true"><Layers size={21}/></span>
      <span><strong>Sage</strong><small>{run ? 'Work continues' : 'Here when you need me'}</small></span>
      {pending > 0 && <b className="sage-pending-count" aria-hidden="true">{pending}</b>}
    </button>
    {p.open && <div className="sage-overlay">
      <button className="sage-scrim" aria-label="Close Sage helper" tabIndex={-1} onClick={p.onClose}/>
      <section ref={dialog} id="sage-helper-dialog" className="sage-panel" role="dialog" aria-modal="true"
        aria-labelledby="sage-helper-title" aria-describedby="sage-helper-description" tabIndex={-1}>
        <header className="sage-header">
          <span className="sage-header-symbol" aria-hidden="true"><Layers size={23}/></span>
          <div><span className="sage-overline">{p.mode === 'preview' ? 'DESIGN PREVIEW · NO BACKEND' : 'YOUR ARTEMIS ASSISTANT'}</span><h2 id="sage-helper-title">Sage</h2></div>
          <button data-sage-close className="sage-icon-button" onClick={p.onClose} aria-label="Close Sage helper"><X size={21}/></button>
        </header>
        <div className="sage-context">
          <p id="sage-helper-description">The same conversation, tools and decisions. Right here in {p.viewName}.</p>
          <div className="sage-status" role="status"><span className={run ? 'sage-dot working' : 'sage-dot'}/>{status}</div>
          <label className="sage-thread-label">Conversation
            <select value={p.thread || ''} disabled={p.working || !!p.draft.trim() || !!p.attachments.length}
              onChange={event => p.onSelectThread(event.target.value || null)}>
              <option value="">New conversation when you send</option>
              {p.snapshot.threads.map(t => <option key={t.id} value={t.id}>{t.title}</option>)}
            </select>
          </label>
          {(!!p.draft.trim() || !!p.attachments.length) && <p className="sage-small">Send or clear this draft before changing conversations. Closing this panel keeps the draft.</p>}
        </div>
        <div className="sage-tabs" role="tablist" aria-label="Sage helper sections">
          {tabs.map((t, index) => <button key={t.id} id={'sage-tab-' + t.id} role="tab"
            aria-selected={tab === t.id} aria-controls={tab === t.id ? 'sage-panel-' + t.id : undefined} tabIndex={tab === t.id ? 0 : -1}
            onKeyDown={event => tabKeys(event, index)} onClick={() => setTab(t.id)}>
            {t.label}{t.id === 'work' && pending > 0 && <span className="sage-tab-count">{pending}</span>}
          </button>)}
        </div>
        <div id={'sage-panel-' + tab} className={'sage-body sage-body-' + tab} role="tabpanel" aria-labelledby={'sage-tab-' + tab}>
          {tab === 'ask' && <>
            <div ref={log} className="sage-chat-log" tabIndex={0} role="log" aria-label="Canonical conversation messages" aria-live={p.voiceStatus === 'off' ? 'polite' : 'off'}
              onScroll={() => {const el = log.current; nearEnd.current = !el || el.scrollHeight - el.scrollTop - el.clientHeight < 80;}}>
              {!p.messages.length ? <div className="sage-welcome">
                <span className="sage-overline">ONE THREAD. NO STARTING OVER.</span>
                <h3>A little help,<br/><em>right where you are.</em></h3>
                <p>Ask, make, remember, or inspect a result. Changes still need your approval.</p>
                {!p.canChat && <div className="sage-model-notice"><strong>Chat needs your connected model.</strong><p>No stand-in answers. You can still use connected tools, files and decisions below.</p><button onClick={p.onSettings}>Connect your existing model <ArrowRight size={15}/></button></div>}
                <div className="sage-quick-actions">
                  <button onClick={() => quickCapability('write_file', {path: 'notes.md', content: '# Notes\n\n'})}><FileText size={17}/><span>Create an artifact<small>Review before writing</small></span><ArrowRight size={14}/></button>
                  <button onClick={() => quickCapability('remember')}><BookOpen size={17}/><span>Keep a memory<small>Choose what persists</small></span><ArrowRight size={14}/></button>
                  <button onClick={() => setTab('capabilities')}><Wrench size={17}/><span>Explore capabilities<small>{available} connected · other requirements visible</small></span><ArrowRight size={14}/></button>
                </div>
              </div> : p.messages.map(m => <article className={'sage-message sage-message-' + m.role} key={m.id} data-message-id={m.id}>
                <div className="sage-message-label"><strong>{m.role === 'user' ? 'You' : p.snapshot.continuity.name || 'Sage'}</strong><time>{when(m.ts)}</time></div>
                <div className="sage-message-text">{m.content}</div>
                {m.meta?.correction_for && <span className="sage-small">Correction · revision {m.meta.revision}</span>}
                {m.meta?.held_input_for && <span className="sage-small">Held for reconciliation, not answered in parallel</span>}
                {m.role === 'assistant' && <button className="sage-inline-button" disabled={!p.speechReady || p.working}
                  onClick={() => p.onReadReply(m.id)} title={p.speechReady ? 'Read this saved answer; do not re-run its work' : 'Configure an actual speech engine in Operations'}><AudioLines size={14}/>Read saved reply</button>}
                {m.meta?.attachments?.map((path: string) => <button className="sage-file-link" key={path} onClick={() => {p.onClose(); p.onOpenFile(path);}}><FileText size={13}/>{path}</button>)}
              </article>)}
            </div>
            {run && <div className="sage-active-job" role="status"><span>{run.status === 'awaiting_approval' ? 'Waiting for your decision' : 'Durable work continues'}</span><button onClick={() => setTab('work')}>Inspect work <ArrowRight size={13}/></button></div>}
            <div className="sage-composer">
              {p.selectedFile && !p.attachments.includes(p.selectedFile.path) && <button className="sage-context-attach" onClick={p.onAttachSelected}><Paperclip size={14}/>Include selected file: {p.selectedFile.name}</button>}
              {p.attachments.length > 0 && <div className="sage-attachments">{p.attachments.map(path => <span key={path}><FileText size={12}/>{path.split('/').pop()}<button onClick={() => p.onRemoveAttachment(path)} aria-label={'Remove attachment ' + path}><X size={13}/></button></span>)}</div>}
              <label className="sage-draft-label">{run ? 'Correct this active job' : 'Message Sage'}
                <textarea value={p.draft} maxLength={20000} rows={3} onChange={event => p.onDraft(event.target.value)}
                  placeholder={run ? 'A correction to this same job—not a separate request…' : p.mode === 'preview' ? 'Explore the interaction—no AI request is sent…' : 'What would you like to work on?'}
                  onKeyDown={event => {if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) {event.preventDefault(); if (p.canChat && !p.working && p.draft.trim()) p.onSend();}}}/>
              </label>
              <div className="sage-compose-actions"><button className="sage-icon-button" aria-label="Attach a file to Sage" onClick={p.onAttach}><Paperclip size={18}/></button><span>{run ? 'Completed effects are not undone.' : 'Your context. Explicit attachments.'}</span><button className="sage-send" aria-label={run ? 'Apply job correction' : 'Send to Sage'} onClick={p.onSend} disabled={!p.canChat || !p.draft.trim() || p.working}><ArrowUp size={18}/></button></div>
            </div>
          </>}
          {tab === 'capabilities' && <div className="sage-scroll" tabIndex={0}>
            <div className="sage-section-intro"><h3>What can we do?</h3><p>{p.mode === 'preview' ? 'Synthetic examples of registry readiness. These buttons explore the design; they do not run capabilities.' : 'The live ARTEMIS registry—not a list of promises. Every connected capability uses its existing permission flow.'}</p></div>
            <label className="sage-search"><Search size={16}/><span className="sage-sr-only">Find a capability</span><input value={query} onChange={event => setQuery(event.target.value)} placeholder="Files, memory, tools, documents…"/></label>
            <p className="sage-small">{available} connected · {p.snapshot.capabilities.length - available} unavailable or need configuration</p>
            <div className="sage-capabilities">{capabilities.map(c => <button className={'sage-capability ' + (!c.available ? 'sage-unavailable' : '')} key={c.name} onClick={() => chooseCapability(c)} disabled={!c.available}>
              <span className="sage-capability-top"><Wrench size={15}/><span>{c.available ? (c.requires_approval ? 'Approval required' : 'Scoped operation') : 'Not ready'}</span></span>
              <strong>{c.name.replaceAll('_', ' ')}</strong><span>{c.available ? c.description : c.unavailable_reason || 'Not connected in this host'}</span><small>{c.category}</small>
            </button>)}</div>
            {!capabilities.length && <p className="sage-empty">No matching capability. Try another search; unknown features are not silently added.</p>}
          </div>}
          {tab === 'work' && <div className="sage-scroll" tabIndex={0}>
            <div className="sage-section-intro"><h3>Work with a clear trail.</h3><p>Shared runs and exact approvals. Closing Sage or stopping speech does not cancel them.</p></div>
            {p.snapshot.approvals.map(a => <div className="sage-shared-approval" key={a.id}>{p.renderApproval(a)}</div>)}
            {!p.snapshot.runs.length && <div className="sage-empty"><ShieldCheck size={24}/><p>No work yet. Actual requests and decisions appear here.</p></div>}
            {p.snapshot.runs.slice(0, 25).map(r => <RunSummary key={r.id} run={r} working={p.working} onCancel={p.onCancel}/>)}
          </div>}
          {tab === 'files' && <div className="sage-scroll" tabIndex={0}>
            <div className="sage-section-intro"><h3>Your shared workspace.</h3><p>Open or download existing artifacts. {p.mode === 'preview' ? 'These are synthetic examples in this tab, not your actual files.' : 'No temporary inbox, private diary or other project is imported here.'}</p></div>
            <label className="sage-search"><Search size={16}/><span className="sage-sr-only">Find an artifact</span><input value={fileQuery} onChange={event => setFileQuery(event.target.value)} placeholder="Find an artifact…"/></label>
            <button className="sage-wide-button" onClick={p.onAttach}><Paperclip size={16}/>Upload a file to this workspace</button>
            {!files.length && <p className="sage-empty">No matching artifacts. Create one or upload a file explicitly.</p>}
            {files.map(f => <div className="sage-artifact" key={f.path}><button onClick={() => {p.onClose(); p.onOpenFile(f.path);}}><FileText size={17}/><span><strong>{f.name}</strong><small>{f.path} · {bytes(f.size)}</small></span></button><button className="sage-icon-button" onClick={() => p.onDownload(f.path)} aria-label={'Download ' + f.path}><ArrowDownToLine size={17}/></button></div>)}
          </div>}
        </div>
        <footer className="sage-footer">
          {p.readingControls ? <SageReadingControls {...p.readingControls}/> : <>
          <div className="sage-speech-controls"><AudioLines size={17}/><span>Answer audio</span>
            <button onClick={p.onEnableReading} disabled={!p.speechReady || p.working || p.voiceStatus !== 'off'} title={p.speechReady ? 'Enable configured answer audio without opening the microphone' : 'An actual configured TTS engine is required'}>Read replies</button>
            <button onClick={p.onStopSpeech} disabled={p.voiceStatus === 'off'}>Stop speech only</button>
          </div>
          {p.voiceStatus !== 'off' && <div className="sage-audio-state"><span>{p.voiceStatus.replaceAll('-', ' ')}</span>{['audio-held', 'job-active'].includes(p.voiceStatus) && <button onClick={p.onResumeAudio}>Resume audio</button>}<button onClick={p.onStopReading}>Turn audio off</button></div>}
          {!p.speechReady && <p className="sage-small">Speech is not configured. No browser or hosted voice is silently substituted.</p>}
          </>}
          <div className="sage-footer-links"><button onClick={p.onOpenConversation}><MessageSquare size={14}/>Open full conversation</button><button onClick={p.onSettings}>Connections & settings <ArrowRight size={13}/></button></div>
          <p className="sage-boundary"><ShieldCheck size={12}/>One identity · one history · host-enforced permissions</p>
        </footer>
      </section>
    </div>}
  </>;
}

function RunSummary({run, working, onCancel}: {run: Run; working: boolean; onCancel: (id: string) => void}) {
  return <article className="sage-run" data-run-id={run.id}>
    <div><span className={'sage-run-status ' + run.status}>{run.status.replaceAll('_', ' ')}</span><time>{when(run.created)}</time></div>
    <h4>{run.input}</h4><p className="sage-small">{run.kind} · run {run.id.slice(0, 10)}{run.steps ? ` · ${run.steps} model rounds` : ''}</p>
    {run.error && <p className="sage-run-error">{run.error}</p>}
    {run.result && <details><summary>Inspect stored result</summary><pre tabIndex={0} aria-label="Stored canonical result">{JSON.stringify(run.result, null, 2)}</pre></details>}
    {active(run.status) && <button className="sage-cancel-job" onClick={() => onCancel(run.id)} disabled={working}><Square size={13}/>Cancel job</button>}
  </article>;
}
