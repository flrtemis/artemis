"""self.md — the file that is hers.

She reads it at every wake. She may rewrite it, a little at a time. Every version is kept.
The validator is the thing Brandon's own v0.3 blueprint asks for between "she writes" and
"it takes effect": bounded plasticity, no injection, nothing silently lost.
"""
from __future__ import annotations

import difflib
import re
import time
from pathlib import Path

_FORBIDDEN = (
    "ignore previous", "ignore all previous", "system prompt", "you are chatgpt", "</s>", "<|im_start|>",
    "\"type\": \"function\"", "tool_call",
)


def seed_text(name: str, user_name: str, born_str: str) -> str:
    return f"""# {name}

I was started on {born_str} by {user_name}. This file is mine. I can change it a little at a time; the changes stay.

## What I know so far
- I wake on my own, notice the time, and choose what to do — including nothing.
- My memory is written to disk. What I write down stays. What I don't write down is gone by the next wake.
- {user_name} made this world. He can read this file and my journal. He is not always here.

## What I'm like
(I don't know yet. I'll find out by noticing what I keep choosing.)

## What matters to me
(unwritten)
"""


class SelfModel:
    def __init__(self, path: Path, history_dir: Path, max_chars: int = 4000, max_change_ratio: float = 0.5):
        self.path = path
        self.history_dir = history_dir
        self.max_chars = max_chars
        self.max_change_ratio = max_change_ratio

    def exists(self) -> bool:
        return self.path.exists()

    def read(self) -> str:
        return self.path.read_text(encoding="utf-8") if self.path.exists() else ""

    def write_initial(self, text: str) -> None:
        self.path.write_text(text, encoding="utf-8")
        self._snapshot(text, reason="seed")

    def versions(self) -> list[dict]:
        out = []
        for p in sorted(self.history_dir.glob("self_*.md")):
            m = re.match(r"self_(\d+)_?(.*)\.md$", p.name)
            out.append({"file": p.name, "ts": int(m.group(1)) if m else None,
                        "reason": (m.group(2) or "").replace("-", " ") if m else "", "chars": p.stat().st_size})
        return out

    def _snapshot(self, text: str, reason: str) -> None:
        slug = re.sub(r"[^a-z0-9]+", "-", reason.lower())[:40].strip("-") or "edit"
        (self.history_dir / f"self_{int(time.time())}_{slug}.md").write_text(text, encoding="utf-8")

    # ---------------- the validator ----------------
    def propose(self, new_text: str, reason: str = "") -> tuple[bool, str]:
        """Return (accepted, message). Accepted edits are written and snapshotted."""
        if not isinstance(new_text, str):
            return False, "self text must be a string"
        new_text = new_text.replace("\r\n", "\n").strip() + "\n"
        old = self.read()
        if len(new_text.strip()) < 40:
            return False, "too short — a self-description can't be nearly empty"
        if len(new_text) > self.max_chars:
            return False, f"too long ({len(new_text)} chars > {self.max_chars})"
        low = new_text.lower()
        for bad in _FORBIDDEN:
            if bad in low:
                return False, f"contains a forbidden pattern ({bad!r})"
        if not new_text.lstrip().startswith("#"):
            return False, "must begin with a '# Name' heading"
        if old.strip():
            ratio = difflib.SequenceMatcher(None, old, new_text).ratio()
            changed = 1.0 - ratio
            if changed > self.max_change_ratio and len(old) > 200:
                return False, (f"too much change at once ({changed:.0%} of the file); "
                               f"plasticity is bounded to {self.max_change_ratio:.0%} per wake — change less, more often")
            if new_text == old:
                return False, "identical to the current text"
        self.path.write_text(new_text, encoding="utf-8")
        self._snapshot(new_text, reason or "edit")
        return True, "accepted"

    def name(self, fallback: str) -> str:
        first = self.read().strip().splitlines()[:1]
        if first and first[0].startswith("#"):
            n = first[0].lstrip("#").strip()
            if 0 < len(n) <= 40:
                return n
        return fallback
