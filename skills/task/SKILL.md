---
name: task
description: File a feature, bug, enhancement, refactor, or chore into the loop backlog without starting a run — classified, scored, queued. Use when the user reports a bug, requests a feature, or says to remember or file something for later.
---

# task

`/solodev:task <what needs doing>`

Files work into `specs/LOOP_STATE.md` so it survives the session. **This does not
start a run** — it puts something in the queue and tells you where it landed.

Use it when something surfaces at the wrong moment: a bug spotted while doing
something else, an idea worth keeping, a request that should not derail today's work.

## 1. Where does it go?

```bash
test -f specs/LOOP_STATE.md
```

| State | What to do |
|---|---|
| Present | Append to the scored backlog |
| Missing, but it is a git repo | The loop has not been bootstrapped. File it in `specs/LOOP_STATE.md` under a `## Scored backlog` heading, creating the file, so `/solodev:autopilot` picks it up on its first run |
| Not a repo | Say so and ask where it should live rather than writing into an arbitrary directory |

## 2. Classify

Read the request; do not ask the user to categorise it themselves.

| Type | Id | Signal |
|---|---|---|
| Feature | `F-<n>` | Something the product cannot do yet |
| Bug | `B-<n>` | Something behaves other than it should |
| Enhancement | `E-<n>` | Something works, but poorly or slowly |
| Refactor | `R-<n>` | Internal structure, no behaviour change |
| Chore | `C-<n>` | Tooling, dependencies, CI, docs upkeep |

Next id continues the existing sequence per type — never reuse a struck-through id.

**A bug needs a severity**, because it changes when the work runs:

| Sev | Meaning |
|---|---|
| **S1** | Data loss, security hole, or a primary flow that cannot be completed at all |
| **S2** | Primary flow broken but a workaround exists |
| **S3** | Cosmetic, or an edge case unlikely in practice |

Infer severity from what was described. Where the description is genuinely ambiguous
between S1 and S2 — the difference decides whether the next run drops everything —
ask. Otherwise decide, and state the reasoning in the note so it can be corrected.

## 3. Score

```
Score = (Value 1–5 × Frequency 1–5) ÷ Size 1–5
```

- **Value**: how much it matters to someone using the product
- **Frequency**: how often that person meets it
- **Size**: how much work it is — 1 is a line, 5 is a week

Bugs get `+2` at S2. S1 does not need a score: it overrides the cadence outright.

Show your reasoning for each number in one line. A score with no reasoning cannot be
argued with, and an unarguable score is a guess with a decimal point.

## 4. Write the row

```
| B-7 | Ledger export writes an empty file when the period has no rows | 5 | 3 | 1 | 15.0 | S2. From: user report 2026-08-04 |
```

The **Notes column always carries the origin**: a user report with its date, "found
during run #N verification", or "found by audit run #N". Origin is what later lets the
loop tell recurring friction from a one-off — and recurring friction earns a scoring
bonus that a one-off does not.

Write the task as an **observable outcome**, not a solution. "Ledger export writes an
empty file when the period has no rows" leaves the fix open; "add a null check to the
export function" has already decided the fix, possibly wrongly, before anyone looked.

## 5. Report where it landed

```
FILED    : B-7 — <title>
TYPE     : bug, severity S2
SCORE    : 15.0  (Value 5 × Frequency 3 ÷ Size 1)
QUEUE    : #1 of 6 — ahead of F-3 (8.0) and E-2 (6.7)
NEXT RUN : run #<N+1> is <a feature run / an audit run per cadence>, so this
           <will be picked up / waits for run #N+2>
```

Say plainly when the cadence will delay it. A backlog that silently reorders itself
teaches people to stop trusting it.

**When an S1 is filed**, say so prominently: it overrides the cadence and any inherited
plan, and the next run takes it immediately. Offer to start that run now.

## Multiple items in one invocation

When the request contains several distinct items, file them separately rather than as
one blurred row. Each gets its own id, score, and origin — a row that bundles three
things can never be finished, only partially finished.
