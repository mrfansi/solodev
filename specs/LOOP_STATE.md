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

Plugin `solodev` v0.1.0. **Eleven skills**, five agents, one structure validator.

Run #1 installed the loop machinery — protocol, state, learnings, reference cache —
and created the `CHANGELOG.md` and `docs/` that the protocol requires of every repo it
runs in but that this repo had not applied to itself.

**Run #2 shipped the first feature: `/solodev:discover`** (`F-1`), the teammate that
decides *what* to build. It works six seams over the repo's own evidence and files
scored rows; `docs/architecture.md` no longer names that gap as missing. Run #2 also
closed `C-2` by caching the researched Claude Code frontmatter key tables into
`specs/REFERENCE.md`.

**Run #3 shipped no feature.** It is the cadence run, and `C-5` was still unruled, so
run #2's provisional default applied. It took `R-2` — `skills/loop/SKILL.md` no longer
restates the protocol, measurably smaller — and folded in `C-4`, giving the validator
two checks it should always have had.

### The measurement that matters, three runs in

The user's standing brief targets the per-run read cost. Six files are read before any
work happens: `specs/LOOP.md` and `skills/loop/SKILL.md` via the skill mechanism, then
the four §3 Phase 0.3 names — `LOOP_LEARNINGS.md`, `LOOP_STATE.md`, `CHANGELOG.md`
`[Unreleased]`, `README.md`.

**Run #1 measured ~14,240 tokens. Run #3 measured roughly 30% more than that,
despite this run shrinking the file it targeted.**

Per-file figures are deliberately **not** repeated here. They are regenerated every
run into `docs/evidence/<date>-<task>/03-token-delta.txt`, and run #3 proved why:
three stale copies of them ended up in this file and the CHANGELOG, disagreeing with
each other and with the truth, because a number retyped into a file that keeps
changing is stale the moment it is written. Read the generated file.

The direction is what matters and it has held for three runs: **the growing half
dominates the fixed half.** `LOOP_STATE.md` and `CHANGELOG.md` have no cap and gained
roughly 4,000 tokens across two runs, while `R-1` — the largest single cut available —
would remove ~2,410 once. `LOOP_STATE.md` is now the second-largest read and overtakes
the protocol itself on trend. `R-3` is rescored to **20.0** on this and is the top
actionable item.

**Where the work physically is:** three stacked branches, none merged.
`loop/run-1-bootstrap` → `loop/run-2-backlog-discovery` → `loop/run-3-skill-dedup`,
each branched from the one before. **`main` still contains no `specs/`.** The remote
`origin` (`github.com/mrfansi/solodev`) is an **empty repository** — nothing has ever
been pushed — so no PR exists for any run.

**Branch the next run from the newest branch above, not from `main`.** From `main` the
loop skill sees no `specs/LOOP.md`, selects BOOTSTRAP, and overwrites this file from
the template — losing the backlog, the Run Log, and every learning.

Confirm the base carries the latest run before Phase 1:

```bash
git log --oneline -1 --format='%h %s'          # newest commit on this branch
grep -c "^Run #" specs/LOOP_STATE.md           # must equal the last run number
```

Do **not** use `git log -- specs/LOOP.md` for this. That file has not changed since
run #1, so every loop branch returns the same commit and the check cannot tell a
stale base from a current one. Run #3 shipped that check and `pr-reviewer` caught it.

---

## Scored backlog

Score = (Value 1–5 × Frequency 1–5) ÷ Size 1–5. Ids are type-prefixed per §10:
`F-` feature · `B-` bug · `E-` enhancement · `R-` refactor · `C-` chore.
Bugs carry a severity (S1/S2/S3); S1 overrides the cadence.

Strike through finished tasks; do not delete them — deleting loses the decision trail.
The Notes column always carries the **origin**.

