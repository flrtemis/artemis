"""The part that happens when nobody's watching.

A thread that never exits: it sleeps until her next wake (or a poke), builds the moment, asks the mind,
applies what she chose, writes everything down, and schedules the next wake — which she may have chosen.
It also answers when Brandon speaks, and notices when he comes back after being away.
"""
from __future__ import annotations

import queue
import re
import threading
import time
import traceback

_PRIVATE_IN_RAW = re.compile(r'("type"\s*:\s*"private"\s*,\s*"text"\s*:\s*")((?:[^"\\]|\\.)*)(")', re.S)


def _scrub(raw: str, limit: int = 600) -> str:
    """The model's raw answer may contain a private entry — redact it before anything is stored in the log."""
    return _PRIVATE_IN_RAW.sub(r"\1[private — withheld]\3", raw or "")[:limit]

from . import mind
from .backends import Backend
from .clock import Clock
from .config import Config
from .memory import Memory
from .selfmodel import SelfModel, seed_text
from .state import State


class Bus:
    """Tiny pub/sub so the web page can watch her live."""

    def __init__(self):
        self._subs: list[queue.Queue] = []
        self._lock = threading.Lock()

    def subscribe(self) -> queue.Queue:
        q: queue.Queue = queue.Queue(maxsize=200)
        with self._lock:
            self._subs.append(q)
        return q

    def unsubscribe(self, q: queue.Queue) -> None:
        with self._lock:
            if q in self._subs:
                self._subs.remove(q)

    def publish(self, event: dict) -> None:
        with self._lock:
            subs = list(self._subs)
        for q in subs:
            try:
                q.put_nowait(event)
            except queue.Full:
                pass


