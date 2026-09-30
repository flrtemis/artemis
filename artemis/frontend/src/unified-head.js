import {TalkingHead} from '@met4citizen/talkinghead';
import {sharedAudio} from './shared-audio';
// TalkingHead's exact node graph; only context creation/ownership is host-managed.
export class UnifiedTalkingHead extends TalkingHead {
  initAudioGraph(sampleRate = null) {
    this.audioCtx = sharedAudio.context();
    // Create audio nodes
    this.audioSpeechSource = this.audioCtx.createBufferSource();
    this.audioBackgroundSource = this.audioCtx.createBufferSource();
    this.audioBackgroundGainNode = this.audioCtx.createGain();
    this.audioSpeechGainNode = this.audioCtx.createGain();
    this.audioStreamGainNode = this.audioCtx.createGain();
    this.audioAnalyzerNode = this.audioCtx.createAnalyser();
    this.audioAnalyzerNode.fftSize = 256;
    this.audioAnalyzerNode.smoothingTimeConstant = 0.1;
    this.audioAnalyzerNode.minDecibels = -70;
    this.audioAnalyzerNode.maxDecibels = -10;
    this.audioReverbNode = this.audioCtx.createConvolver();
    
    // Connect nodes
    this.audioBackgroundGainNode.connect(this.audioReverbNode);
    this.audioAnalyzerNode.connect(this.audioSpeechGainNode);
    this.audioSpeechGainNode.connect(this.audioReverbNode);
    this.audioStreamGainNode.connect(this.audioReverbNode);
    this.audioReverbNode.connect(this.audioCtx.destination);
    
    // Apply reverb and mixer settings
    this.setReverb(this.currentReverb || null);
    this.setMixerGain(
      this.opt.mixerGainSpeech, 
      this.opt.mixerGainBackground
    );
    
    // Delete the stream audio worklet if initialised
    this.workletLoaded = false;
    if (this.streamWorkletNode) {
      try {
        this.streamWorkletNode.port.postMessage({type: 'stop'});
        this.streamWorkletNode.disconnect();
        this.isStreaming = false;
      } catch(e) { 
        console.error('Error disconnecting streamWorkletNode:', e);
        /* ignore */ 
      }
      this.streamWorkletNode = null;
    }
  }

}
