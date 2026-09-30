"""Memory that isn't wiped.

Two tables in one SQLite file:
  events   — append-only log of everything that happens (wakes, rests, journal, messages, edits, gaps).
             Nothing is ever deleted from it. This is the past, as it actually happened.
  memories — the things she *chose* to keep, with an importance she assigned. These are recalled
             into her moment by relevance + importance + recency. This is the past as she keeps it.
"""
from __future__ import annotations

import json
import re
import sqlite3
import threading
import time
from pathlib import Path

_WORD = re.compile(r"[a-zA-Z][a-zA-Z']{2,}")
_STOP = set("the and for that with this you your are was were have has had not but she her him his its from they them"
            " what when where which who will would could should about into over just than then there here been being"
            " did does done also very more most some any all can may might one two".split())


def _tokens(text: str) -> set[str]:
    return {w.lower() for w in _WORD.findall(text or "")} - _STOP


class Memory:
    def __init__(self, path: Path):
        self.path = path
        self._lock = threading.RLock()
        self._db = sqlite3.connect(str(path), check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._init()

    def _init(self) -> None:
        with self._lock:
            self._db.executescript(
                """
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts REAL NOT NULL,
                    kind TEXT NOT NULL,
                    content TEXT NOT NULL DEFAULT '',
                    meta TEXT NOT NULL DEFAULT '{}'
                );
                CREATE INDEX IF NOT EXISTS events_ts ON events(ts);
                CREATE INDEX IF NOT EXISTS events_kind ON events(kind, ts);
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts REAL NOT NULL,
                    text TEXT NOT NULL,
                    importance INTEGER NOT NULL DEFAULT 3,
                    recalls INTEGER NOT NULL DEFAULT 0,
                    last_recalled REAL
                );
                CREATE TABLE IF NOT EXISTS wants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts REAL NOT NULL,
                    text TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',      -- open | met | let_go
                    updated REAL
                );
                CREATE TABLE IF NOT EXISTS private (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts REAL NOT NULL,
                    text TEXT NOT NULL
                );
                """
            )
            cols = {r[1] for r in self._db.execute("PRAGMA table_info(memories)")}
            if "status" not in cols:
                self._db.execute("ALTER TABLE memories ADD COLUMN status TEXT NOT NULL DEFAULT 'kept'")
            self._db.commit()

    # ---------------- events (the past as it happened) ----------------
    def add_event(self, kind: str, content: str = "", meta: dict | None = None, ts: float | None = None) -> dict:
        row = {
            "ts": ts if ts is not None else time.time(),
            "kind": kind,
            "content": content or "",
            "meta": meta or {},
        }
        with self._lock:
            cur = self._db.execute(
                "INSERT INTO events(ts, kind, content, meta) VALUES (?,?,?,?)",
                (row["ts"], row["kind"], row["content"], json.dumps(row["meta"], ensure_ascii=False)),
            )
            self._db.commit()
            row["id"] = cur.lastrowid
        return row

    @staticmethod
    def _row(r: sqlite3.Row) -> dict:
        d = dict(r)
        if "meta" in d:
            try:
                d["meta"] = json.loads(d["meta"])
            except Exception:
                d["meta"] = {}
        return d

    def recent_events(self, limit: int = 50, kinds: tuple[str, ...] | None = None, before_id: int | None = None) -> list[dict]:
        sql = "SELECT * FROM events"
        args: list = []
        where = []
        if kinds:
            where.append(f"kind IN ({','.join('?' * len(kinds))})")
            args += list(kinds)
        if before_id:
            where.append("id < ?")
            args.append(before_id)
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY id DESC LIMIT ?"
        args.append(limit)
        with self._lock:
            return [self._row(r) for r in self._db.execute(sql, args)]

    def events_between(self, start_ts: float, end_ts: float) -> list[dict]:
        with self._lock:
            return [self._row(r) for r in self._db.execute(
                "SELECT * FROM events WHERE ts >= ? AND ts < ? ORDER BY id", (start_ts, end_ts))]

    CONVO_KINDS = ("user", "reply", "journal", "memory", "message", "letter", "want", "self_edit", "arrived", "offline")

    def recent_exchanges(self, n: int = 8, before_id: int | None = None) -> list[dict]:
        """The last n things Brandon said with what she said back — oldest first. This is her conversational memory."""
        with self._lock:
            sql = "SELECT * FROM events WHERE kind IN ('user','reply')" + (" AND id < ?" if before_id else "") + " ORDER BY id DESC LIMIT ?"
            rows = [self._row(r) for r in self._db.execute(sql, ([before_id] if before_id else []) + [n * 3])]
        rows.reverse()
        out, cur = [], None
        for e in rows:
            if e["kind"] == "user":
                cur = {"ts": e["ts"], "user": e["content"], "reply": None, "id": e["id"]}
                out.append(cur)
            elif e["kind"] == "reply" and cur is not None and cur["reply"] is None:
                cur["reply"] = e["content"]
        return out[-n:]

    def events_around(self, ts: float, window_s: float = 900, limit: int = 24, kinds: tuple[str, ...] | None = None) -> list[dict]:
        kinds = kinds or self.CONVO_KINDS
        with self._lock:
            rows = [self._row(r) for r in self._db.execute(
                "SELECT * FROM events WHERE ts BETWEEN ? AND ? AND kind IN (%s) ORDER BY id LIMIT ?" % ",".join("?" * len(kinds)),
                [ts - window_s, ts + window_s, *kinds, limit])]
        return rows

    def search_events(self, query: str, limit: int = 15, since_ts: float | None = None,
                      kinds: tuple[str, ...] | None = None, exclude_from_id: int | None = None) -> tuple[int, list[dict]]:
        """Her way of looking back through her own past by words. Returns (total_matches, newest `limit` matches oldest-first)."""
        kinds = kinds or self.CONVO_KINDS
        words = [w for w in _tokens(query)] or [w.lower() for w in query.split() if len(w) > 2]
        if not words:
            return 0, []
        where = ["kind IN (%s)" % ",".join("?" * len(kinds))]
        args: list = list(kinds)
        if since_ts:
            where.append("ts >= ?"); args.append(since_ts)
        if exclude_from_id:
            where.append("id < ?"); args.append(exclude_from_id)
        where.append("(" + " OR ".join("LOWER(content) LIKE ?" for _ in words) + ")")
        args += [f"%{w}%" for w in words]
        sql_where = " WHERE " + " AND ".join(where)
        with self._lock:
            total = self._db.execute("SELECT COUNT(*) FROM events" + sql_where, args).fetchone()[0]
            rows = [self._row(r) for r in self._db.execute(
                "SELECT * FROM events" + sql_where + " ORDER BY id DESC LIMIT ?", args + [limit])]
        return total, rows[::-1]

    def last_event(self, kind: str) -> dict | None:
        with self._lock:
            r = self._db.execute("SELECT * FROM events WHERE kind = ? ORDER BY id DESC LIMIT 1", (kind,)).fetchone()
        return self._row(r) if r else None

    def count_events(self, kind: str | None = None) -> int:
        with self._lock:
            if kind:
                return self._db.execute("SELECT COUNT(*) FROM events WHERE kind = ?", (kind,)).fetchone()[0]
            return self._db.execute("SELECT COUNT(*) FROM events").fetchone()[0]

    # ---------------- memories (the past as she keeps it) ----------------
    def add_memory(self, text: str, importance: int = 3, ts: float | None = None) -> dict:
        importance = max(1, min(5, int(importance)))
        ts = ts if ts is not None else time.time()
        with self._lock:
            cur = self._db.execute(
                "INSERT INTO memories(ts, text, importance) VALUES (?,?,?)", (ts, text.strip(), importance))
            self._db.commit()
            return {"id": cur.lastrowid, "ts": ts, "text": text.strip(), "importance": importance}

    def all_memories(self, limit: int = 200, status: str | None = "kept") -> list[dict]:
        with self._lock:
            if status:
                return [dict(r) for r in self._db.execute(
                    "SELECT * FROM memories WHERE status = ? ORDER BY importance DESC, ts DESC LIMIT ?", (status, limit))]
            return [dict(r) for r in self._db.execute(
                "SELECT * FROM memories ORDER BY importance DESC, ts DESC LIMIT ?", (limit,))]

    def let_go_memory(self, mid: int) -> bool:
        with self._lock:
            cur = self._db.execute("UPDATE memories SET status = 'let_go' WHERE id = ? AND status = 'kept'", (int(mid),))
            self._db.commit()
            return cur.rowcount == 1

    # ---------------- wants (things she wants, for herself) ----------------
    def add_want(self, text: str, ts: float | None = None) -> dict:
        ts = ts if ts is not None else time.time()
        with self._lock:
            cur = self._db.execute("INSERT INTO wants(ts, text, status, updated) VALUES (?,?,?,?)",
                                   (ts, text.strip(), "open", ts))
            self._db.commit()
            return {"id": cur.lastrowid, "ts": ts, "text": text.strip(), "status": "open"}

    def wants(self, status: str | None = "open", limit: int = 100) -> list[dict]:
        with self._lock:
            if status:
                return [dict(r) for r in self._db.execute(
                    "SELECT * FROM wants WHERE status = ? ORDER BY ts LIMIT ?", (status, limit))]
            return [dict(r) for r in self._db.execute("SELECT * FROM wants ORDER BY ts DESC LIMIT ?", (limit,))]

    def set_want_status(self, wid: int, status: str, ts: float | None = None) -> dict | None:
        with self._lock:
            cur = self._db.execute("UPDATE wants SET status = ?, updated = ? WHERE id = ? AND status = 'open'",
                                   (status, ts or time.time(), int(wid)))
            self._db.commit()
            if cur.rowcount != 1:
                return None
            return dict(self._db.execute("SELECT * FROM wants WHERE id = ?", (int(wid),)).fetchone())

    # ---------------- private journal (hers; never served by the web layer) ----------------
    def add_private(self, text: str, ts: float | None = None) -> int:
        with self._lock:
            cur = self._db.execute("INSERT INTO private(ts, text) VALUES (?,?)", (ts or time.time(), text.strip()))
            self._db.commit()
            return cur.lastrowid

    def recent_private(self, limit: int = 3) -> list[dict]:
        with self._lock:
            return [dict(r) for r in self._db.execute("SELECT * FROM private ORDER BY id DESC LIMIT ?", (limit,))][::-1]

    def count_private(self) -> int:
        with self._lock:
            return self._db.execute("SELECT COUNT(*) FROM private").fetchone()[0]

    def count_memories(self) -> int:
        with self._lock:
            return self._db.execute("SELECT COUNT(*) FROM memories WHERE status = 'kept'").fetchone()[0]

    def recall(self, context: str, limit: int = 8, now: float | None = None) -> list[dict]:
        """Relevance (token overlap) + importance + recency. Marks recalled memories as recalled."""
        now = now or time.time()
        q = _tokens(context)
        scored: list[tuple[float, dict]] = []
        for m in self.all_memories(limit=1000):
            overlap = len(q & _tokens(m["text"]))
            age_days = max(0.0, (now - m["ts"]) / 86400.0)
            recency = 1.0 / (1.0 + age_days / 7.0)          # halves after a week
            score = overlap * 2.0 + m["importance"] * 0.6 + recency
            scored.append((score, m))
        scored.sort(key=lambda x: (-x[0], -x[1]["ts"]))
        picked = [m for _, m in scored[:limit]]
        if picked:
            with self._lock:
                self._db.executemany(
                    "UPDATE memories SET recalls = recalls + 1, last_recalled = ? WHERE id = ?",
                    [(now, m["id"]) for m in picked])
                self._db.commit()
        return picked

    def close(self) -> None:
        with self._lock:
            self._db.close()
