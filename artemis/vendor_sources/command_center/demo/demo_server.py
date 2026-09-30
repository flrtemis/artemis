"""
demo/demo_server.py — GPU-free demo backend for the ARTEMIS Command Center / neural-sim world.

WHAT THIS IS
  The real stack needs Qwen3-8B on a CUDA GPU (launch.py) plus the Windows-side
  workspace dashboard (dashboard_server.py, which shells out to PowerShell/WSL).
  Neither can run here. This file stands in for BOTH so the 3D world can be explored:

    * Serves a patched copy of dashboard_3d.html (WebSocket URL made relative
      instead of hard-coded ws://localhost:8765).
    * /api/status            -> stub so the "BACKEND" dot turns green.
    * /ws                    -> streams {"type":"metrics", ai, bio} at ~4 Hz.
                                  bio = the REAL IzhikevichNetwork from bio_model.py
                                        (with the three bugs fixed).
                                  ai  = SYNTHETIC numbers shaped like metrics.to_dict()
                                        (no LLM here). Clearly not real training.
                                Also emits a fake self_modify_event every 25 steps
                                so the electric-blue flash + log panel can be seen.
    * /api/analyze-dataset   -> the REAL DatasetAnalyzer from dataset_analyzer.py.
    * /ws/brain-analysis     -> passthrough used by the dataset panel.

Run:  python demo/demo_server.py   (from repo root)   then open the printed URL.
"""
import asyncio, json, math, random, sys, time
from pathlib import Path

import yaml
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from bio_model import IzhikevichNetwork          # real
from metrics import MetricComputer               # real (bio_to_dict only)
from dataset_analyzer import DatasetAnalyzer     # real

app = FastAPI(title="ARTEMIS demo backend")

# Three.js served locally — the page no longer needs the internet (was cdn.jsdelivr.net)
from fastapi.staticfiles import StaticFiles
_three = ROOT / "vendor" / "three" / "lib" / "three.module.js"
if not _three.exists():
    raise SystemExit(f"\n  MISSING: {_three}\n  The vendor/three folder is incomplete — re-extract command-center.zip.\n")
print(f"  three.js  : {_three} ({_three.stat().st_size:,} bytes) OK", flush=True)
app.mount("/vendor", StaticFiles(directory=str(ROOT / "vendor")), name="vendor")

@app.get("/favicon.ico")
async def _favicon():
    from fastapi import Response
    return Response(status_code=204)

# ---------------------------------------------------------------- HTML (patched copy)
_html = (ROOT / "dashboard_3d.html").read_text(encoding="utf-8")
_html = _html.replace(
    "const wsUrl = 'ws://localhost:8765/ws';",
    "const wsUrl = (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws';",
)
assert "location.host + '/ws'" in _html, "WS patch failed"

@app.get("/", response_class=HTMLResponse)
@app.get("/3d", response_class=HTMLResponse)
async def index():
    return _html

# ---------------------------------------------------------------- recovered assets (from HF Spaces)
REC = ROOT / "recovered"

@app.get("/galaxy_5k.json")
@app.get("/galaxy_25k.json")
@app.get("/galaxy_50k.json")
async def galaxy(request: Request):
    name = request.url.path.lstrip("/")
    return FileResponse(REC / name, media_type="application/json")

@app.get("/assets/{asset_name}")
async def asset(asset_name: str):
    target = (REC / asset_name).resolve()
    if not str(target).startswith(str(REC.resolve())) or not target.is_file():
        return JSONResponse({"detail": f"not found: {asset_name}"}, status_code=404)
    return FileResponse(target)

# Second fork of the Command Center: HF artemis-command-center @ 2026-05-03
# (mobile touch controls + Pip-Boy arm [TAB] + Sage avatar; NO brain engine)
_html_may3 = (REC / "dashboard_3d_may3_pipboy_sage.html").read_text(encoding="utf-8")

@app.get("/may3", response_class=HTMLResponse)
async def index_may3():
    return _html_may3

# ---------------------------------------------------------------- workspace-dashboard stubs
TOOL_IDS = ["artemis", "ears", "csm", "neural-sim", "artemis-server", "comms",
            "converter-gui", "gateway", "mirror", "ghidra"]

@app.get("/api/status")
async def status():
    return {"tools": {t: {"running": t == "neural-sim"} for t in TOOL_IDS}}

@app.post("/api/launch")
@app.post("/api/stop")
async def not_here():
    return JSONResponse({"detail": "Demo backend: tools cannot be launched from the sandbox."}, status_code=501)

@app.get("/api/output/{tool_id}")
async def output(tool_id: str):
    return {"output": f"[demo] no live process output for {tool_id} in this sandbox"}

# ---------------------------------------------------------------- neural-sim stream
cfg = yaml.safe_load((ROOT / "config.yaml").read_text())
bio = IzhikevichNetwork(cfg)

