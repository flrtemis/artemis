import {useRef} from 'react';
import {AudioLines} from 'lucide-react';
import type {DeviceVoice, ReaderOptions, ReaderSnapshot} from './device-reader';

export type ReadingPreferences = {source: 'configured' | 'device'; device: ReaderOptions};
export type ReadingControlProps = {
  mode?: 'runtime' | 'preview'; preferences: ReadingPreferences; voices: DeviceVoice[];
  configuredReady: boolean; reader: ReaderSnapshot; voiceStatus: string; working: boolean;
  onPreferences: (value: ReadingPreferences) => void; onEnable: () => void;
  onStop: () => void; onOff: () => void; onResume: () => void;
};

/** Both choices are explicit; a missing configured engine never switches providers. */
export function SageReadingControls(p: ReadingControlProps) {
  const options = useRef<HTMLDetailsElement>(null);
  const enable = () => {p.onEnable(); if (options.current) options.current.open = false;};
  const device = p.preferences.source === 'device';
  const eligible = p.voices.some(v => v.localService === true && v.voiceURI === p.preferences.device.voiceURI);
  const ready = device ? eligible : p.configuredReady;
  const active = p.voiceStatus !== 'off';
  const autoOn = device ? p.reader.automatic : active;
  const changeDevice = (next: Partial<ReaderOptions>) => p.onPreferences({...p.preferences, device: {...p.preferences.device, ...next}});
  return <section className="sage-reading" aria-label="Answer reading controls">
    <div className="sage-reading-title"><AudioLines size={17}/><strong>Answer reading</strong><span>Presentation, not job control</span></div>
    <details ref={options} className="sage-reading-settings"><summary>Voice & reading options <span>{device ? 'Device choice' : 'Configured engine'}</span></summary><div className="sage-reading-settings-body" tabIndex={0} aria-label="Voice settings">
    <label className="sage-reading-provider">Speech source
      <select aria-label="Speech source" value={p.preferences.source} onChange={e => p.onPreferences({...p.preferences, source: e.target.value as ReadingPreferences['source']})}>
        <option value="configured" disabled={p.mode === 'preview'}>Configured ARTEMIS engine{!p.configuredReady ? ' · not ready' : ''}</option>
        <option value="device">Device voice · explicit local-reported choice</option>
      </select>
    </label>
    {device ? <>
      <label className="sage-reading-voice">Device-reported local voice
        <select aria-label="Device-reported local voice" value={p.preferences.device.voiceURI} onChange={e => changeDevice({voiceURI: e.target.value})}>
          <option value="">Choose a voice — no automatic substitution</option>
          {p.voices.filter(v => v.localService).map(v => <option key={v.voiceURI} value={v.voiceURI}>{v.name} · {v.lang}</option>)}
        </select>
      </label>
      <div className="sage-reading-options">
        <label>Reading speed <strong>{p.preferences.device.rate.toFixed(1)}×</strong>
          <input type="range" min="0.5" max="2" step="0.1" value={p.preferences.device.rate}
            aria-label="Device reading speed" aria-valuetext={p.preferences.device.rate.toFixed(1) + ' times normal'}
            onChange={e => changeDevice({rate: Number(e.target.value)})}/>
        </label>
        <label className="sage-reading-code"><input type="checkbox" checked={p.preferences.device.skipCode} onChange={e => changeDevice({skipCode: e.target.checked})}/>Skip fenced code in speech only</label>
      </div>
      <p className="sage-reading-disclosure">This uses an OS/browser voice the device reports as local. That report is not an independently verified offline/privacy guarantee. No remote voice, model, microphone or download is substituted. Device speech provides no avatar PCM/lip-sync.</p>
      {!eligible && <p className="sage-reading-warning" role="status">{p.voices.length ? 'Choose an available local-reported voice before reading.' : 'No local-reported voices are available yet. The complete answer remains readable.'}</p>}
    </> : <p className="sage-reading-disclosure">{p.configuredReady ? 'Uses your configured ARTEMIS speech pipeline and the same audio owner. Device voices and rate settings do not alter this engine.' : 'Configure an actual TTS engine in Operations, or deliberately choose the separate device-voice option. No silent fallback.'}</p>}
    </div></details>
    <div className="sage-reading-actions">
      <button onClick={enable} disabled={!ready || p.working || autoOn}>Read replies</button>
      <button onClick={p.onStop} disabled={!active}>Stop speech only</button>
      {active && <button onClick={p.onOff}>Turn audio off</button>}
      {['device-held', 'device-error', 'audio-held', 'job-active'].includes(p.voiceStatus) && <button onClick={p.onResume} disabled={!ready}>Resume audio</button>}
    </div>
    {active && <p className="sage-reading-state" role="status">{device ? p.reader.detail : p.voiceStatus.replaceAll('-', ' ')}{p.mode === 'preview' ? ' Static examples only; no AI or durable job.' : ''}</p>}
    <p className="sage-reading-boundary">Only saved user-facing answers are read. Original text and durable work stay intact. Voice selection/settings last only in this page; there is no hidden persistence.</p>
  </section>;
}
