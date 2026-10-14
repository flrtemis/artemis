"""Explicit, disposable Sage UI contract host: scripted decisions, real canonical state.

No model weights, remote provider, personal Sage import, fabricated sandbox,
physical speech or production fallback. Run only with the confirmation flag.
"""
import argparse
import secrets
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from artemis_app.api import create_app
from tests.test_integration import FixtureProvider, call


class SageUIProvider(FixtureProvider):
    def config(self):
        return {'base_url': 'http://127.0.0.1:11434', 'model': 'SCRIPTED_SAGE_UI_TEST_NO_LLM', 'allow_remote_context': False}

    async def health(self):
        return {'connected': True, 'model_ready': True, 'models': ['SCRIPTED_SAGE_UI_TEST_NO_LLM'],
                'configured_model': 'SCRIPTED_SAGE_UI_TEST_NO_LLM', 'evidence': 'scripted UI contract; no inference'}

    async def chat(self, messages, schemas, *, config=None):
        # A real mutating file operation stays pending until the operator decides.
        last = messages[-1]
        if last['role'] == 'tool':
            return {'content': 'Scripted UI test answer. The canonical tool result was received in this same job and conversation; this is not real model inference.'}
        return {'tool_calls': [call('write_file', {'path': 'sage-scripted-ui-note.md', 'content': '# Synthetic UI test\n\nExact operator approval required.\n'})]}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--confirm-scripted-provider', required=True, action='store_true')
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--port', default=8040, type=int)
    args = p.parse_args()
    import uvicorn
    with tempfile.TemporaryDirectory(prefix='artemis-sage-ui-contract-') as data:
        key = secrets.token_urlsafe(24)
        print('TEST ONLY: scripted model decisions; real runtime, files, thread, runs and approvals. No LLM.', flush=True)
        print('Temporary operator key: ' + key, flush=True)
        app = create_app(Path(data), key, SageUIProvider([]))
        uvicorn.run(app, host=args.host, port=args.port)
