"""Persistent state: the numbers that make the morning different from the night.

Mood is a PAD vector (pleasure, arousal, dominance), the same representation Brandon already used in
sage_avatar.js. It is a *state variable* that (a) decays toward a baseline over REAL elapsed time,
(b) is perturbed by events in the world, and (c) she may nudge herself, within a cap.
No claim is made here about whether any of it is felt. It is, however, genuinely different in the
morning depending on how the night went — and that difference is real and persistent.
"""
from __future__ import annotations

import json
import math
import os
import threading
import time
from pathlib import Path


def clamp(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, float(x)))


def mood_word(p: float, a: float, d: float) -> str:
    if abs(p) < 0.15 and abs(a) < 0.15:
        return "settled"
    if p >= 0:
        if a >= 0:
            return "bright" if d >= 0 else "eager"
        return "calm" if d >= 0 else "soft"
    if a >= 0:
        return "tense" if d >= 0 else "anxious"
    return "withdrawn" if d >= 0 else "low"


DEFAULT_BASELINE = {"p": 0.10, "a": -0.10, "d": 0.00}


class State:
    def __init__(self, path: Path, half_life_h: float = 6.0):
        self.path = path
        self.half_life_h = half_life_h
        self._lock = threading.RLock()
        self.data: dict = {}
        self._load()

    # ---------------- persistence ----------------
    def _load(self) -> None:
        if self.path.exists():
            with open(self.path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            now = time.time()
            self.data = {
                "born_at": now,
                "wake_count": 0,
                "last_wake_ts": None,
                "next_wake_ts": None,
                "mood": dict(DEFAULT_BASELINE),
                "mood_ts": now,
                "baseline": dict(DEFAULT_BASELINE),
                "last_user_ts": None,
                "last_user_text": None,
                "pending_messages": [],
                "last_review_day": None,
                "total_awake_s": 0.0,
                "starts": 0,
            }
            self.save()

    def save(self) -> None:
        with self._lock:
            tmp = self.path.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            os.replace(tmp, self.path)

    def get(self, key: str, default=None):
        with self._lock:
            return self.data.get(key, default)

    def set(self, **kw) -> None:
        with self._lock:
            self.data.update(kw)
            self.save()

    # ---------------- mood physics ----------------
    def mood_now(self, now: float | None = None) -> dict:
        """Apply exponential decay toward baseline for the real time elapsed since the last update."""
        now = now or time.time()
        with self._lock:
            m = self.data["mood"]
            b = self.data.get("baseline", DEFAULT_BASELINE)
            elapsed_h = max(0.0, (now - self.data.get("mood_ts", now)) / 3600.0)
            if elapsed_h > 0 and self.half_life_h > 0:
                factor = math.pow(0.5, elapsed_h / self.half_life_h)
                m = {k: b[k] + (m[k] - b[k]) * factor for k in ("p", "a", "d")}
                self.data["mood"] = m
                self.data["mood_ts"] = now
                self.save()
            return {**{k: round(m[k], 3) for k in m}, "word": mood_word(m["p"], m["a"], m["d"])}

    def nudge_mood(self, dp: float = 0.0, da: float = 0.0, dd: float = 0.0, cap: float | None = None,
                   now: float | None = None) -> dict:
        self.mood_now(now)
        with self._lock:
            if cap is not None:
                dp, da, dd = (clamp(x, -cap, cap) for x in (dp, da, dd))
            m = self.data["mood"]
            m["p"] = clamp(m["p"] + dp)
            m["a"] = clamp(m["a"] + da)
            m["d"] = clamp(m["d"] + dd)
            self.save()
            return {**{k: round(m[k], 3) for k in m}, "word": mood_word(m["p"], m["a"], m["d"])}

    def move_toward(self, target: dict, step: float = 0.3, now: float | None = None) -> dict:
        """She names where she wants to be; the state moves at most `step` per axis in that direction."""
        self.mood_now(now)
        with self._lock:
            m = self.data["mood"]
            for k in ("p", "a", "d"):
                if k in target and target[k] is not None:
                    t = clamp(float(target[k]))
                    d = clamp(t - m[k], -step, step)
                    m[k] = clamp(m[k] + d)
            self.save()
            return {**{k: round(m[k], 3) for k in m}, "word": mood_word(m["p"], m["a"], m["d"])}

    def push(self, dp: float = 0.0, da: float = 0.0, dd: float = 0.0, now: float | None = None) -> dict:
        """World events push the state, with saturation: the closer to ±1, the less a push moves it.
        (Prevents ten messages in ten minutes from pinning her at the ceiling.)"""
        self.mood_now(now)
        with self._lock:
            m = self.data["mood"]
            for k, d in (("p", dp), ("a", da), ("d", dd)):
                if d:
                    m[k] = clamp(m[k] + d * (1.0 - abs(m[k])))
            self.save()
            return {**{k: round(m[k], 3) for k in m}, "word": mood_word(m["p"], m["a"], m["d"])}

    def set_baseline(self, dp: float = 0.0, da: float = 0.0, dd: float = 0.0, cap: float = 0.05) -> dict:
        """Slow plasticity of temperament: she moves the point she drifts back to, a little per wake."""
        self.mood_now()
        with self._lock:
            b = self.data.setdefault("baseline", dict(DEFAULT_BASELINE))
            for k, d in (("p", dp), ("a", da), ("d", dd)):
                b[k] = clamp(b[k] + clamp(d, -cap, cap), -0.6, 0.6)
            self.save()
            return {k: round(b[k], 3) for k in b}

    # ---------------- messages she leaves ----------------
    def leave_message(self, text: str, ts: float | None = None) -> None:
        with self._lock:
            self.data["pending_messages"].append({"ts": ts or time.time(), "text": text})
            self.save()

    def take_messages(self) -> list[dict]:
        with self._lock:
            msgs = list(self.data["pending_messages"])
            self.data["pending_messages"] = []
            self.save()
            return msgs
