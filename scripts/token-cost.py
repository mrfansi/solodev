#!/usr/bin/env python3
"""What a session processed, read from Claude Code's own transcripts.

    python3 scripts/token-cost.py            # this project's newest session
    python3 scripts/token-cost.py --all      # every session, oldest first
    python3 scripts/token-cost.py <id>       # one session, full or 8-char prefix
    python3 scripts/token-cost.py --agents   # every subagent ever spawned, by type
    python3 scripts/token-cost.py --mark     # "this run starts here", at its start
    python3 scripts/token-cost.py --selfcheck  # assert the accounting still holds

Why this exists: for eight runs the loop reported the size of the files it reads at
startup and called that its cost, without ever measuring the whole it was a part of.

    context processed = SUM over turns of (prompt size at that turn)

Every turn re-reads the accumulated context, so a token admitted to the main context
is not paid once — it is re-read by every turn after it. That is the shape of the
thing. The magnitude needs care, and two corrections are baked in here because the
first draft of this script got both wrong:

**Turns are deduplicated by message id.** Claude Code writes one JSONL line per
content block and repeats the same `usage` object on each, so a six-block message
looks like six turns carrying six copies of one context read. Counting lines inflated
this project's sessions by 1.68x to 3.24x — and unevenly, so it did not cancel out in
any comparison.

**Cache reads are not priced like fresh input.** Around 90% of the prompt tokens
below are `cache_read`, billed at roughly a tenth of input; cache writes cost about a
quarter more. So the raw token sum is a measure of *volume*, not of money, and the
two are not a fixed multiple of each other — the ratio across this project's sessions
ranges 3.6x to 6.3x. Both are printed. Neither is called "cost" alone.

**Subagents are counted, not guessed.** Their transcripts are on disk beside the
parent, under `<session-id>/subagents/`. Their context is their own and never enters
the caller's, but it is billed, and on this project it runs 20-35% of the parent —
not the ~1% you get by mistaking the result payload for the work.

Weights are the published input-relative multipliers, named here so nobody reads the
weighted figure as a currency: it is input-equivalent tokens, nothing more.
"""
import glob
import json
import os
import string
import sys

W_INPUT, W_CACHE_WRITE, W_CACHE_READ, W_OUTPUT = 1.0, 1.25, 0.1, 5.0

SAFE = set(string.ascii_letters + string.digits)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Claude Code's per-project directory: the absolute path with every character
# outside [A-Za-z0-9] replaced by a dash. Consecutive separators are not collapsed.
SLUG = "".join(c if c in SAFE else "-" for c in ROOT)
TRANSCRIPTS = os.path.expanduser(f"~/.claude/projects/{SLUG}")


def read(path: str) -> dict:
    """One entry per assistant message, deduplicated by message id.

    A message with no prompt tokens is not a turn: Claude Code writes zero-token
    `<synthetic>` stubs for things like a rate-limit notice, and counting those
    would inflate the turn count the same way the per-block duplicates did.
    """
    seen: dict[str, int] = {}   # message id -> the output figure counted so far
    curve: list[int] = []
    fresh = write = cached = out = agents = orphans = 0
    for line in open(path, encoding="utf-8", errors="replace"):
        try:
            entry = json.loads(line)
        except ValueError:
            continue  # a truncated final line while the session is still live
        message = entry.get("message") or {}
        for block in message.get("content") or []:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                if block.get("name") == "Agent":
                    agents += 1
        usage = message.get("usage")
        if not isinstance(usage, dict):
            continue
        mid = message.get("id")
        # No id means no way to tell a repeat from a real turn, so it is dropped —
        # and counted, because a silently discarded number is how this script was
        # wrong the first time. None occur in practice; the footnote proves it.
        if not mid:
            orphans += 1
            continue
        got = usage.get("output_tokens") or 0
        if mid in seen:
            # The three input fields repeat identically, but `output_tokens` grows as
            # the message streams: early blocks carry a partial count, the last block
            # the total. Keeping the first copy undercounted output ~16x, and output
            # is the heaviest-weighted class. Take the largest and bank the delta.
            if got > seen[mid]:
                out += got - seen[mid]
                seen[mid] = got
            continue
        seen[mid] = got
        out += got
        i = usage.get("input_tokens") or 0
        w = usage.get("cache_creation_input_tokens") or 0
        r = usage.get("cache_read_input_tokens") or 0
        fresh += i
        write += w
        cached += r
        if i + w + r:
            curve.append(i + w + r)
    return {
        "id": os.path.basename(path).removesuffix(".jsonl"),
        "curve": curve,
        "fresh": fresh,
        "write": write,
        "cached": cached,
        "output": out,
        "spawned": agents,
        "orphans": orphans,
    }


