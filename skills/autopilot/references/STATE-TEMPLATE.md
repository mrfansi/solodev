# LOOP STATE

> Written by the loop every run. Source of truth for the backlog, the current task,
> metrics, and the next-iteration plan. Protocol: `specs/LOOP.md`.
> Pruned per §4C — Run Log caps at 20 lines; this file must not grow without bound.

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

Strike through finished tasks; do not delete them — deleting loses the decision trail.
The Notes column always carries the **origin**: user report with its date, or
"found during run #N".

| Id | Task | V | F | S | Score | Notes (severity + origin) |
|---|---|---|---|---|---|---|
| — | _(filled at bootstrap)_ | | | | | |

---

## Current task

**Run #N — <task title>**

Score: `<n>` (Value `<n>` × Frequency `<n>` ÷ Size `<n>`).
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
Score       : <n>  (Value <n> × Frequency <n> ÷ Size <n>)
Why this    : <tie it to a gap, the Run Log, or a user request>
Cadence     : run #<N+1> → <feature allowed / audit required / meta-review required>
Prereqs     : <what must exist first, or "none">
Slice       : <the concrete boundary that counts as complete for that run>
Risk        : <what could blow up the scope>
```

---

## Run Log

One line per run. Format:
`Run #N | task | rubric-iterations | score initial→final | rework? (cause) | gate failures`

```
```
