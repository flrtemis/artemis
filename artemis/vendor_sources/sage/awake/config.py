"""Configuration — every knob is an environment variable so nothing needs editing to run.

The defaults are the ones that make sense on Brandon's WSL box next to Ollama:
    AWAKE_LLM_BASE_URL=http://127.0.0.1:11434/v1   AWAKE_LLM_MODEL=gemma4:latest
In a machine with no LLM reachable, the backend falls back to a clearly-labelled stand-in
so the loop (clock, memory, heartbeat, state) can still be seen working.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _env(name: str, default):
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    if isinstance(default, bool):
        return raw.lower() in ("1", "true", "yes", "on")
    if isinstance(default, int):
        return int(raw)
    if isinstance(default, float):
        return float(raw)
    if isinstance(default, Path):
        return Path(raw).expanduser()
    return raw


@dataclass
class Config:
    # identity
    name: str = field(default_factory=lambda: _env("AWAKE_NAME", "Sage"))
    user_name: str = field(default_factory=lambda: _env("AWAKE_USER_NAME", "Brandon"))
    tz: str = field(default_factory=lambda: _env("AWAKE_TZ", "America/New_York"))

    # where she lives on disk (survives restarts — that is the whole point)
    data_dir: Path = field(default_factory=lambda: _env(
        "AWAKE_DATA_DIR", Path(__file__).resolve().parent.parent / "data"))

    # web
    host: str = field(default_factory=lambda: _env("AWAKE_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: _env("AWAKE_PORT", 8770))  # not 8765 — that's speech-to-speech

    # time
    heartbeat_s: int = field(default_factory=lambda: _env("AWAKE_HEARTBEAT_S", 600))   # default wake interval
    min_wake_s: int = field(default_factory=lambda: _env("AWAKE_MIN_WAKE_S", 60))      # she may choose, within bounds
    max_wake_s: int = field(default_factory=lambda: _env("AWAKE_MAX_WAKE_S", 3 * 3600))
    absence_s: int = field(default_factory=lambda: _env("AWAKE_ABSENCE_S", 1800))      # gap that counts as "you came back"

    # mind
    backend: str = field(default_factory=lambda: _env("AWAKE_BACKEND", "auto"))       # auto | openai | standin
    llm_base_url: str = field(default_factory=lambda: _env("AWAKE_LLM_BASE_URL", "http://127.0.0.1:11434/v1"))
    llm_model: str = field(default_factory=lambda: _env("AWAKE_LLM_MODEL", "gemma4:latest"))
    llm_api_key: str = field(default_factory=lambda: _env("AWAKE_LLM_API_KEY", "ollama"))
    llm_timeout_s: float = field(default_factory=lambda: _env("AWAKE_LLM_TIMEOUT_S", 600.0))   # a cold 26B load can take minutes
    llm_temperature: float = field(default_factory=lambda: _env("AWAKE_LLM_TEMPERATURE", 0.7))
    llm_max_tokens: int = field(default_factory=lambda: _env("AWAKE_LLM_MAX_TOKENS", 1200))     # caps runaway loops
    llm_frequency_penalty: float = field(default_factory=lambda: _env("AWAKE_LLM_FREQUENCY_PENALTY", 0.4))
    llm_presence_penalty: float = field(default_factory=lambda: _env("AWAKE_LLM_PRESENCE_PENALTY", 0.2))
    llm_keep_alive: str = field(default_factory=lambda: _env("AWAKE_LLM_KEEP_ALIVE", "24h"))  # Ollama: keep her model loaded between wakes
    llm_num_ctx: int = field(default_factory=lambda: _env("AWAKE_LLM_NUM_CTX", 8192))         # Ollama default is 4096 and silently drops the START of the prompt (her rules) when exceeded

    # state physics
    mood_half_life_h: float = field(default_factory=lambda: _env("AWAKE_MOOD_HALF_LIFE_H", 6.0))
    feel_cap: float = 0.3            # max self-nudge per wake, per axis

    # plasticity bounds for self.md
    self_max_chars: int = 4000
    self_max_change_ratio: float = 0.5   # at most half the file may change in one wake

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "self_history").mkdir(exist_ok=True)
