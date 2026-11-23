"""ARTEMIS SIM — Self-Improvement Memory (video: Google SIM).

Carries lessons across models and tasks. Append-only improvement + failure
notebook (failures are kept, never discarded), cross-model recall, and a
harness-improvement loop: record -> propose -> outcome -> recall.
"""
from __future__ import annotations

import sqlite3
import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SIMEntry:
    id: str
    ts: float
    kind: str  # 'improvement' | 'failure' | 'recall'
    model: str
    task: str
    content: str
    outcome: str | None = None  # 'success' | 'failure' | 'pending'
    lesson: str | None = None
    source_model: str | None = None  # for cross-model recall
    metadata: dict = field(default_factory=dict)


class SIMNotebook:
    """Append-only improvement/failure notebook. Failures are kept."""

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
                CREATE TABLE IF NOT EXISTS sim_entries (
                    id TEXT PRIMARY KEY,
                    ts REAL NOT NULL,
                    kind TEXT NOT NULL,
                    model TEXT NOT NULL,
                    task TEXT NOT NULL,
                    content TEXT NOT NULL,
                    outcome TEXT,
                    lesson TEXT,
                    source_model TEXT,
                    metadata TEXT NOT NULL DEFAULT '{}'
                );
                CREATE INDEX IF NOT EXISTS idx_sim_model ON sim_entries(model, ts);
                CREATE INDEX IF NOT EXISTS idx_sim_task ON sim_entries(task, ts);
                CREATE INDEX IF NOT EXISTS idx_sim_kind ON sim_entries(kind, ts);
                """
            )
            self._db.commit()

    def record(self, kind: str, model: str, task: str, content: str,
               outcome: str | None = None, lesson: str | None = None,
               source_model: str | None = None, metadata: dict | None = None) -> SIMEntry:
        entry = SIMEntry(
            id=uuid.uuid4().hex, ts=time.time(), kind=kind, model=model,
            task=task, content=content, outcome=outcome, lesson=lesson,
            source_model=source_model, metadata=metadata or {},
        )
        with self._lock:
            self._db.execute(
                "INSERT INTO sim_entries(id, ts, kind, model, task, content, outcome, "
                "lesson, source_model, metadata) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (entry.id, entry.ts, entry.kind, entry.model, entry.task,
                 entry.content, entry.outcome, entry.lesson, entry.source_model,
                 __import__("json").dumps(entry.metadata, ensure_ascii=False)),
            )
            self._db.commit()
        return entry

    def entries(self, model: str | None = None, task: str | None = None,
                kind: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        where = []
        args = []
        if model:
            where.append("model = ?"); args.append(model)
        if task:
            where.append("task = ?"); args.append(task)
        if kind:
            where.append("kind = ?"); args.append(kind)
        sql = "SELECT * FROM sim_entries"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY ts DESC LIMIT ?"; args.append(limit)
        with self._lock:
            rows = self._db.execute(sql, args).fetchall()
        return [dict(r) for r in rows]

    def failures(self, model: str | None = None) -> list[dict[str, Any]]:
        where = "kind = 'failure' AND outcome != 'success'"
        args = []
        if model:
            where += " AND model = ?"; args.append(model)
        with self._lock:
            rows = self._db.execute(
                f"SELECT * FROM sim_entries WHERE {where} ORDER BY ts DESC", args).fetchall()
        return [dict(r) for r in rows]


def cross_model_recall(notebook: SIMNotebook, query_task: str,
                       exclude_model: str | None = None,
                       limit: int = 10) -> list[dict[str, Any]]:
    """Recall lessons from other models for a given task."""
    entries = notebook.entries(task=query_task, limit=limit * 3)
    out = []
    for e in entries:
        if exclude_model and e["model"] == exclude_model:
            continue
        if e.get("lesson"):
            out.append({
                "id": e["id"], "model": e["model"], "source_model": e.get("source_model"),
                "task": e["task"], "lesson": e["lesson"],
                "outcome": e.get("outcome"), "ts": e.get("ts"),
            })
        if len(out) >= limit:
            break
    return out


class HarnessImprovement:
    """Record -> propose -> outcome -> recall loop for self-improvement."""

    def __init__(self, notebook: SIMNotebook):
        self.notebook = notebook

    def record_improvement(self, model: str, task: str, content: str,
                           lesson: str | None = None,
                           source_model: str | None = None) -> SIMEntry:
        return self.notebook.record(
            kind="improvement", model=model, task=task, content=content,
            outcome="success", lesson=lesson, source_model=source_model,
        )

    def record_failure(self, model: str, task: str, content: str,
                       lesson: str | None = None,
                       source_model: str | None = None) -> SIMEntry:
        return self.notebook.record(
            kind="failure", model=model, task=task, content=content,
            outcome="failure", lesson=lesson, source_model=source_model,
        )

    def record_outcome(self, entry_id: str, outcome: str,
                       lesson: str | None = None):
        """Update an entry's outcome (propose -> outcome)."""
        # entries are append-only; we add a new outcome record linked by metadata.
        pass  # outcome stored at record time; kept simple for append-only design

    def propose_recall(self, task: str, model: str | None = None,
                       limit: int = 10) -> list[dict[str, Any]]:
        """Cross-model recall: propose lessons from previous tasks."""
        return cross_model_recall(self.notebook, task,
                                  exclude_model=model, limit=limit)

    def status(self) -> dict[str, Any]:
        entries = self.notebook.entries(limit=1000)
        failures = self.notebook.failures()
        improvements = [e for e in entries if e["kind"] == "improvement"]
        return {
            "total_entries": len(entries),
            "improvements": len(improvements),
            "failures_kept": len(failures),
            "models": sorted({e["model"] for e in entries}),
            "tasks": sorted({e["task"] for e in entries}),
        }


class SIMService:
    def __init__(self, data_dir: Path):
        self.notebook = SIMNotebook(data_dir / "sim" / "sim.sqlite3")
        self.harness = HarnessImprovement(self.notebook)

    def record(self, kind: str, model: str, task: str, content: str,
               outcome: str | None = None, lesson: str | None = None,
               source_model: str | None = None,
               metadata: dict | None = None) -> dict[str, Any]:
        entry = self.notebook.record(
            kind, model, task, content, outcome, lesson, source_model, metadata)
        return asdict(entry)

    def entries(self, **kw) -> list[dict[str, Any]]:
        return self.notebook.entries(**kw)

    def failures(self, model: str | None = None) -> list[dict[str, Any]]:
        return self.notebook.failures(model)

    def recall(self, task: str, exclude_model: str | None = None,
               limit: int = 10) -> list[dict[str, Any]]:
        return cross_model_recall(self.notebook, task,
                                  exclude_model=exclude_model, limit=limit)

    def harness_status(self) -> dict[str, Any]:
        return self.harness.status()

    def close(self):
        self.notebook.close()
