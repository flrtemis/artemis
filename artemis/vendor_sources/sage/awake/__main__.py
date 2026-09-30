"""python -m awake  — start her."""
from __future__ import annotations

import signal
import sys
import time

from .backends import make_backend
from .config import Config
from .daemon import Daemon
from .server import serve


def main() -> int:
    cfg = Config()
    cfg.ensure_dirs()
    backend = make_backend(cfg)
    d = Daemon(cfg, backend)
    httpd = serve(d, cfg.host, cfg.port)
    print(f"awake {__import__('awake').__version__}")
    print(f"  name      : {d.name}")
    print(f"  data      : {cfg.data_dir}")
    print(f"  mind      : {backend.name}" + ("   <-- STAND-IN: no LLM reachable; the loop runs, nobody is thinking" if backend.is_standin else ""))
    print(f"  heartbeat : every {cfg.heartbeat_s}s by default (she may choose {cfg.min_wake_s}–{cfg.max_wake_s}s)")
    print(f"  web       : http://{cfg.host}:{cfg.port}/", flush=True)
    d.start()

    def _stop(*_):
        print("stopping…", flush=True)
        d.stop()
        httpd.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    raise SystemExit(main())
