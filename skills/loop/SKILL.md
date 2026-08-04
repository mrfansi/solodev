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
   directory with `docs/README.md` as its index. A `README.md` you create describes
   **the product**, never the loop — see protocol §6, and note that `docs/` is
   local-only per §2.
6. **Add `specs/` and `docs/` to `.gitignore`**, creating the file if absent. They are
   the loop's workspace and never enter the repo's history (§2). Verify with
   `git check-ignore --no-index specs docs` before continuing — the bootstrap has
   already written into both by this point, so an unignored workspace means the next
   commit carries it.
7. **Build the initial scored backlog** from reading the repo plus the user's
   request, and write it to `specs/LOOP_STATE.md`.
8. Write memory as described below.
9. Commit, then open the run's PR via `pr-new`.
10. Write the §9 report, including the plan for the next iteration.

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

Classified and scored per **protocol §10** before selection, then filed with a
type-prefixed id and its origin. It does not jump the queue for being the most recent
thing said. When it competes with the cadence, **§3 Phase 1** decides; an S1 bug is
the only sanctioned override, per **§10**.

One rule here lives only in this file: **a feature deferred by the audit/refactor
cadence becomes the next run's first candidate, and the report says so.** §8 binds the
next run to whatever plan the current run *chooses* to write, which is a weaker
promise — it does not guarantee the deferred item is what gets written down. Without
this, work can be pushed aside by cadence and quietly never come back.

---

## One run, one branch, one PR

Branch naming, branching point, the draft-PR rule, and what to do without a remote are
all **protocol §3 Phase 8**.

---

## Companion agents

**Protocol §3 says which agent runs at which phase, on what condition, and what its
findings oblige.** Phases 4, 5, and 8 each name their own; that table is not repeated
here.

Four things about them live only in this file, because the protocol does not cover
them:

- **Every agent's prompt must carry** the slice under test, how to run the artifact,
  the tightest condition to test first, and where to write evidence. §3 Phase 4 says
  this of `qa-runner` alone — "**Its** prompt must carry…" — and Phases 5 and 8 impose
  no prompt requirement at all. An auditor left to guess what it is auditing produces
  findings about the wrong thing, and that applies to all five.

- **Every agent's prompt must also forbid returning before its own helpers do.** The
  auditors are denied `Write`/`Edit` but not `Agent`, so they can spawn helpers — and a
  helper reports to the agent that spawned it, not to you. If that agent returns first,
  the helper's findings reach nobody; you get an idle notification and no report. Say
  it explicitly: *if you spawn subagents, wait for them and fold their findings into
  your report; if you cannot wait, do not spawn.* This happened five times in one
  session before anyone noticed, and each time the phase had to be redone inline.

- **`task` loads inline**, alongside `fe` and `be`. §3 Phase 3 names only the two
  implementation tiers, but filing is the run's own work too, with nothing to isolate.
- **`pr-new` runs inline, not as a subagent.** §3 Phase 8 delegates to it without
  saying where it runs. It acts rather than judges, so there is nothing to isolate.
- **If a subagent returns nothing usable, or its type is unavailable because the
  plugin is only partially installed, say so in the report and run that phase
  inline.** Degraded but honest beats a phase silently skipped. The protocol assumes
  a complete install; this is what to do when that assumption fails.

---

## MEMORY (always on, two layers that must not overlap)

Both layers are written every run. **Protocol §2 lists layer 1** — the state files in
the repo — and hands layer 2 to this file by name.

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
