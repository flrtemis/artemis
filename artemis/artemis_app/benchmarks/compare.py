"""Head-to-head model comparison and score-per-dollar ranking."""
from __future__ import annotations

from typing import Any


def compare_models(results_a: list[dict], results_b: list[dict],
                   model_a: str, model_b: str) -> dict[str, Any]:
    """Compare two models' benchmark results."""
    def agg(results):
        if not results:
            return {"n": 0, "avg_score": 0.0, "passed": 0, "total_cost_usd": 0.0,
                    "avg_latency_s": 0.0}
        scores = [r["score"] for r in results if r.get("score") is not None]
        latencies = [r["latency_s"] for r in results if r.get("latency_s") is not None]
        costs = [r["estimated_cost_usd"] for r in results if r.get("estimated_cost_usd") is not None]
        passed = sum(1 for r in results if r.get("passed"))
        return {
            "n": len(results),
            "avg_score": round(sum(scores) / max(len(scores), 1), 2),
            "passed": passed,
            "pass_rate": round(passed / max(len(results), 1) * 100, 1),
            "total_cost_usd": round(sum(costs), 6),
            "avg_latency_s": round(sum(latencies) / max(len(latencies), 1), 3),
        }

    a = agg(results_a)
    b = agg(results_b)
    winner = model_a if a["avg_score"] > b["avg_score"] else (model_b if b["avg_score"] > a["avg_score"] else "tie")
    return {
        "model_a": model_a, "model_b": model_b,
        "a": a, "b": b,
        "winner": winner,
        "score_delta": round(a["avg_score"] - b["avg_score"], 2),
        "cost_delta_usd": round(a["total_cost_usd"] - b["total_cost_usd"], 6),
    }


def score_per_dollar(results: list[dict], model: str) -> dict[str, Any]:
    """Score per $1,000 spent."""
    if not results:
        return {"model": model, "score_per_1000_usd": 0.0, "avg_score": 0.0,
                "total_cost_usd": 0.0, "n": 0}
    scores = [r["score"] for r in results if r.get("score") is not None]
    costs = [r["estimated_cost_usd"] for r in results if r.get("estimated_cost_usd") is not None]
    total_cost = sum(costs)
    avg_score = sum(scores) / max(len(scores), 1)
    spd = (avg_score / max(total_cost, 1e-9)) * 1000.0 if total_cost > 0 else 0.0
    return {
        "model": model,
        "score_per_1000_usd": round(spd, 4),
        "avg_score": round(avg_score, 2),
        "total_cost_usd": round(total_cost, 6),
        "n": len(results),
    }
