---
name: loop
description: Run ONE iteration of a development loop whose state lives in the repo, so it survives across sessions, and schedule the next iteration itself. Use when the user invokes /solodev:loop, asks to start or resume iterative development, or wants continuous measured iterations with a definition of done, mandatory documentation, persistent memory, and a self-improving protocol. Accepts an optional interval and an optional plan or request.
---

# loop

```
/solodev:loop [interval] [plan]
```

One invocation = **ONE full run**, Phase 0 through 10, in order, no skipping — then
schedule the next one and stop. Never chain two runs inside a single turn.

This skill works in any repository. Stack, quality-gate commands, and the way to
verify are detected from the repo in Phase 0 — never assume a language or framework.

## Arguments

| Form | Meaning |
|---|---|
| `/solodev:loop` | Run once, then reschedule at a self-chosen pace |
| `/solodev:loop 45m` | Run once, then every 45 minutes |
| `/solodev:loop 2h fix the export bug` | Every 2 hours, with a request attached |
| `/solodev:loop once add PDF export` | Run exactly once, no scheduling |
| `/solodev:loop stop` | Cancel scheduling; no run |

Parse the first token as an interval only when it matches `<n>m` / `<n>h` / `once` /
`stop`. Anything else is part of the plan — `/solodev:loop 3 bugs from testing` is a
request, not an interval.

## Scheduling the next run

At the end of a successful run, before reporting:

| Interval | Mechanism |
|---|---|
| ≤ 60 minutes | `ScheduleWakeup` with `delaySeconds`, `prompt` = the same invocation verbatim |
| > 60 minutes | `CronCreate` with a cron expression; pick an **off-peak minute**, never `0` or `30` |
| none given | `ScheduleWakeup`, choosing the delay yourself — long enough that a human could review the last run, typically 1200–1800s |
| `once` | Do not schedule |
| `stop` | `ScheduleWakeup` with `stop: true`, and `CronDelete` any job this loop created |

Pass the invocation back **verbatim** so the interval and plan survive into the next
run. **Do not schedule if the run failed its gates** — a broken run repeating on a
timer only multiplies the mess. Report the failure and let the user decide.

`ScheduleWakeup`, `CronCreate`, and `CronDelete` may be deferred rather than loaded —
fetch their schemas first (`ToolSearch`) instead of calling them blind. If they are
unavailable altogether, say scheduling is unavailable, report the run, and stop; a run
that silently fails to reschedule looks identical to one that never ran.

**Be honest about the limits:** scheduling is session-only, and cron jobs also expire
after 7 days. Say this once when scheduling starts. It costs little, because the
loop's state lives in the repo — a fresh session only needs `/solodev:loop` again to
pick up exactly where the last one stopped.

---

## First step: decide the mode

Check whether `specs/LOOP.md` exists in the current working repo.

| Condition | Mode |
|---|---|
| `specs/LOOP.md` **missing** | **BOOTSTRAP** — this is Run #1 |
| `specs/LOOP.md` **present** | **NORMAL** — read it and follow its protocol |

In NORMAL mode, **`specs/LOOP.md` in the repo is the source of truth**, not this
skill's copy. The repo protocol may already have been patched by earlier runs;
respect its version. Only fall back to this skill's template if the user explicitly
asks for a reset.

---

## BOOTSTRAP mode (Run #1)

The first run **ships no feature**. Its job is to stand up the loop machinery:

