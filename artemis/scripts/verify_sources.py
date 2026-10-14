"""Strict retained-source verification, including Git LFS pointers + payloads.

An LFS pointer is NOT a byte-identical binary. Accept it only if its oid/size
match the historical pinned hash and actual payload size AND the bundled runtime payload
matches those bytes. No hydration/download, hash relabelling or vendor edits.
"""
from pathlib import Path
import hashlib
import json
import re
import sys

LFS = re.compile(rb'version https://git-lfs.github.com/spec/v1\noid sha256:([a-f0-9]{64})\nsize ([0-9]+)\n?')
PAYLOADS = {
    'vendor_sources/gemma_avatar/public/avatars/brunette.glb': 'web/avatars/brunette.glb',
    'vendor_sources/gemma_avatar/public/vendor/model-en-mixed.bin': 'web/vendor/model-en-mixed.bin',
}


def verify(root):
    manifest = json.loads((root / 'SOURCE_MAP.json').read_text())
    blobs, pointers, failures = 0, 0, []
    for item in manifest['files']:
        path = root / item['bundled_path']
        if not path.is_file():
            failures.append(item['bundled_path'] + ': missing')
            continue
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() == item['sha256']:
            blobs += 1
            continue
        pointer = LFS.fullmatch(data)
        runtime = root / PAYLOADS.get(item['bundled_path'], '__no_payload_mapping__')
        if (pointer and pointer[1].decode() == item['sha256'] and
                runtime.is_file() and runtime.stat().st_size == int(pointer[2]) and
                (item.get('bytes') is None or int(pointer[2])==item['bytes']) and
                hashlib.sha256(runtime.read_bytes()).hexdigest() == item['sha256']):
            pointers += 1
        else:
            failures.append(item['bundled_path'] + ': pinned bytes or LFS/runtime payload mismatch')
    return {'byte_identical_blobs': blobs, 'lfs_pointers_with_verified_runtime_payloads': pointers,
            'total': len(manifest['files']), 'failures': failures}


def main():
    result = verify(Path(__file__).resolve().parent.parent)
    print(json.dumps(result, indent=2))
    if result['failures']:
        sys.exit(1)
    print('Adapters remain separate. LFS pointers are explicitly NOT counted as byte-identical blobs.')


if __name__ == '__main__':
    main()
