/** Explicit device-reported-local speech presentation, not a model or a history owner.
 * Only committed assistant messages enter this reader. No DOM scraping, network,
 * microphone, persistence, tool execution, or destructive canonical-text cleanup.
 */
export type ReaderMessage = {id: string; role: string; content: string; meta?: {run_id?: string}};
export type ReaderOptions = {voiceURI: string; rate: number; skipCode: boolean};
export type ReaderStatus = 'off' | 'device-ready' | 'device-reading' | 'device-held' | 'device-error';
export type DeviceVoice = Pick<SpeechSynthesisVoice, 'voiceURI' | 'name' | 'lang' | 'localService'>;
export type ReaderSnapshot = {enabled: boolean; automatic: boolean; held: boolean; queued: number; status: ReaderStatus; detail: string};
export type UtteranceLike = {text: string; voice: DeviceVoice | null; rate: number; lang: string;
  onstart: (() => void) | null; onend: (() => void) | null; onerror: ((event: {error?: string}) => void) | null};
export type SpeechAdapter = {voices: () => DeviceVoice[]; utterance: (text: string) => UtteranceLike;
  speak: (utterance: UtteranceLike) => void; cancel: () => void};
const MAX_MESSAGE = 20000, MAX_QUEUE = 16, MAX_SEEN = 1024, MAX_CHUNK = 240;

export function deviceVoices(): DeviceVoice[] {
  try { return typeof window !== 'undefined' && window.speechSynthesis
    ? window.speechSynthesis.getVoices().filter(v => v.localService === true && !!v.voiceURI) : []; }
  catch { return []; }
}