| Id | Task | V | F | S | Score | Notes (severity + origin) |
|---|---|---|---|---|---|---|
| ~~R-2~~ | ~~`skills/loop/SKILL.md` restates protocol §2, §3, and §10. Delete the copies, point at `specs/LOOP.md`~~ | 4 | 5 | 2 | 10.0 | **Done in run #3.** Size delta in `docs/evidence/2026-08-04-skill-dedup/03-token-delta.txt`. **Five** clauses kept because they exist nowhere else — and **two rules were deleted in error and restored**, one after `qa-runner` filed it S1, one after `pr-reviewer` found a quantifier mismatch |
| R-1 | Split the protocol into a hot core (§0–§4, read at Phase 0) and cold references (§5–§12, read at the phase that needs them). Measured: cold half is ~2,410 of ~6,151 tokens — a 40% cut to the Phase 0 read | 5 | 5 | 3 | 8.3 | From: user request 2026-08-04. Evidence: `docs/evidence/2026-08-04-bootstrap/01-token-baseline.txt` §B |
| E-2 | No format gate exists. Pick one markdown formatter, pin it, wire it into the Detected stack table | 2 | 5 | 2 | 5.0 | Found during run #1 stack detection. A gate that reads "none" is a gate that cannot fail |
| ~~C-2~~ | ~~`specs/REFERENCE.md` has only the plugin-spec skeleton. Fill in the exact frontmatter keys Claude Code accepts~~ | 2 | 4 | 1 | 8.0 | **Done in run #2**, folded in per §10. Both full key tables now in `specs/REFERENCE.md`, read from `code.claude.com/docs/en/skills` and `/sub-agents`, not guessed |
| ~~F-1~~ | ~~Nothing in the plugin decides *what* to build — the product-thinking teammate is missing from the "solo dev has a team" goal~~ | 5 | 5 | 2 | 12.5 | **Done in run #2** as `/solodev:discover`. Rescored from 2.0: the standing directive of 2026-08-04 raised Frequency to every-run and Value to blocking, and the shipped slice was Size 2, not 4 |
| E-3 | `discover` runs inline, so a whole-repo sweep lands its grep output in the caller's context — the exact cost the standing brief targets. `context: fork` would move it into a subagent. Not used in run #2 because the docs do not state what `agent` defaults to when omitted | 3 | 4 | 2 | 6.0 | Found during run #2 Phase 2 research. Needs a live invocation to test, which needs a Claude Code restart — cannot be verified by the validator alone |
| C-5 | The standing directive ("every iteration ships one impactful feature") **contradicts** protocol §3 Phase 1 (`N % 3 == 0` → audit/refactor mandatory, **not** a new feature). They collide on run #3, the next run | 4 | 3 | 1 | 12.0 | From: user directive 2026-08-04. Not resolved by the loop — amending a cadence rule is the user's call, and §4D patch guardrails require a recorded Run Log failure the loop does not yet have |
| ~~C-4~~ | ~~`scripts/validate.py` cannot catch the class of bug that nearly sank run #1. Add a `git check-ignore` check and scan `docs/architecture.md` for the agent-count claim~~ | 3 | 4 | 1 | 12.0 | **Done in run #3**, folded in per §10. Took three attempts to build a check that could actually fail — see the Run Log note. Covers `specs/`, `docs/`, and every directory beneath them |
| C-1 | `README.md` and `docs/` were created before the loop existed and have never been checked against a live install. Walk the documented install path end to end once the remote has content | 2 | 2 | 1 | 4.0 | Blocked on `B-2`. Recorded so the id is not reused and the dependency is visible |
| C-6 | `pr-review` is the one skill named in no `docs/flows/` file. Give it a flow doc, or state in `docs/README.md` why the review flow does not need one | 1 | 3 | 1 | 3.0 | **Found by discovery, run #2, seam 2.** Cite: `docs/evidence/2026-08-04-discover/03-seam-2-corrected.txt`, "skills with no flow doc mentioning them: pr-review". **Narrowed after run #2 review:** originally filed as "11 skills, 1 flow doc" against §6's "one file per major user flow". `pr-reviewer` rejected the framing — a skill is not a flow, and reading it as one would commission ten always-resident documents in a repo whose three top refactors all exist to cut per-run read cost. The one-skill gap is what the evidence actually supports |
| C-7 | `skills/task/SKILL.md:88` writes a report score with the `×` and `÷` glyphs; `discover` writes the same score in ASCII. ASCII is the safer choice in a terminal, so `task` is the side that should move | 1 | 3 | 1 | 3.0 | Found during run #2 Phase 5 by `ui-auditor` (major 2). Deliberately **not** fixed in run #2: `task` is outside the slice, and §11G sends unrelated improvements to the backlog rather than into this commit |
| ~~B-1~~ | ~~`.gitignore` listed `specs/` and `docs/`, so every bootstrap commit would have silently contained nothing but `.gitignore` and `CHANGELOG.md`~~ | — | — | — | — | **S1. Fixed in run #1.** Found by `qa-runner` in Phase 4. Origin: the two lines were absent at Phase 0 and present by Phase 4 — added mid-run by something outside this run's edits |
| B-2 | `README.md` install command named `mrfansi/claude-solodev`, which does not exist. **Half fixed** in run #1: it now names `mrfansi/solodev`, the repo that does exist — but that repo is **empty**, so `/plugin marketplace add mrfansi/solodev` still fails. The name is right; the content is not there | 5 | 4 | 1 | 20.0 | **S1, still open.** Found by `qa-runner` (wrong name) and `pr-reviewer` (empty repo) in run #1. Closing it means pushing this repo to `origin` — an outward-facing first publication, so it is the **user's call**, not the loop's. Cannot be closed by a loop run alone |
| R-3 | `specs/LOOP_STATE.md` and `CHANGELOG.md` are read every run and grow every run, with no cap on either. Give the Run Log and the backlog a roll-off rule the way `LOOP_LEARNINGS.md` has its 150-line cap | 5 | 5 | 1.25 | 20.0 | Found run #1 by `pr-reviewer`. **Rescored 10.0 → 20.0 in run #3 on three runs of measurement.** `LOOP_STATE.md` more than doubled in two runs and is now the second-largest Phase 0 read, close behind the protocol itself. Despite run #3 shrinking `SKILL.md`, the total Phase 0 read **rose** by roughly 30%. The growing half dominates the fixed half. Figures regenerate each run — see `docs/evidence/2026-08-04-skill-dedup/03-token-delta.txt` rather than any number retyped here |
| C-3 | Protocol §3 Phase 4 and §10 give **contradictory** S1 rules: §3 says "S1 and S2 findings are fixed in this run before the phase completes"; §10 says an S1 found mid-run means "stop, report it, and let the user decide". Run #1 acted on the §3 reading twice without noticing | 3 | 3 | 1 | 9.0 | Found during run #1 Phase 8 by `pr-reviewer`. This is a real Run Log failure, so it is a valid target for a §4D protocol patch on the run #5 meta-review |