MARK = os.path.join(ROOT, "specs", ".cost-mark")


def mark_write(s: dict, kid_weighted: int, nkids: int) -> bool:
    """Record where a run starts, so its own cost can be told from the session's.

    Several runs share one session, and a session's total is the sum of all of them.
    Without a starting point there is no arithmetic that recovers one run's share —
    the figure is simply the wrong quantity, however carefully it is computed.
    """
    try:
        os.makedirs(os.path.dirname(MARK), exist_ok=True)
        with open(MARK, "w", encoding="utf-8") as fh:
            json.dump({"session": s["id"], "turns": len(s["curve"]),
                       "weighted": weighted(s), "kids": kid_weighted,
                       "nkids": nkids}, fh)
    except OSError as e:
        print(f"Could not write the mark at {MARK}: {e}", file=sys.stderr)
        return False
    return True


def mark_read(session_id: str) -> "dict | None":   # quoted: 3.9 evaluates annotations
    """The mark, or None — including when it belongs to a different session.

    A mark from another session would subtract one transcript's total from another's,
    which is not a smaller number, it is a meaningless one. Silence there would be the
    worst outcome: a plausible figure with nothing behind it.
    """
    try:
        with open(MARK, encoding="utf-8") as fh:
            m = json.load(fh)
    except (OSError, ValueError):
        return None
    if not isinstance(m, dict) or m.get("session") != session_id:
        return None
    keys = ("turns", "weighted", "kids", "nkids")
    return m if all(isinstance(m.get(k), int) for k in keys) else None


def weighted(s: dict) -> int:
    return int(s["fresh"] * W_INPUT + s["write"] * W_CACHE_WRITE
               + s["cached"] * W_CACHE_READ + s["output"] * W_OUTPUT)


def subagents(session_id: str) -> list[dict]:
    return [read(p) for p in
            sorted(glob.glob(f"{TRANSCRIPTS}/{session_id}/subagents/*.jsonl"))]


def by_agent_type() -> None:
    """Total bill per agent type, across every session.

    Totals, never averages. Deciding whether a check is worth keeping is a question
    about the bill it removes, and a per-unit average cannot answer it: drop the
    dearest item and the bill falls while the average rises. That mistake has been
    made here four times, and once nearly became a binding rule.
    """
    totals: dict[str, dict] = {}
    skipped = 0
    for meta in glob.glob(f"{TRANSCRIPTS}/*/subagents/*.meta.json"):
        try:
            kind = json.load(open(meta, encoding="utf-8")).get("agentType") or "unknown"
        except (ValueError, OSError):
            skipped += 1
            continue
        path = meta[: -len(".meta.json")] + ".jsonl"
        if not os.path.exists(path):
            skipped += 1
            continue
        s = read(path)
        d = totals.setdefault(kind, {"n": 0, "turns": 0, "ie": 0})
        d["n"] += 1
        d["turns"] += len(s["curve"])
        d["ie"] += weighted(s)
    if not totals:
        print("No subagent transcripts. Either none were spawned, or this project has "
              "not run one since Claude Code started recording them.")
        return
    grand = sum(d["ie"] for d in totals.values()) or 1
    print(f"  {'agent type':<28} {'spawns':>6} {'turns':>6} {'input-equiv':>13}  share")
    for kind, d in sorted(totals.items(), key=lambda kv: -kv[1]["ie"]):
        print(f"  {kind:<28} {d['n']:>6} {d['turns']:>6} {d['ie']:>13,}"
              f"  {d['ie'] * 100 // grand:>3}%")
    print(f"  {'TOTAL':<28} {sum(d['n'] for d in totals.values()):>6} "
          f"{sum(d['turns'] for d in totals.values()):>6} {grand:>13,}  100%")
    if skipped:
        print(f"\n  {skipped} subagent record(s) unreadable or missing their transcript, "
              "excluded from every figure above")
    print("\n  Totals, not averages — see the docstring. Before cutting any of these,"
          "\n  list what it has actually caught.")


