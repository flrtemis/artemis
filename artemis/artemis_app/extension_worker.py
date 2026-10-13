"""Trusted *sandbox-side* entry point. Generated modules NEVER enter the gateway.

Copied read-only beside tool.py and request.json into the isolated worker. Only
stdlib Python is available. stdout is one bounded JSON envelope; tool output is
untrusted data, not an authorization or a claim of safety.
"""
import contextlib
import io
import json
import runpy
import sys


def main():
    logs = io.StringIO()
    try:
        with open('/extension/request.json', encoding='utf-8') as f:
            arguments = json.load(f)
        with contextlib.redirect_stdout(logs), contextlib.redirect_stderr(logs):
            module = runpy.run_path('/extension/tool.py')
            result = module['execute'](**arguments)
        # Fail on NaN/Infinity, non-JSON values and oversized results.
        encoded = json.dumps(result, ensure_ascii=False, allow_nan=False)
        if len(encoded.encode('utf-8')) > 64_000:
            raise ValueError('Extension result exceeds 64 KB')
        envelope = {'ok': True, 'result': result, 'logs': logs.getvalue()[:4000]}
    except BaseException as e:
        envelope = {'ok': False, 'error': type(e).__name__ + ': ' + str(e)[:1500],
                    'logs': logs.getvalue()[:4000]}
    sys.stdout.write(json.dumps(envelope, ensure_ascii=False, allow_nan=False))


if __name__ == '__main__':
    main()
