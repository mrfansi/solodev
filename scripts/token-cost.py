#!/usr/bin/env python3
"""What a session processed, read from Claude Code's own transcripts.

    python3 scripts/token-cost.py            # this project's newest session
    python3 scripts/token-cost.py --all      # every session, oldest first
    python3 scripts/token-cost.py <id>       # one session, full or 8-char prefix

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
    seen: set[str] = set()
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
        if mid in seen:
            continue
        seen.add(mid)
        i = usage.get("input_tokens") or 0
        w = usage.get("cache_creation_input_tokens") or 0
        r = usage.get("cache_read_input_tokens") or 0
        fresh += i
        write += w
        cached += r
        out += usage.get("output_tokens") or 0
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


def weighted(s: dict) -> int:
    return int(s["fresh"] * W_INPUT + s["write"] * W_CACHE_WRITE
               + s["cached"] * W_CACHE_READ + s["output"] * W_OUTPUT)


def subagents(session_id: str) -> list[dict]:
    return [read(p) for p in
            sorted(glob.glob(f"{TRANSCRIPTS}/{session_id}/subagents/*.jsonl"))]


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
    print(f"\n  Run Log field:  cost {weighted(s) // 1000}k input-equiv "
          f"(+{kid_weighted // 1000}k subagents) / {turns} turns / {len(kids)} subagents")


def main() -> int:
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    unknown = [f for f in flags if f != "--all"]
    if unknown:
        print(f"Unknown flag: {' '.join(unknown)}", file=sys.stderr)
        return 2
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
