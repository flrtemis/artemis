"""ARTEMIS Multi-Provider Model Registry.

Registry of model providers beyond a single Ollama instance: Ollama,
OpenAI-compatible endpoints, Cerebras, and custom providers. Health checks,
model discovery, capability tagging, and task-based routing. Ollama-first
(with your existing local models), but extensible to any provider.
"""
from __future__ import annotations

import json
import sqlite3
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import httpx


@dataclass
class Provider:
    id: str
    name: str
    kind: str  # 'ollama' | 'openai' | 'cerebras' | 'custom'
    base_url: str
    model: str = ""
    api_key: str | None = None
    enabled: bool = True
    allow_remote_context: bool = False
    health: dict = field(default_factory=dict)
    last_checked: float = 0.0
    metadata: dict = field(default_factory=dict)


@dataclass
class ModelEntry:
    id: str
    provider_id: str
    name: str
    capabilities: list[str] = field(default_factory=list)  # 'chat'|'tools'|'vision'|'embedding'
    context_tokens: int = 8192
    score: float | None = None
    cost_per_1m_input: float = 0.0
    cost_per_1m_output: float = 0.0
    metadata: dict = field(default_factory=dict)


class ModelRegistry:
    """Registry of providers and models with health monitoring."""

    def __init__(self, db_path: Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._db = sqlite3.connect(str(db_path), check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._init()
        self._seed_defaults()

    def _init(self):
        with self._lock:
            self._db.executescript(
                """
                CREATE TABLE IF NOT EXISTS providers (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    base_url TEXT NOT NULL,
                    model TEXT NOT NULL DEFAULT '',
                    api_key TEXT,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    allow_remote_context INTEGER NOT NULL DEFAULT 0,
                    health TEXT NOT NULL DEFAULT '{}',
                    last_checked REAL NOT NULL DEFAULT 0,
                    metadata TEXT NOT NULL DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS models (
                    id TEXT PRIMARY KEY,
                    provider_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    capabilities TEXT NOT NULL DEFAULT '[]',
                    context_tokens INTEGER NOT NULL DEFAULT 8192,
                    score REAL,
                    cost_per_1m_input REAL NOT NULL DEFAULT 0,
                    cost_per_1m_output REAL NOT NULL DEFAULT 0,
                    metadata TEXT NOT NULL DEFAULT '{}'
                );
                """
            )
            self._db.commit()

    def _seed_defaults(self):
        with self._lock:
            count = self._db.execute("SELECT COUNT(*) FROM providers").fetchone()[0]
        if count == 0:
            self.add_provider(Provider(
                id="ollama-local", name="Local Ollama", kind="ollama",
                base_url="http://127.0.0.1:11434", model="",
                enabled=True, allow_remote_context=False,
                metadata={"description": "Your existing Ollama instance (primary)"},
            ))

    def add_provider(self, provider: Provider) -> Provider:
        with self._lock:
            self._db.execute(
                "INSERT OR REPLACE INTO providers(id,name,kind,base_url,model,api_key,enabled,"
                "allow_remote_context,health,last_checked,metadata) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                (provider.id, provider.name, provider.kind, provider.base_url, provider.model,
                 provider.api_key, int(provider.enabled), int(provider.allow_remote_context),
                 json.dumps(provider.health, ensure_ascii=False), provider.last_checked,
                 json.dumps(provider.metadata, ensure_ascii=False)),
            )
            self._db.commit()
        return provider

    def list_providers(self, enabled_only=True) -> list[Provider]:
        where = " WHERE enabled = 1" if enabled_only else ""
        with self._lock:
            rows = self._db.execute(f"SELECT * FROM providers{where}").fetchall()
        return [self._row_provider(r) for r in rows]

    def get_provider(self, pid: str) -> Provider | None:
        with self._lock:
            r = self._db.execute("SELECT * FROM providers WHERE id=?", (pid,)).fetchone()
        return self._row_provider(r) if r else None

    def remove_provider(self, pid: str):
        with self._lock:
            self._db.execute("DELETE FROM models WHERE provider_id=?", (pid,))
            self._db.execute("DELETE FROM providers WHERE id=?", (pid,))
            self._db.commit()

    def _row_provider(self, r: sqlite3.Row) -> Provider:
        return Provider(
            id=r["id"], name=r["name"], kind=r["kind"], base_url=r["base_url"],
            model=r["model"], api_key=r["api_key"], enabled=bool(r["enabled"]),
            allow_remote_context=bool(r["allow_remote_context"]),
            health=json.loads(r["health"] or "{}"), last_checked=r["last_checked"],
            metadata=json.loads(r["metadata"] or "{}"),
        )

    def add_model(self, model: ModelEntry) -> ModelEntry:
        with self._lock:
            self._db.execute(
                "INSERT OR REPLACE INTO models(id,provider_id,name,capabilities,context_tokens,"
                "score,cost_per_1m_input,cost_per_1m_output,metadata) VALUES(?,?,?,?,?,?,?,?,?)",
                (model.id, model.provider_id, model.name,
                 json.dumps(model.capabilities, ensure_ascii=False), model.context_tokens,
                 model.score, model.cost_per_1m_input, model.cost_per_1m_output,
                 json.dumps(model.metadata, ensure_ascii=False)),
            )
            self._db.commit()
        return model

    def list_models(self, provider_id: str | None = None) -> list[ModelEntry]:
        where = " WHERE provider_id=?" if provider_id else ""
        args = [provider_id] if provider_id else []
        with self._lock:
            rows = self._db.execute(f"SELECT * FROM models{where}").fetchall()
        return [self._row_model(r) for r in rows]

    def _row_model(self, r: sqlite3.Row) -> ModelEntry:
        return ModelEntry(
            id=r["id"], provider_id=r["provider_id"], name=r["name"],
            capabilities=json.loads(r["capabilities"] or "[]"),
            context_tokens=r["context_tokens"], score=r["score"],
            cost_per_1m_input=r["cost_per_1m_input"], cost_per_1m_output=r["cost_per_1m_output"],
            metadata=json.loads(r["metadata"] or "{}"),
        )

    async def check_health(self, pid: str | None = None) -> dict[str, Any]:
        providers = self.list_providers() if pid is None else [self.get_provider(pid)]
        results = {}
        for p in providers:
            h = await self._probe(p)
            p.health = h
            p.last_checked = time.time()
            self.add_provider(p)
            results[p.id] = {"provider": p.name, "kind": p.kind,
                             "connected": h.get("connected", False),
                             "models": h.get("models", []),
                             "error": h.get("error")}
        return results

    async def _probe(self, p: Provider) -> dict:
        try:
            headers = {}
            if p.api_key:
                headers["Authorization"] = f"Bearer {p.api_key}"
            async with httpx.AsyncClient(timeout=8, trust_env=False,
                                          follow_redirects=False) as c:
                if p.kind == "ollama":
                    r = await c.get(f"{p.base_url.rstrip('/')}/api/tags", headers=headers)
                    r.raise_for_status()
                    data = r.json()
                    models = [m["name"] for m in data.get("models", [])
                              if isinstance(m.get("name"), str)]
                    return {"connected": True, "models": models,
                            "base_url": p.base_url}
                elif p.kind == "openai":
                    r = await c.get(f"{p.base_url.rstrip('/')}/v1/models", headers=headers)
                    r.raise_for_status()
                    data = r.json()
                    models = [m["id"] for m in data.get("data", [])
                              if isinstance(m.get("id"), str)]
                    return {"connected": True, "models": models,
                            "base_url": p.base_url}
                else:
                    return {"connected": False, "models": [],
                            "error": f"unsupported kind {p.kind}"}
        except Exception as exc:  # noqa: BLE001
            return {"connected": False, "models": [], "error": str(exc)[:200]}

    def close(self):
        with self._lock:
            self._db.close()


class ModelRouter:
    """Route tasks to the best provider/model based on capabilities, cost, score."""

    def __init__(self, registry: ModelRegistry):
        self.registry = registry

    def select(self, *, task: str = "chat", require_tools: bool = False,
               require_vision: bool = False, prefer: str = "cost",
               model_hint: str | None = None) -> ModelEntry | None:
        models = self.registry.list_models()
        if not models:
            return None
        caps = ["chat"]
        if require_tools:
            caps.append("tools")
        if require_vision:
            caps.append("vision")
        eligible = [m for m in models if all(c in m.capabilities for c in caps)]
        if not eligible:
            eligible = models
        if model_hint:
            for m in eligible:
                if m.name == model_hint:
                    return m
        if prefer == "cost":
            eligible.sort(key=lambda m: (m.cost_per_1m_input + m.cost_per_1m_output))
        elif prefer == "score":
            eligible.sort(key=lambda m: -(m.score or 0))
        return eligible[0]

    def route(self, *, task: str = "chat", **kwargs) -> dict:
        m = self.select(task=task, **kwargs)
        if not m:
            return {"error": "No eligible model", "provider": None, "model": None}
        p = self.registry.get_provider(m.provider_id)
        return {"provider": p.name if p else m.provider_id, "provider_id": m.provider_id,
                "model": m.name, "model_id": m.id, "capabilities": m.capabilities,
                "context_tokens": m.context_tokens, "score": m.score,
                "cost_per_1m_input": m.cost_per_1m_input, "cost_per_1m_output": m.cost_per_1m_output}


class ModelService:
    def __init__(self, data_dir: Path):
        self.registry = ModelRegistry(data_dir / "model_registry" / "registry.sqlite3")
        self.router = ModelRouter(self.registry)

    def add_provider(self, provider: Provider):
        return self.registry.add_provider(provider)

    def list_providers(self, **kw):
        return self.registry.list_providers(**kw)

    def get_provider(self, pid: str):
        return self.registry.get_provider(pid)

    def remove_provider(self, pid: str):
        return self.registry.remove_provider(pid)

    def add_model(self, model: ModelEntry):
        return self.registry.add_model(model)

    def list_models(self, provider_id=None):
        return self.registry.list_models(provider_id)

    async def check_health(self, pid=None):
        return await self.registry.check_health(pid)

    def route(self, **kw):
        return self.router.route(**kw)

    def status(self) -> dict:
        providers = self.registry.list_providers()
        models = self.registry.list_models()
        return {
            "providers": [{"id": p.id, "name": p.name, "kind": p.kind,
                           "enabled": p.enabled, "connected": bool(p.health.get("connected"))}
                          for p in providers],
            "models": [{"id": m.id, "provider_id": m.provider_id, "name": m.name,
                        "capabilities": m.capabilities, "score": m.score}
                       for m in models],
        }

    def close(self):
        self.registry.close()
