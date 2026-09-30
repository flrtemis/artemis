"""A small window onto her. Standard library only: http.server + SSE.

GET  /              the page
GET  /api/state     clock, state, counters
GET  /api/journal   recent events (?limit=&before=&kinds=)
GET  /api/memories  what she chose to keep
GET  /api/self      self.md + version list
GET  /api/context   continuity preamble (text/plain) for other systems, e.g. gemma-avatar instructions
GET  /api/export    everything as one plain-text file (log, state, memories, wants, self.md; private journal excluded)
GET  /api/stream    server-sent events: live wakes, journal, replies, state
POST /api/say       {"text": "..."} → {"reply": "...", "delivered": [...], ...}
POST /api/wake      wake her now
"""
from __future__ import annotations

import json
import queue
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .daemon import Daemon

WEB_DIR = Path(__file__).resolve().parent / "web"


def make_handler(d: Daemon):
    class Handler(BaseHTTPRequestHandler):
        server_version = "awake/0.1"

        def log_message(self, fmt, *args):  # quiet
            pass

        # ---------- helpers ----------
        def _json(self, obj, status=200):
            body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _text(self, text, status=200, ctype="text/plain; charset=utf-8"):
            body = text.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _body(self) -> dict:
            n = int(self.headers.get("Content-Length") or 0)
            if n <= 0:
                return {}
            try:
                return json.loads(self.rfile.read(n).decode("utf-8") or "{}")
            except Exception:
                return {}

        # ---------- GET ----------
        def do_GET(self):
            u = urlparse(self.path)
            q = parse_qs(u.query)
            p = u.path
            if p in ("/", "/index.html"):
                return self._text((WEB_DIR / "index.html").read_text(encoding="utf-8"), ctype="text/html; charset=utf-8")
            if p == "/api/state":
                return self._json(d.snapshot())
            if p == "/api/journal":
                limit = min(500, int(q.get("limit", ["80"])[0]))
                before = int(q["before"][0]) if q.get("before") else None
                kinds = tuple(q["kinds"][0].split(",")) if q.get("kinds") else None
                evs = d.memory.recent_events(limit=limit, kinds=kinds, before_id=before)
                for e in evs:
                    e["ts_str"] = d.clock.fmt(e["ts"], seconds=True)
                return self._json({"events": evs})
            if p == "/api/memories":
                ms = d.memory.all_memories(limit=300)
                for m in ms:
                    m["ts_str"] = d.clock.fmt(m["ts"])
                return self._json({"memories": ms})
            if p == "/api/wants":
                ws = d.memory.wants(status=None)
                for w in ws:
                    w["ts_str"] = d.clock.fmt(w["ts"])
                return self._json({"wants": ws})
            if p == "/api/letters":
                return self._json({"letters": d.letters()})
            if p == "/api/self":
                return self._json({"text": d.selfmodel.read(), "versions": d.selfmodel.versions()})
            if p == "/api/context":
                return self._text(d.context_text())
            if p == "/api/export":
                body = d.export_text().encode("utf-8")
                fname = f"awake-{d.name}-{d.clock.local().strftime('%Y%m%d-%H%M%S')}.txt"
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Disposition", f'attachment; filename="{fname}"')
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(body)
                return
            if p == "/api/stream":
                return self._stream()
            if p == "/healthz":
                return self._text("ok")
            return self._text("not found", 404)

        # ---------- POST ----------
        def do_POST(self):
            p = urlparse(self.path).path
            if p == "/api/say":
                body = self._body()
                text = str(body.get("text", ""))[:4000]
                if not text.strip():
                    return self._json({"error": "empty"}, 400)
                res = d.say(text)
                res["state"] = d.snapshot()
                return self._json(res)
            if p == "/api/wake":
                d.poke("web")
                return self._json({"ok": True})
            return self._text("not found", 404)

        # ---------- SSE ----------
        def _stream(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "keep-alive")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()
            qq = d.bus.subscribe()
            try:
                self.wfile.write(("data: " + json.dumps({"type": "state", "state": d.snapshot()}) + "\n\n").encode())
                self.wfile.flush()
                last_ping = time.time()
                while True:
                    try:
                        ev = qq.get(timeout=1.0)
                        self.wfile.write(("data: " + json.dumps(ev, ensure_ascii=False) + "\n\n").encode())
                        self.wfile.flush()
                    except queue.Empty:
                        if time.time() - last_ping > 15:
                            self.wfile.write(b": ping\n\n")
                            self.wfile.flush()
                            last_ping = time.time()
            except (BrokenPipeError, ConnectionResetError, OSError):
                pass
            finally:
                d.bus.unsubscribe(qq)

    return Handler


def serve(d: Daemon, host: str, port: int) -> ThreadingHTTPServer:
    httpd = ThreadingHTTPServer((host, port), make_handler(d))
    httpd.daemon_threads = True
    t = threading.Thread(target=httpd.serve_forever, name="awake-http", daemon=True)
    t.start()
    return httpd