**Considered and rejected this run:** "agent definitions duplicate their skills."
Reading `agents/qa-runner.md` and `agents/ux-auditor.md` showed they already delegate
(`invoke the Skill tool with skill: "solodev:qa"`) and only add the isolation framing
and the return contract. There is nothing to deduplicate. Recorded so a later run does
not re-open it.

---

## Current task

**Run #3 — R-2: strip `skills/loop/SKILL.md` of protocol duplication. C-4 folds in.**

Score: `10.0` (Value 4 × Frequency 5 ÷ Size 2). Taken from the inherited plan
unchanged.

Cadence: run #3 → `3 % 3 == 0` → **audit/refactor mandatory, a new feature is
forbidden**. `3 % 5 != 0`, so no meta-review is due.

### C-5 resolved for this run by the provisional default — and it went against the directive

Run #2 left `C-5` open: the standing directive says every iteration ships one
impactful feature; §3 Phase 1 says every third run must be a refactor and must not.
Run #2 wrote a provisional default to be used **only if the user had still not ruled**
by the time run #3 started.

**They had not.** This run was started by the scheduled wakeup, not by a person:
fired at 05:23:30 against a wakeup scheduled for 05:23, carrying arguments
byte-identical to the ones run #2 passed to `ScheduleWakeup` itself. Treating the
loop's own echoed prompt as the user reaffirming the directive would manufacture a
ruling out of nothing — which is exactly the assumption the same directive forbids.

