# solodev

Claude Code skills for solo developers who want the discipline of a team: a
self-improving development loop that keeps its state in the repo, plus the review,
audit, and QA skills it calls along the way.

## Skills

| Skill | What it does |
|---|---|
| `/solodev:loop [interval] [plan]` | Runs one full development iteration, then schedules the next one itself |
| `/solodev:discover [area]` | Finds work the repo proves is needed but nobody filed — and files it with citations |
| `/solodev:task <what>` | Files a feature, bug, enhancement, or chore into the backlog — classified, scored, queued |
| `/solodev:fe [target]` | Front-end engineering — architecture, state, runtime cost, code-level a11y |
| `/solodev:be [target]` | Back-end engineering — boundaries, API and data design, transactions |
| `/solodev:pr-new [title]` | Opens a PR with a title and body that follow GitHub best practice |
| `/solodev:ship [bump]` | Cuts a release — derives the SemVer bump, moves the changelog, stops before tagging |
| `/solodev:pr-review [pr]` | Reviews a PR and reports findings ranked by severity |
| `/solodev:ux [flow]` | UX audit — task flows, cognitive load, error recovery |
| `/solodev:ui [screen]` | UI audit — hierarchy, typography, spacing, contrast, states |
| `/solodev:qa [change]` | QA — builds a test matrix, executes it, files reproducible bugs |
| `/solodev:bug-hunter [target]` | Security audit — thinks like an attacker against your own code |

Each works standalone. `loop` calls the others automatically at the phase where each
belongs.

`fe` covers front-end **engineering**; for visual craft — typography, palette, motion —
it defers to the [`impeccable`](https://github.com/pbakaus/impeccable) skill, which is
far deeper on that.

## Agents

The audits ship as subagents too, so `loop` can run them in isolated contexts:

| Agent | Edits files? | Role |
|---|---|---|
| `solodev:qa-runner` | yes — evidence only | Executes the test matrix against the real artifact |
| `solodev:bug-hunter` | **no** | Attacks trust boundaries, reports vulnerabilities with proof |
| `solodev:pr-reviewer` | **no** | Reviews the diff, reports by severity, never approves |
| `solodev:ux-auditor` | **no** | Judges whether the task can be completed |
| `solodev:ui-auditor` | **no** | Judges how it presents |

Four of the five have no edit tools at all. An auditor that can patch what it finds
tends to patch instead of report, and the finding never reaches the Run Log.

## The loop

```
/solodev:loop                      # run, then reschedule at a self-chosen pace
/solodev:loop 45m                  # every 45 minutes
/solodev:loop 2h fix export bug    # every 2 hours, with a request attached
/solodev:loop once add PDF export  # exactly one run
/solodev:loop stop                 # cancel scheduling
```

The first run in a repo **bootstraps** rather than shipping a feature: it writes the
protocol to `specs/LOOP.md`, detects the stack, creates `README.md`, `CHANGELOG.md`,
and `docs/` if missing, and builds the initial scored backlog. The second run is the
first to touch code.

### Every run produces

1. One **complete slice** a user can carry out end to end
2. One **improvement to the loop itself** — a recorded lesson or a protocol patch
3. One **plan for the next iteration**, written to a file

### Every run must

- Write its Definition of Done **before** the code
- Verify on the real artifact and keep evidence
- Pass a quality rubric (≥14/16, no item at 0)
- Pass format, lint, and test gates
- Update `README.md`, `CHANGELOG.md`, and `docs/`
- Get reviewed by a separate agent before committing
- End in a PR on its own branch — ready for review, never auto-merged

### It survives sessions

The loop's state lives in the repo, not in the conversation:

| File | Holds |
|---|---|
| `specs/LOOP.md` | The protocol — the loop patches its own copy over time |
| `specs/LOOP_STATE.md` | Scored backlog, current task, Run Log, next-iteration plan |
| `specs/LOOP_LEARNINGS.md` | Binding rules learned from real failures, capped at 150 lines |
| `specs/REFERENCE.md` | Cached external API patterns |
| `docs/evidence/` | Verification captures |

**`specs/` and `docs/` are never committed.** The loop adds them to `.gitignore` at
bootstrap and the quality gate fails if either is tracked. They are the workflow's
bookkeeping, not your product's, and `docs/evidence/` holds raw command transcripts
that can capture anything a run happened to print. Nothing about the loop is written
into your `README.md` or `CHANGELOG.md` either.

The trade is stated rather than hidden: **the loop's memory does not survive a fresh
clone.** It lives with the working copy.

A fresh session only needs `/solodev:loop` again. Scheduling itself is session-only,
so it stops when the session ends — the work does not.

## Install

```bash
/plugin marketplace add mrfansi/solodev
/plugin install solodev@solodev
```

Developing on it locally? Point the marketplace at the clone instead —
`/plugin marketplace add /path/to/claude-solodev` — and run
`python3 scripts/validate.py` before committing; it checks the manifests, every
frontmatter block, and every cross-reference between skills, agents, and this README.

## Design notes

**The loop improves itself, but cannot bloat.** Rules only come from things that
actually went wrong — never hypotheses. Rules the compiler, tests, or lint already
enforce must be deleted. Protocol patches must point at a failure recorded in the Run
Log, may change at most two sections, and must delete as many lines as they add.

**Audits run as separate agents.** An agent that grades its own work is generous with
itself, so `qa`, `ux`, `ui`, and `pr-review` each run in their own context.

**Cadence beats enthusiasm.** Every third run is audit or refactor instead of a
feature; every fifth adds a meta-review. Only an S1 bug — data loss, a security hole,
or a primary flow that cannot be completed — is allowed to break that.

## License

MIT
