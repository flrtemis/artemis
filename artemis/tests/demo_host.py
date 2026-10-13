"""EXPLICIT TEST-ONLY host for reproducible screenshots/integration evidence.

Model decisions are scripted. Generated code still runs through the actual
approval, durable Store and real sandbox. Never a normal-launch fallback.
Fresh temporary data only; no personal Sage import, weights or provider calls.
"""
import argparse
import secrets
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from artemis_app.api import create_app
from tests.test_hot_tools import HotToolProvider


class ScreenshotProvider(HotToolProvider):
    def config(self):
        return {'base_url': 'http://127.0.0.1:11434', 'model': 'SCRIPTED_TEST_PROVIDER_NO_LLM', 'allow_remote_context': False}

    async def health(self):
        return {'connected': True, 'models': ['SCRIPTED_TEST_PROVIDER_NO_LLM'],
                'configured_model': 'SCRIPTED_TEST_PROVIDER_NO_LLM', 'model_ready': True,
                'base_url': 'http://127.0.0.1:11434', 'evidence': 'scripted test decisions, no real LLM'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--confirm-fixture-provider', action='store_true', required=True)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8030)
    args = parser.parse_args()
    import uvicorn
    with tempfile.TemporaryDirectory(prefix='artemis-synthetic-demo-') as data:
        key = secrets.token_urlsafe(24)
        print('TEST ONLY: scripted provider decisions, synthetic data; sandbox execution is real.', flush=True)
        print('Temporary operator key: ' + key, flush=True)
        app = create_app(Path(data), key, ScreenshotProvider())
        uvicorn.run(app, host=args.host, port=args.port)
