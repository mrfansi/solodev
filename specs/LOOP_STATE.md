# LOOP STATE

> Written by the loop every run. Source of truth for the backlog, the current task,
> metrics, and the next-iteration plan. Protocol: `specs/LOOP.md`.

## Detected stack

This repo is a Claude Code plugin: markdown skills and agent definitions, plus one
Python validator. There is no compiler, no package manager, and no CI.

| Gate | Command |
|---|---|
| Format | none — no markdown formatter is installed (`prettier`, `markdownlint`, `ruff` all absent). Tracked as `E-2`. |
| Lint | `python3 scripts/validate.py` |
| Test | `python3 scripts/validate.py` — the same command. It is the only executable check the repo has. |
| Build | none — markdown ships as-is |

Baseline at bootstrap: validator green — `skills: 10  agents: 5 (4 without edit
tools)  OK`. **Zero unit tests exist.** The validator checks structure and
cross-references, not behaviour; do not report it as a test count.

Phase 4 verification method for this product:
`CLI — run the validator, then load the plugin in Claude Code and invoke the affected
skill for real. Keep stdout transcripts under docs/evidence/.`

---

## Current state

Plugin `solodev` v0.1.0. Ten skills, five agents, one structure validator. Run #1
installed the loop machinery — protocol, state, learnings, reference cache — and
created the `CHANGELOG.md` and `docs/` that the protocol requires of every repo it
runs in but that this repo had not applied to itself.

Measured baseline, the thing the user's request names: **~14,240 tokens are read
before any work happens on every run.** Protocol §3 Phase 0.3 mandates six reads, not
two — `specs/LOOP.md` ~6,151 · `skills/loop/SKILL.md` ~2,920 · `LOOP_STATE.md` ~2,552
· `README.md` ~1,314 · `LOOP_LEARNINGS.md` ~750 · `CHANGELOG.md` ~553. Breakdown in
`docs/evidence/2026-08-04-bootstrap/06-token-baseline-corrected.txt`; the first
measurement (`01-`) counted only the first two and is superseded in part.

The correction changed the shape of the problem, not just the number. Two of those
six files are **ungoverned and grow monotonically** — `LOOP_STATE.md` (backlog + Run
Log) and `CHANGELOG.md` (`[Unreleased]`) already cost ~3,105 tokens after a single
run, and nothing caps either. So the token cost has a fixed half and a growing half;
run #1 nearly shipped a plan that addressed only the fixed one. Tracked as `R-3`.

No feature shipped, by design: run #1 bootstraps, run #2 is the first to change
behaviour.

**Where the work physically is:** branch `loop/run-1-bootstrap`, committed, **not
merged**. `main` does not contain `specs/`. The remote `origin`
(`github.com/mrfansi/solodev`) is an **empty repository** — nothing has ever been
pushed to it — so no PR exists. Run #2 must read the Prereqs line in the plan below
before doing anything else.

---

## Scored backlog

Score = (Value 1–5 × Frequency 1–5) ÷ Size 1–5. Ids are type-prefixed per §10:
`F-` feature · `B-` bug · `E-` enhancement · `R-` refactor · `C-` chore.
Bugs carry a severity (S1/S2/S3); S1 overrides the cadence.

Strike through finished tasks; do not delete them — deleting loses the decision trail.
The Notes column always carries the **origin**.