/** Skip fenced code only when chosen. Do not remove emphasis, warnings, math, quotes or actions. */
export function speechPresentation(text: string, skipCode: boolean): string {
  if (!skipCode) return text;
  const lines = text.split(/(?<=\n)/); let fence: {char: string; length: number} | null = null;
  const out: string[] = [];
  for (const line of lines) {
    const marker = /^ {0,3}(`{3,}|~{3,})([^\r\n]*)/.exec(line);
    if (!fence && marker) {
      fence = {char: marker[1][0], length: marker[1].length};
      out.push('[Code block omitted from speech; the original answer is unchanged.]\n');
    } else if (fence) {
      if (marker && marker[1][0] === fence.char && marker[1].length >= fence.length && !marker[2].trim()) fence = null;
    } else out.push(line);
  }
  return out.join('');
}

/** Exact concatenation, including short final tails and Unicode surrogate pairs. */
export function speechChunks(text: string, max = MAX_CHUNK): string[] {
  if (!Number.isInteger(max) || max < 32 || max > 1000) throw new Error('Invalid speech chunk budget');
  const result: string[] = []; let rest = text;
  while (rest.length > max) {
    let end = max;
    const candidates = [...rest.slice(0, max + 1).matchAll(/[.!?]\s+|\n+/g)];
    if (candidates.length) {
      const last = candidates[candidates.length - 1];
      const boundary = last.index! + last[0].length;
      if (boundary >= Math.floor(max / 3)) end = Math.min(max, boundary);
    } else {
      const space = rest.slice(0, max).lastIndexOf(' ');
      if (space > Math.floor(max / 2)) end = space + 1;
    }
    // Never split a UTF-16 surrogate pair.
    if (/^[\uDC00-\uDFFF]$/.test(rest[end]) && /^[\uD800-\uDBFF]$/.test(rest[end - 1])) end--;
    result.push(rest.slice(0, end)); rest = rest.slice(end);
  }
  if (rest) result.push(rest);
  return result;
}

function browserAdapter(): SpeechAdapter {
  return {
    voices: deviceVoices,
    utterance: text => {
      if (typeof window === 'undefined' || !window.speechSynthesis || !window.SpeechSynthesisUtterance)
        throw new Error('This browser does not provide device speech');
      return new window.SpeechSynthesisUtterance(text) as unknown as UtteranceLike;
    },
    speak: u => window.speechSynthesis.speak(u as unknown as SpeechSynthesisUtterance),
    cancel: () => {if (typeof window !== 'undefined') window.speechSynthesis?.cancel();},
  };
}

type QueuedReply = {key: string; run: string | undefined; chunks: string[]; cursor: number};
export class DeviceReplyReader {
  private adapter: SpeechAdapter;
  private onChange: (state: ReaderSnapshot) => void;
  private options: ReaderOptions = {voiceURI: '', rate: 1, skipCode: true};
  private voice: DeviceVoice | null = null;
  private thread: string | null = null;
  private seen = new Set<string>();
  private queue: QueuedReply[] = [];
  private epoch = 0;
  private speaking = false;
  private expectedRun: string | null | undefined = undefined;
  private state: ReaderSnapshot = {enabled: false, automatic: false, held: false, queued: 0, status: 'off', detail: 'Device reading is off.'};

  constructor(onChange: (state: ReaderSnapshot) => void = () => {}, adapter?: SpeechAdapter) {
    this.onChange = onChange; this.adapter = adapter || browserAdapter();
  }
  snapshot(): ReaderSnapshot {return {...this.state, queued: this.queue.length};}
  private emit(status: ReaderStatus, detail: string) {
    this.state = {...this.state, status, detail, queued: this.queue.length}; this.onChange(this.snapshot());
  }
  private key(message: ReaderMessage): string {return this.thread + ':' + message.id;}
  private remember(key: string) {
    this.seen.add(key);
    while (this.seen.size > MAX_SEEN) this.seen.delete(this.seen.values().next().value!);
  }
  configure(options: ReaderOptions) {
    if (!Number.isFinite(options.rate) || options.rate < 0.5 || options.rate > 2)
      throw new Error('Device speech speed must be between 0.5 and 2.0');
    const voice = this.adapter.voices().find(v => v.localService === true && v.voiceURI === options.voiceURI);
    if (!voice) throw new Error('Choose an available voice reported local by this device. No remote voice was substituted.');
    this.options = {...options}; this.voice = voice;
  }
  enable(thread: string, messages: ReaderMessage[], options: ReaderOptions) {
    if (!thread) throw new Error('Choose a canonical conversation before enabling reading');
    this.configure(options); this.interrupt(); this.thread = thread; this.queue = []; this.seen.clear();
    for (const message of messages.slice(-MAX_SEEN)) this.remember(this.key(message)); // do not automatically replay existing history
    this.expectedRun = undefined;
    this.state = {...this.state, enabled: true, automatic: true, held: false};
    this.emit('device-ready', 'Automatic device reading enabled for new committed answers. The microphone remains closed.');
  }
  observe(thread: string | null, messages: ReaderMessage[]) {
    if (!this.state.enabled || !this.state.automatic || thread !== this.thread) return;
    for (const message of messages.slice(-MAX_SEEN)) {
      if (message.role !== 'assistant' || !message.id || typeof message.content !== 'string') continue;
      const key = this.key(message); if (this.seen.has(key)) continue;
      this.remember(key);
      if (typeof this.expectedRun === 'string' && message.meta?.run_id !== this.expectedRun) continue;
      this.enqueue(message, key);
    }
    this.drain();
  }
  private enqueue(message: ReaderMessage, key: string) {
    if (message.content.length > MAX_MESSAGE || this.queue.length >= MAX_QUEUE) {
      this.emit('device-error', 'Reading budget reached. The complete answer is still saved; choose an individual reply to read.'); return;
    }
    const text = speechPresentation(message.content, this.options.skipCode);
    if (!text.trim()) return;
    this.queue.push({key, run: message.meta?.run_id, chunks: speechChunks(text), cursor: 0});
  }
  /** User input yields presentation, not the model/tool job. New results can remain held. */
  hold() {
    if (!this.state.enabled) return;
    const interrupted = this.speaking;
    this.state.held = true; this.interrupt();
    // An interrupted reply is saved text, not an automatically restarted utterance.
    if (interrupted) this.queue.shift();
    this.emit('device-held', 'Speech held. Durable work continues; saved answers can be replayed explicitly.');
  }
  /** A new explicit turn must not release an older held automatic answer. */
  beginTurn(thread: string | null) {
    if (!this.state.enabled || thread !== this.thread) return;
    this.interrupt(); this.queue = []; this.expectedRun = null; this.state.held = true;
    this.emit('device-held', 'New turn started. Older automatic audio was discarded, not its saved text or work.');
  }
  expectReply(run: string) {
    if (!this.state.enabled || !this.state.automatic) return;
    this.expectedRun = run; this.queue = this.queue.filter(q => q.run === run); this.state.held = false; this.drain();
  }
  turnFailed() {
    if (!this.state.enabled) return;
    this.expectedRun = undefined; this.state.held = true;
    this.emit('device-error', 'The new turn was not confirmed. Inspect the saved work before resuming audio.');
  }
  resume() {
    if (!this.state.enabled || this.expectedRun === null) return;
    this.state.held = false; this.drain();
  }
  readSaved(thread: string, message: ReaderMessage, options: ReaderOptions) {
    if (message.role !== 'assistant' || !message.id) throw new Error('Only a saved assistant answer can be read');
    if (message.content.length > MAX_MESSAGE) throw new Error('This answer exceeds the device reading budget; no text was truncated');
    this.configure(options); this.interrupt(); this.queue = [];
    const sameAutoThread = this.state.automatic && this.thread === thread;
    this.thread = thread; this.state = {...this.state, enabled: true, automatic: sameAutoThread, held: false};
    this.enqueue(message, this.key(message)); this.drain();
  }
  /** Explicit one-off presentation (e.g. labelled static introduction), no model invocation. */
  readText(text: string, options: ReaderOptions) {
    this.readSaved('static-presentation', {id: 'static-introduction', role: 'assistant', content: text}, options);
  }
  stopSpeech() {
    if (!this.state.enabled) return;
    this.interrupt(); this.queue = []; this.state.held = true;
    this.emit('device-held', 'Speech stopped. No durable job was cancelled.');
  }
  disable() {
    this.interrupt(); this.thread = null; this.queue = []; this.seen.clear(); this.expectedRun = undefined;
    this.state = {...this.state, enabled: false, automatic: false, held: false}; this.emit('off', 'Device reading is off.');
  }
  private interrupt() {
    this.epoch++; this.speaking = false;
    try {this.adapter.cancel();} catch { /* cancellation is best effort; epoch fences all callbacks */ }
  }
  private drain() {
    if (!this.state.enabled || this.state.held || this.expectedRun === null || this.speaking) return;
    const reply = this.queue[0];
    if (!reply) {if (this.state.status !== 'device-error') this.emit('device-ready', this.state.automatic ? 'Ready for the next committed answer.' : 'Saved-answer reading finished.'); return;}
    if (reply.cursor >= reply.chunks.length) {this.queue.shift(); this.drain(); return;}
    const voice = this.adapter.voices().find(v => v.localService === true && v.voiceURI === this.options.voiceURI);
    if (!voice) {this.state.held = true; this.emit('device-error', 'The selected local-reported voice is no longer available. No fallback voice was used.'); return;}
    const epoch = this.epoch;
    try {
      const u = this.adapter.utterance(reply.chunks[reply.cursor]);
      u.voice = voice; u.lang = voice.lang; u.rate = this.options.rate; this.speaking = true;
      u.onstart = () => {if (epoch === this.epoch) this.emit('device-reading', 'Browser reports speech started; audible output is not independently verified.');};
      u.onend = () => {
        if (epoch !== this.epoch) return;
        this.speaking = false; reply.cursor++;
        // Schedule rather than recurse: a synchronous platform/test callback must not overflow the stack.
        queueMicrotask(() => {if (epoch === this.epoch) this.drain();});
      };
      u.onerror = event => {
        if (epoch !== this.epoch) return;
        this.speaking = false; this.state.held = true;
        this.emit('device-error', event.error === 'not-allowed' ? 'Browser audio is blocked. Use a reading/resume gesture; work and text are retained.' : 'Device speech did not complete. Text and durable work remain saved.');
      };
      this.adapter.speak(u);
    } catch {
      if (epoch !== this.epoch) return;
      this.speaking = false; this.state.held = true;
      this.emit('device-error', 'Device speech could not start. Text remains saved; no remote fallback was used.');
    }
  }
}
