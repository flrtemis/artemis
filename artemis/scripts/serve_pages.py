#!/usr/bin/env python3
"""Serve only root docs under /artemis/ for a faithful GitHub Pages preview.

This is a STATIC guide, not the authenticated application or an Ollama proxy.
No credentials/state or backend are exposed. Default local binding is private;
use --host 0.0.0.0 only for an intentional sandbox/browser preview.
"""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2] / 'docs'


class Pages(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == '/':
            self.send_response(302)
            self.send_header('Location', '/artemis/')
            self.end_headers()
            return
        if not path.startswith('/artemis/'):
            self.send_error(404, 'Static site lives under /artemis/')
            return
        self.path = self.path[len('/artemis'):]
        super().do_GET()

    def do_HEAD(self):
        path = urlsplit(self.path).path
        if not path.startswith('/artemis/'):
            self.send_error(404)
            return
        self.path = self.path[len('/artemis'):]
        super().do_HEAD()

    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        super().end_headers()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=4173)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Pages)
    print(f'Static ARTEMIS guide: http://{args.host}:{args.port}/artemis/ (not the app, not published)', flush=True)
    server.serve_forever()