1. Copy `references/PROTOCOL.md` (from this skill's directory) → `specs/LOOP.md`.
2. Copy `references/STATE-TEMPLATE.md` → `specs/LOOP_STATE.md`.
3. Copy `references/LEARNINGS-TEMPLATE.md` → `specs/LOOP_LEARNINGS.md`, and create
   `specs/REFERENCE.md` with a title plus one line explaining it is the incremental
   cache of external API/patterns filled in during Phase 2.
4. **Detect the stack** (table below) and write the resulting quality-gate commands
   into the "Detected stack" section of `specs/LOOP_STATE.md`. Run them once as a
   baseline and record the test count.
5. **Create the mandatory documents if absent**: `README.md`, `CHANGELOG.md`
   (Keep a Changelog format, with an `## [Unreleased]` section), and a `docs/`
   directory with `docs/README.md` as its index.
6. **Build the initial scored backlog** from reading the repo plus the user's
   request, and write it to `specs/LOOP_STATE.md`.
7. Write memory as described below.
8. Commit, then open the run's draft PR via `pr-new`.
9. Write the §9 report, including the plan for the next iteration.

Run #2 is the first one to touch a feature.

### Stack detection

Look for markers in the repo root. If a `Makefile`, `justfile`, or `Taskfile.yml`
defines relevant targets, **those targets win** over this table.

| Marker | Format | Lint | Test |
|---|---|---|---|
| `Cargo.toml` | `cargo fmt --check` | `cargo clippy --all-targets --all-features -- -D warnings` | `cargo test` |
| `package.json` | `prettier --check .` or `biome check` | `eslint .` or `biome lint` | the `test` script |
| `pyproject.toml` | `ruff format --check .` | `ruff check .` | `pytest` |
| `go.mod` | `gofmt -l .` | `go vet ./...` | `go test ./...` |
| anything else | read CI in `.github/workflows/` | same | same |

Record the detected commands in `specs/LOOP_STATE.md` so later runs skip detection.

---

## NORMAL mode

1. Read `specs/LOOP.md` in full.
2. Execute Phases 0–10 in order.
3. Schedule the next run, then stop after the report.

### Work attached to the invocation

Anything attached to the invocation — a feature, a bug report, an enhancement — is
**classified and scored per §10 of the protocol before selection**, then added to the
backlog with a type-prefixed id and its origin. It does not jump the queue merely by
being the most recent thing said.

| Attached as | Handling |
|---|---|
| Feature or enhancement | Scored normally; prioritised in Phase 1 **unless** this run falls on the audit/refactor cadence. Deferred → it becomes the next run's first candidate, and the report says so. |
| Bug, severity S2/S3 | Scored with a severity bonus; competes on the same scale. |
| **Bug, severity S1** (data loss, security, primary flow impossible) | Taken immediately. **Overrides the cadence and any inherited plan.** The override is recorded in the Run Log and the report. |

This is the only sanctioned way to break cadence.

---

## Companion agents

Audits run as **separate subagents**, never inline. An audit performed by the agent
that wrote the code grades its own homework, and the protocol forbids approving in
the pass that authored the change. Four of the five cannot edit files at all, so a
finding can never be quietly fixed instead of reported.

Spawn them with the `Agent` tool:

| Phase | `subagent_type` | Edits? | When |
|---|---|---|---|
| 4 — verification | `solodev:qa-runner` | yes (evidence) | **Every run**, including refactor runs, where the matrix narrows to regression and persistence |
| 4 — verification | `solodev:bug-hunter` | no | **Only when the slice touched a trust boundary** — auth, input, data access, upload, external requests |
| 5 — quality critique | `solodev:ux-auditor` | no | **Only when the slice touched a user-facing surface** |
| 5 — quality critique | `solodev:ui-auditor` | no | Same condition; skipped together with `ux-auditor`, and the report says it skipped them and why |
| 8 — before commit | `solodev:pr-reviewer` | no | **Every run**, against the working diff |

Send the ones that share a phase in a **single message** so they run concurrently:
`qa-runner` with `bug-hunter` in Phase 4, `ux-auditor` with `ui-auditor` in Phase 5.
They are independent and there is nothing to gain by serialising them.

Implementation tiers — `fe`, `be` — and the backlog filer `task` are **skills, not
agents**: they load inline in Phase 3, because building and filing are the run's own
work, with nothing to isolate. Only the audits, which must not grade their own author,
run as subagents.

Each agent's prompt must carry: the slice under test, how to run the artifact, the
tightest condition to test first, and where to write evidence. An agent that has to
guess what it is auditing produces findings about the wrong thing.

`pr-new` runs **inline**, not as a subagent — it acts rather than judges, and there
is nothing to isolate.

Their findings are not advisory:

- `qa-runner` S1/S2 → fixed this run · S3 → backlog with origin
- `bug-hunter` Critical/High → **S1**, overrides the cadence, fixed this run
- `ux-auditor` severity 4 or `ui-auditor` blocker → **fails the rubric**, fixed this run
- `pr-reviewer` blocker/major → fixed **before** the commit

If a subagent returns nothing usable, or the agent type is unavailable because the
plugin is only partially installed, **say so in the report and run that phase
inline** — degraded but honest beats a phase silently skipped.

### One run, one branch, one PR

Each run works on its own branch and ends with a draft PR:

```
loop/run-<N>-<short-slug>
```

Branch from the default branch at the start of the run, once Phase 0 confirms a clean
tree. The PR stays a **draft** — promoting it to ready is the user's decision, as is
merging. If the repo has no remote or `gh` is unavailable, commit to the branch, say
the PR step was skipped and why, and carry on.

---

## MEMORY (always on, two layers that must not overlap)

Both layers are written every run. The split is strict so they never drift into two
diverging copies:

**Layer 1 — state files in the repo** (committed, readable by teammates):

| File | Contents |
|---|---|
| `specs/LOOP_STATE.md` | scored backlog, current task + its DoD, Run Log, detected stack, **next-iteration plan** |
| `specs/LOOP_LEARNINGS.md` | binding rules learned so far (150 lines max) |
| `specs/REFERENCE.md` | cached external API/patterns, so they are not re-read each run |
| `docs/evidence/<date>-<task>/` | Phase 4 verification evidence |

**Layer 2 — Claude Code memory** (the memory directory named in the running
session's system prompt, plus `MEMORY.md` as its index). It holds **only what is not
in the repo**:

- `project` — goals, constraints, and decisions not captured by code or git history
- `feedback` — the user's corrections and working preferences, with the reasoning
- `reference` — URLs, dashboards, tickets, external docs this loop relies on
- `user` — the user's role and preferences

**Do not** copy the backlog, Run Log, or learnings into layer 2 — they already live
in the repo, and an out-of-sync duplicate is worse than none. A single pointer line
in `MEMORY.md` aimed at `specs/LOOP_STATE.md` is enough.

In Phase 0, **read both layers** before choosing a task. This is what lets a
brand-new session continue without any prior conversation context.

---

## Invariants

The eleven invariants live in **§1 of the protocol** — `references/PROTOCOL.md` before
bootstrap, `specs/LOOP.md` afterwards. They are not repeated here: two copies of a
rule drift, and the repo's copy is the one a run actually reads. No patch may remove
or weaken them.

One invariant belongs to this skill rather than to the protocol, because scheduling
lives here:

- **A failed run does not reschedule.** Report and stop. A broken run repeating on a
  timer only multiplies the mess.

---

## If the user asks to reset or upgrade the protocol

A patched `specs/LOOP.md` is **never overwritten silently**. When asked to upgrade,
show the version diff first, and preserve the sections that were born from earlier
runs' patches unless the user says otherwise.
