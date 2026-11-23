"""ARTEMIS Cost-Efficiency Analytics — price/performance from the video.

Video: Gemini 4 Neon ($3.50/job, score 61) vs Claude Opus 5.5 ($720/job,
score 59) vs GPT-6.2 Sol (score 57). Track per-model pricing, record usage
(input/output tokens -> USD cost), and rank models by cost-adjusted
performance (score per $1,000). Compare any Ollama model against the video's
baselines and estimate savings vs Opus.
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
class ModelPrice:
    model: str
    input_per_1m: float
    output_per_1m: float
    context_tokens: int
    source: str = "ollama-local"


VIDEO_PRICING = {
    "gemini-4-neon": ModelPrice("gemini-4-neon", 3.0, 15.0, 1_000_000, "video"),
    "claude-opus-5-5": ModelPrice("claude-opus-5-5", 4.0, 20.0, 200_000, "video"),
    "gpt-6-2-sol": ModelPrice("gpt-6-2-sol", 3.0, 15.0, 1_000_000, "video"),
    "gemini-4-carbon": ModelPrice("gemini-4-carbon", 4.0, 20.0, 1_000_000, "video"),
    "gemini-4-hydrogen": ModelPrice("gemini-4-hydrogen", 1.5, 0.75, 1_000_000, "video"),
}

VIDEO_SCORES = {
    "gemini-4-neon": 61,
    "claude-opus-5-5": 59,
    "gpt-6-2-sol": 57,
    "gemini-4-carbon": 60,
    "gemini-4-hydrogen": 54,
}


@dataclass
class UsageRecord:
    id: str
    ts: float
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    run_id: str | None = None
    benchmark_case: str | None = None
    benchmark_score: float | None = None
    metadata: dict = field(default_factory=dict)


class CostLedger:
    """Persistent usage + cost ledger for every model call."""

    def __init__(self, db_path: Path):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._db = sqlite3.connect(str(db_path), check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self.prices: dict[str, ModelPrice] = {}
        self._init()

    def _init(self):
        with self._lock:
            self._db.executescript(
                """
                CREATE TABLE IF NOT EXISTS usage (
                    id TEXT PRIMARY KEY,
                    ts REAL NOT NULL,
                    model TEXT NOT NULL,
                    input_tokens INTEGER NOT NULL DEFAULT 0,
                    output_tokens INTEGER NOT NULL DEFAULT 0,
                    cost_usd REAL NOT NULL DEFAULT 0,
                    run_id TEXT,
                    benchmark_case TEXT,
                    benchmark_score REAL,
                    metadata TEXT NOT NULL DEFAULT '{}'
                );
                CREATE INDEX IF NOT EXISTS idx_usage_model ON usage(model, ts);
                CREATE TABLE IF NOT EXISTS model_prices (
                    model TEXT PRIMARY KEY,
                    input_per_1m REAL NOT NULL,
                    output_per_1m REAL NOT NULL,
                    context_tokens INTEGER NOT NULL,
                    source TEXT NOT NULL
                );
                """
            )
            self._db.commit()

    def set_price(self, price: ModelPrice):
        with self._lock:
            self.prices[price.model] = price
            self._db.execute(
                "INSERT INTO model_prices(model, input_per_1m, output_per_1m, context_tokens, source) "
                "VALUES (?,?,?,?,?) ON CONFLICT(model) DO UPDATE SET "
                "input_per_1m=excluded.input_per_1m, output_per_1m=excluded.output_per_1m, "
                "context_tokens=excluded.context_tokens, source=excluded.source",
                (price.model, price.input_per_1m, price.output_per_1m,
                 price.context_tokens, price.source),
            )
            self._db.commit()

    def record(self, model: str, input_tokens: int, output_tokens: int,
               run_id: str | None = None, benchmark_case: str | None = None,
               benchmark_score: float | None = None,
               metadata: dict | None = None) -> UsageRecord:
        price = self.prices.get(model)
        if price:
            cost_usd = (input_tokens / 1_000_000) * price.input_per_1m + \
                       (output_tokens / 1_000_000) * price.output_per_1m
        else:
            cost_usd = 0.0
        rec = UsageRecord(
            id=uuid.uuid4().hex, ts=time.time(), model=model,
            input_tokens=int(input_tokens), output_tokens=int(output_tokens),
            cost_usd=cost_usd, run_id=run_id, benchmark_case=benchmark_case,
            benchmark_score=benchmark_score, metadata=metadata or {},
        )
        with self._lock:
            self._db.execute(
                "INSERT INTO usage(id, ts, model, input_tokens, output_tokens, cost_usd, "
                "run_id, benchmark_case, benchmark_score, metadata) "
                "VALUES (?,?,?,?,?,?,?,?,?,?)",
                (rec.id, rec.ts, rec.model, rec.input_tokens, rec.output_tokens,
                 rec.cost_usd, rec.run_id, rec.benchmark_case, rec.benchmark_score,
                 json.dumps(rec.metadata, ensure_ascii=False)),
            )
            self._db.commit()
        return rec

    def totals(self, model: str | None = None, since: float | None = None) -> dict[str, Any]:
        where = []
        args = []
        if model:
            where.append("model=?"); args.append(model)
        if since is not None:
            where.append("ts >= ?"); args.append(since)
        where_sql = " WHERE " + " AND ".join(where) if where else ""
        with self._lock:
            row = self._db.execute(
                f"SELECT COUNT(*) AS n, COALESCE(SUM(input_tokens),0) AS it, "
                f"COALESCE(SUM(output_tokens),0) AS ot, COALESCE(SUM(cost_usd),0) AS cost "
                f"FROM usage{where_sql}", args).fetchone()
        return {
            "model": model or "all",
            "calls": row["n"],
            "input_tokens": row["it"],
            "output_tokens": row["ot"],
            "total_tokens": row["it"] + row["ot"],
            "cost_usd": round(row["cost"], 6),
        }

    def by_model(self) -> list[dict[str, Any]]:
        with self._lock:
            rows = self._db.execute(
                "SELECT model, COUNT(*) AS n, COALESCE(SUM(input_tokens),0) AS it, "
                "COALESCE(SUM(output_tokens),0) AS ot, COALESCE(SUM(cost_usd),0) AS cost "
                "FROM usage GROUP BY model ORDER BY cost DESC").fetchall()
        return [
            {"model": r["model"], "calls": r["n"], "input_tokens": r["it"],
             "output_tokens": r["ot"], "total_tokens": r["it"] + r["ot"],
             "cost_usd": round(r["cost"], 6)}
            for r in rows
        ]


class CostAnalyzer:
    """Cost-efficiency: score per dollar, comparisons vs video benchmarks."""

    def __init__(self, ledger: CostLedger):
        self.ledger = ledger

    def efficiency(self, model: str) -> dict[str, Any]:
        rows = self._scored_usage(model)
        total_score = sum(r["benchmark_score"] for r in rows if r["benchmark_score"] is not None)
        total_cost = sum(r["cost_usd"] for r in rows)
        calls_with_score = sum(1 for r in rows if r["benchmark_score"] is not None)
        avg_score = (total_score / calls_with_score) if calls_with_score else 0.0
        score_per_1000 = (avg_score / max(total_cost, 1e-9)) * 1000.0 if total_cost > 0 else 0.0
        return {
            "model": model,
            "calls_with_score": calls_with_score,
            "avg_score": round(avg_score, 2),
            "total_cost_usd": round(total_cost, 6),
            "score_per_1000_usd": round(score_per_1000, 4),
        }

    def _scored_usage(self, model: str | None = None) -> list[dict]:
        where = " WHERE benchmark_score IS NOT NULL"
        args = []
        if model:
            where += " AND model=?"; args.append(model)
        with self.ledger._lock:
            rows = self.ledger._db.execute(
                f"SELECT model, benchmark_score, cost_usd FROM usage{where}", args).fetchall()
        return [dict(r) for r in rows]

    def rank(self) -> list[dict[str, Any]]:
        with self.ledger._lock:
            models = [r[0] for r in self.ledger._db.execute(
                "SELECT DISTINCT model FROM usage").fetchall()]
        out = [self.efficiency(m) for m in models]
        out.sort(key=lambda x: x["score_per_1000_usd"], reverse=True)
        for i, r in enumerate(out):
            r["rank"] = i + 1
        return out

    def video_comparison(self, model: str, score: float,
                         input_tokens: int, output_tokens: int) -> dict[str, Any]:
        price = self.ledger.prices.get(model)
        our_cost = ((input_tokens / 1_000_000) * (price.input_per_1m if price else 0) +
                    (output_tokens / 1_000_000) * (price.output_per_1m if price else 0))
        neon_cost_per_point = 3.50 / 61.0
        opus_cost_per_point = 720.0 / 59.0
        our_cost_per_point = (our_cost / score) if score > 0 else float('inf')
        return {
            "model": model,
            "our_score": score,
            "our_cost_usd": round(our_cost, 6),
            "our_cost_per_point": round(our_cost_per_point, 6) if our_cost_per_point != float('inf') else None,
            "video_baselines": {
                "gemini-4-neon": {"score": 61, "cost_usd": 3.50, "cost_per_point": round(neon_cost_per_point, 6)},
                "claude-opus-5-5": {"score": 59, "cost_usd": 720.0, "cost_per_point": round(opus_cost_per_point, 6)},
                "gpt-6-2-sol": {"score": 57},
            },
            "cheaper_than_neon": our_cost_per_point < neon_cost_per_point if score > 0 else None,
            "cheaper_than_opus": our_cost_per_point < opus_cost_per_point if score > 0 else None,
        }

    def savings_vs_opus(self, model: str, score: float, jobs: int = 1) -> dict[str, Any]:
        opus_per_job = 720.0
        eff = self.efficiency(model)
        cost_per_point = eff["score_per_1000_usd"]
        our_per_job = (score / 1000.0) / max(cost_per_point, 1e-9) if cost_per_point > 0 else 0.0
        savings = opus_per_job * jobs - our_per_job * jobs
        return {
            "model": model,
            "opus_cost_usd": round(opus_per_job * jobs, 2),
            "our_est_cost_usd": round(our_per_job * jobs, 2),
            "estimated_savings_usd": round(savings, 2),
            "savings_percent": round((savings / (opus_per_job * jobs)) * 100, 1) if opus_per_job * jobs > 0 else 0.0,
            "jobs": jobs,
        }


class CostService:
    def __init__(self, data_dir: Path):
        self.ledger = CostLedger(data_dir / "cost_analytics" / "usage.sqlite3")
        for p in VIDEO_PRICING.values():
            self.ledger.set_price(p)
        self.analyzer = CostAnalyzer(self.ledger)

    def record(self, **kwargs):
        return self.ledger.record(**kwargs)

    def set_price(self, price: ModelPrice):
        self.ledger.set_price(price)

    def totals(self, **kwargs):
        return self.ledger.totals(**kwargs)

    def by_model(self):
        return self.ledger.by_model()

    def efficiency(self, model: str):
        return self.analyzer.efficiency(model)

    def rank(self):
        return self.analyzer.rank()

    def video_comparison(self, model: str, score: float, input_tokens: int,
                         output_tokens: int):
        return self.analyzer.video_comparison(model, score, input_tokens, output_tokens)

    def savings_vs_opus(self, model: str, score: float, jobs: int = 1):
        return self.analyzer.savings_vs_opus(model, score, jobs)

    def status(self) -> dict:
        return {
            "priced_models": list(self.ledger.prices.keys()),
            "video_pricing": {k: {"input_per_1m": v.input_per_1m, "output_per_1m": v.output_per_1m,
                                  "context_tokens": v.context_tokens}
                              for k, v in VIDEO_PRICING.items()},
            "video_scores": VIDEO_SCORES,
        }

    def close(self):
        self.ledger._db.close()
