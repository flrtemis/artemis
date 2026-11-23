"""ARTEMIS Neural Architecture Search — zero-training neural networks (video: Microsoft 166-param).

Builds a network from a parameter vector with NO training. Forward() does
zero-training inference. NASStore: persistent network gallery. NASearch:
model-driven architecture proposal + evaluation. All driven by Ollama models.
"""
from __future__ import annotations

import json
import math
import random
import sqlite3
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class NetworkSpec:
    id: str
    name: str
    vector: list[float]  # flattened architecture parameters
    layer_sizes: list[int]
    activation: str = "relu"
    created_at: float = field(default_factory=time.time)
    score: float | None = None
    metadata: dict = field(default_factory=dict)


def build_network_from_vector(vector: list[float], layer_sizes: list[int],
                              activation: str = "relu") -> dict[str, Any]:
    """Construct network weights from a flat parameter vector. No training."""
    weights = []
    biases = []
    idx = 0
    for i in range(len(layer_sizes) - 1):
        n_in, n_out = layer_sizes[i], layer_sizes[i + 1]
        n_weights = n_in * n_out
        w = [[vector[idx + r * n_out + c] for c in range(n_out)] for r in range(n_in)]
        idx += n_weights
        b = [vector[idx + j] for j in range(n_out)]
        idx += n_out
        weights.append(w)
        biases.append(b)
    return {
        "layer_sizes": layer_sizes,
        "activation": activation,
        "weights": weights,
        "biases": biases,
        "vector_len": len(vector),
    }


def forward(network: dict[str, Any], inputs: list[float]) -> list[float]:
    """Zero-training inference: forward pass through the constructed network."""
    x = [float(v) for v in inputs]
    act = network.get("activation", "relu")
    for w, b in zip(network["weights"], network["biases"]):
        x = [sum(wi * xi for wi, xi in zip(row, x)) + bi
             for row, bi in zip(w, b)]
        if act == "relu":
            x = [max(0.0, v) for v in x]
        elif act == "tanh":
            x = [math.tanh(v) for v in x]
        elif act == "sigmoid":
            x = [1.0 / (1.0 + math.exp(-max(-500, min(500, v)))) for v in x]
        elif act == "linear":
            pass
    return x


@dataclass
class NetworkScore:
    network_id: str
    score: float
    task: str
    evaluated_at: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)