class _NoModel:
    def parameters(self): return iter([])
    def named_parameters(self): return iter([])
mc = MetricComputer(_NoModel(), cfg)

_clients: set[WebSocket] = set()
_step = 0
_loss = 3.2

def synthetic_ai(step: int) -> dict:
    """Numbers shaped like MetricComputer.to_dict() — NOT a real model."""
    global _loss
    _loss = max(0.35, _loss * 0.995 + random.gauss(0, 0.02))
    n_layers = 36  # Qwen3-8B has 36 blocks
    gnorms = [max(0.0, 0.8 * math.exp(-i / 14) + random.gauss(0, 0.05)) for i in range(n_layers)]
    return {
        "step": step,
        "loss": round(_loss, 4),
        "perplexity": round(math.exp(_loss), 2),
        "confidence": round(1 - _loss / 4.0 + random.gauss(0, 0.02), 3),
        "effective_lr": 1e-4 * (0.5 + 0.5 * math.cos(2 * math.pi * (step % 50) / 50)),
        "gradient_norms": gnorms,
        "gradient_snr": round(2.0 + random.gauss(0, 0.3), 3),
        "clip_rate": round(min(1.0, max(0.0, 0.3 - step / 400 + random.gauss(0, 0.05))), 3),
        "forgetting_score": round(max(0.0, 0.02 + 0.0004 * step + random.gauss(0, 0.005)), 4),
        "mean_cka": round(0.7 + random.gauss(0, 0.03), 3),
        "attention_entropy": [2.0 + random.gauss(0, 0.2) for _ in range(n_layers)],
        "activation_survival": [0.9 - 0.01 * i + random.gauss(0, 0.02) for i in range(n_layers)],
        "momentum_velocity": round(abs(random.gauss(0.3, 0.05)), 3),
        "embedding_drift": round(step * 1e-5, 6),
        "_synthetic": True,
    }

async def producer():
    global _step
    loop = asyncio.get_event_loop()
    tokens = [791, 4062, 14198, 39935, 35308, 927, 279, 16053, 5679, 13]
    while True:
        if _clients:
            _step += 1
            I = bio.encode_text_to_current(tokens) if _step % 3 == 0 else None
            bm = await loop.run_in_executor(None, bio.simulate_step, I)
            msg = {"type": "metrics", "step": _step, "timestamp": time.time(),
                   "ai": synthetic_ai(_step), "bio": mc.bio_to_dict(bm)}
            await _broadcast(msg)
            if _step % 25 == 0:
                param = random.choice(["learning_rate", "sam_rho", "ewc_lambda", "dropout"])
                await _broadcast({"type": "self_modify_event", "step": _step, "parameter": param,
                                  "old_value": 1e-4, "new_value": 8e-5,
                                  "reason": "[demo] synthetic event — real engine would ask Qwen3-8B"})
        await asyncio.sleep(0.25)

async def _broadcast(msg: dict):
    dead = []
    data = json.dumps(msg)
    for ws in list(_clients):
        try: await ws.send_text(data)
        except Exception: dead.append(ws)
    for ws in dead: _clients.discard(ws)

@app.on_event("startup")
async def _start():
    asyncio.create_task(producer())

@app.websocket("/ws")
async def ws_neural(ws: WebSocket):
    await ws.accept(); _clients.add(ws)
    await ws.send_json({"type": "train_state", "action": "started"})
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        _clients.discard(ws)

# ---------------------------------------------------------------- dataset analysis (real)
_brain_clients: set[WebSocket] = set()

@app.websocket("/ws/brain-analysis")
async def ws_brain(ws: WebSocket):
    await ws.accept(); _brain_clients.add(ws)
    try:
        while True:
            try: await asyncio.wait_for(ws.receive_text(), timeout=30)
            except asyncio.TimeoutError: await ws.send_text('{"type":"ping"}')
    except Exception:
        pass
    finally:
        _brain_clients.discard(ws)

@app.post("/api/analyze-dataset")
async def analyze(file: UploadFile = File(...)):
    content = await file.read()
    frames = []
    async def sink(js: str):
        frames.append(json.loads(js))
        for c in list(_brain_clients):
            try: await c.send_text(js)
            except Exception: pass
        for c in list(_clients):   # the 3D page also listens for cognitive_frame on /ws
            try: await c.send_text(js)
            except Exception: pass
    an = DatasetAnalyzer()
    await an.analyze(content, file.filename or "dataset.txt", sink)
    return {"status": "ok", "filename": file.filename, "frames": frames,
            "summary": an.get_summary(), "frame_count": len(frames)}

if __name__ == "__main__":
    import uvicorn
    print("ARTEMIS Command Center — demo backend (no GPU, no LLM)")
    uvicorn.run(app, host="0.0.0.0", port=8765, log_level="warning")
