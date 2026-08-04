# LOOP PROTOCOL — PATCH HISTORY

> Every §4D patch this protocol has taken, oldest first. **No run reads this file at
> Phase 0.** It is the decision trail behind the rules, not a rule — the same split
> `specs/LOOP_ARCHIVE.md` makes for the backlog.
>
> Open it when you need to know *why* a rule reads the way it does, or when §4D is
> about to add an entry. Protocol: `skills/autopilot/references/PROTOCOL.md`.

## Patches

- **v1.0** — initial protocol, bootstrapped from the `dev-loop` skill.
- **v1.1** — §1 absorbed the three skill-only invariants; §3 Phase 1: stacked cadences.
- **v1.2** — §3 Phase 1: a standing feature directive outranks the cadence's
  *prohibition*, not its choice of slice (user ruling, `C-5`).
- **v1.3** — §3 Phase 8: branches are `<type>/<backlog-id>-<what-it-does>` (user
  directive).
- **v1.4** — §2: `specs/` and `docs/` never committed; §6: nothing about the loop in
  `README.md`/`CHANGELOG.md` unless the workflow tooling *is* the product. From live
  use: the plugin was contaminating the repos it ran in.
- **v1.5** — §3 Phase 8: PRs open **ready**, not draft. Opening is reversible,
  merging is not, and merging was already the user's.
- **v1.6** — ambiguity + token pass, by the user: invariant 5 scopes README to §6's
  usage test; the subagent prompt rules moved from the skill into §3 and now cover
  Phases 4/5/8 alike; Phase 6 enforces the §2 untracked-workspace rule; §4C prunes
  `LOOP_STATE.md`; §8 owns the deferred-feature guarantee; §10 S3 wording aligned
  with the `task` and `qa` skills.
- **v1.7** — the code map (`graph` skill), by the user: §2 lists `specs/graph/**`;
  Phase 0 reads `GRAPH.md` when present; Phase 3 starts the call-site inventory
  from its `Used by` edges, grep-verified; §4B refreshes touched modules' cards.
  The map is optional — no phase fails for its absence.

- **v1.8** — roll-off, by the user: §2 adds `specs/LOOP_ARCHIVE.md`; §4C replaces
  "prune the Run Log to its last 20 lines" with **move, never delete** — closed
  backlog rows and Run Log entries older than the last three go to the archive,
  which Phase 0 is told not to read. Both Phase 0 caps are now enforced by
  `scripts/validate.py` (`LOOP_STATE.md` ≤ 14000 bytes, `LOOP_LEARNINGS.md` ≤ 150
  lines). Recorded failure: the 150-line cap was prose for four runs and the file
  was over it, unnoticed; `LOOP_STATE.md` more than doubled across three runs while
  every refactor aimed at the fixed half of the read.

- **v1.9** — the S1 contradiction (`C-3`), by the user: §3 Phase 4 said S1 and S2
  findings "are fixed in this run", §10 said an S1 found mid-run means "stop, report
  it, and let the user decide". Both now scope themselves: **in-slice** S1/S2 are
  fixed by Phase 4; an **out-of-slice** S1 stops the run per §10. Recorded failure:
  run #1 acted on the §3 reading twice without noticing the other rule existed —
  found by `pr-reviewer` in run #1 Phase 8 and open for five runs.

- **v1.10** — §12 moved out, by the user (`R-1`, partial): the patch history now lives
  in `references/PROTOCOL-HISTORY.md` and §12 is a five-line pointer. §4D guardrail 5
  appends there. Recorded failure: the history had grown to 637 tokens — a tenth of
  the whole protocol — and was read at Phase 0 of every run while governing no phase
  at all. §4D itself reads it every fifth run; the other four pay for nothing.
  The rest of `R-1` (splitting §5-§11 into a cold half) was measured and **rejected**:
  six of those eight sections are needed by every run, four of them because an
  invariant says so, so moving them relocates the tokens instead of removing them.
  See `docs/evidence/2026-08-04-r3-roll-off/07-r1-remeasure.txt`.

