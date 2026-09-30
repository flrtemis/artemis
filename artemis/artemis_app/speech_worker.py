"""Local STT/TTS model worker. Does not own conversation, tools or an LLM."""
import sys,json,base64,io,wave,math,os
from pathlib import Path
os.environ.setdefault('OMP_NUM_THREADS','1')
def main():
    cfg=json.loads(Path(sys.argv[1]).read_text());voice=None;whisper=None
    import numpy as np
    for line in sys.stdin:
        try:
            request=json.loads(line);typ=request['type']
            if typ=='tts':
                if voice is None:
                    from piper import PiperVoice
                    voice=PiperVoice.load(cfg['piper_model'])
                buf=io.BytesIO()
                try:
                    with wave.open(buf,'wb') as w:voice.synthesize_wav(request['text'],w)
                    with wave.open(io.BytesIO(buf.getvalue()),'rb') as r:rate=r.getframerate();samples=np.frombuffer(r.readframes(r.getnframes()),dtype='<i2').astype(np.float32)
                except Exception:
                    # Native failure must reach CLI fallback (not the old try/else bug).
                    import subprocess,tempfile
                    with tempfile.TemporaryDirectory() as td:
                        output=Path(td)/'out.wav';p=subprocess.run([cfg.get('piper_executable','piper'),'--model',cfg['piper_model'],'--output_file',str(output)],input=request['text'],text=True,capture_output=True,timeout=30)
                        if p.returncode or not output.exists():raise RuntimeError('Piper native and CLI synthesis failed')
                        with wave.open(str(output),'rb') as r:rate=r.getframerate();samples=np.frombuffer(r.readframes(r.getnframes()),dtype='<i2').astype(np.float32)
                if rate!=16000:samples=np.interp(np.arange(int(len(samples)*16000/rate))*rate/16000,np.arange(len(samples)),samples)
                pcm=np.clip(samples,-32768,32767).astype('<i2').tobytes();result={'pcm16':base64.b64encode(pcm).decode(),'sample_rate':16000,'samples':len(pcm)//2,'quality':'actual_piper_synthesis'}
            elif typ=='stt':
                if whisper is None:
                    from faster_whisper import WhisperModel
                    whisper=WhisperModel(cfg['whisper_model'],device=cfg.get('device','cpu'),compute_type='int8' if cfg.get('device','cpu')=='cpu' else 'float16',local_files_only=True,cpu_threads=1,num_workers=1)
                pcm=base64.b64decode(request['pcm16'],validate=True);samples=np.frombuffer(pcm,dtype='<i2').astype(np.float32)/32768
                segments,info=whisper.transcribe(samples,beam_size=1,language=cfg.get('language','en'),vad_filter=False,condition_on_previous_text=False)
                result={'text':' '.join(s.text.strip() for s in segments).strip(),'language':info.language,'quality':'actual_faster_whisper_transcription'}
            else:raise ValueError('Unknown speech worker request')
            print(json.dumps({'id':request['id'],'result':result}),flush=True)
        except Exception as e:print(json.dumps({'id':request.get('id') if 'request' in locals() else None,'error':str(e)}),flush=True)
if __name__=='__main__':main()
