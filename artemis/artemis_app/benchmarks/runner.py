"""Benchmark runner: executes cases against an Ollama model via the Artemis
runtime, scores results, and records cost."""
from __future__ import annotations

import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

from .cost_tracker import CostTracker


@dataclass
class BenchmarkCase:
    id: str
    name: str
    family: str  # terminal-bench | cursor-bench | swiss-sweep | graph-walks
    prompt: str
    expected: str | None = None
    checks: list[dict] | None = None  # list of {type, value, weight}
    max_tokens: int = 4000
    temperature: float = 0.2
    context_tokens: int = 0  # for long-context cases


@dataclass
class BenchmarkResult:
    case_id: str
    model: str
    family: str
    score: float  # 0-100
    subscores: dict[str, float] = field(default_factory=dict)
    latency_s: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost_usd: float = 0.0
    passed: bool = False
    checks: list[dict] = field(default_factory=list)
    raw_reply: str = ""
    artifact_paths: list[str] = field(default_factory=list)
    error: str | None = None
    created_at: float = field(default_factory=time.time)


@dataclass
class BenchmarkSuite:
    id: str
    name: str
    cases: list[BenchmarkCase] = field(default_factory=list)


class BenchmarkRunner:
    def __init__(self, runtime, cost_tracker: CostTracker, data_dir: Path):
        self.runtime = runtime
        self.cost_tracker = cost_tracker
        self.data_dir = data_dir
        self.results: list[BenchmarkResult] = []
        self.results_dir = data_dir / "benchmarks" / "results"
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def run_case(self, case: BenchmarkCase, model: str) -> BenchmarkResult:
        start = time.time()
        result = BenchmarkResult(
            case_id=case.id,
            model=model,
            family=case.family,
            score=0.0,
        )
        try:
            messages = [{"role": "user", "content": case.prompt}]
            schemas = []
            reply = self.runtime.provider.chat(messages, schemas)
            latency = time.time() - start
            text = reply.get("content", "") if isinstance(reply, dict) else str(reply)
            result.raw_reply = text
            result.latency_s = round(latency, 3)

            # Token estimation (Ollama doesn't always return counts).
            result.input_tokens = max(1, len(case.prompt.split()) * 4 // 3)
            result.output_tokens = max(1, len(text.split()) * 4 // 3)

            # Score via checks.
            score, subscores, checks, passed = self._score(text, case)
            result.score = score
            result.subscores = subscores
            result.checks = checks
            result.passed = passed

            # Cost.
            result.estimated_cost_usd = self.cost_tracker.estimate_cost(
                model, result.input_tokens, result.output_tokens
            )

            # Persist cost ledger entry.
            self.cost_tracker.record(
                model=model,
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                cost_usd=result.estimated_cost_usd,
                run_id=f"bench-{case.id}",
                benchmark_case=case.id,
                benchmark_score=result.score,
            )

        except Exception as exc:  # noqa: BLE001
            result.error = str(exc)[:500]
            result.score = 0.0
            result.passed = False

        self.results.append(asdict(result))
        self._persist(result)
        return result

    def run_suite(self, suite: BenchmarkSuite, model: str) -> list[BenchmarkResult]:
        return [self.run_case(c, model) for c in suite.cases]

    def _score(self, text: str, case: BenchmarkCase):
        checks = case.checks or []
        subscores: dict[str, float] = {}
        check_results: list[dict] = []
        total_weight = 0.0
        earned = 0.0

        for check in checks:
            ctype = check.get("type", "contains")
            cvalue = check.get("value", "")
            weight = float(check.get("weight", 1.0))
            name = check.get("name", ctype)
            passed = False
            if ctype == "contains":
                passed = cvalue.lower() in text.lower()
            elif ctype == "equals":
                passed = text.strip() == cvalue
            elif ctype == "not_contains":
                passed = cvalue.lower() not in text.lower()
            elif ctype == "regex":
                import re

                passed = bool(re.search(cvalue, text))
            total_weight += weight
            if passed:
                earned += weight
            check_results.append({"name": name, "type": ctype, "passed": passed})
            subscores[name] = 100.0 if passed else 0.0

        score = (earned / max(total_weight, 1e-9)) * 100.0 if total_weight > 0 else 0.0
        return round(score, 2), subscores, check_results, score >= 70.0

    def _persist(self, result: BenchmarkResult):
        path = self.results_dir / f"{result.case_id}_{result.model}_{uuid.uuid4().hex[:8]}.json"
        with open(path, "w") as f:
            json.dump(asdict(result), f, indent=2)
        result.artifact_paths = [str(path)]

    def summary(self) -> dict[str, Any]:
        if not self.results:
            return {"cases": 0, "avg_score": 0.0, "passed": 0, "total_cost_usd": 0.0}
        scores = [r["score"] for r in self.results]
        total_cost = sum(r["estimated_cost_usd"] for r in self.results)
        passed = sum(1 for r in self.results if r["passed"])
        return {
            "cases": len(self.results),
            "avg_score": round(sum(scores) / len(scores), 2),
            "passed": passed,
            "total_cost_usd": round(total_cost, 6),
            "families": sorted({r["family"] for r in self.results}),
        }


class BenchmarkService:
    def __init__(self, runtime, cost_tracker: CostTracker, data_dir: Path):
        self.runner = BenchmarkRunner(runtime, cost_tracker, data_dir)
        self.cost_tracker = cost_tracker
        self.suites: dict[str, BenchmarkSuite] = {}

    def register_suite(self, suite: BenchmarkSuite):
        self.suites[suite.id] = suite

    def list_suites(self) -> list[dict[str, Any]]:
        return [
            {"id": s.id, "name": s.name, "cases": len(s.cases), "family": s.cases[0].family if s.cases else ""}
            for s in self.suites.values()
        ]

    def run_case(self, suite_id: str, case_id: str, model: str) -> dict[str, Any]:
        suite = self.suites.get(suite_id)
        if not suite:
            return {"error": f"Suite {suite_id} not found"}
        case = next((c for c in suite.cases if c.id == case_id), None)
        if not case:
            return {"error": f"Case {case_id} not found in suite {suite_id}"}
        result = self.runner.run_case(case, model)
        return asdict(result)

    def run_suite(self, suite_id: str, model: str) -> dict[str, Any]:
        suite = self.suites.get(suite_id)
        if not suite:
            return {"error": f"Suite {suite_id} not found"}
        results = [asdict(r) for r in self.runner.run_suite(suite, model)]
        return {"suite": suite.id, "model": model, "results": results, "summary": self.runner.summary()}

    def results(self) -> list[dict[str, Any]]:
        return self.runner.results

    def summary(self) -> dict[str, Any]:
        return self.runner.summary()
