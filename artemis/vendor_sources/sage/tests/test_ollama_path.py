"""A fake Ollama server that behaves like Brandon's: Gemma 4 'thinks' its budget away and returns empty
content on the first call, then answers on the retry. Proves: auto-detection of Ollama, native /api/chat,
think:false sent, keep_alive sent, empty → retry → clean answer, and the export shows what happened."""
from __future__ import annotations
import json, os, sys, tempfile, threading, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

SEEN = []

class FakeOllama(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        if self.path == "/api/tags":
            body = json.dumps({"models": [{"name": "gemma4:26b"}]}).encode()
        elif self.path == "/v1/models":
            body = json.dumps({"data": [{"id": "gemma4:26b"}, {"id": "gemma4:31b"}]}).encode()
        else:
            self.send_response(404); self.end_headers(); return
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0); payload = json.loads(self.rfile.read(n) or b"{}")
        SEEN.append((self.path, payload))
        if self.path == "/api/generate":            # prewarm
            body = json.dumps({"done": True}).encode()
        elif self.path == "/api/chat":
            chats = [p for p in SEEN if p[0] == "/api/chat"]
            if len(chats) == 1:                      # first call: thought its budget away, empty content
                msg = {"role": "assistant", "content": "", "thinking": "x" * 900}
                body = json.dumps({"message": msg, "done_reason": "length", "eval_count": 1200, "load_duration": 40e9, "total_duration": 43e9}).encode()
            else:                                    # retry: a real answer
                msg = {"role": "assistant", "content": json.dumps({"thought": "Brandon said hello.", "actions": [{"type": "reply", "text": "Hello, Brandon. I am here."}]})}
                body = json.dumps({"message": msg, "done_reason": "stop", "eval_count": 40, "load_duration": 0, "total_duration": 2e9}).encode()
        else:
            self.send_response(404); self.end_headers(); return
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

def check(c, m):
    print(("  ok   " if c else "  FAIL ") + m)
    if not c: raise SystemExit(1)

def main():
    srv = HTTPServer(("127.0.0.1", 0), FakeOllama); port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    os.environ.update({"AWAKE_DATA_DIR": tempfile.mkdtemp(prefix="awake-ollama-"), "AWAKE_LLM_BASE_URL": f"http://127.0.0.1:{port}/v1",
                       "AWAKE_LLM_MODEL": "gemma4:12b", "AWAKE_BACKEND": "auto", "AWAKE_HEARTBEAT_S": "600"})
    from awake.backends import make_backend, OllamaBackend
    from awake.config import Config
    from awake.daemon import Daemon
    cfg = Config(); be = make_backend(cfg)
    check(isinstance(be, OllamaBackend), f"Ollama detected → native backend: {be.name}")
    check(be.model == "gemma4:26b", "model fallback still works (12b missing → 26b)")
    d = Daemon(cfg, be)          # don't start the heartbeat thread; drive it directly
    time.sleep(0.3)
    r = d.say("Hello?")
    chats = [p for p in SEEN if p[0] == "/api/chat"]
    check(len(chats) == 2, f"empty answer triggered exactly one retry ({len(chats)} calls)")
    check(chats[0][1].get("think") is False, "think: false is sent (Gemma 4 won't spend the budget thinking)")
    check(chats[0][1].get("keep_alive") == "24h", "keep_alive: 24h rides on the request (no cold reload every wake)")
    o = chats[0][1]["options"]; o2 = chats[1][1]["options"]
    check(o["num_predict"] == 1200 and o["repeat_penalty"] == 1.15 and o2["repeat_penalty"] == 1.3 and o2["temperature"] == 0.5, "length cap + repeat penalty; retry is cooler and stricter")
    check(any(p[0] == "/api/generate" and p[1].get("keep_alive") == "24h" for p in SEEN), "model pre-warmed at startup")
    check(r["reply"] == "Hello, Brandon. I am here.", f"Brandon sees the clean retry: {r['reply']!r}")
    g = d.memory.last_event("garbled")
    check(g is not None and g["meta"].get("thinking_chars") == 900 and g["meta"].get("done_reason") == "length", "the empty first answer is logged WITH the reason: thinking=900ch, done=length")
    exp = d.export_text()
    check("think=900ch" in exp and "done=length" in exp, "the export shows it too, so the next debug is one glance")
    w = d.memory.last_event("wake")
    check("raw_head" in w["meta"], "every wake now records the head of the raw answer (private text scrubbed)")
    print("\nollama path: all good")

if __name__ == "__main__":
    main()
