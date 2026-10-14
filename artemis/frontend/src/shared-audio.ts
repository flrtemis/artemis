import {post, type Message} from './client';
import {S2sWsRealtimeClient} from './s2s-client.js';
import {DeviceReplyReader, deviceVoices, type ReaderOptions, type ReaderSnapshot} from './device-reader';

/** One presentation coordinator. No method here owns/cancels a durable Runtime job. */
class SharedAudio extends EventTarget {
  ctx: AudioContext | null = null; stage: any = null; client: any = null;
  thread: string | null = null; tour: AudioBufferSourceNode | null = null; status = 'off';
  mode: 'off' | 'configured' | 'device' | 'tour' = 'off';
  private generation = 0;
  private reader = new DeviceReplyReader(state => {
    if (this.mode !== 'device') return;
    this.emit(state.status);
    this.dispatchEvent(new CustomEvent('reader', {detail: state}));
  });
  context() {
    if (!this.ctx || this.ctx.state === 'closed') this.ctx = new AudioContext({latencyHint: 'interactive'});
    return this.ctx;
  }
  active() {return this.mode !== 'off';}
  deviceVoices() {return deviceVoices();}
  readerState(): ReaderSnapshot {return this.reader.snapshot();}
  observeSaved(thread: string | null, messages: Message[]) {this.reader.observe(thread, messages);}
  adoptStage(stage: any) {
    this.stage = stage;
    if (stage) {
      if (stage.audioCtx !== this.context()) throw new Error('Avatar and speech must share the same AudioContext');
      this.client?.bindOutput(stage.voiceSink);
    }
  }
  emit(status: string) {
    this.status = status; this.dispatchEvent(new CustomEvent('status', {detail: status}));
    // Device speech exposes no PCM/visemes. Do not manufacture avatar lip-sync from API state.
    if (this.stage) this.stage.setConversationState(status === 'ai-speaking' ? 'speaking'
      : status === 'user-speaking' ? 'listening' : status === 'processing' ? 'processing' : 'idle');
  }
  private detachConfigured() {
    const old = this.client; this.client = null;
    return old ? Promise.resolve(old.close()).catch(() => {}) : Promise.resolve();
  }
  async start(thread: string, microphone = true) {
    const generation = ++this.generation;
    const ctx = this.context(); void ctx.resume(); // gesture unlock before awaits
    this.mode = 'off'; this.reader.disable(); this.stopTour();
    await this.detachConfigured();
    if (generation !== this.generation) throw new Error('Audio setup was superseded; durable work was not cancelled');
    const grant = await post('/speech/session', {thread_id: thread});
    if (generation !== this.generation) throw new Error('Audio setup was superseded; no session was opened');
    const url = new URL(grant.path, location.href); url.protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
    const client = new S2sWsRealtimeClient({directUrl: url.href, voice: 'sage', instructions: 'Host-controlled canonical conversation',
      audioContext: ctx, outputNode: this.stage?.voiceSink || ctx.destination, workletBaseUrl: '/worklets/',
      acquireMic: microphone ? () => navigator.mediaDevices.getUserMedia({audio: {echoCancellation: true, noiseSuppression: true, autoGainControl: true}}) : undefined,
      tools: [], noiseGate: {enabled: true, thresholdDb: -45}});
    this.client = client; this.thread = thread; this.mode = 'configured';
    const current = () => generation === this.generation && this.client === client && this.mode === 'configured';
    client.addEventListener('status', (e: any) => {if (current()) this.emit(typeof e.detail === 'string' ? e.detail : e.detail?.status || 'connected');});
    for (const type of ['transcript', 'artemis', 'error']) {
      client.addEventListener(type, (e: any) => {if (current()) this.dispatchEvent(new CustomEvent(type, {detail: e.detail}));});
    }
    try {
      await client.connect();
      if (!current()) {await client.close(); return null;}
      this.emit('connected'); return client;
    } catch (error) {
      if (current()) {this.client = null; this.thread = null; this.mode = 'off'; this.emit('off');}
      await client.close().catch(() => {}); throw error;
    }
  }
  /** Explicit selection only: no configured-engine failure silently enters this path. */
  enableDevice(thread: string, messages: Message[], options: ReaderOptions) {
    this.reader.configure(options); // fail before disrupting the current working audio source
    ++this.generation; this.mode = 'device'; this.thread = thread; this.stopTour();
    void this.detachConfigured(); this.reader.enable(thread, messages, options);
  }
  readDeviceMessage(thread: string, message: Message, options: ReaderOptions) {
    this.reader.configure(options);
    ++this.generation; this.mode = 'device'; this.thread = thread; this.stopTour();
    void this.detachConfigured(); this.reader.readSaved(thread, message, options);
  }
  configureDevice(options: ReaderOptions) {this.reader.configure(options);}
  beginText(thread: string | null) {if (this.mode === 'device') this.reader.beginTurn(thread);}
  expectDeviceReply(run: string) {if (this.mode === 'device') this.reader.expectReply(run);}
  deviceTurnFailed() {if (this.mode === 'device') this.reader.turnFailed();}
  async stopVoice() {
    const generation = ++this.generation; this.mode = 'off'; this.reader.disable(); this.stopTour();
    this.thread = null; await this.detachConfigured();
    if (generation === this.generation) this.emit('off');
  }
  cancel() {
    if (this.mode === 'device') this.reader.stopSpeech();
    this.client?.cancelUnifiedTurn(); this.stopTour(); this.stage?.setConversationState('idle');
  }
  /** Input yield keeps later results held; it never invokes /runs/:id/cancel. */
  holdForInput() {
    if (this.mode === 'device') this.reader.hold(); else this.cancel();
  }
  resumeAudio() {if (this.mode === 'device') this.reader.resume(); else this.client?.resumeAudio();}
  sendText(text: string) {
    if (!this.client) throw new Error('Start a configured speech session first');
    this.client.sendUserText(text); this.client.requestResponse();
  }
  speakMessage(id: string) {this.client?.speakMessage(id);}
  async playTour(url: string) {
    const ctx = this.context(); void ctx.resume(); await this.stopVoice();
    const generation = ++this.generation; this.mode = 'tour';
    const r = await fetch(url); if (!r.ok) throw new Error('Recorded narration not found');
    const buffer = await ctx.decodeAudioData(await r.arrayBuffer());
    if (generation !== this.generation || this.mode !== 'tour') return;
    const source = ctx.createBufferSource(); source.buffer = buffer; source.connect(this.stage?.voiceSink || ctx.destination);
    source.onended = () => {if (this.tour !== source) return; this.tour = null; this.mode = 'off'; this.emit('off'); this.dispatchEvent(new Event('tour-ended'));};
    this.tour = source; source.start();
  }
  stopTour() {
    if (this.tour) {const old = this.tour; this.tour = null; try {old.stop(); old.disconnect();} catch {}}
    if (this.mode === 'tour') {this.mode = 'off'; this.emit('off');}
  }
  stopAll() {this.cancel();}
}
export const sharedAudio = new SharedAudio();
