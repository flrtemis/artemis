"""ARTEMIS World Model — Project Genie / Genie 4 (video: 3D world generation).

Prompt -> Three.js scene JSON via Ollama. Versioned, remixable world gallery.
Walkable viewer at web/world-viewer.html (?id= world id).
"""
from __future__ import annotations

import json
import sqlite3
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class WorldModel:
    id: str
    name: str
    prompt: str
    scene_json: dict
    version: int = 1
    parent_id: str | None = None  # for remixing
    created_at: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)


class WorldModelStore:
    """Persistent gallery of generated worlds; versioned and remixable."""

    def __init__(self, db_path: Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._db = sqlite3.connect(str(db_path), check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._init()

    def _init(self):
        with self._lock:
            self._db.executescript(
                """
                CREATE TABLE IF NOT EXISTS world_models (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    scene_json TEXT NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1,
                    parent_id TEXT,
                    created_at REAL NOT NULL,
                    metadata TEXT NOT NULL DEFAULT '{}'
                );
                CREATE INDEX IF NOT EXISTS idx_worlds_created ON world_models(created_at DESC);
                """
            )
            self._db.commit()

    def add(self, world: WorldModel) -> WorldModel:
        with self._lock:
            self._db.execute(
                "INSERT INTO world_models(id, name, prompt, scene_json, version, "
                "parent_id, created_at, metadata) VALUES (?,?,?,?,?,?,?,?)",
                (world.id, world.name, world.prompt,
                 json.dumps(world.scene_json, ensure_ascii=False), world.version,
                 world.parent_id, world.created_at,
                 json.dumps(world.metadata, ensure_ascii=False)),
            )
            self._db.commit()
        return world

    def list(self) -> list[dict[str, Any]]:
        with self._lock:
            rows = self._db.execute(
                "SELECT * FROM world_models ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]

    def get(self, wid: str) -> WorldModel | None:
        with self._lock:
            r = self._db.execute("SELECT * FROM world_models WHERE id=?", (wid,)).fetchone()
        if not r:
            return None
        return WorldModel(
            id=r["id"], name=r["name"], prompt=r["prompt"],
            scene_json=json.loads(r["scene_json"] or "{}"),
            version=r["version"], parent_id=r["parent_id"],
            created_at=r["created_at"],
            metadata=json.loads(r["metadata"] or "{}"),
        )

    def remix(self, wid: str, new_name: str, new_prompt: str,
              scene_overlay: dict | None = None) -> WorldModel | None:
        base = self.get(wid)
        if not base:
            return None
        scene = dict(base.scene_json)
        if scene_overlay:
            scene.update(scene_overlay)
        remix = WorldModel(
            id=uuid.uuid4().hex, name=new_name, prompt=new_prompt,
            scene_json=scene, version=base.version + 1,
            parent_id=base.id,
            metadata={"remixed_from": base.id, "base_name": base.name},
        )
        self.add(remix)
        return remix


class WorldModelGenerator:
    """Prompt -> Three.js scene JSON via Ollama."""

    def __init__(self, runtime, store: WorldModelStore):
        self.runtime = runtime
        self.store = store

    def generate(self, prompt: str, name: str | None = None,
                 model: str | None = None) -> WorldModel:
        system = (
            "You are a Three.js scene generator. Output ONLY valid JSON describing "
            "a 3D scene. Schema: {objects:[{type:'box|sphere|plane|light',"
            "position:[x,y,z],rotation:[x,y,z],scale:[x,y,z],color:'#hex',"
            "emissive:'#hex'}]}. No markdown, no explanation, just JSON."
        )
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Generate a Three.js scene for: {prompt}"},
        ]
        reply = self.runtime.provider.chat(messages, [])
        text = reply.get("content", "") if isinstance(reply, dict) else str(reply)
        # Extract JSON from the reply.
        scene_json = {"objects": []}
        try:
            start = text.index("{"); end = text.rindex("}") + 1
            scene_json = json.loads(text[start:end])
        except Exception:  # noqa: BLE001
            scene_json = {"objects": [{"type": "box", "position": [0, 1, 0],
                                       "scale": [1, 1, 1], "color": "#4488ff"}]}
        world = WorldModel(
            id=uuid.uuid4().hex,
            name=name or f"World: {prompt[:40]}",
            prompt=prompt,
            scene_json=scene_json,
        )
        self.store.add(world)
        return world


class WorldModelService:
    def __init__(self, runtime, data_dir: Path):
        self.store = WorldModelStore(data_dir / "world_model" / "worlds.sqlite3")
        self.generator = WorldModelGenerator(runtime, self.store)

    def generate(self, prompt: str, name: str | None = None,
                 model: str | None = None) -> dict[str, Any]:
        world = self.generator.generate(prompt, name=name, model=model)
        return asdict(world)

    def list(self) -> list[dict[str, Any]]:
        return self.store.list()

    def get(self, wid: str) -> dict[str, Any] | None:
        w = self.store.get(wid)
        return asdict(w) if w else None

    def remix(self, wid: str, new_name: str, new_prompt: str,
              scene_overlay: dict | None = None) -> dict[str, Any] | None:
        w = self.store.remix(wid, new_name, new_prompt, scene_overlay)
        return asdict(w) if w else None

    def status(self) -> dict[str, Any]:
        worlds = self.store.list()
        return {"worlds": len(worlds), "store": "world_model"}

    def close(self):
        self.store.close()
