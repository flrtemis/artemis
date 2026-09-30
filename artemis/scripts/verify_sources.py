"""Verify that retained originals are still byte-identical to the pinned source inventory."""
from pathlib import Path
import json,hashlib,sys
root=Path(__file__).resolve().parent.parent
manifest=json.loads((root/'SOURCE_MAP.json').read_text());fail=[]
for x in manifest['files']:
    p=root/x['bundled_path']
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=x['sha256']:fail.append(x['bundled_path'])
if fail:print('Original-source integrity failures:\n'+'\n'.join(fail));sys.exit(1)
print(f"Verified {len(manifest['files'])} retained source/asset files against pinned original hashes. Adapters are separate.")