def report(s: dict, verbose: bool) -> None:
    curve, turns = s["curve"], len(s["curve"])
    if not turns:
        print(f"{s['id'][:8]}  no billed turns recorded")
        return
    kids = subagents(s["id"])
    volume = s["fresh"] + s["write"] + s["cached"]
    kid_volume = sum(k["fresh"] + k["write"] + k["cached"] for k in kids)
    kid_weighted = sum(weighted(k) for k in kids)

    print(f"session {s['id'][:8]}   {turns} turns   {len(kids)} subagent transcripts"
          f"   ({s['spawned']} Agent calls seen in the parent)")
    print(f"  prompt tokens     {volume:>13,}   "
          f"fresh {s['fresh']:,} · cache-write {s['write']:,} · cache-read {s['cached']:,}")
    print(f"  output            {s['output']:>13,}")
    print(f"  input-equivalent  {weighted(s):>13,}   "
          f"(x{W_INPUT:g}/{W_CACHE_WRITE:g}/{W_CACHE_READ:g} in, x{W_OUTPUT:g} out)")
    if kids:
        pct = kid_volume * 100 // volume if volume else 0
        print(f"  subagents         {kid_volume:>13,}   {pct}% of this session's prompt "
              f"tokens, in their own contexts; {kid_weighted:,} input-equivalent")
    if verbose:
        print(f"\n  context grew {curve[0]:,} -> {max(curve):,} across {turns} turns")
        step = max(1, (turns - 1) // 4) if turns > 1 else 1
        # ...and always the last one: the header quotes its value, so a table that
        # stops short of it reads as a contradiction.
        for i in sorted(set(range(0, turns, step)) | {turns - 1}):
            print(f"    turn {i + 1:>4}  {curve[i]:>9,}")
        print(f"\n  mean context per turn: {volume // turns:,}"
              "   <- what one more turn costs, and what one more"
              "\n"
              "                            early token is re-billed by")
        for k in sorted(kids, key=lambda k: -(k["fresh"] + k["write"] + k["cached"])):
            kv = k["fresh"] + k["write"] + k["cached"]
            print(f"    subagent {k['id'][-8:]}  {len(k['curve']):>3} turns  {kv:>12,}")
    if s["orphans"]:
        print(f"  dropped           {s['orphans']:>13,} messages carried usage but no id "
              "and could not be deduplicated — excluded from every figure above")
    field = (f"cost {weighted(s) // 1000}k input-equiv "
             f"(+{kid_weighted // 1000}k subagents) / {turns} turns / {len(kids)} subagents")
    m = mark_read(s["id"])
    if m is not None and (m["turns"] > turns or m["weighted"] > weighted(s)
                          or m["kids"] > kid_weighted or m["nkids"] > len(kids)):
        # Ahead of the session it claims to be inside: the transcript was replaced,
        # or the file was edited. Subtracting would print a negative cost, which is
        # not a smaller number but a false one — and a run would copy it out.
        print("\n  The mark is ahead of this session — stale, or edited. Ignored.")
        print("  Re-run `--mark` to set a fresh one.")
        m = None
    if m is None:
        print(f"\n  Run Log field:  {field}")
        print("    this is the SESSION, which may hold several runs. Set --mark at")
        print("    the run's start and this line reports the run instead.")
        return
    print(f"\n  Run Log field:  cost {(weighted(s) - m['weighted']) // 1000}k input-equiv "
          f"(+{(kid_weighted - m['kids']) // 1000}k subagents) / {turns - m['turns']} turns "
          f"/ {len(kids) - m['nkids']} subagents")
    # Deliberately NOT the same shape as the line above: a reader scanning for the
    # figure to copy — or a `grep cost | tail -1` — must not be able to land on the
    # session total by accident.
    print(f"    this run, from the mark at turn {m['turns']}. Session so far: "
          f"{weighted(s) // 1000}k over {turns} turns.")


def selfcheck() -> int:
    """The smallest thing that fails if the accounting breaks. `--selfcheck`."""
    import re
    import tempfile
    msg = lambda mid, out, blocks: json.dumps({"message": {
        "id": mid, "content": [{"type": "text"}] * blocks,
        "usage": {"input_tokens": 1, "cache_creation_input_tokens": 100,
                  "cache_read_input_tokens": 1000, "output_tokens": out}}})
    with tempfile.TemporaryDirectory() as d:
        f = os.path.join(d, "t.jsonl")
        # one message streamed over three blocks: output grows, the prompt repeats
        with open(f, "w") as fh:
            fh.write(msg("a", 2, 1) + "\n" + msg("a", 2, 1) + "\n" + msg("a", 500, 1) + "\n")
            fh.write(msg("b", 7, 1) + "\n")
            fh.write('{"message": {"content": [], "usage": {"input_tokens": 5}}}\n')
            fh.write("{ truncated\n")
        s = read(f)
    assert len(s["curve"]) == 2, f"turns {len(s['curve'])}, want 2 — dedup by id"
    assert s["output"] == 507, f"output {s['output']}, want 507 — take the LAST copy"
    assert s["cached"] == 2000, f"cached {s['cached']}, want 2000 — prompt counted once"
    assert s["orphans"] == 1, f"orphans {s['orphans']}, want 1 — no id, dropped, counted"
    assert weighted(s) == int(1 * 2 + 100 * 1.25 * 2 + 1000 * 0.1 * 2 + 507 * 5)

    # The mark: a delta is only worth printing if it is arithmetic, not plumbing.
    # The expected numbers below are computed here, by hand, from the fixture — not
    # read back from the thing under test, which would assert only that it agrees
    # with itself.
    global MARK, TRANSCRIPTS
    keep, keep_t = MARK, TRANSCRIPTS
    try:
        with tempfile.TemporaryDirectory() as d:
            MARK = os.path.join(d, "specs", ".cost-mark")
            # Two subagent transcripts on disk, so the printed line's subagent term is
            # a real subtraction rather than 0 - 0. Without them a dropped subtraction
            # there is invisible, which is how the first version of this check passed
            # a mutant that removed it.
            TRANSCRIPTS = os.path.join(d, "t")
            kid_dir = os.path.join(TRANSCRIPTS, "S", "subagents")
            os.makedirs(kid_dir)
            for n in ("k1", "k2"):     # 1_000_000 output each, x5 -> ~5_000_000 apiece
                with open(os.path.join(kid_dir, n + ".jsonl"), "w") as fh:
                    fh.write(msg(n, 1_000_000, 1) + "\n")
            # Figures are in the millions on purpose: the printed line divides by 1000,
            # so a fixture in the hundreds floors every variant to "0k" and a dropped
            # subtraction is invisible. That mistake was made here once.
            early = {"id": "S", "curve": [1, 1, 1], "fresh": 1_000_000, "write": 0,
                     "cached": 0, "output": 0}          # weighted 1_000_000, 3 turns
            mark_write(early, 5_000_000, 1)
            m = mark_read("S")
            assert m is not None, "a mark just written must read back"
            assert (m["turns"], m["weighted"], m["kids"], m["nkids"]) == (3, 1_000_000, 5_000_000, 1), m
            assert mark_read("OTHER") is None, "a mark from another session must not count"

            # The printed line is what a run copies out, so that is what gets asserted
            # — an oracle over the intermediate values would have passed while the
            # subtraction was missing from the line itself.
            import contextlib, io
            later = {"id": "S", "curve": [1] * 11, "fresh": 5_000_000, "write": 0,
                     "cached": 0, "output": 0, "spawned": 0, "orphans": 0}
            def printed(fixture):
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    report(fixture, verbose=False)
                return buf.getvalue()

            # A mark claiming more turns than the session has: stale or edited. The
            # subtraction would print a negative cost, which a run would copy out.
            # Each field guards independently, so each gets its own ahead-mark: a
            # fixture ahead on turns alone lets a dropped guard on any other field
            # ride along behind it.
            for ahead in ({"turns": 99}, {"weighted": 9_000_000},
                          {"kids": 99_000_000}, {"nkids": 9}):
                mark_write({**early, "curve": [1] * 3}, 5_000_000, 1)
                with open(MARK) as fh:
                    good = json.load(fh)
                with open(MARK, "w") as fh:
                    json.dump({**good, **ahead}, fh)
                out = printed(later)
                assert "ahead of this session" in out, f"ahead on {ahead} must be refused, got:\n{out}"
            field_line = out.split("Run Log field:")[1].split("\n")[0]
            assert not re.search(r"-\d", field_line), \
                f"no negative figure may reach the line, got: {field_line!r}"
            mark_write({**early, "curve": [1] * 3}, 5_000_000, 1)   # 3 turns, 1 of 2 kids
            out = printed(later)
            assert "this run, from the mark at turn 3" in out, f"the delta must be labelled, got:\n{out}"
            # by hand: 5_000_000 - 1_000_000 = 4_000_000 -> 4000k; 11-3 = 8 turns;
            # 2 subagent transcripts on disk minus the 1 the mark recorded = 1.
            # subagents on disk are ~10_000_452 weighted; the mark banked 5_000_000,
            # so the run's share is ~5000k against the session's ~10000k.
            assert "cost 4000k input-equiv (+5000k subagents)" in out, f"weighted deltas must reach the line, got:\n{out}"
            assert "/ 8 turns / 1 subagents" in out, f"turns and subagent deltas must both reach the line, got:\n{out}"
            assert "Session so far: 5000k over 11 turns" in out, f"session must sit beside it, got:\n{out}"
            assert out.count("input-equiv (+") == 1, \
                f"only the run's line may carry the copy-paste shape, got:\n{out}"

            # E1: a mark EQUAL to the session is a real state — a run marked and then
            # measured before doing anything. `>=` in the ahead-check would reject it.
            mark_write({**later, "curve": [1] * 11}, 10_000_452, 2)
            out = printed(later)
            assert "this run, from the mark at turn 11" in out, \
                f"a mark equal to the session is not ahead of it, got:\n{out}"
            assert "/ 0 turns / 0 subagents" in out, f"an equal mark is a zero-cost run, got:\n{out}"

            # E2: a delta that is not a round multiple of 1000, so floor and round
            # disagree. 4_999_999 - 1_000_000 = 3_999_999 -> 3999k floored, 4000k rounded.
            mark_write(early, 5_000_000, 1)
            odd = {**later, "fresh": 4_999_999}
            out = printed(odd)
            assert "cost 3999k input-equiv" in out, f"the figure floors, never rounds, got:\n{out}"

            # E4: two session ids sharing an 8-char prefix. This file treats a prefix as
            # an identifier elsewhere (display, --mark lookup), so comparing on one here
            # is a plausible mistake — and it would attribute another run's mark.
            with open(MARK, "w") as fh:
                json.dump({"session": "abcdef12-one", "turns": 1,
                           "weighted": 1, "kids": 0, "nkids": 0}, fh)
            assert mark_read("abcdef12-two") is None, \
                "a shared id prefix is not the same session"

            # E5: a session whose weight is dominated by cache and output rather than
            # fresh input — the realistic case. Comparing the mark against `fresh`
            # instead of `weighted()` would reject a perfectly good mark.
            # session weighted = 500 + 4M*1.25 + 10M*0.1 + 1M*5 = 11_000_500, but
            # `fresh` alone is 500. The mark below sits between the two on purpose:
            # correct code accepts it, code comparing against `fresh` rejects it.
            mixed = {"id": "S", "curve": [1] * 11, "fresh": 500, "write": 4_000_000,
                     "cached": 10_000_000, "output": 1_000_000, "spawned": 0, "orphans": 0}
            assert weighted(mixed) == 11_000_500, weighted(mixed)
            mark_write({**mixed, "curve": [1] * 2, "fresh": 50_000, "write": 0,
                        "cached": 0, "output": 0}, 0, 0)
            out = printed(mixed)
            assert "ahead of this session" not in out, \
                f"a mark behind a cache-heavy session must be accepted, got:\n{out}"

            # A partly-valid mark: one good int, one string. Distinguishes all() from
            # any() in the key check — a fixture with no valid fields cannot.
            with open(MARK, "w") as fh:
                fh.write('{"session": "S", "turns": 3, "weighted": "ten", "kids": 0, "nkids": 0}')
            assert mark_read("S") is None, "a partly-valid mark must not count"
            os.remove(MARK)
            assert mark_read("S") is None, "no mark is not an error"

            MARK = os.path.join(d, "specs")      # a directory, not a file
            with contextlib.redirect_stderr(io.StringIO()):
                assert mark_write(early, 0, 0) is False, "unwritable must report, not crash"
    finally:
        MARK, TRANSCRIPTS = keep, keep_t

    print("selfcheck OK — dedup, streamed output, orphan count, weights, mark delta")
    return 0


def main() -> int:
    flags = [a for a in sys.argv[1:] if a.startswith("-")]
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    unknown = [f for f in flags if f not in ("--all", "--agents", "--selfcheck", "--mark")]
    if unknown:
        print(f"Unknown flag: {' '.join(unknown)}", file=sys.stderr)
        return 2
    if "--mark" in flags and ("--all" in flags or args or "--agents" in flags
                              or "--selfcheck" in flags):
        print("--mark records where THIS run starts, in the newest session. It takes "
              "no session argument and pairs with no other flag.", file=sys.stderr)
        return 2
    if "--selfcheck" in flags:
        return selfcheck()
    if "--agents" in flags:
        if args or "--all" in flags:
            print("--agents reports every session at once and takes no session "
                  "argument. Drop it, or drop --agents.", file=sys.stderr)
            return 2
        by_agent_type()
        return 0
    every = "--all" in flags
    found = sorted(glob.glob(f"{TRANSCRIPTS}/*.jsonl"), key=os.path.getmtime)
    if not found:
        print(f"No transcripts under {TRANSCRIPTS}", file=sys.stderr)
        print("Claude Code writes one per session; a repo it has never run in has "
              "none, which is not an error.", file=sys.stderr)
        return 1
    if args:
        found = [p for p in found if os.path.basename(p).startswith(args[0])]
        if not found:
            print(f"No session matching {args[0]!r}", file=sys.stderr)
            return 1
    elif not every:
        found = found[-1:]
    if "--mark" in flags:
        s = read(found[-1])
        kids = subagents(s["id"])
        if not mark_write(s, sum(weighted(k) for k in kids), len(kids)):
            return 1
        print(f"mark set at turn {len(s['curve'])} of session {s['id'][:8]} — "
              "a later run of this script reports the delta since here as the run,\n"
              "and the session total beside it.")
        return 0
    detail = len(found) == 1 and not every
    for i, path in enumerate(found):
        if i:
            print()
        report(read(path), verbose=detail)
    if not args and not every:
        print("\n  (newest session — if that is this one, it is still growing)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