class NASStore:
    """Persistent gallery of generated networks."""

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
                CREATE TABLE IF NOT EXISTS networks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    vector TEXT NOT NULL,
                    layer_sizes TEXT NOT NULL,
                    activation TEXT NOT NULL DEFAULT 'relu',
                    created_at REAL NOT NULL,
                    score REAL,
                    metadata TEXT NOT NULL DEFAULT '{}'
                );
                CREATE TABLE IF NOT EXISTS network_scores (
                    id TEXT PRIMARY KEY,
                    network_id TEXT NOT NULL,
                    score REAL NOT NULL,
                    task TEXT NOT NULL,
                    evaluated_at REAL NOT NULL,
                    metadata TEXT NOT NULL DEFAULT '{}'
                );
                CREATE INDEX IF NOT EXISTS idx_networks_score ON networks(score DESC);
                CREATE INDEX IF NOT EXISTS idx_scores_network ON network_scores(network_id);
                """
            )
            self._db.commit()

    def add(self, spec: NetworkSpec) -> NetworkSpec:
        with self._lock:
            self._db.execute(
                "INSERT INTO networks(id, name, vector, layer_sizes, activation, "
                "created_at, score, metadata) VALUES (?,?,?,?,?,?,?,?)",
                (spec.id, spec.name, json.dumps(spec.vector, ensure_ascii=False),
                 json.dumps(spec.layer_sizes), spec.activation, spec.created_at,
                 spec.score, json.dumps(spec.metadata, ensure_ascii=False)),
            )
            self._db.commit()
        return spec

    def list(self, min_score: float | None = None) -> list[dict[str, Any]]:
        with self._lock:
            if min_score is not None:
                rows = self._db.execute(
                    "SELECT * FROM networks WHERE score >= ? ORDER BY score DESC",
                    (min_score,)).fetchall()
            else:
                rows = self._db.execute(
                    "SELECT * FROM networks ORDER BY created_at DESC").fetchall()
        out = []
        for r in rows:
            out.append({
                "id": r["id"], "name": r["name"],
                "vector": json.loads(r["vector"] or "[]"),
                "layer_sizes": json.loads(r["layer_sizes"] or "[]"),
                "activation": r["activation"],
                "created_at": r["created_at"],
                "score": r["score"],
                "metadata": json.loads(r["metadata"] or "{}"),
            })
        return out

    def get(self, nid: str) -> NetworkSpec | None:
        with self._lock:
            r = self._db.execute("SELECT * FROM networks WHERE id=?", (nid,)).fetchone()
        if not r:
            return None
        return NetworkSpec(
            id=r["id"], name=r["name"], vector=json.loads(r["vector"] or "[]"),
            layer_sizes=json.loads(r["layer_sizes"] or "[]"),
            activation=r["activation"], created_at=r["created_at"],
            score=r["score"],
            metadata=json.loads(r["metadata"] or "{}"),
        )

    def set_score(self, nid: str, score: float, task: str,
                  metadata: dict | None = None):
        with self._lock:
            self._db.execute(
                "UPDATE networks SET score=? WHERE id=?", (score, nid))
            self._db.execute(
                "INSERT INTO network_scores(id, network_id, score, task, evaluated_at, metadata) "
                "VALUES (?,?,?,?,?,?)",
                (uuid.uuid4().hex, nid, score, task, time.time(),
                 json.dumps(metadata or {}, ensure_ascii=False)),
            )
            self._db.commit()

    def best(self) -> dict[str, Any] | None:
        with self._lock:
            r = self._db.execute(
                "SELECT * FROM networks WHERE score IS NOT NULL ORDER BY score DESC LIMIT 1").fetchone()
        if not r:
            return None
        return {
            "id": r["id"], "name": r["name"], "score": r["score"],
            "layer_sizes": json.loads(r["layer_sizes"] or "[]"),
            "activation": r["activation"],
        }

    def close(self):
        with self._lock:
            self._db.close()


class NASearch:
    """Model-driven architecture proposal + evaluation via Ollama."""

    def __init__(self, runtime, store: NASStore):
        self.runtime = runtime
        self.store = store

    def propose(self, task: str, model: str | None = None) -> NetworkSpec:
        """Ask Ollama to propose an architecture (layer sizes + params) for a task."""
        prompt = (
            f"Propose a small neural network architecture for the task: {task}. "
            f"Return JSON: {{'layer_sizes':[int,...], 'activation':'relu|tanh|sigmoid|linear', "
            f"'vector':[float,...]}}. The vector length must equal sum(layer_sizes[i]*layer_sizes[i+1] + layer_sizes[i+1]). "
            f"Keep it tiny (<200 params). Only JSON."
        )
        messages = [{"role": "user", "content": prompt}]
        reply = self.runtime.provider.chat(messages, [])
        text = reply.get("content", "") if isinstance(reply, dict) else str(reply)
        try:
            start = text.index("{"); end = text.rindex("}") + 1
            data = json.loads(text[start:end])
        except Exception:  # noqa: BLE001
            data = {"layer_sizes": [4, 8, 1], "activation": "relu", "vector": []}
        layer_sizes = data.get("layer_sizes", [4, 8, 1])
        activation = data.get("activation", "relu")
        vector = data.get("vector", [])
        expected = sum(layer_sizes[i] * layer_sizes[i + 1] + layer_sizes[i + 1]
                       for i in range(len(layer_sizes) - 1))
        if len(vector) != expected:
            vector = [random.uniform(-1, 1) for _ in range(expected)]
        return NetworkSpec(
            id=uuid.uuid4().hex,
            name=f"NAS-{task[:30]}",
            vector=vector, layer_sizes=layer_sizes, activation=activation,
            metadata={"task": task, "proposed_by": "ollama"},
        )

    def evaluate(self, spec: NetworkSpec, task: str,
                 test_cases: list[dict] | None = None) -> NetworkScore:
        """Evaluate a network on test cases using zero-training forward()."""
        network = build_network_from_vector(spec.vector, spec.layer_sizes,
                                            spec.activation)
        cases = test_cases or [
            {"inputs": [0.0, 0.0], "expected": [0.0]},
            {"inputs": [1.0, 0.0], "expected": [1.0]},
            {"inputs": [0.0, 1.0], "expected": [1.0]},
            {"inputs": [1.0, 1.0], "expected": [0.0]},
        ]
        total_err = 0.0
        for case in cases:
            out = forward(network, case["inputs"])
            exp = case["expected"]
            total_err += sum((o - e) ** 2 for o, e in zip(out, exp)) / max(len(exp), 1)
        mse = total_err / max(len(cases), 1)
        score = max(0.0, 100.0 - mse * 100.0)
        self.store.set_score(spec.id, score, task,
                             metadata={"mse": mse, "cases": len(cases)})
        return NetworkScore(network_id=spec.id, score=score, task=task,
                            metadata={"mse": mse})

    def propose_and_evaluate(self, task: str, model: str | None = None,
                             test_cases: list[dict] | None = None) -> dict[str, Any]:
        spec = self.propose(task, model=model)
        self.store.add(spec)
        score = self.evaluate(spec, task, test_cases)
        return {"spec": asdict(spec), "score": asdict(score)}


class NASService:
    def __init__(self, runtime, data_dir: Path):
        self.store = NASStore(data_dir / "nas" / "networks.sqlite3")
        self.search = NASearch(runtime, self.store)

    def propose(self, task: str, model: str | None = None) -> dict[str, Any]:
        spec = self.search.propose(task, model=model)
        self.store.add(spec)
        return asdict(spec)

    def evaluate(self, network_id: str, task: str,
                 test_cases: list[dict] | None = None) -> dict[str, Any]:
        spec = self.store.get(network_id)
        if not spec:
            return {"error": "network not found"}
        score = self.search.evaluate(spec, task, test_cases)
        return asdict(score)

    def propose_and_evaluate(self, task: str, model: str | None = None,
                             test_cases: list[dict] | None = None) -> dict[str, Any]:
        return self.search.propose_and_evaluate(task, model=model,
                                                test_cases=test_cases)

    def networks(self, min_score: float | None = None) -> list[dict[str, Any]]:
        return self.store.list(min_score=min_score)

    def best(self) -> dict[str, Any] | None:
        return self.store.best()

    def status(self) -> dict[str, Any]:
        nets = self.store.list()
        scored = [n for n in nets if n.get("score") is not None]
        return {
            "networks": len(nets),
            "scored": len(scored),
            "best": scored[0] if scored else None,
        }

    def close(self):
        self.store.close()