| Id | Task | V | F | S | Score | Notes (severity + origin) |
|---|---|---|---|---|---|---|
| R-2 | `skills/loop/SKILL.md` restates protocol §2 (state files), §3 (agent spawning per phase), and §10 (intake + bug severity). Delete the copies, point at `specs/LOOP.md` — same treatment the invariants already got | 4 | 5 | 2 | 10.0 | From: user request 2026-08-04 ("tidak token eater"). SKILL.md loads on every invocation, so its size is pure per-run overhead |
| R-1 | Split the protocol into a hot core (§0–§4, read at Phase 0) and cold references (§5–§12, read at the phase that needs them). Measured: cold half is ~2,410 of ~6,151 tokens — a 40% cut to the Phase 0 read | 5 | 5 | 3 | 8.3 | From: user request 2026-08-04. Evidence: `docs/evidence/2026-08-04-bootstrap/01-token-baseline.txt` §B |
| E-2 | No format gate exists. Pick one markdown formatter, pin it, wire it into the Detected stack table | 2 | 5 | 2 | 5.0 | Found during run #1 stack detection. A gate that reads "none" is a gate that cannot fail |
| C-2 | `specs/REFERENCE.md` has only the plugin-spec skeleton. Fill in the exact frontmatter keys Claude Code accepts for skills and for agents, read from the installed plugin cache rather than guessed | 2 | 4 | 1 | 8.0 | Found during run #1. Chore per §10 — fold into another run, not its own |
| F-1 | Nothing in the plugin decides *what* to build. The loop can build, verify, review, and ship a slice, but the backlog is only ever fed by the user or by Phase 4 findings — the product-thinking teammate is missing from the "solo dev has a team" goal | 4 | 2 | 4 | 2.0 | From: `/goal` restated 2026-08-04. Parked deliberately: low score, and large enough to need its own design pass first |
| C-4 | `scripts/validate.py` cannot catch the class of bug that nearly sank this run. Add (a) a check that `git check-ignore` is clean for `specs/` and `docs/`, and (b) `docs/architecture.md` to the file list the agent-count regex already scans — it currently checks only `README.md` and `skills/loop/SKILL.md`, so the new doc can drift silently | 3 | 4 | 1 | 12.0 | Found during run #1 Phase 4 by `qa-runner` (a) and Phase 8 by `pr-reviewer` (b). A gate that cannot fail the way the run actually failed is not a gate |
| C-1 | `README.md` and `docs/` were created before the loop existed and have never been checked against a live install. Walk the documented install path end to end once the remote has content | 2 | 2 | 1 | 4.0 | Blocked on `B-2`. Recorded so the id is not reused and the dependency is visible |
| ~~B-1~~ | ~~`.gitignore` listed `specs/` and `docs/`, so every bootstrap commit would have silently contained nothing but `.gitignore` and `CHANGELOG.md`~~ | — | — | — | — | **S1. Fixed in run #1.** Found by `qa-runner` in Phase 4. Origin: the two lines were absent at Phase 0 and present by Phase 4 — added mid-run by something outside this run's edits |
| B-2 | `README.md` install command named `mrfansi/claude-solodev`, which does not exist. **Half fixed** in run #1: it now names `mrfansi/solodev`, the repo that does exist — but that repo is **empty**, so `/plugin marketplace add mrfansi/solodev` still fails. The name is right; the content is not there | 5 | 4 | 1 | 20.0 | **S1, still open.** Found by `qa-runner` (wrong name) and `pr-reviewer` (empty repo) in run #1. Closing it means pushing this repo to `origin` — an outward-facing first publication, so it is the **user's call**, not the loop's. Cannot be closed by a loop run alone |
| R-3 | `specs/LOOP_STATE.md` and `CHANGELOG.md` are read every run and grow every run, with no cap on either. ~3,105 tokens after one run. Give the Run Log and the backlog a roll-off rule the way `LOOP_LEARNINGS.md` has its 150-line cap | 4 | 5 | 2 | 10.0 | Found during run #1 Phase 8 by `pr-reviewer`, correcting the run's own baseline measurement. This is the half of the token problem run #1 nearly missed |
| C-3 | Protocol §3 Phase 4 and §10 give **contradictory** S1 rules: §3 says "S1 and S2 findings are fixed in this run before the phase completes"; §10 says an S1 found mid-run means "stop, report it, and let the user decide". Run #1 acted on the §3 reading twice without noticing | 3 | 3 | 1 | 9.0 | Found during run #1 Phase 8 by `pr-reviewer`. This is a real Run Log failure, so it is a valid target for a §4D protocol patch on the run #5 meta-review |

**Considered and rejected this run:** "agent definitions duplicate their skills."
Reading `agents/qa-runner.md` and `agents/ux-auditor.md` showed they already delegate
(`invoke the Skill tool with skill: "solodev:qa"`) and only add the isolation framing
and the return contract. There is nothing to deduplicate. Recorded so a later run does
not re-open it.

---

## Current task

**Run #1 — BOOTSTRAP: install the loop machinery and measure the token baseline**

Score: n/a — bootstrap is prescribed by the skill, not scored.
Cadence: run #1 → neither a multiple of three nor of five; bootstrap ships no feature
by design.

Binding `LOOP_LEARNINGS.md` rules for this task: none existed at Phase 1 — the file
was created empty by this run. Four rules were added in Phase 9 and bind from run #2
onward.

### Call-site inventory (Phase 3 — filled in before editing)

| File | Location | Change |
|---|---|---|
| `specs/LOOP.md` | new | copy of `skills/loop/references/PROTOCOL.md` v1.1 |
| `specs/LOOP_STATE.md` | new | this file |
| `specs/LOOP_LEARNINGS.md` | new | copy of the template |
| `specs/REFERENCE.md` | new | cache seeded with what run #1 actually looked up |
| `CHANGELOG.md` | new | Keep a Changelog, `[Unreleased]` |
| `docs/README.md` | new | index |
| `docs/architecture.md` | new | why skills, agents, and the protocol split the way they do |
| `docs/evidence/2026-08-04-bootstrap/` | new | Phase 4 evidence |

No existing file's behaviour was changed, so there were no callers to inventory.

### Definition of Done for this iteration (Phase 1 — before any code)

