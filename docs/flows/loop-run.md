# Flow: one loop run

`/solodev:loop [interval] [plan]` performs **one** run — Phase 0 through 10, in order
— then schedules the next one and stops. Two runs never happen in one turn.

## Before the run

The skill checks whether `specs/LOOP.md` exists in the working repo.

- **Missing** → BOOTSTRAP. Run #1 ships no feature. It installs the protocol and state
  files, detects the stack, creates `README.md` / `CHANGELOG.md` / `docs/` if absent,
  and builds the first scored backlog.
- **Present** → NORMAL. The repo's copy of the protocol is the source of truth, not
  the skill's template — earlier runs may have patched it.

## The eleven phases

| Phase | What happens | Where the output lands |
|---|---|---|
| 0 | Orientation: check the branch, finish any uncommitted prior run, read learnings → state → changelog → readme, plus Claude Code memory | a 4-line summary in the report |
| 1 | Score the candidates, pick **one**, write this iteration's Definition of Done **before any code**. A thin backlog is what `discover` is for — it supplies candidates from repo evidence instead of from invention | `specs/LOOP_STATE.md` |
| 2 | Look up what is genuinely unknown; use the cache for what is not | `specs/REFERENCE.md` |
| 3 | Inventory every call site, *then* implement. `fe` / `be` load inline | `specs/LOOP_STATE.md`, then the code |
| 4 | Verify on the real artifact — `qa-runner` subagent every run, plus `bug-hunter` if a trust boundary moved | `docs/evidence/<date>-<task>/` |
| 5 | Quality critique — `ux-auditor` + `ui-auditor` subagents if a user-facing surface changed. Rubric passes at ≥14/16 with no zero | the report |
| 6 | Format, lint, test — the commands recorded under Detected stack | the Run Log records gate failures |
| 7 | Documentation: README, CHANGELOG, and `docs/`. Skipping it fails the run | those files |
| 8 | `pr-reviewer` subagent against the working diff, *then* commit, then a draft PR | the branch and the PR |
| 9 | Self-improvement: one recorded lesson or a protocol patch, plus memory | `specs/LOOP_LEARNINGS.md` |
| 10 | Report, and write the plan that binds the next run's Phase 1 | `specs/LOOP_STATE.md` |

## Why the audits are subagents and the builders are not

`qa-runner`, `bug-hunter`, `ux-auditor`, `ui-auditor`, and `pr-reviewer` run in their
own contexts because an audit performed by the agent that wrote the code grades its
own homework. Four of them cannot edit files, so a finding can never be quietly fixed
instead of reported.

`fe`, `be`, `task`, and `pr-new` load **inline**. Building and filing are the run's own
work — there is nothing to isolate, and a subagent would only add a context handoff.

## One run, one branch, one PR

Each run branches from the default branch as `<type>/<backlog-id>-<what-it-does>` — see
protocol §3 Phase 8 for the type table — and ends in a
**draft** PR. Promoting it to ready, and merging, are the user's decisions. No remote
or no `gh` → the run commits to the branch, says the PR step was skipped, and carries
on.

## What survives the session

Scheduling does not — it is session-only, and cron jobs expire after seven days. The
work does: everything the run learned is in `specs/` and `docs/`, committed. A fresh
session needs only `/solodev:loop` to pick up exactly where the last run stopped.
