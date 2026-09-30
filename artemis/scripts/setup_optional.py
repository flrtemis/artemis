"""Explicit optional downloads. Nothing runs/downloads merely by importing the app.
Model/engine files remain outside the integration package; originals are not modified.
"""
from pathlib import Path
import argparse,httpx,zipfile,io,hashlib,json,sys
ROOT=Path(__file__).resolve().parent.parent
p=argparse.ArgumentParser();p.add_argument('--godot',action='store_true');p.add_argument('--cpu-speech',action='store_true');args=p.parse_args()
cache=ROOT.parent/'.cache';cache.mkdir(exist_ok=True)
if args.godot:
    target=cache/'native-engines';target.mkdir(exist_ok=True)
    url='https://github.com/godotengine/godot/releases/download/4.4.1-stable/Godot_v4.4.1-stable_linux.x86_64.zip'
    with httpx.Client(follow_redirects=True,timeout=120) as c:r=c.get(url);r.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        for n in z.namelist():
            if '/' in n or '..' in n:raise ValueError('Unexpected engine archive path')
        z.extractall(target)
    binary=target/'Godot_v4.4.1-stable_linux.x86_64';binary.chmod(0o755)
    (target/'download-provenance.json').write_text(json.dumps({'url':url,'version':'4.4.1-stable','archive_sha256':hashlib.sha256(r.content).hexdigest()},indent=2))
    print('Godot installed:',binary,'(Linux x86_64 pinned build; not a latest-release claim)')
if args.cpu_speech:
    from huggingface_hub import snapshot_download
    folder=cache/'speech-models';voice=folder/'piper';voice.mkdir(parents=True,exist_ok=True)
    base='https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/low/en_US-lessac-low.onnx'
    with httpx.Client(follow_redirects=True,timeout=120) as c:
        for suffix in ['', '.json']:
            r=c.get(base+suffix);r.raise_for_status();(voice/('en_US-lessac-low.onnx'+suffix)).write_bytes(r.content)
    whisper=folder/'whisper-tiny'
    snapshot_download('Systran/faster-whisper-tiny.en',local_dir=str(whisper),allow_patterns=['model.bin','config.json','tokenizer.json','vocabulary.txt','preprocessor_config.json'])
    print('Optional CPU baseline models installed. In Operations → Speech use:')
    print('Piper model:',voice/'en_US-lessac-low.onnx');print('Whisper directory:',whisper)
    print('This baseline voice/model is not claimed to be your existing Qwen/Parakeet/voice profile. Original asset terms remain applicable.')
if not args.godot and not args.cpu_speech:p.print_help()
