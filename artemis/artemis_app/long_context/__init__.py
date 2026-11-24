"""ARTEMIS Long-Context Evaluation (video: graph walks, million-token context).

GraphWalkGenerator: needle-in-haystack + graph-walk cases buried in filler up
to ~1M tokens. LongContextRunner: runs cases through Ollama, scores correctness.
LongContextStore: persistent results + summary. /api/long_context/* endpoints.
"""
from __future__ import annotations

import json
import random
import sqlite3
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


def estimate_tokens(text: str) -> int:
    return max(1, len(text.split()) * 4 // 3)


@dataclass
class LongContextCase:
    id: str
    family: str  # 'needle' | 'graph_walk'
    context: str
    question: str
    answer: str
    context_tokens: int
    difficulty: str


@dataclass
class LongContextResult:
    case_id: str
    model: str
    family: str
    correct: bool
    score: float  # 0-100
    latency_s: float
    context_tokens: int
    reply: str
    error: str | None = None
    created_at: float = field(default_factory=time.time)


class GraphWalkGenerator:
    """Generates needle-in-haystack and graph-walk cases with filler text."""

    NEEDLE_TEMPLATES = [
        "The hidden fact is: {needle}. Remember this for later.",
        "Deep in the document: {needle}.",
        "Key information: {needle}.",
    ]

    def __init__(self, rng_seed: int = 42):
        self.rng = random.Random(rng_seed)
        self.words = [
            "alpha","beta","gamma","delta","epsilon","zeta","eta","theta","iota",
            "kappa","lambda","mu","nu","xi","omicron","pi","rho","sigma","tau",
            "upsilon","phi","chi","psi","omega",
        ]

    def _filler(self, n_words: int) -> str:
        return " ".join(self.rng.choice(self.words) for _ in range(n_words))

    def generate_needle(self, needle: str, context_tokens: int) -> LongContextCase:
        """Needle-in-haystack: hide a fact in filler text."""
        n_filler = max(0, context_tokens - estimate_tokens(needle) - 100)
        filler_before = self._filler(n_filler // 2)
        filler_after = self._filler(n_filler - n_filler // 2)
        template = self.rng.choice(self.NEEDLE_TEMPLATES)
        context = f"{filler_before} {template.format(needle=needle)} {filler_after}"
        question = "What is the hidden fact?"
        return LongContextCase(
            id=uuid.uuid4().hex, family="needle", context=context,
            question=question, answer=needle,
            context_tokens=estimate_tokens(context),
            difficulty="medium" if context_tokens > 50000 else "easy",
        )

    def generate_graph_walk(self, num_hops: int, context_tokens: int) -> LongContextCase:
        """Graph walk: follow a trail of connected facts buried in filler."""
        nodes = [f"node-{i}" for i in range(num_hops + 1)]
        edges = []
        for i in range(num_hops):
            edges.append(f"{nodes[i]} is connected to {nodes[i+1]}.")
        final_answer = f"The final destination is {nodes[-1]}."
        trail = " ".join(edges) + " " + final_answer
        n_filler = max(0, context_tokens - estimate_tokens(trail) - 100)
        filler_before = self._filler(n_filler // 2)
        filler_after = self._filler(n_filler - n_filler // 2)
        context = f"{filler_before} {trail} {filler_after}"
        question = f"Starting from {nodes[0]}, follow the connections. What is the final destination?"
        return LongContextCase(
            id=uuid.uuid4().hex, family="graph_walk", context=context,
            question=question, answer=nodes[-1],
            context_tokens=estimate_tokens(context),
            difficulty="hard" if num_hops > 5 else "medium",
        )


class LongContextRunner:
    """Runs long-context cases through an Ollama model via the Artemis runtime."""

    def __init__(self, runtime):
        self.runtime = runtime

    def run_case(self, case: LongContextCase, model: str) -> LongContextResult:
        start = time.time()
        result = LongContextResult(
            case_id=case.id, model=model, family=case.family,
            correct=False, score=0.0, latency_s=0.0,
            context_tokens=case.context_tokens, reply="",
        )
        try:
            prompt = (
                f"Context:\n{case.context}\n\n"
                f"Question: {case.question}\n"
                f"Answer with only the answer, no explanation."
            )
            messages = [{"role": "user", "content": prompt}]
            reply = self.runtime.provider.chat(messages, [])
            latency = time.time() - start
            text = reply.get("content", "") if isinstance(reply, dict) else str(reply)
            result.reply = text
            result.latency_s = round(latency, 3)
            result.context_tokens = estimate_tokens(prompt)
            # Score: does the answer appear in the reply?
            result.correct = case.answer.lower() in text.lower()
            result.score = 100.0 if result.correct else 0.0
        except Exception as exc:  # noqa: BLE001
            result.error = str(exc)[:500]
            result.score = 0.0
        return result


class LongContextStore:
    """Persistent storage for long-context evaluation results."""

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
                CREATE TABLE IF NOT EXISTS lc_results (
                    id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL,
                    model TEXT NOT NULL,
                    family TEXT NOT NULL,
                    correct INTEGER NOT NULL DEFAULT 0,
                    score REAL NOT NULL DEFAULT 0,
                    latency_s REAL NOT NULL DEFAULT 0,
                    context_tokens INTEGER NOT NULL DEFAULT 0,
                    reply TEXT,
                    error TEXT,
                    created_at REAL NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_lc_model ON lc_results(model, created_at);
                CREATE INDEX IF NOT EXISTS idx_lc_family ON lc_results(family);
                """
            )
            self._db.commit()

    def add(self, result: LongContextResult):
        with self._lock:
            self._db.execute(
                "INSERT INTO lc_results(id, case_id, model, family, correct, score, "
                "latency_s, context_tokens, reply, error, created_at) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (result.id if hasattr(result, 'id') else uuid.uuid4().hex,
                 result.case_id, result.model, result.family,
                 int(result.correct), result.score, result.latency_s,
                 result.context_tokens, result.reply, result.error,
                 result.created_at),
            )
            self._db.commit()

    def results(self, model: str | None = None,
                family: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        where = []
        args = []
        if model:
            where.append("model = ?"); args.append(model)
        if family:
            where.append("family = ?"); args.append(family)
        sql = "SELECT * FROM lc_results"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY created_at DESC LIMIT ?"; args.append(limit)
        with self._lock:
            rows = self._db.execute(sql, args).fetchall()
        return [dict(r) for r in rows]

    def summary(self) -> dict[str, Any]:
        with self._lock:
            row = self._db.execute(
                "SELECT COUNT(*) AS n, COALESCE(AVG(score),0) AS avg_score, "
                "COALESCE(SUM(correct),0) AS correct_count FROM lc_results").fetchone()
            by_family = self._db.execute(
                "SELECT family, COUNT(*) AS n, COALESCE(AVG(score),0) AS avg_score, "
                "COALESCE(SUM(correct),0) AS correct_count FROM lc_results GROUP BY family").fetchall()
        return {
            "total": row["n"],
            "avg_score": round(row["avg_score"], 2),
            "correct_count": row["correct_count"],
            "pass_rate": round(row["correct_count"] / max(row["n"], 1) * 100, 1),
            "by_family": [
                {"family": r["family"], "n": r["n"],
                 "avg_score": round(r["avg_score"], 2),
                 "pass_rate": round(r["correct_count"] / max(r["n"], 1) * 100, 1)}
                for r in by_family
            ],
        }

    def close(self):
        with self._lock:
            self._db.close()


class LongContextService:
    def __init__(self, runtime, data_dir: Path):
        self.store = LongContextStore(data_dir / "long_context" / "results.sqlite3")
        self.runner = LongContextRunner(runtime)
        self.generator = GraphWalkGenerator()

    def generate_case(self, family: str, **kw) -> dict[str, Any]:
        if family == "needle":
            case = self.generator.generate_needle(
                kw.get("needle", "The meeting is at 3pm on Thursday"),
                kw.get("context_tokens", 100000))
        elif family == "graph_walk":
            case = self.generator.generate_graph_walk(
                kw.get("num_hops", 5), kw.get("context_tokens", 100000))
        else:
            return {"error": f"Unknown family: {family}"}
        return asdict(case)

    def run_case(self, case_id: str, model: str,
                 context: str | None = None, question: str | None = None,
                 answer: str | None = None) -> dict[str, Any]:
        case = LongContextCase(
            id=case_id, family="custom", context=context or "",
            question=question or "", answer=answer or "",
            context_tokens=estimate_tokens(context or ""), difficulty="custom",
        )
        result = self.runner.run_case(case, model)
        self.store.add(result)
        return asdict(result)

    def run_generated(self, family: str, model: str, **kw) -> dict[str, Any]:
        case_dict = self.generate_case(family, **kw)
        if "error" in case_dict:
            return case_dict
        case = LongContextCase(**case_dict)
        result = self.runner.run_case(case, model)
        self.store.add(result)
        return {"case": asdict(case), "result": asdict(result)}

    def results(self, **kw) -> list[dict[str, Any]]:
        return self.store.results(**kw)

    def summary(self) -> dict[str, Any]:
        return self.store.summary()

    def close(self):
        self.store.close()