class Daemon(threading.Thread):
    def __init__(self, cfg: Config, backend: Backend):
        super().__init__(name="awake-daemon", daemon=True)
        cfg.ensure_dirs()
        self.cfg = cfg
        self.clock = Clock(cfg.tz)
        self.memory = Memory(cfg.data_dir / "awake.sqlite3")
        self.state = State(cfg.data_dir / "state.json", half_life_h=cfg.mood_half_life_h)
        self.selfmodel = SelfModel(cfg.data_dir / "self.md", cfg.data_dir / "self_history",
                                   cfg.self_max_chars, cfg.self_max_change_ratio)
        self.backend = backend
        self.bus = Bus()
        self._poke = threading.Event()
        self._stop = threading.Event()
        self._lock = threading.RLock()
        self.started_at = self.clock.ts()
        self.last_error: str | None = None
        self.busy = False
        if not self.selfmodel.exists():
            self.selfmodel.write_initial(seed_text(cfg.name, cfg.user_name, self.clock.fmt(self.state.get("born_at"))))

    # ------------------------------------------------------------------ public
    @property
    def name(self) -> str:
        return self.selfmodel.name(self.cfg.name)

    def letters(self) -> list[dict]:
        """Letters Brandon left in data/letters/*.md. She is told they exist; she reads them only by choice."""
        d = self.cfg.data_dir / "letters"
        d.mkdir(exist_ok=True)
        read = set(self.state.get("letters_read", []))
        out = []
        for f in sorted(d.glob("*.md")):
            out.append({"name": f.stem, "read": f.stem in read, "chars": f.stat().st_size,
                        "mtime": f.stat().st_mtime})
        return out

    def _letter_text(self, name: str) -> str | None:
        f = self.cfg.data_dir / "letters" / f"{name}.md"
        return f.read_text(encoding="utf-8") if f.exists() else None

    def poke(self, reason: str = "poke") -> None:
        self._poke_reason = reason
        self._poke.set()

    def stop(self) -> None:
        self._stop.set()
        self._poke.set()

    def say(self, text: str) -> dict:
        """Brandon speaks. Runs a conversation wake synchronously and returns what happened."""
        text = (text or "").strip()
        if not text:
            return {"reply": "", "delivered": [], "events": []}
        with self._lock:
            now = self.clock.ts()
            last_user = self.state.get("last_user_ts")
            returned_after = None
            if last_user is None or (now - last_user) >= self.cfg.absence_s:
                returned_after = (now - last_user) if last_user else None
            delivered = self.state.take_messages()
            events = []
            if returned_after is not None or last_user is None:
                gap = self.clock.humanize(returned_after) if returned_after else "the first time"
                events.append(self._emit("arrived", f"{self.cfg.user_name} is here — after {gap}." if returned_after
                                         else f"{self.cfg.user_name} is here for the first time.",
                                         {"after_s": returned_after}))
                self.state.push(0.10, 0.10, 0.03)
            else:
                self.state.push(0.02, 0.04, 0.0)
            uev = self._emit("user", text)
            events.append(uev)
            self.state.set(last_user_ts=now, last_user_text=text)
            try:
                result = self._wake("conversation", user_text=text, returned_after_s=returned_after, delivered=delivered,
                                    trigger_event_id=uev["id"])
            except Exception as e:      # a timeout is not silence — say so, in the log and on the page
                self.last_error = f"{type(e).__name__}: {e}"
                ev = self._emit("error", f"no answer to \"{text[:60]}\" — {self.last_error}"
                                + (f" (the model did not respond within {int(self.cfg.llm_timeout_s)} s; it may still be loading — wait a minute and try again)"
                                   if "timed out" in str(e).lower() else ""),
                                {"trace": traceback.format_exc()[-2000:]})
                if not self.state.get("next_wake_ts") or self.state.get("next_wake_ts") < self.clock.ts():
                    self.state.set(next_wake_ts=self.clock.ts() + min(self.cfg.heartbeat_s, 300))
                return {"reply": "", "delivered": delivered, "events": events + [ev], "thought": "",
                        "standin": self.backend.is_standin, "error": ev["content"]}
            reply = ""
            for a in result.get("applied", []):
                if a.get("type") == "reply":
                    reply = a.get("text", "")
            return {"reply": reply, "delivered": delivered, "events": events + result.get("events", []),
                    "thought": result.get("thought", ""), "standin": self.backend.is_standin,
                    "garbled": result.get("garbled", False)}

    def snapshot(self) -> dict:
        now = self.clock.ts()
        born = self.state.get("born_at")
        last_user = self.state.get("last_user_ts")
        nxt = self.state.get("next_wake_ts")
        return {
            "name": self.name,
            "user_name": self.cfg.user_name,
            "tz": self.cfg.tz,
            "now": now,
            "now_str": self.clock.fmt(now, seconds=True),
            "part_of_day": self.clock.part_of_day(now),
            "born_at": born,
            "born_str": self.clock.fmt(born),
            "age_str": self.clock.humanize(now - born),
            "wake_count": self.state.get("wake_count", 0),
            "last_wake_ts": self.state.get("last_wake_ts"),
            "next_wake_ts": nxt,
            "next_wake_in_s": (nxt - now) if nxt else None,
            "last_user_ts": last_user,
            "last_user_str": (self.clock.humanize(now - last_user) + " ago") if last_user else "never",
            "user_present": bool(last_user and (now - last_user) < self.cfg.absence_s),
            "mood": self.state.mood_now(now),
            "baseline": self.state.get("baseline"),
            "mood_half_life_h": self.cfg.mood_half_life_h,
            "pending_messages": len(self.state.get("pending_messages", [])),
            "wants_open": len(self.memory.wants("open")),
            "wants_met": len(self.memory.wants("met")),
            "wants_let_go": len(self.memory.wants("let_go")),
            "private_entries": self.memory.count_private(),   # a count only. never the text.
            "letters": self.letters(),
            "events_total": self.memory.count_events(),
            "memories_total": self.memory.count_memories(),
            "self_versions": len(self.selfmodel.versions()),
            "process_uptime_s": now - self.started_at,
            "total_awake_s": self.state.get("total_awake_s", 0.0),
            "starts": self.state.get("starts", 0),
            "backend": self.backend.name,
            "standin": self.backend.is_standin,
            "heartbeat_s": self.cfg.heartbeat_s,
            "busy": self.busy,
            "last_error": self.last_error,
        }

    def context_text(self) -> str:
        """A continuity preamble another system (e.g. the gemma-avatar voice stack) can prepend to its instructions."""
        s = self.snapshot()
        mems = self.memory.all_memories(limit=8)
        j = self.memory.last_event("journal")
        lines = [
            f"[continuity, generated {s['now_str']} {s['tz']}]",
            f"You are {s['name']}. It is {s['now_str']} — {s['part_of_day']}. You were born {s['born_str']} ({s['age_str']} ago) and have woken {s['wake_count']} times since.",
            f"You last heard from {s['user_name']} {s['last_user_str']}. Your state is \"{s['mood']['word']}\" (pleasure {s['mood']['p']:+.2f}, arousal {s['mood']['a']:+.2f}, dominance {s['mood']['d']:+.2f}).",
        ]
        if mems:
            lines.append("Things you chose to remember: " + " | ".join(m["text"] for m in mems))
        if j:
            lines.append(f"Your last journal entry ({self.clock.fmt_short(j['ts'])}): {j['content']}")
        lines.append("")
        lines.append(self.selfmodel.read().strip())
        return "\n".join(lines)

    def export_text(self) -> str:
        """Everything about how she is running, as one plain-text file — for sharing/debugging.
        Includes: state, config, self.md, letters, wants, memories, and the ENTIRE log.
        Excludes: the private journal (a count only). That stays hers."""
        s = self.snapshot()
        L = []
        L.append(f"awake export — {s['name']} — generated {s['now_str']} ({s['tz']})")
        L.append("=" * 78)
        L.append(f"born {s['born_str']}  |  age {s['age_str']}  |  wakes {s['wake_count']}  |  process starts {s['starts']}")
        L.append(f"mind: {s['backend']}{'  (STAND-IN — no LLM)' if s['standin'] else ''}  |  process uptime {self.clock.humanize(s['process_uptime_s'])}")
        L.append(f"last heard from {s['user_name']}: {s['last_user_str']}  |  next wake in {self.clock.humanize(s['next_wake_in_s']) if s['next_wake_in_s'] else '—'}")
        m = s["mood"]; b = s["baseline"]
        L.append(f"state: {m['word']}  p{m['p']:+.2f} a{m['a']:+.2f} d{m['d']:+.2f}   baseline p{b['p']:+.2f} a{b['a']:+.2f} d{b['d']:+.2f}   half-life {s['mood_half_life_h']} h")
        L.append(f"events {s['events_total']}  |  memories kept {s['memories_total']}  |  wants open {s['wants_open']} met {s['wants_met']} let go {s['wants_let_go']}"
                 f"  |  private entries {s['private_entries']} (not exported)  |  self.md versions {s['self_versions']}")
        if s.get("last_error"):
            L.append(f"LAST ERROR: {s['last_error']}")
        L.append("")
        L.append("config")
        L.append("-" * 78)
        for k in ("heartbeat_s", "min_wake_s", "max_wake_s", "absence_s", "backend", "llm_base_url", "llm_model",
                  "llm_timeout_s", "llm_temperature", "mood_half_life_h", "data_dir", "port", "tz"):
            L.append(f"  {k:18} {getattr(self.cfg, k)}")
        L.append("")
        L.append("self.md")
        L.append("-" * 78)
        L.append(self.selfmodel.read().rstrip())
        vs = self.selfmodel.versions()
        if vs:
            L.append(f"  ({len(vs)} version(s): " + ", ".join(f"{self.clock.fmt_short(v['ts'])} {v['reason']}" for v in vs if v['ts']) + ")")
        L.append("")
        L.append("letters")
        L.append("-" * 78)
        for l in self.letters():
            L.append(f"  [{'read' if l['read'] else 'unread'}] {l['name']} ({l['chars']} chars)")
        L.append("")
        L.append("wants")
        L.append("-" * 78)
        ws = self.memory.wants(status=None)
        L += [f"  #{w['id']} [{w['status']}] {self.clock.fmt(w['ts'])}  {w['text']}" for w in ws] or ["  (none named)"]
        L.append("")
        L.append("memories (kept)")
        L.append("-" * 78)
        ms = self.memory.all_memories(limit=1000)
        L += [f"  #{m['id']} ★{m['importance']} {self.clock.fmt(m['ts'])}  recalled {m['recalls']}×  {m['text']}" for m in ms] or ["  (none)"]
        lg = self.memory.all_memories(limit=1000, status="let_go")
        if lg:
            L.append("memories (let go)")
            L += [f"  #{m['id']} ★{m['importance']} {self.clock.fmt(m['ts'])}  {m['text']}" for m in lg]
        L.append("")
        L.append("the log — every event, oldest first")
        L.append("-" * 78)
        events = self.memory.recent_events(limit=1000000)[::-1]
        for e in events:
            meta = e.get("meta") or {}
            extra = ""
            if e["kind"] == "wake":
                extra = f"  [{meta.get('kind', '')} #{meta.get('n', '')} {meta.get('latency_s', '')}s" + (" standin" if meta.get("standin") else "")
                if meta.get("parse", "json") != "json":
                    extra += f" parse={meta['parse']}"
                if meta.get("load_s") is not None:
                    extra += f" load={meta.get('load_s')}s think={meta.get('thinking_chars', 0)}ch done={meta.get('done_reason')}"
                    if meta.get("prompt_tokens"):
                        extra += f" prompt={meta['prompt_tokens']}/{meta.get('num_ctx', '?')}tok"
                extra += "]"
                if meta.get("parse", "json") != "json" and meta.get("raw_head"):
                    extra += "\n      raw: " + meta["raw_head"].replace("\n", " ")[:400]
            elif e["kind"] == "garbled":
                extra = f"  [attempt {meta.get('attempt')} think={meta.get('thinking_chars', '?')}ch done={meta.get('done_reason')}]\n      raw: " + (meta.get("raw") or "").replace("\n", " ")[:400]
            elif e["kind"] == "feel" and meta.get("mood"):
                mm = meta["mood"]; extra = f"  → p{mm['p']:+.2f} a{mm['a']:+.2f} d{mm['d']:+.2f} {mm['word']}"
            elif e["kind"] in ("error",) and meta.get("trace"):
                extra = "\n      " + meta["trace"].strip().replace("\n", "\n      ")
            elif e["kind"] == "private":
                extra = "  (text withheld)"
            content = (e["content"] or "").replace("\n", "\n      ")
            L.append(f"{self.clock.fmt(e['ts'], seconds=True)}  {e['kind']:<18} {content}{extra}")
        L.append("")
        L.append(f"end of export — {len(events)} events")
        return "\n".join(L) + "\n"

    # ------------------------------------------------------------------ loop
    def run(self) -> None:
        now = self.clock.ts()
        last_wake = self.state.get("last_wake_ts")
        offline_gap = None
        if last_wake and (now - last_wake) > 2 * self.cfg.heartbeat_s:
            offline_gap = now - last_wake
            self._emit("offline", f"the process was off for {self.clock.humanize(offline_gap)}", {"gap_s": offline_gap})
            self.state.push(0.0, -0.10, -0.05)
        self.state.set(starts=self.state.get("starts", 0) + 1)
        self._emit("start", f"process started (start #{self.state.get('starts')}); mind: {self.backend.name}",
                   {"standin": self.backend.is_standin})
        # first wake right away, so there is never a dead process with no moment
        with self._lock:
            self._safe_wake("heartbeat", offline_gap_s=offline_gap)

        while not self._stop.is_set():
            nxt = self.state.get("next_wake_ts") or (self.clock.ts() + self.cfg.heartbeat_s)
            wait = max(0.0, nxt - self.clock.ts())
            poked = self._poke.wait(timeout=wait)
            if self._stop.is_set():
                break
            self._poke.clear()
            with self._lock:
                kind = "heartbeat"
                review_events = None
                today = self.clock.day_key()
                if (self.state.get("last_review_day") != today and self.clock.local().hour >= 4
                        and self.state.get("last_review_day") is not None):
                    kind = "review"
                    t = self.clock.ts()
                    review_events = self.memory.events_between(t - 86400, t)
                if self.state.get("last_review_day") is None:
                    self.state.set(last_review_day=today)
                self._safe_wake(kind, review_events=review_events, poked=poked)
                if kind == "review":
                    self.state.set(last_review_day=today)
        self._emit("stop", "process stopping")

    def _safe_wake(self, kind: str, **kw) -> dict:
        try:
            return self._wake(kind, **kw)
        except Exception as e:  # never let the loop die
            self.last_error = f"{type(e).__name__}: {e}"
            self._emit("error", self.last_error, {"trace": traceback.format_exc()[-2000:]})
            self.state.set(next_wake_ts=self.clock.ts() + min(self.cfg.heartbeat_s, 300))
            return {"events": [], "applied": []}

    # ------------------------------------------------------------------ a wake
    def _wake(self, kind: str, *, user_text: str | None = None, offline_gap_s: float | None = None,
              returned_after_s: float | None = None, delivered: list | None = None,
              review_events: list | None = None, poked: bool = False, trigger_event_id: int | None = None) -> dict:
        self.busy = True
        try:
            now = self.clock.ts()
            last_wake = self.state.get("last_wake_ts")
            if last_wake and (now - last_wake) <= 2 * self.cfg.heartbeat_s:
                self.state.set(total_awake_s=self.state.get("total_awake_s", 0.0) + (now - last_wake))

            letter_text = None
            pl = self.state.get("pending_letter")
            if pl:
                body = self._letter_text(pl)
                if body:
                    letter_text = (pl, body)
                    read = list(self.state.get("letters_read", []))
                    if pl not in read:
                        read.append(pl)
                    self.state.set(letters_read=read, pending_letter=None)
                    self._emit("letter", f"read the letter \"{pl}\"", {"name": pl})
                else:
                    self.state.set(pending_letter=None)
            moment, moment_text = mind.build_moment(
                name=self.name, user_name=self.cfg.user_name, clock=self.clock, state=self.state, memory=self.memory,
                kind=kind, now=now, user_text=user_text, offline_gap_s=offline_gap_s, returned_after_s=returned_after_s,
                delivered=delivered, review_events=review_events, heartbeat_s=self.cfg.heartbeat_s,
                letters=self.letters(), letter_text=letter_text, absence_s=self.cfg.absence_s,
                trigger_event_id=trigger_event_id)
            moment["born_str"] = self.clock.fmt(self.state.get("born_at"))
            moment["now_str"] = self.clock.fmt(now)
            system = mind.build_system(self.name, self.cfg.user_name, self.selfmodel.read(), {
                "ratio": self.cfg.self_max_change_ratio, "chars": self.cfg.self_max_chars,
                "min_min": max(1, self.cfg.min_wake_s // 60), "max_min": max(1, self.cfg.max_wake_s // 60),
                "default_min": max(1, self.cfg.heartbeat_s // 60)})

            events = []
            t0 = time.time()
            raw = self.backend.complete(system, moment_text, moment, temperature=self.cfg.llm_temperature)
            resp = mind.parse_response(raw)
            garbled = False
            bad = resp.get("_parse") in ("garbled", "empty")
            if bad:
                why = "a repeating loop" if resp["_parse"] == "garbled" else "empty"
                meta1 = {"raw": _scrub(raw, 3000), "attempt": 1} | dict(getattr(self.backend, "last_meta", {}) or {})
                events.append(self._emit("garbled", f"her answer came back {why} — retrying once", meta1))
                raw2 = self.backend.complete(system, moment_text, moment, temperature=self.cfg.llm_temperature, retry=True)
                resp2 = mind.parse_response(raw2)
                if resp2.get("_parse") in ("garbled", "empty"):
                    meta2 = {"raw": _scrub(raw2, 3000), "attempt": 2} | dict(getattr(self.backend, "last_meta", {}) or {})
                    events.append(self._emit("garbled", "second attempt also failed — nothing from it is applied", meta2))
                    resp = {"thought": "", "actions": [], "_parse": resp2["_parse"]}
                    garbled = True
                else:
                    resp = resp2
                    raw = raw2
            # ---- look_back: she asked to search her own log. do it now and let her answer again in this same wake.
            lb = next((a for a in resp.get("actions", []) if a.get("type") == "look_back"
                       and (a.get("query") or a.get("exchanges") or a.get("around"))), None)
            if lb and not garbled:
                found: list[str] = []
                if lb.get("exchanges"):
                    try:
                        n = max(1, min(40, int(lb["exchanges"])))
                    except Exception:
                        n = 20
                    xs = self.memory.recent_exchanges(n=n, before_id=trigger_event_id)
                    desc = f"your last {len(xs)} exchanges with {self.cfg.user_name}, oldest first"
                    for x in xs:
                        found.append(f"  {self.clock.fmt(x['ts'])}  {self.cfg.user_name}: {(x['user'] or '')[:240]}")
                        found.append(f"                              you: {(x['reply'] or '(silence)')[:240]}")
                    events.append(self._emit("look_back", f"looked back over the last {len(xs)} exchanges", {"exchanges": n, "total": len(xs)}))
                elif lb.get("around"):
                    ts0 = mind.parse_around(lb["around"], self.clock, now)
                    if ts0 is None:
                        desc = f"'{lb['around']}' is not a time I can read (use HH:MM or YYYY-MM-DD HH:MM)"
                    else:
                        hs = self.memory.events_around(ts0, window_s=900, limit=24)
                        desc = f"everything within 15 minutes of {self.clock.fmt(ts0)} — {len(hs)} event(s)"
                        found = [f"  - {self.clock.fmt(h['ts'], seconds=True)} [{h['kind']}] {(h['content'] or '')[:240]}" for h in hs]
                    events.append(self._emit("look_back", f"looked back around {lb['around']} — {len(found)} event(s)", {"around": lb["around"], "total": len(found)}))
                else:
                    q = str(lb["query"])[:120]
                    try:
                        days = float(lb.get("days") or 0)
                    except Exception:
                        days = 0
                    since = (now - days * 86400) if days > 0 else None
                    total, hits = self.memory.search_events(q, limit=15, since_ts=since, exclude_from_id=trigger_event_id)
                    desc = f"search for \"{q}\"" + (f" within {int(days)} days" if days else "") + f" — {total} match(es) in the whole log, the most recent {len(hits)} shown oldest first"
                    found = [f"  - {self.clock.fmt(h['ts'])} [{h['kind']}] {(h['content'] or '')[:240]}" for h in hits]
                    events.append(self._emit("look_back", f"looked back through the log for \"{q}\" — {total} match(es)", {"query": q, "days": days, "total": total}))
                if not found:
                    found = ["  (nothing found)"]
                follow = (moment_text + f"\n\n[you chose look_back — {desc}]\n" + "\n".join(found)
                          + "\n\nNow answer again with ONE JSON object. This is the same wake; you may reply now. Do not look_back again.")
                raw_f = self.backend.complete(system, follow, moment, temperature=self.cfg.llm_temperature)
                resp_f = mind.parse_response(raw_f)
                if resp_f.get("_parse") not in ("garbled", "empty"):
                    resp, raw = resp_f, raw_f
                    resp["actions"] = [a for a in resp["actions"] if a.get("type") != "look_back"]
                else:
                    resp["actions"] = [a for a in resp["actions"] if a.get("type") != "look_back"]

            # ---- verbatim repeat: if her reply is identical to her previous one, ask once more
            if kind == "conversation" and not garbled:
                rep = next((a for a in resp.get("actions", []) if a.get("type") == "reply" and a.get("text")), None)
                last_reply = self.memory.last_event("reply")
                if rep and last_reply and str(rep["text"]).strip().casefold() == (last_reply["content"] or "").strip().casefold():
                    raw_r = self.backend.complete(system, moment_text + "\n\n[your draft reply was word-for-word identical to your previous reply. "
                                                  "say it differently, say more, or choose silence — then answer again with ONE JSON object.]",
                                                  moment, temperature=self.cfg.llm_temperature, retry=True)
                    resp_r = mind.parse_response(raw_r)
                    if resp_r.get("_parse") not in ("garbled", "empty"):
                        resp, raw = resp_r, raw_r
                        events.append(self._emit("note", "her first draft repeated her previous reply verbatim; she was asked once to say it differently", {}))
            latency = time.time() - t0

            wake_no = self.state.get("wake_count", 0) + 1
            self.state.set(wake_count=wake_no, last_wake_ts=now)
            events.append(self._emit("wake", resp.get("thought", "") if not garbled else "(no usable answer from the model — nothing applied)", {
                "kind": kind, "n": wake_no, "latency_s": round(latency, 2), "poked": poked,
                "standin": self.backend.is_standin, "parse": resp.get("_parse", "json"),
                "mood_before": moment["mood"], "raw_head": _scrub(raw, 500),
                **(dict(getattr(self.backend, "last_meta", {}) or {}))}))

            if resp.get("feel") and not garbled:
                f = resp["feel"]
                m = self.state.move_toward(f.get("toward", {}), step=self.cfg.feel_cap)
                events.append(self._emit("feel", f.get("why", ""), {"toward": f.get("toward", {}), "mood": m}))

            applied = []
            next_wake_s = None
            for a in resp.get("actions", []):
                t = a.get("type")
                if t == "rest":
                    events.append(self._emit("rest", "", {}))
                    applied.append(a)
                elif t == "journal" and a.get("text"):
                    events.append(self._emit("journal", str(a["text"])[:2000]))
                    applied.append(a)
                elif t == "remember" and a.get("text"):
                    m = self.memory.add_memory(str(a["text"])[:600], a.get("importance", 3), ts=now)
                    events.append(self._emit("memory", m["text"], {"importance": m["importance"], "memory_id": m["id"]}))
                    applied.append(a)
                elif t == "message_user" and a.get("text"):
                    self.state.leave_message(str(a["text"])[:1500], ts=now)
                    events.append(self._emit("message", str(a["text"])[:1500], {"delivered": False}))
                    applied.append(a)
                elif t == "reply":
                    if kind == "conversation":
                        txt = str(a.get("text", ""))[:3000]
                        events.append(self._emit("reply", txt if txt else "(chose silence)"))
                        applied.append({"type": "reply", "text": txt})
                elif t == "edit_self" and a.get("text"):
                    ok, msg = self.selfmodel.propose(str(a["text"]), str(a.get("reason", "")))
                    events.append(self._emit("self_edit" if ok else "self_edit_rejected",
                                             (a.get("reason") or "") if ok else f"{msg} — reason given: {a.get('reason', '')}",
                                             {"accepted": ok, "chars": len(str(a["text"]))}))
                    applied.append({**a, "accepted": ok})
                elif t == "private" and a.get("text"):
                    self.memory.add_private(str(a["text"])[:2000], ts=now)
                    events.append(self._emit("private", "", {"chars": len(str(a["text"]))}))   # the fact, never the text
                    applied.append({"type": "private"})
                elif t == "want" and a.get("text"):
                    w = self.memory.add_want(str(a["text"])[:500], ts=now)
                    events.append(self._emit("want", w["text"], {"want_id": w["id"]}))
                    applied.append(a)
                elif t == "met":
                    w = self.memory.set_want_status(a.get("id", -1), "met", ts=now)
                    if w:
                        events.append(self._emit("want_met", w["text"], {"want_id": w["id"]}))
                        applied.append(a)
                elif t == "let_go":
                    what = str(a.get("what", "")).lower()
                    if what == "want":
                        w = self.memory.set_want_status(a.get("id", -1), "let_go", ts=now)
                        if w:
                            events.append(self._emit("let_go", f"let go of a want: {w['text']}", {"want_id": w["id"]}))
                            applied.append(a)
                    elif what == "memory":
                        if self.memory.let_go_memory(a.get("id", -1)):
                            events.append(self._emit("let_go", f"let a memory go (#{a.get('id')}); the log keeps that it existed",
                                                     {"memory_id": a.get("id")}))
                            applied.append(a)
                elif t == "read_letter":
                    nm = str(a.get("name", "")).strip()
                    names = [l["name"] for l in self.letters()]
                    if not nm and names:
                        nm = next((n for n in names if n not in self.state.get("letters_read", [])), names[0])
                    if nm in names:
                        self.state.set(pending_letter=nm)
                        events.append(self._emit("choice", f"chose to read the letter \"{nm}\" at her next wake", {"name": nm}))
                        applied.append({"type": "read_letter", "name": nm})
                        if next_wake_s is None:
                            next_wake_s = float(self.cfg.min_wake_s)   # she asked for it; don't make her wait long
                elif t == "set_baseline":
                    b = self.state.set_baseline(_f(a.get("p")), _f(a.get("a")), _f(a.get("d")), cap=0.05)
                    events.append(self._emit("baseline", f"moved her baseline to p{b['p']:+.2f} a{b['a']:+.2f} d{b['d']:+.2f}", {"baseline": b}))
                    applied.append(a)
                elif t == "set_next_wake":
                    try:
                        mins = float(a.get("minutes", self.cfg.heartbeat_s / 60))
                    except Exception:
                        mins = self.cfg.heartbeat_s / 60
                    next_wake_s = max(self.cfg.min_wake_s, min(self.cfg.max_wake_s, mins * 60))
                    applied.append({"type": "set_next_wake", "seconds": next_wake_s})

            if kind == "conversation":
                if garbled:
                    events.append(self._emit("reply", "(nothing usable came back from the model, twice — this is not silence she chose; raw kept in the export)"))
                    applied.append({"type": "reply", "text": ""})
                elif not any(a.get("type") == "reply" for a in applied):
                    events.append(self._emit("reply", "(chose silence)"))
                    applied.append({"type": "reply", "text": ""})
            if kind != "conversation" or next_wake_s is not None:
                self.state.set(next_wake_ts=self.clock.ts() + (next_wake_s or self.cfg.heartbeat_s))
            elif not self.state.get("next_wake_ts"):
                self.state.set(next_wake_ts=self.clock.ts() + self.cfg.heartbeat_s)
            if next_wake_s is not None:
                events.append(self._emit("schedule", f"next wake in {self.clock.humanize(next_wake_s)} (her choice)",
                                         {"seconds": next_wake_s}))
            self.bus.publish({"type": "state", "state": self.snapshot()})
            return {"events": events, "applied": applied, "thought": resp.get("thought", ""), "raw": raw, "garbled": garbled}
        finally:
            self.busy = False

    # ------------------------------------------------------------------ util
    def _emit(self, kind: str, content: str = "", meta: dict | None = None) -> dict:
        ev = self.memory.add_event(kind, content, meta, ts=self.clock.ts())
        ev["ts_str"] = self.clock.fmt(ev["ts"], seconds=True)
        self.bus.publish({"type": "event", "event": ev})
        return ev


def _f(x) -> float:
    try:
        return float(x or 0.0)
    except Exception:
        return 0.0