So the default applies: **protocol wins, this run ships no feature.** Stated plainly
because the directive's author is owed it in plain words, per the run #2 plan.
The question is put to the user directly at the end of this run rather than left in
prose a wakeup cannot answer.

Binding `LOOP_LEARNINGS.md` rules, and how this run complies:
- `[backlog]` "X duplicates Y" → read both files first. **Applied as the whole of
  Phase 3:** every one of 22 deletion candidates was grepped against `specs/LOOP.md`
  before removal. Four came back absent and were kept. Evidence:
  `docs/evidence/2026-08-04-skill-dedup/01-duplication-audit.txt`.
- `[authoring]` shell command into markdown → fenced block, never a table cell.
  **Applies to C-4:** the validator gains a `git check-ignore` call; its command goes
  in code, not in a doc table.
- `[measurement]` / `[claims]` a cost-justified task → measure it and name the inputs.
  **Applied:** SKILL.md byte size before and after, and the Phase 0 read total
  recomputed over the same six files run #1 measured.
- `[evidence]` a transcript measuring a repo that will contain it → regenerate last.
- `[verification]` deliverable is files → `git add -n` before Phase 8.
- `[docs]` a documented command → run it, not a plausibility check. **Applies to
  C-4:** the new validator checks must be shown failing on a deliberately broken
  `.gitignore`, not merely passing on the good one.

### Call-site inventory (Phase 3 — filled in before editing)

| File | Location | Change |
|---|---|---|
| `skills/loop/SKILL.md` | "Work attached to the invocation" | delete table, point at §10 + §3 Phase 1 |
| `skills/loop/SKILL.md` | "Companion agents" | delete the phase table and the findings list; **keep** the three clauses that exist nowhere else |
| `skills/loop/SKILL.md` | "One run, one branch, one PR" | delete, point at §3 Phase 8 |
| `skills/loop/SKILL.md` | MEMORY layer 1 table | delete, point at §2; **keep** layer 2, which §2 explicitly hands to this file |
| `scripts/validate.py` | new checks | `git check-ignore` on `specs/`+`docs/`; add `docs/architecture.md` to the agent-count scan |
| `specs/LOOP_LEARNINGS.md` | `[verification]` rule | delete once the validator enforces it, per §4C |
| `README.md`, `CHANGELOG.md`, `docs/` | — | §6 |

`grep -rn "solodev:task\|degraded\|pr-new" specs/LOOP.md` is what established which
clauses are unique; no other file references SKILL.md's section headings, so there are
no external callers to update.

### Definition of Done for this iteration (Phase 1 — before any code)

- [x] Every deleted line of `SKILL.md` is proven to exist in `specs/LOOP.md`, with
      the section recorded — and anything absent from the protocol is **kept**
      *(22 candidates grepped. **Failed on the first pass**: the audit treated a
      two-clause table row as one claim and deleted a rule that exists nowhere.
      Caught by `qa-runner` as S1, restored. Now four clauses live only in SKILL.md,
      not three)*
- [x] `skills/loop/SKILL.md` is measurably smaller; the byte delta is stated
      *(see the generated measurement)*
- [x] The protocol-absent clauses all survive *(four: `task` inline, `pr-new` inline,
      degraded-agent fallback, and the deferred-feature rule restored after S1)*
