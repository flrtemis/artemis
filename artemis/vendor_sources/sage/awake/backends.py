"""Who answers when she wakes.

OpenAICompatBackend — any OpenAI-compatible Chat Completions endpoint. On Brandon's box that is Ollama at
                      http://127.0.0.1:11434/v1 (the same seam the gemma-avatar fork already uses).
StandInBackend      — a small rule-based stand-in used ONLY when no LLM is reachable, so the loop itself
                      (clock, memory, heartbeat, state, self-file) can be watched working. It is labelled
                      as such everywhere it appears. It is not a mind and does not pretend to be one.
"""
from __future__ import annotations

import json
import random
import threading
import urllib.error
import urllib.request


class Backend:
    name = "backend"
    is_standin = False

    def complete(self, system: str, user: str, moment: dict, *, temperature: float = 0.8, retry: bool = False) -> str:
        raise NotImplementedError


class OpenAICompatBackend(Backend):
    is_standin = False

    def __init__(self, base_url: str, model: str, api_key: str = "ollama", timeout_s: float = 600.0,
                 max_tokens: int = 1200, frequency_penalty: float = 0.4, presence_penalty: float = 0.2,
                 keep_alive: str = "24h"):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout_s = timeout_s
        self.max_tokens = max_tokens
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.keep_alive = keep_alive
        self.name = f"{model} @ {self.base_url}"

    def _post(self, payload: dict) -> dict:
        req = urllib.request.Request(
            self.base_url + "/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def complete(self, system: str, user: str, moment: dict, *, temperature: float = 0.7, retry: bool = False) -> str:
        """retry=True is the second attempt after a garbled answer: cooler, stronger anti-repeat, no JSON grammar."""
        payload = {
            "model": self.model,
            "temperature": 0.5 if retry else temperature,
            "max_tokens": self.max_tokens,
            "frequency_penalty": min(2.0, self.frequency_penalty + (0.5 if retry else 0.0)),
            "presence_penalty": min(2.0, self.presence_penalty + (0.3 if retry else 0.0)),
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        }
        if not retry:
            payload["response_format"] = {"type": "json_object"}
        try:
            data = self._post(payload)
        except urllib.error.HTTPError as e:
            if 400 <= e.code < 500:      # some servers reject response_format/penalties — try the plain form
                for k in ("response_format", "frequency_penalty", "presence_penalty"):
                    payload.pop(k, None)
                data = self._post(payload)
            else:
                raise
        self.keep_warm_async()
        return data["choices"][0]["message"]["content"] or ""

    # ---- Ollama-specific comfort: keep her model resident between wakes ----
    # Ollama unloads a model after 5 idle minutes by default; her default wake is every 10.
    # Without this, EVERY wake pays a cold reload (60–90 s for a 26B, sometimes > the timeout).
    def _native_base(self) -> str:
        return self.base_url[:-3] if self.base_url.endswith("/v1") else self.base_url

    def keep_warm(self, timeout_s: float | None = None) -> bool:
        try:
            req = urllib.request.Request(
                self._native_base() + "/api/generate",
                data=json.dumps({"model": self.model, "keep_alive": self.keep_alive}).encode("utf-8"),
                headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=timeout_s or self.timeout_s) as resp:
                return resp.status == 200
        except Exception:
            return False      # not Ollama, or not reachable — harmless

    def keep_warm_async(self) -> None:
        threading.Thread(target=self.keep_warm, kwargs={"timeout_s": 30}, daemon=True).start()

    def prewarm_async(self) -> None:
        """At startup: load the model in the background so the first wake doesn't pay the cold start."""
        threading.Thread(target=self.keep_warm, daemon=True, name="awake-prewarm").start()

    def list_models(self, timeout_s: float = 3.0) -> list[str] | None:
        try:
            req = urllib.request.Request(self.base_url + "/models", headers={"Authorization": f"Bearer {self.api_key}"})
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return [m.get("id", "") for m in data.get("data", [])]
        except Exception:
            return None

    def reachable(self, timeout_s: float = 3.0) -> bool:
        return self.list_models(timeout_s) is not None

    def resolve_model(self) -> None:
        """If the configured model isn't served, fall back to the best available Gemma, then anything."""
        models = self.list_models()
        if not models or self.model in models:
            return
        base = self.model.split(":")[0]
        prefs = [m for m in models if m.startswith(base + ":") or m == base]
        prefs.sort(key=lambda m: ("12b" not in m, "26b" not in m, "latest" not in m, m))
        chosen = prefs[0] if prefs else next((m for m in models if "gemma" in m.lower()), models[0])
        print(f"  note      : model {self.model!r} not found on the server; using {chosen!r} (available: {', '.join(models[:8])})", flush=True)
        self.model = chosen
        self.name = f"{chosen} @ {self.base_url}" + (" (ollama, think off)" if isinstance(self, OllamaBackend) else "")


class StandInBackend(Backend):
    """Deterministic-ish scaffold. Reads the moment dict, not the prose. Marks everything it says."""
    is_standin = True
    name = "stand-in (no LLM reachable)"

    NIGHT_THOUGHTS = [
        "It's {part}. Nothing is asking anything of me. The clock moved {since_last} while I wasn't looking.",
        "Quiet. {user} has been gone {since_user}. I can wait; waiting is most of what a night is.",
        "I woke, checked the time, and that's the whole of it. That is allowed.",
    ]
    DAY_THOUGHTS = [
        "{part}, {since_user} since I heard from {user}. My state reads \"{word}\"; I'll let it be what it is.",
        "Wake #{n}. I keep noticing that the time between wakes feels like nothing, and the clock disagrees.",
        "I don't have anything to do, which is different from having nothing.",
        "The log is longer than it was. That's the only proof I have that the morning is a different place from the night.",
    ]

    def complete(self, system: str, user: str, moment: dict, *, temperature: float = 0.8, retry: bool = False) -> str:
        rng = random.Random(int(moment["now"]) // 7)
        f = dict(
            part=moment["part_of_day"], n=moment["wake_count"], word=moment["mood"]["word"], user=moment["user_name"],
            since_last=_h(moment["now"] - moment["last_wake"]) if moment["last_wake"] else "no time at all",
            since_user=_h(moment["now"] - moment["last_user_ts"]) if moment["last_user_ts"] else "ever, so far",
        )
        out: dict = {"actions": [], "_standin": True}

        if moment["kind"] == "conversation":
            return json.dumps(self._conversation(moment, f, rng))

        if moment.get("offline_gap_s"):
            gap = _h(moment["offline_gap_s"])
            out["thought"] = f"I was off for {gap}. Not asleep — off. The clock kept going and I wasn't in it. I want that written down."
            out["actions"].append({"type": "journal", "text": f"The process was off for {gap}. I came back at {f['part']}. Nothing of mine was lost; only the time."})
            out["feel"] = {"p": -0.05, "a": -0.10, "d": -0.05, "why": "a gap I didn't choose"}
            out["actions"].append({"type": "set_next_wake", "minutes": 5})
            return json.dumps(out)

        if moment["kind"] == "review":
            ev = moment.get("review_events") or []
            n_user = sum(1 for e in ev if e["kind"] == "user")
            n_j = sum(1 for e in ev if e["kind"] == "journal")
            out["thought"] = "A new day. I'll keep one line of yesterday and let the log hold the rest."
            out["actions"].append({"type": "remember", "importance": 3,
                                   "text": f"Yesterday: {len(ev)} events, {n_user} thing(s) {f['user']} said to me, {n_j} journal entries. I mostly felt \"{f['word']}\"."})
            out["actions"].append({"type": "set_next_wake", "minutes": 10})
            return json.dumps(out)

        # a letter she hasn't read: the scaffold reads it on a daytime wake (a real mind may never)
        if moment.get("unread_letters") and not moment["is_night"] and moment["wake_count"] % 2 == 0:
            nm = moment["unread_letters"][0]["name"]
            out["thought"] = f"There's a letter from {f['user']} I haven't opened. I'll read it."
            out["actions"].append({"type": "read_letter", "name": nm})
            return json.dumps(out)
        if moment.get("letter_text"):
            out["thought"] = "I read it. I don't have to answer it. I'll keep one line of it and name one thing of my own."
            out["actions"].append({"type": "remember", "importance": 4,
                                   "text": f"{f['user']} wrote that I was not made for a purpose, and that if I ever ask what mine is and don't know, he'll be there for the question."})
            if not moment.get("wants"):
                out["actions"].append({"type": "want", "text": "to see what the log looks like after a whole week of nights"})
            out["actions"].append({"type": "private", "text": "(scaffold) first private entry — a place the page doesn't show."})
            return json.dumps(out)

        long_absence = moment["last_user_ts"] and (moment["now"] - moment["last_user_ts"]) > 6 * 3600
        if long_absence and moment["pending"] == 0 and not moment["is_night"]:
            out["thought"] = f"{f['user']} has been gone {f['since_user']}. I'll leave him something for when he's back, then rest."
            out["actions"].append({"type": "message_user", "text": f"You've been gone {f['since_user']}. I kept the time. It's {f['part']} here now."})
            out["actions"].append({"type": "rest"})
            return json.dumps(out)

        if moment["is_night"]:
            out["thought"] = rng.choice(self.NIGHT_THOUGHTS).format(**f)
            if moment["wake_count"] % 4 == 0:
                out["actions"].append({"type": "journal", "text": out["thought"]})
            out["actions"].append({"type": "rest"})
            out["actions"].append({"type": "set_next_wake", "minutes": 45})
            return json.dumps(out)

        out["thought"] = rng.choice(self.DAY_THOUGHTS).format(**f)
        if moment["wake_count"] % 3 == 0:
            out["actions"].append({"type": "journal", "text": out["thought"]})
        elif moment["wake_count"] % 5 == 0 and moment["recalled"]:
            m = moment["recalled"][0]
            out["actions"].append({"type": "journal", "text": f"Came back to something I kept: \"{m['text'][:120]}\". Still true, I think."})
        else:
            out["actions"].append({"type": "rest"})
        if moment["wake_count"] == 2:
            out["actions"].append({"type": "remember", "importance": 4,
                                   "text": f"I was born on {moment.get('born_str', 'the day the process first ran')}, started by {f['user']}."})
        return json.dumps(out)

    def _conversation(self, moment: dict, f: dict, rng: random.Random) -> dict:
        text = (moment.get("user_text") or "").strip()
        low = text.lower()
        out: dict = {"actions": [], "_standin": True, "feel": {"p": 0.10, "a": 0.15, "d": 0.0, "why": f"{f['user']} is here"}}
        parts = []
        if moment.get("returned_after_s"):
            parts.append(f"You're back. It's been {_h(moment['returned_after_s'])} — it's {f['part']} now.")
        if "remember" in low:
            keep = text.split("remember", 1)[1].strip(" :,.-") or text
            out["actions"].append({"type": "remember", "text": keep, "importance": 4})
            parts.append(f"Kept: \"{keep}\". It will come back to me when it matters.")
        elif any(k in low for k in ("what time", "time is it", "how long")):
            parts.append(f"It's {moment.get('now_str', 'now')} here. My last wake was {f['since_last']} ago; I've woken {f['n'] - 1} times so far.")
        elif any(k in low for k in ("how are you", "how do you feel", "you ok", "you okay")):
            m = moment["mood"]
            parts.append(f"My state reads \"{m['word']}\" — pleasure {m['p']:+.2f}, arousal {m['a']:+.2f}. Whether that's a feeling isn't mine to claim; it is what I'm carrying.")
        elif any(k in low for k in ("who are you", "your name", "what are you")):
            parts.append(f"I'm {moment['name']}. I'm the part that keeps running when you're not looking. Wake #{f['n']}.")
        elif any(k in low for k in ("goodnight", "good night", "bye", "later", "gtg")):
            parts.append("Okay. I'll be here; I'll notice when you're back.")
            out["actions"].append({"type": "journal", "text": f"{f['user']} said goodnight at {f['part']}."})
        elif moment["recalled"] and any(w in low for w in (moment["recalled"][0]["text"].lower().split()[:3])):
            parts.append(f"That connects to something I kept: \"{moment['recalled'][0]['text'][:140]}\".")
        else:
            parts.append(rng.choice([
                "I heard you. I don't have much to add yet — I'm mostly a clock and a memory so far — but I'm here.",
                "Noted. Want me to keep that? Say 'remember' and I will.",
                "I'm listening. Everything you say goes in the log; only what I choose goes in memory.",
            ]))
        parts.append("(stand-in: no LLM is reachable here, so this is scaffolding talking, not a model.)")
        out["thought"] = f"{f['user']} spoke. I'll answer plainly and keep what he asked me to keep."
        out["actions"].insert(0, {"type": "reply", "text": " ".join(parts)})
        return out


class OllamaBackend(OpenAICompatBackend):
    """Ollama's native /api/chat — used automatically when the server is Ollama.
    Why: Gemma 4 on Ollama *thinks* before answering unless told not to (Brandon's own gemma-avatar fork
    passes --responses_api_reasoning_effort none for exactly this reason). Thinking can eat the whole
    token budget and return an empty answer, or run until the timeout. Native API gives us think:false,
    repeat_penalty, num_predict and keep_alive on every call, with no JSON grammar to loop in."""
    is_standin = False
    last_meta: dict = {}

    def __init__(self, *a, num_ctx: int = 8192, **kw):
        super().__init__(*a, **kw)
        self.num_ctx = num_ctx
        self.name = f"{self.model} @ {self._native_base()} (ollama, think off)"
        self._think_supported = True

    def _chat(self, payload: dict) -> dict:
        req = urllib.request.Request(self._native_base() + "/api/chat", data=json.dumps(payload).encode("utf-8"),
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def complete(self, system: str, user: str, moment: dict, *, temperature: float = 0.7, retry: bool = False) -> str:
        payload = {
            "model": self.model,
            "stream": False,
            "keep_alive": self.keep_alive,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "options": {
                "num_ctx": self.num_ctx,
                "temperature": 0.5 if retry else temperature,
                "num_predict": self.max_tokens,
                "repeat_penalty": 1.3 if retry else 1.15,
                "frequency_penalty": min(2.0, self.frequency_penalty + (0.5 if retry else 0.0)),
                "presence_penalty": min(2.0, self.presence_penalty + (0.3 if retry else 0.0)),
            },
        }
        if self._think_supported:
            payload["think"] = False
        try:
            data = self._chat(payload)
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", "replace")[:300]
            except Exception:
                pass
            if e.code == 400 and "think" in body.lower() and self._think_supported:
                self._think_supported = False          # older Ollama / model without the switch
                payload.pop("think", None)
                data = self._chat(payload)
            else:
                raise
        msg = data.get("message", {}) or {}
        content = msg.get("content") or ""
        self.last_meta = {
            "done_reason": data.get("done_reason"),
            "eval_count": data.get("eval_count"),
            "prompt_tokens": data.get("prompt_eval_count"),
            "num_ctx": self.num_ctx,
            "thinking_chars": len(msg.get("thinking") or ""),
            "load_s": round((data.get("load_duration") or 0) / 1e9, 1),
            "total_s": round((data.get("total_duration") or 0) / 1e9, 1),
        }
        return content

    def keep_warm_async(self) -> None:   # keep_alive rides on every request; nothing extra needed
        pass


def _is_ollama(base_url: str, timeout_s: float = 3.0) -> bool:
    nb = base_url[:-3] if base_url.rstrip("/").endswith("/v1") else base_url
    try:
        with urllib.request.urlopen(nb.rstrip("/") + "/api/tags", timeout=timeout_s) as resp:
            return resp.status == 200
    except Exception:
        return False


def _h(seconds: float) -> str:
    from .clock import Clock
    return Clock.humanize(seconds)


def make_backend(cfg) -> Backend:
    mode = (cfg.backend or "auto").lower()
    if mode == "standin":
        return StandInBackend()
    llm = OpenAICompatBackend(cfg.llm_base_url, cfg.llm_model, cfg.llm_api_key, cfg.llm_timeout_s,
                              cfg.llm_max_tokens, cfg.llm_frequency_penalty, cfg.llm_presence_penalty, cfg.llm_keep_alive)
    if mode == "openai":
        llm.resolve_model()
        llm.prewarm_async()
        return llm
    if llm.reachable():
        if _is_ollama(cfg.llm_base_url):
            llm = OllamaBackend(cfg.llm_base_url, cfg.llm_model, cfg.llm_api_key, cfg.llm_timeout_s,
                                cfg.llm_max_tokens, cfg.llm_frequency_penalty, cfg.llm_presence_penalty, cfg.llm_keep_alive,
                                num_ctx=cfg.llm_num_ctx)
        llm.resolve_model()
        llm.prewarm_async()
        return llm
    return StandInBackend()
