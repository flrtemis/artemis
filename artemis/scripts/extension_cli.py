#!/usr/bin/env python3
"""Explicit local proposal/import/export client. Never auto-approves or loads code.

Use the operator key printed by your local launcher (prompted, not saved).
An exported contribution contains only that tool's code/schema/test/manifest,
not conversations, provider credentials, Sage memories or general state.
"""
import argparse
import getpass
import json
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from artemis_app.capability_contract import CONTRACT, valid_name


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--url', default='http://localhost:8000', help='Your local authenticated ARTEMIS gateway, not Ollama')
    commands = p.add_subparsers(dest='command', required=True)
    propose = commands.add_parser('propose', help='Import one JSON contribution as an approval proposal')
    propose.add_argument('file', type=Path)
    use = commands.add_parser('use', help='Propose use of a live generated tool (approval still required)')
    use.add_argument('name')
    use.add_argument('arguments', help='A JSON object')
    export = commands.add_parser('export', help='Explicitly export one selected tested tool, not private state')
    export.add_argument('name')
    export.add_argument('--out', required=True, type=Path)
    status = commands.add_parser('status')
    status.add_argument('run_id')
    chat = commands.add_parser('chat', help='Real configured Ollama request; no fixture fallback')
    chat.add_argument('text')
    chat.add_argument('--thread', help='Existing canonical thread ID; otherwise create one')
    args = p.parse_args()
    origin = args.url.rstrip('/')
    token = None

    def request(path, data=None):
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['X-Artemis-Session'] = token
        body = json.dumps(data, ensure_ascii=False, allow_nan=False).encode() if data is not None else None
        req = Request(origin + '/api' + path, data=body, headers=headers)
        try:
            with urlopen(req, timeout=180) as r:
                return json.load(r)
        except HTTPError as e:
            raise ValueError(e.read().decode(errors='replace')) from e

    token = request('/auth', {'key': getpass.getpass('Local operator key (not stored): ')})['token']
    if args.command == 'propose':
        if args.file.stat().st_size > 100_000:
            raise ValueError('Contribution exceeds 100 KB')
        obj = json.loads(args.file.read_text())
        if obj.get('contract') != CONTRACT:
            raise ValueError('Use the documented artemis.capability/v1 import contract')
        result = request('/tools/propose', {'tool': 'create_tool', 'arguments': obj['proposal']})
    elif args.command == 'use':
        valid_name(args.name)
        result = request('/tools/propose', {'tool': args.name, 'arguments': json.loads(args.arguments)})
    elif args.command == 'export':
        valid_name(args.name)
        obj = request('/extensions/' + quote(args.name, safe='') + '/export')
        # Do not overwrite somebody's contribution or export unrelated state.
        with args.out.open('x', encoding='utf-8') as f:
            json.dump(obj, f, ensure_ascii=False, indent=2, allow_nan=False)
            f.write('\n')
        print('Exported only the selected tool to ' + str(args.out))
        return
    elif args.command == 'chat':
        thread = args.thread or request('/threads', {})['id']
        result = request('/chat', {'thread_id': thread, 'text': args.text})
        result['thread_id'] = thread
    else:
        result = request('/runs/' + quote(args.run_id, safe=''))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.command in ('propose', 'use', 'chat'):
        print('Open Activity in your LOCAL app to review any approvals. Nothing is auto-approved.\nUse status RUN_ID or return to the same conversation for the verified result.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError) as e:
        raise SystemExit(str(e))