- [x] `scripts/validate.py` fails on a **deliberately broken** `.gitignore` and
      passes on the real one — demonstrated, not asserted
      *(**Failed twice before it held.** v1 used plain `git check-ignore`, which
      skips tracked paths — a gate that could not fire. v2 with `--no-index` caught
      the roots but not `docs/evidence/`, found by `qa-runner` as S1. v3 walks every
      subdirectory. Evidence: `08-gate-subpath-fixed.txt`)*
- [x] `scripts/validate.py` scans `docs/architecture.md` for the agent-count claim,
      and that new check is shown failing on a deliberately wrong count
- [x] The `[verification]` learning is deleted and replaced by a pointer to the
      check that now enforces it (§4C) *(retirement was premature at v2 — the check
      was narrower than the rule. Valid only after v3, with the scope limit stated)*
- [x] Behaviour is preserved *(not on the first attempt — one rule was lost and
      restored. Verified after the fix)*
- [x] The Phase 0 read total is recomputed over the same six files run #1 measured
      *(regenerated as the final pre-commit step after `qa-runner` filed the first
      measurement as stale — S2, and a violation of this run's own `[evidence]` rule)*
- [x] README, CHANGELOG, and `docs/` updated (§6)
- [x] The report states plainly that this run shipped no feature, and why

Score: `12.5` (Value 5 × Frequency 5 ÷ Size 2). Rescored upward from its parked 2.0
— see the deviation note below; the standing directive changed both Value and
Frequency, and the slice is much smaller than the original F-1 framing.
---

## Next iteration plan (written by Run #3, for Run #4)

```
Task        : R-3 — cap the two Phase 0 files that grow without bound
Score       : 20.0  (Value 5 x Frequency 5 / Size 1.25)
Why this    : Highest actionable score, and three runs of measurement now
              say it is the dominant cost. specs/LOOP_STATE.md went ~2552
              -> its run-#1 size in two runs and is now the second-largest file
              the loop reads, close behind the protocol itself. Run #3 shrank
              SKILL.md and the TOTAL Phase 0 read still ROSE by roughly 30%.
              Cutting the fixed half while the growing half compounds is
              losing ground. Read run #3's generated measurement at
              docs/evidence/2026-08-04-skill-dedup/03-token-delta.txt for the
              exact figures; do not trust a number retyped into prose.
              B-2 still scores 20.0 too and still cannot be closed by a loop
              run — publishing to the empty remote is the user's call.
Cadence     : run #4 -> 4 % 3 != 0 and 4 % 5 != 0. A feature is ALLOWED but
              not required by the protocol. See the C-5 note below.
C-5         : Run #3 broke the directive's streak under the provisional
              default, because the run was started by a wakeup echoing the
              loop's own prompt rather than by the user. If the user has
              ruled by run #4, follow the ruling. If they still have not,
              note that run #4 is NOT a cadence run — so R-3 and the
              directive do not actually conflict here. R-3 can be taken as
              the slice AND a small feature shipped alongside it only if
              that feature is genuinely impactful; otherwise take R-3 alone
              and say the streak is still broken. Do not invent a feature to
              satisfy a count.
Prereqs     : Branch from `loop/run-3-skill-dedup`, NOT from `main`. `main`
              still has no specs/. Confirm:
              `git log --oneline -1 -- specs/LOOP.md`
Slice       : Give LOOP_STATE.md and CHANGELOG.md the roll-off that
              LOOP_LEARNINGS.md already has. Concretely: the Run Log keeps
              the last N entries inline and older ones move to an archive
              file the loop does NOT read at Phase 0; struck-through backlog
              rows move with them. CHANGELOG [Unreleased] is not roll-off
              material — it is release material — so the honest fix there is
              to cut released entries into version sections, not to trim.
              Decide N from the measurement, not from taste, and write down
              why.
              Complete when: the Phase 0 read total is measured DOWN against
              run #3's ~18707, the decision trail is still reachable (moved,
              never deleted -- the backlog's own rule), and scripts/
              validate.py gains a check that fails if LOOP_STATE.md exceeds
              the chosen budget. Per the [gates] learning, break it on
              purpose and watch it fail, including one narrow case.
Risk        : Roll-off destroys the decision trail if it deletes instead of
              moves. The backlog explicitly forbids deleting struck rows.
              Second risk: an archive file the loop never reads is a file
              nobody maintains -- state where it is read from, or it becomes
              a graveyard. Third: this run edits the very file that records
              its own work, so measure before and after in the same pass.
```

<details>
<summary>Superseded: the plan run #2 wrote for run #3 (kept for the trail)</summary>

Run #3 executed it as written — R-2 plus C-4 folded in — and used its
provisional C-5 default. Preserved in git history at commit 33b353e rather
than duplicated here, since it ran to completion.

</details>

---

## Run Log

One line per run. Format:
`Run #N | task | rubric-iterations | score initial→final | rework? (cause) | gate failures`

```
Run #1 | BOOTSTRAP: loop machinery + token baseline | 0 iterations | rubric n/a (no user-facing slice) | rework: no | gate failures: 0 | 2×S1 found by qa-runner and fixed in-run (B-1 .gitignore, B-2 README install target)
Run #2 | F-1: /solodev:discover, the what-to-build teammate | 1 iteration | rubric 10→15 of 16 | rework: yes (seam-1 command was broken by a markdown table escape; transcript regenerated 3× as its own measurement drifted) | gate failures: 0 | 1 blocker + 4 majors from pr-reviewer, 2 blockers from ui-auditor, S2+S3 from qa-runner — all fixed pre-commit | deviated from the inherited plan on the user's standing directive, R-2 carried forward
Run #3 | R-2 SKILL.md dedup + C-4 gate checks | rubric n/a (pure refactor, ux+ui skipped per §3 Phase 5) | rework: yes, heavily (2 rules deleted and restored; the gate check rebuilt 4× before it could fail correctly; the token measurement regenerated 4× and then removed from prose entirely) | gate failures: 0 | qa-runner: 2×S1 + S2 + S3. pr-reviewer: 2 blockers + 4 majors + 4 minors. All fixed pre-commit | SHIPPED NO FEATURE — cadence run, C-5 still unruled, run #2's provisional default applied
```

**Note on run #3 and the directive.** The run was started by the scheduled wakeup at
05:23:30 against a wakeup set for 05:23, carrying arguments byte-identical to the ones
run #2 passed to `ScheduleWakeup`. That is the loop echoing its own prompt, not the
user reaffirming the directive, so `C-5` remained unruled and the provisional default
— protocol wins — applied. **This run therefore did not satisfy the standing directive
to ship a feature every iteration.** Recorded here rather than only in the report,
because the next run needs to know the streak was broken and why.

**Note on run #3's rework.** This run was wrong more often than any before it, and
every fault was caught by an audit rather than by the run itself:

- **Two rules deleted** in a refactor whose entire risk is deleting rules. One was a
  two-clause table row checked as a single claim (`qa-runner`, S1); one turned on a
  quantifier — "each agent's" matched against the protocol's "its" — and the
  verification transcript certified the deletion (`pr-reviewer`).
- **The gate check was rebuilt four times.** Plain `check-ignore` could never fire;
  `--no-index` on roots missed `docs/evidence/`; adding subdirectories missed `*.txt`.
  Each version passed the obvious injection and failed a narrower one.
- **The token measurement was wrong four times** — sign inverted, taken mid-run, then
  correct but never propagated, then propagated into files whose editing changed the
  number again.

Three learnings came out of it. The third is the structural one: **stop copying
measured numbers into prose.** The always-read files now state the direction and point
at the generated evidence, which also shrinks the very files R-3 exists to cap.

Note on the S1s: neither overrode a cadence — run #1 is bootstrap, which has no
cadence to break — but both were fixed before the commit per §3 Phase 4. `B-1` is the
more instructive one: the failure mode was a **silent** one. `git commit` would have
succeeded, the report would have said the machinery was installed, and the next
session would have found an empty `specs/`. Only running the artifact caught it;
reading the diff would not have.
