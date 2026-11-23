"""ARTEMIS Benchmark / Evaluation Framework (video: competitive head-to-head).

Terminal Bench, Cursor Bench, Swiss Sweep, Graph Walks — run cases through
Ollama models, score 0-100, track cost, rank models by score-per-dollar.
"""
from .runner import BenchmarkRunner, BenchmarkCase, BenchmarkResult, BenchmarkSuite
from .cost_tracker import CostTracker, ModelCost
from .compare import compare_models, score_per_dollar

__all__ = [
    "BenchmarkRunner",
    "BenchmarkCase",
    "BenchmarkResult",
    "BenchmarkSuite",
    "CostTracker",
    "ModelCost",
    "compare_models",
    "score_per_dollar",
]