- [x] `specs/LOOP.md` exists and is byte-identical to `PROTOCOL.md` v1.1
- [x] `specs/LOOP_STATE.md` carries a filled Detected stack table with real commands
- [x] `specs/LOOP_LEARNINGS.md` and `specs/REFERENCE.md` exist
- [x] `CHANGELOG.md` exists in Keep a Changelog format with an `[Unreleased]` section
- [x] `docs/` exists with `docs/README.md` as its index
- [x] The quality gate runs and is green, and its exact command is recorded
- [x] The per-run token cost is **measured**, not estimated in prose, and the number
      is stored as evidence a later run can diff against
- [x] The backlog contains at least one scored item traceable to the user's request
- [x] The next-iteration plan is written into this file
- [x] Every S1 found during verification is fixed before the commit — two were
      (`B-1`, `B-2`), with evidence in `05-s1-fixes.txt`

---

## Next iteration plan (written by Run #1, for Run #2)

```
Task        : R-2 — strip skills/loop/SKILL.md of the protocol content it duplicates
              (C-4 folds in as a chore, per §10)
Score       : 10.0  (Value 4 × Frequency 5 ÷ Size 2)
Why this    : NOT the highest score in the table — B-2 is 20.0 and C-4 is 12.0. Both
              are excluded for stated reasons:
                · B-2 cannot be closed by a loop run. Closing it means publishing
                  this repo to an empty public remote — outward-facing, so it is the
                  user's decision. It stays at the top of the table until they make
                  it, and the loop must not quietly do it instead.
                · C-4 is Size 1 and is a chore, which §10 says to fold into another
                  run rather than give its own. It is folded into this one.
              Of what remains, R-2 attacks the measured problem directly: SKILL.md
              loads on every /solodev:loop invocation, so every line that merely
              restates specs/LOOP.md is paid for on every run forever. The invariants
              already moved this exact way in commit af752a3 and nothing broke, so
              the pattern is proven on this exact file. R-3 also scores 10.0 and is
              the better long-term fix, but it edits the file that holds the decision
              trail; doing the proven change first is the safer order.
Cadence     : run #2 → not a multiple of three or five → feature allowed, but a
              refactor is chosen on merit. Run #3 IS the audit/refactor cadence run;
              it should take R-1 (protocol hot/cold split) or R-3 (cap the growing
              files) — both are refactors and both land where cadence demands one.
Prereqs     : **Run #1's work is on branch `loop/run-1-bootstrap`, unmerged. `main`
              has no `specs/`.** If run #2 starts from `main`, the loop skill will
              see no `specs/LOOP.md`, select BOOTSTRAP again, and overwrite this
              file from the template — losing the backlog, the Run Log, and four
              binding learnings. So, before anything else:
                either  merge `loop/run-1-bootstrap` into `main` and branch from there
                or      branch `loop/run-2-*` from `loop/run-1-bootstrap` directly.
              Confirm with `git log --oneline -1 -- specs/LOOP.md` before Phase 1.
Slice       : SKILL.md's "MEMORY" state-file table, "Companion agents" phase table,
              and "Work attached to the invocation" severity table each replaced by a
              pointer to the protocol section that owns it. Scheduling, argument
              parsing, bootstrap steps, and stack detection STAY — they live nowhere
              else. Then C-4: teach scripts/validate.py to fail when `git
              check-ignore` matches `specs/` or `docs/`, and to scan
              `docs/architecture.md` for the agent-count claim alongside the two
              files it already scans. Once that check exists, DELETE the
              `[verification]` rule from LOOP_LEARNINGS.md and replace it with a
              pointer to the check — §4C requires exactly that when code takes over
              from the brain.
              Complete when: SKILL.md is measurably smaller, the new validator checks
              fail on a deliberately broken .gitignore and pass on the real one, and
              a diff review confirms every deleted SKILL.md line exists verbatim in
              specs/LOOP.md.
Risk        : Deleting a rule that only looked like a duplicate. Mitigation: for each
              deletion, grep specs/LOOP.md for the rule first and record the section
              number in the commit body. If it is not in the protocol, it is not a
              duplicate — leave it. Second risk: folding C-4 in tempts scope creep
              into a general validator rewrite. It is two checks, nothing more.
```

---

## Run Log

One line per run. Format:
`Run #N | task | rubric-iterations | score initial→final | rework? (cause) | gate failures`

```
Run #1 | BOOTSTRAP: loop machinery + token baseline | 0 iterations | rubric n/a (no user-facing slice) | rework: no | gate failures: 0 | 2×S1 found by qa-runner and fixed in-run (B-1 .gitignore, B-2 README install target)
```

Note on the S1s: neither overrode a cadence — run #1 is bootstrap, which has no
cadence to break — but both were fixed before the commit per §3 Phase 4. `B-1` is the
more instructive one: the failure mode was a **silent** one. `git commit` would have
succeeded, the report would have said the machinery was installed, and the next
session would have found an empty `specs/`. Only running the artifact caught it;
reading the diff would not have.
