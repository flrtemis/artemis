"""Persistent SQLite cost ledger: per-model input/output tokens and USD cost."""
from __future__ import annotations

import sqlite3
import threading
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class ModelCost:
    id: str
    ts: float
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    provider: str
    run_id: str | None = None
    benchmark_case: str | None = None
    metadata: dict = None


class CostTracker:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        db_path = data_dir / "benchmarks" / "costs.sqlite3"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._db = sqlite3.connect(str(db_path), check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._pricing: dict[str, dict[str, float]] = {}
        self._init()

    def _init(self):
        with self._lock:
            self._db.executescript(
                """
                CREATE TABLE IF NOT EXISTS model_costs (
                    id TEXT PRIMARY KEY,
                    ts REAL NOT NULL,
                    model TEXT NOT NULL,
                    input_tokens INTEGER NOT NULL DEFAULT 0,
                    output_tokens INTEGER NOT NULL DEFAULT 0,
                    cost_usd REAL NOT NULL DEFAULT 0,
                    provider TEXT NOT NULL DEFAULT 'ollama',
                    run_id TEXT,
                    benchmark_case TEXT,
                    metadata TEXT NOT NULL DEFAULT '{}'
                );
                CREATE INDEX IF NOT EXISTS idx_costs_model ON model_costs(model, ts);
                CREATE INDEX IF NOT EXISTS idx_costs_case ON model_costs(benchmark_case, ts);
                """
            )
            self._db.commit()

    def set_pricing(self, model: str, input_per_1m: float, output_per_1m: float):
        self._pricing[model] = {"input_per_1m": input_per_1m, "output_per_1m": output_per_1m}

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        p = self._pricing.get(model, {"input_per_1m": 0.0, "output_per_1m": 0.0})
        return (input_tokens / 1_000_000) * p["input_per_1m"] + (output_tokens / 1_000_000) * p["output_per_1m"]

    def record(self, model: str, input_tokens: int, output_tokens: int,
               cost_usd: float, provider: str = "ollama",
               run_id: str | None = None, benchmark_case: str | None = None,
               metadata: dict | None = None) -> ModelCost:
        rec = ModelCost(
            id=uuid.uuid4().hex, ts=time.time(), model=model,
            input_tokens=int(input_tokens), output_tokens=int(output_tokens),
            cost_usd=float(cost_usd), provider=provider, run_id=run_id,
            benchmark_case=benchmark_case, metadata=metadata or {},
        )
        with self._lock:
            self._db.execute(
                "INSERT INTO model_costs(id, ts, model, input_tokens, output_tokens, cost_usd, "
                "provider, run_id, benchmark_case, metadata) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (rec.id, rec.ts, rec.model, rec.input_tokens, rec.output_tokens,
                 rec.cost_usd, rec.provider, rec.run_id, rec.benchmark_case,
                 __import__("json").dumps(rec.metadata or {}, ensure_ascii=False)),
            )
            self._db.commit()
        return rec

    def by_model(self, model: str | None = None,
                 since: float | None = None) -> list[dict[str, Any]]:
        where = []
        args = []
        if model:
            where.append("model = ?"); args.append(model)
        if since is not None:
            where.append("ts >= ?"); args.append(since)
        sql = "SELECT * FROM model_costs"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY ts DESC"
        with self._lock:
            rows = self._db.execute(sql, args).fetchall()
        return [dict(r) for r in rows]

    def totals(self, model: str | None = None) -> dict[str, Any]:
        where = []
        args = []
        if model:
            where.append("model = ?"); args.append(model)
        sql = "SELECT COUNT(*) AS n, COALESCE(SUM(input_tokens),0) AS it, COALESCE(SUM(output_tokens),0) AS ot, COALESCE(SUM(cost_usd),0) AS cost FROM model_costs"
        if where:
            sql += " WHERE " + " AND ".join(where)
        with self._lock:
            row = self._db.execute(sql, args).fetchone()
        return {
            "model": model or "all",
            "calls": row["n"],
            "input_tokens": row["it"],
            "output_tokens": row["ot"],
            "total_tokens": row["it"] + row["ot"],
            "cost_usd": round(row["cost"], 6),
        }

    def close(self):
        with self._lock:
            self._db.close()
