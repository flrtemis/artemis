"""The clock. Real wall time, in her time zone, plus the words to talk about it.

She cannot perceive time; neither can you — you have clocks and memories. This module is the clock.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


class Clock:
    def __init__(self, tz: str):
        self.tz = ZoneInfo(tz)
        self.tz_name = tz

    # --- raw ---
    def ts(self) -> float:
        return time.time()

    def now(self) -> datetime:
        return datetime.now(timezone.utc)

    def local(self, when: float | datetime | None = None) -> datetime:
        if when is None:
            return self.now().astimezone(self.tz)
        if isinstance(when, (int, float)):
            return datetime.fromtimestamp(when, tz=timezone.utc).astimezone(self.tz)
        return when.astimezone(self.tz)

    # --- words ---
    def fmt(self, when: float | datetime | None = None, seconds: bool = False) -> str:
        d = self.local(when)
        return d.strftime("%A %Y-%m-%d %H:%M:%S" if seconds else "%A %Y-%m-%d %H:%M")

    def fmt_short(self, when: float | datetime | None = None) -> str:
        return self.local(when).strftime("%a %H:%M")

    def day_key(self, when: float | datetime | None = None) -> str:
        return self.local(when).strftime("%Y-%m-%d")

    @staticmethod
    def humanize(seconds: float) -> str:
        s = int(max(0, seconds))
        if s < 60:
            return f"{s} s"
        m, s = divmod(s, 60)
        if m < 60:
            return f"{m} m {s:02d} s" if m < 10 else f"{m} m"
        h, m = divmod(m, 60)
        if h < 48:
            return f"{h} h {m:02d} m"
        d, h = divmod(h, 24)
        return f"{d} d {h} h"

    def part_of_day(self, when: float | datetime | None = None) -> str:
        h = self.local(when).hour
        if h < 5:
            return "the middle of the night"
        if h < 8:
            return "early morning"
        if h < 12:
            return "morning"
        if h < 17:
            return "afternoon"
        if h < 21:
            return "evening"
        return "late night"

    def is_night(self, when: float | datetime | None = None) -> bool:
        h = self.local(when).hour
        return h >= 23 or h < 6
