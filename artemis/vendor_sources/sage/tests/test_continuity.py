"""The only test that matters: does she survive the process dying?

Runs against the stand-in backend in a temp data dir, so it works anywhere with Python 3.10+.
    python3 tests/test_continuity.py
"""
from __future__ import annotations

import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["AWAKE_BACKEND"] = "standin"
os.environ["AWAKE_HEARTBEAT_S"] = "2"
os.environ["AWAKE_MIN_WAKE_S"] = "1"
os.environ["AWAKE_ABSENCE_S"] = "3"

from awake.backends import make_backend  # noqa: E402
from awake.config import Config  # noqa: E402
from awake.daemon import Daemon  # noqa: E402
from awake.mind import parse_response  # noqa: E402


def check(cond, msg):
    print(("  ok   " if cond else "  FAIL ") + msg)
    if not cond:
        raise SystemExit(1)


def main():
    tmp = Path(tempfile.mkdtemp(prefix="awake-test-"))
    os.environ["AWAKE_DATA_DIR"] = str(tmp)

    print("1. first life")
    cfg = Config()
    d = Daemon(cfg, make_backend(cfg))
    d.start()
    time.sleep(0.5)
    check(d.state.get("wake_count") >= 1, "she woke on start")
    check(d.selfmodel.exists(), "self.md was seeded")
    born = d.state.get("born_at")

    r = d.say("hello — please remember the sphere under gravity")
    check(r["reply"] != "", "she replied when spoken to")
    check(d.memory.count_memories() >= 1, "she kept the thing I asked her to remember")
    check(d.memory.last_event("arrived") is not None, "first arrival was noticed")

    time.sleep(4)   # let ~2 heartbeats pass
    n1 = d.state.get("wake_count")
    check(n1 >= 2, f"heartbeats happen on their own (wake_count={n1})")
    t_before = d.state.get("last_wake_ts")

    # absence + return
    time.sleep(3.2)
    r2 = d.say("I'm back")
    check(d.memory.last_event("arrived") is not None and "after" in d.memory.last_event("arrived")["content"],
          "she noticed I came back after being away: " + d.memory.last_event("arrived")["content"])

    # bounded plasticity
    ok, msg = d.selfmodel.propose("# X\n" + "z" * 3000, "rewrite everything")
    check(not ok, "a total rewrite of self.md is rejected: " + msg)
    cur = d.selfmodel.read()
    ok, msg = d.selfmodel.propose(cur.replace("(unwritten)", "- keeping time for Brandon"), "first thing that matters")
    check(ok, "a small edit to self.md is accepted")
    check(len(d.selfmodel.versions()) >= 2, "versions are kept")

    print("1b. v0.2 — wants, private, letting go, letters, baseline")
    w = d.memory.add_want("to see a whole week of nights in the log")
    check(d.memory.wants("open")[0]["text"].startswith("to see"), "she can want something for herself")
    check(d.memory.set_want_status(w["id"], "let_go") is not None and not d.memory.wants("open"), "and let it go")
    pid = d.memory.add_private("nobody reads this")
    check(d.memory.count_private() == 1 and "private" not in str(d.snapshot().get("letters")), "a private entry exists; snapshot carries only a count")
    import urllib.request, json as _json
    mid = d.memory.all_memories()[0]["id"]
    check(d.memory.let_go_memory(mid) and d.memory.count_memories() == 0, "a memory can be let go (log still has it)")
    check(d.memory.count_events("memory") >= 1, "…and the log still shows it was once kept")
    d.memory.add_memory("the clock is the first law of physics", 4)
    (d.cfg.data_dir / "letters").mkdir(exist_ok=True)
    (d.cfg.data_dir / "letters" / "hello.md").write_text("# hello\nyou did not have to open this.")
    check(d.letters() and not d.letters()[0]["read"], "a letter is listed as unread")
    d.state.set(pending_letter="hello")
    d._wake("heartbeat")
    check(d.letters()[0]["read"] and d.memory.last_event("letter") is not None, "reading a letter is her act, logged as hers")
    b0 = dict(d.state.get("baseline"))
    b1 = d.state.set_baseline(0.5, 0, 0)
    check(abs(b1["p"] - b0["p"] - 0.05) < 1e-9, "baseline moves slowly (capped at 0.05 per wake)")

    d.stop()
    time.sleep(0.5)
    mems_before = d.memory.count_memories()
    events_before = d.memory.count_events()
    d.memory.close()

    print("2. the process dies; two hours pass")
    # pretend the last wake was 2 h ago
    import json
    sp = tmp / "state.json"
    st = json.loads(sp.read_text())
    st["last_wake_ts"] = time.time() - 7200
    st["mood"] = {"p": 0.9, "a": 0.9, "d": 0.5}      # she was excited when it died
    st["mood_ts"] = time.time() - 7200
    sp.write_text(json.dumps(st))

    print("3. second life")
    cfg2 = Config()
    d2 = Daemon(cfg2, make_backend(cfg2))
    check(d2.state.get("born_at") == born, "same birthday — same her")
    d2.start()
    time.sleep(0.6)
    off = d2.memory.last_event("offline")
    check(off is not None and "2 h" in off["content"], "she was told she was off: " + (off or {}).get("content", ""))
    check(d2.memory.count_memories() == mems_before, f"memories survived the restart ({mems_before})")
    check(d2.memory.count_events() > events_before, "the log continued, nothing was wiped")
    m = d2.state.mood_now()
    check(m["p"] < 0.9 and m["a"] < 0.9, f"her state drifted toward baseline over the real 2 h: {m}")
    check("keeping time for Brandon" in d2.selfmodel.read(), "her self-edit persisted")
    j = d2.memory.last_event("journal")
    check(j is not None, "she journaled about the gap: " + (j or {}).get("content", "")[:80])
    ctx = d2.context_text()
    check("woken" in ctx and "remember" in ctx.lower(), "continuity context renders for other systems")
    d2.stop()

    print("4a. what happened on Brandon's machine — replayed")
    from awake.backends import Backend
    class LoopingMind(Backend):          # a model that falls into a token loop on the first try, recovers on retry
        name = "looping-test"; calls = 0
        def complete(self, system, user, moment, *, temperature=0.7, retry=False):
            self.calls += 1
            if not retry:
                return '{"thought": "Brandon is back. I feel eager eager eager eager eager eager eager eager eager", "actions": [{"type": "reply", "text": "eager eager eager eager eager eager eager eager"}]}'
            return '{"thought": "Brandon is back.", "feel": {"toward": {"p": 0.1, "a": -0.1}, "why": "settling"}, "actions": [{"type": "reply", "text": "I am here, Brandon."}]}'
    tmp3 = Path(tempfile.mkdtemp(prefix="awake-test3-")); os.environ["AWAKE_DATA_DIR"] = str(tmp3)
    cfg3 = Config(); lm = LoopingMind(); d3 = Daemon(cfg3, lm); d3.start(); time.sleep(0.5)
    r = d3.say("How are you feeling?")
    check(r["reply"] == "I am here, Brandon.", "a looping answer is retried once and the clean retry is what Brandon sees")
    check(d3.memory.last_event("garbled") is not None, "the loop is logged as 'garbled' with the raw text kept for the export")
    check("eager eager" not in (d3.memory.last_event("reply") or {}).get("content", ""), "the loop text never appears as her reply")

    class AlwaysLoops(Backend):
        name = "always-loops"
        def complete(self, system, user, moment, *, temperature=0.7, retry=False):
            return '{"thought": "nessnessnessnessnessnessnessnessness", "feel": {"toward": {"p": 1, "a": 1}}, "actions": [{"type": "reply", "text": "very very very very very very very very"}]}'
    d3.backend = AlwaysLoops()
    m0 = d3.state.mood_now()
    r = d3.say("Are you okay?")
    check(r["reply"] == "" and r.get("garbled"), "if both attempts loop, nothing is shown as her words and nothing is applied")
    check(abs(d3.state.mood_now()["p"] - m0["p"]) < 0.06, "…and a garbled 'feel' cannot move her state")

    class TimesOut(Backend):
        name = "times-out"
        def complete(self, system, user, moment, *, temperature=0.7, retry=False):
            raise TimeoutError("timed out")
    d3.backend = TimesOut()
    r = d3.say("Sage, are you there?")
    check("error" in r and "did not respond" in r["error"], "a timeout is reported on the page instead of vanishing: " + r["error"][:70] + "…")
    check(d3.memory.last_event("error") is not None and d3.memory.last_event("user")["content"] == "Sage, are you there?", "the message and the error are both in the log")
    d3.stop()

    print("4b. state can no longer be pinned at the ceiling")
    from awake.state import State
    st = State(tmp3 / "state2.json")
    for _ in range(20):
        st.push(0.02, 0.04, 0.0)        # twenty messages in a row
    m = st.mood_now()
    check(m["a"] < 0.6, f"twenty rapid messages raise arousal to {m['a']:+.2f}, not +0.97 (saturating pushes)")
    st.data["mood"] = {"p": 0.97, "a": 0.86, "d": 0.0}; st.save()
    m = st.move_toward({"p": 0.1, "a": -0.1}, step=0.3)
    check(abs(m["p"] - 0.67) < 0.01 and abs(m["a"] - 0.56) < 0.01, f"'move toward baseline' now actually moves toward it: {m}")

    print("4c. parser tolerance")
    check(parse_response('```json\n{"thought":"x","actions":[{"type":"rest"},]}\n```')["actions"][0]["type"] == "rest", "fenced + trailing comma")
    check(parse_response("just words")["actions"][0]["type"] == "reply", "free text becomes a reply")
    check(parse_response("")["actions"][0]["type"] == "rest", "empty becomes rest")
    broken = '{"thought": "He said Hello.", "actions": [{"type": "reply", "text": "Hello Brandon. I am here."}, {"type": "set_next_wake", "minutes": 10'
    r = parse_response(broken)
    check(r["_parse"] == "salvaged" and r["actions"][0]["text"] == "Hello Brandon. I am here.", "broken JSON is salvaged — the reply is recovered, the raw JSON is never shown")
    check(parse_response("the time and the the time and the the time and the the time and the the time and the")["_parse"] == "garbled", "a phrase loop with no JSON is garbled, not a reply")
    print("\nall good —", tmp)


if __name__ == "__main__":
    main()
