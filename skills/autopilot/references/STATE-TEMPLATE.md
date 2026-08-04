# LOOP STATE

> Written by the loop every run. Source of truth for the backlog, the current task,
> metrics, and the next-iteration plan. Protocol: `specs/LOOP.md`.
> Rolls off per §4C to `specs/LOOP_ARCHIVE.md`, which Phase 0 never reads: closed
> backlog rows and Run Log entries older than the last three MOVE there, never get
> deleted. `scripts/validate.py` fails the gate if this file passes 14000 bytes.

## Detected stack

Filled in at bootstrap; update when the repo's tooling changes.

| Gate | Command |
|---|---|
| Format | `<filled at bootstrap>` |
| Lint | `<filled at bootstrap>` |
| Test | `<filled at bootstrap>` |
| Build | `<filled at bootstrap, or "none">` |

Baseline at bootstrap: `<count>` tests green.

Phase 4 verification method for this product:
`<CLI / TUI under tmux / web screenshots / runnable example / API calls>`

---

## Current state

> Updated every run: where the product stands, what just landed.

_(no runs yet)_

---

## Scored backlog

Score = (Value 1–5 × Frequency 1–5) ÷ Size 1–5. Ids are type-prefixed per §10:
`F-` feature · `B-` bug · `E-` enhancement · `R-` refactor · `C-` chore.
Bugs carry a severity (S1/S2/S3); S1 overrides the cadence.

Strike a finished task, then MOVE the row to `specs/LOOP_ARCHIVE.md` — deleting it
loses the decision trail, and leaving it here is what made this file the second-
largest thing the loop reads.
The Notes column always carries the **origin**: user report with its date, or
"found during run #N".

| Id | Task | V | F | S | Score | Notes (severity + origin) |
|---|---|---|---|---|---|---|
| — | _(filled at bootstrap)_ | | | | | |

---

## Current task

**Run #N — <task title>**

Score: `<n>` (V`<n>` x F`<n>` / S`<n>`).
Cadence: run #N `<multiple of three? of five?>` → `<feature allowed / audit required>`.

Binding `LOOP_LEARNINGS.md` rules for this task: `<list them>`.

### Call-site inventory (Phase 3 — filled in before editing)

| File | Location | Change |
|---|---|---|
| | | |

### Definition of Done for this iteration (Phase 1 — before any code)

- [ ] `<a criterion someone else could verify without asking>`
- [ ] `<...>`

---

## Next iteration plan (written by Run #N, for Run #N+1)

```
Task        : <id + title>
Score       : <n>  (V<n> x F<n> / S<n>)
Why this    : <tie it to a gap, the Run Log, or a user request>
Cadence     : run #<N+1> → <feature allowed / audit required / meta-review required>
Prereqs     : <what must exist first, or "none">
Slice       : <the concrete boundary that counts as complete for that run>
Risk        : <what could blow up the scope>
```

---

## Run Log

The three most recent runs, newest first. One line per run and **no prose** — notes
and older entries live in `specs/LOOP_ARCHIVE.md`. Format:
`Run #N | task | rubric-iterations | score initial→final | rework? (cause) | gate failures | cost <n>k tok / <n> turns / <n> subagents`

```
```
