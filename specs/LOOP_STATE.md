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

**Where the work physically is:** two stacked branches, neither merged.
`loop/run-1-bootstrap` holds the machinery; `loop/run-2-backlog-discovery` branches
from it and holds `discover`. **`main` still contains no `specs/`.** The remote
`origin` (`github.com/mrfansi/solodev`) is an **empty repository** — nothing has ever
been pushed — so no PR exists for either run.

Any later run must branch from `loop/run-2-backlog-discovery` (or from `main` once
both are merged). Branching from `main` makes the loop skill see no `specs/LOOP.md`,
select BOOTSTRAP, and overwrite this file from the template. Confirm with
`git log --oneline -1 -- specs/LOOP.md` before Phase 1.

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
| ~~C-2~~ | ~~`specs/REFERENCE.md` has only the plugin-spec skeleton. Fill in the exact frontmatter keys Claude Code accepts~~ | 2 | 4 | 1 | 8.0 | **Done in run #2**, folded in per §10. Both full key tables now in `specs/REFERENCE.md`, read from `code.claude.com/docs/en/skills` and `/sub-agents`, not guessed |
| ~~F-1~~ | ~~Nothing in the plugin decides *what* to build — the product-thinking teammate is missing from the "solo dev has a team" goal~~ | 5 | 5 | 2 | 12.5 | **Done in run #2** as `/solodev:discover`. Rescored from 2.0: the standing directive of 2026-08-04 raised Frequency to every-run and Value to blocking, and the shipped slice was Size 2, not 4 |
| E-3 | `discover` runs inline, so a whole-repo sweep lands its grep output in the caller's context — the exact cost the standing brief targets. `context: fork` would move it into a subagent. Not used in run #2 because the docs do not state what `agent` defaults to when omitted | 3 | 4 | 2 | 6.0 | Found during run #2 Phase 2 research. Needs a live invocation to test, which needs a Claude Code restart — cannot be verified by the validator alone |
| C-5 | The standing directive ("every iteration ships one impactful feature") **contradicts** protocol §3 Phase 1 (`N % 3 == 0` → audit/refactor mandatory, **not** a new feature). They collide on run #3, the next run | 4 | 3 | 1 | 12.0 | From: user directive 2026-08-04. Not resolved by the loop — amending a cadence rule is the user's call, and §4D patch guardrails require a recorded Run Log failure the loop does not yet have |
| C-4 | `scripts/validate.py` cannot catch the class of bug that nearly sank this run. Add (a) a check that `git check-ignore` is clean for `specs/` and `docs/`, and (b) `docs/architecture.md` to the file list the agent-count regex already scans — it currently checks only `README.md` and `skills/loop/SKILL.md`, so the new doc can drift silently | 3 | 4 | 1 | 12.0 | Found during run #1 Phase 4 by `qa-runner` (a) and Phase 8 by `pr-reviewer` (b). A gate that cannot fail the way the run actually failed is not a gate |
| C-1 | `README.md` and `docs/` were created before the loop existed and have never been checked against a live install. Walk the documented install path end to end once the remote has content | 2 | 2 | 1 | 4.0 | Blocked on `B-2`. Recorded so the id is not reused and the dependency is visible |
| C-6 | `pr-review` is the one skill named in no `docs/flows/` file. Give it a flow doc, or state in `docs/README.md` why the review flow does not need one | 1 | 3 | 1 | 3.0 | **Found by discovery, run #2, seam 2.** Cite: `docs/evidence/2026-08-04-discover/03-seam-2-corrected.txt`, "skills with no flow doc mentioning them: pr-review". **Narrowed after run #2 review:** originally filed as "11 skills, 1 flow doc" against §6's "one file per major user flow". `pr-reviewer` rejected the framing — a skill is not a flow, and reading it as one would commission ten always-resident documents in a repo whose three top refactors all exist to cut per-run read cost. The one-skill gap is what the evidence actually supports |
| C-7 | `skills/task/SKILL.md:88` writes a report score with the `×` and `÷` glyphs; `discover` writes the same score in ASCII. ASCII is the safer choice in a terminal, so `task` is the side that should move | 1 | 3 | 1 | 3.0 | Found during run #2 Phase 5 by `ui-auditor` (major 2). Deliberately **not** fixed in run #2: `task` is outside the slice, and §11G sends unrelated improvements to the backlog rather than into this commit |
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

**Run #2 — F-1: `/solodev:discover`, the teammate who finds work nobody filed**

Score: `12.5` (Value 5 × Frequency 5 ÷ Size 2). Rescored upward from its parked 2.0
— see the deviation note below; the standing directive changed both Value and
Frequency, and the slice is much smaller than the original F-1 framing.

Cadence: run #2 → `2 % 3 != 0`, `2 % 5 != 0` → **feature allowed**. No conflict.

**Deviation from the inherited plan, recorded per §3 Phase 1.** Run #1 planned R-2
(a refactor). The user's standing directive attached to this invocation is *"di setiap
iterasi kamu harus menambahkan 1 fitur yang impactfull"* — every iteration must add
one impactful feature. A refactor is not a feature, so the inherited plan is
displaced. R-2, R-3, and R-1 stay in the backlog for run #3, which is the audit/
refactor cadence run and cannot take a feature anyway.

**Why F-1 specifically, and why now.** The directive creates a demand the plugin
cannot currently meet. Counting the backlog: of eleven items, exactly **one** is a
feature — F-1 itself. Once this run consumes it, the backlog holds **zero** features
while standing under a rule that every run must ship one. The loop would be forced to
invent features on the spot, which is the assumption-making the same directive
forbids. F-1 is the item that supplies feature candidates from evidence, so it is
both the highest-value item and the one that unblocks the directive itself.

**Cadence conflict to resolve (not this run).** The directive says *every* iteration
ships a feature; protocol §3 Phase 1 says every third run is mandatorily audit/
refactor and **not** a new feature. Run #3 is where these collide. Flagged in the
report for the user's decision rather than silently resolved — changing a §1-adjacent
cadence rule is theirs to authorise. Filed as `C-5`.

Binding `LOOP_LEARNINGS.md` rules for this task, and how this run complies:
- `[backlog]` "X duplicates Y" → read both files first. **Applied:** read
  `skills/task/SKILL.md` in full before accepting that discovery is missing. It files
  work already decided; it cannot find work. No overlap.
- `[claims]` a measured headline → list its inputs against the spec. **Applied:** the
  resident-description figure names its input set (the `description:` field of every
  shipped skill) and the spec line that makes them resident. Final value after
  `discover` shipped: **~1,042 tokens across eleven skills**, up from ~954 across ten.
  The first draft of this bullet still said "~954 / ten" after the eleventh skill had
  landed; `qa-runner` filed that as S3.
- `[docs]` a documented command → run it, not a plausibility check. **Applied in
  Phase 4:** `/solodev:discover` is executed against this repo, not merely read.
- `[verification]` deliverable is files → `git add -n` before Phase 8.

### Call-site inventory (Phase 3 — filled in before editing)

| File | Location | Change |
|---|---|---|
| `skills/discover/SKILL.md` | new | the skill itself |
| `README.md` | Skills table, after `task` | one row |
| `docs/architecture.md` | "What is deliberately missing" | that section claims nothing decides what to build — now false, must be rewritten |
| `docs/flows/loop-run.md` | Phase 1 row | discovery is where backlog candidates come from |
| `CHANGELOG.md` | `[Unreleased]` → `Added` | one entry |
| `specs/REFERENCE.md` | new section | the frontmatter spec this run researched (folds in `C-2`) |
| `scripts/validate.py` | none | reads `skills/*/SKILL.md` by glob and cross-checks README rows; a new skill is picked up with no code change — **verified, not assumed**, in Phase 4 |

`grep -rn "deliberately missing\|decides what to build\|what to build"` found the two
doc claims above and no others. No skill or agent references a discovery step today,
so there are no callers to update.

### Definition of Done for this iteration (Phase 1 — before any code)

- [x] `skills/discover/SKILL.md` exists, and every frontmatter key it uses is one
      confirmed to exist in the fetched Claude Code spec — no invented keys
      *(uses `name` + `description` only; qa-runner confirmed no invented key)*
- [x] The skill files items into the **same** backlog table format `task` uses, so
      the two cannot produce rows the loop reads differently
      *(§3 points at `task` rather than restating; qa-runner found no contradiction)*
- [x] Every item the skill files must cite **evidence** — a file, a line, a log
      entry, a command. An item with no citation is out of contract
      *(C-6 cites `03-seam-2-corrected.txt` and `specs/LOOP.md` §6)*
- [x] The skill **deduplicates** against the existing backlog *and* against the
      "Considered and rejected" block, and says what it skipped
      *(seam-4 candidate dropped as a duplicate of C-4(b); qa-runner confirmed the
      duplicate is genuine, so nothing was lost)*
- [x] The skill caps how many items it files in one pass and states what it dropped
- [x] `python3 scripts/validate.py` is green and counts 11 skills, with the README
      cross-reference satisfied
- [x] The skill is **executed against this repo** in Phase 4 and files at least one
      item that was genuinely not in the backlog, with its evidence checked by hand
      *(C-6, independently re-verified by qa-runner against §6 and `docs/flows/`)*
- [x] `docs/architecture.md`'s "What is deliberately missing" no longer claims the
      gap this run closed *(replaced by "Two ways work enters the backlog"; the
      section now names shipping/release as the real remaining gap)*
- [x] README, CHANGELOG, and `docs/` updated (§6)
- [x] The resident description cost is re-measured after adding the 11th skill, and
      the delta is stated *(~1,042 tok across 11 skills, from ~954 across 10;
      ~90 tok per skill added. Written into `specs/REFERENCE.md`. Was left undone
      until qa-runner filed it as S3)*

---

## Next iteration plan (written by Run #2, for Run #3)

```
Task        : R-2 — strip skills/loop/SKILL.md of the protocol content it
              duplicates. C-4 folds in as a chore per §10.
Score       : 10.0  (Value 4 × Frequency 5 ÷ Size 2)
Why this    : Inherited unchanged from run #1's plan, which run #2 displaced
              rather than rejected. It is the highest-scoring refactor, and
              run #3 is a cadence run that must take a refactor anyway.
              C-4 folds in: Size 1, and it retires the [verification]
              learning by turning it into a validator check, which §4C
              requires once code can enforce a rule.

CADENCE CONFLICT — READ BEFORE PHASE 1. This is the run where it lands.
              §3 Phase 1 : 3 % 3 == 0, so audit/refactor is MANDATORY and a
                           new feature is forbidden.
              The user's standing directive of 2026-08-04 : every iteration
                           must add one impactful feature.
              These cannot both hold. Filed as C-5 for the user to settle;
              at the time of writing they had not.

              PROVISIONAL DEFAULT, to be used only if the user has still not
              ruled by the time run #3 starts: FOLLOW THE PROTOCOL, take
              R-2, ship no feature. Reasons: §3 is the repo's written rule
              and the directive was given in chat; §4D forbids patching the
              protocol without a Run Log failure to point at, and there is
              none; and a refactor run that turns out to be unwanted costs
              one run, whereas silently overriding a cadence rule costs the
              protocol its authority.
              Run #3 MUST state in its report which way it went and why. If
              it follows this default, it is deviating from the directive,
              and the directive's author is owed that in plain words.
Prereqs     : Branch from `loop/run-2-backlog-discovery`, NOT from `main`.
              `main` has no specs/, so the loop would re-bootstrap and
              destroy this file. Confirm:
              `git log --oneline -1 -- specs/LOOP.md`
Slice       : SKILL.md's MEMORY state-file table, Companion agents phase
              table, and "Work attached to the invocation" severity table
              each replaced by a pointer to the protocol section that owns
              it. Scheduling, argument parsing, bootstrap steps, and stack
              detection STAY — they live nowhere else.
              Then C-4: teach scripts/validate.py to fail when
              `git check-ignore` matches specs/ or docs/, and to scan
              docs/architecture.md for the agent-count claim alongside the
              two files it already scans. Then DELETE the [verification]
              rule from LOOP_LEARNINGS.md and replace it with a pointer to
              the new check.
              Complete when: SKILL.md is measurably smaller, the new checks
              fail on a deliberately broken .gitignore and pass on the real
              one, and a diff review confirms every deleted SKILL.md line
              exists verbatim in specs/LOOP.md.
Risk        : Deleting a rule that only looked like a duplicate. For each
              deletion, grep specs/LOOP.md first and record the section
              number in the commit body; if it is not in the protocol, it is
              not a duplicate. Second risk: folding C-4 in tempts a general
              validator rewrite. It is two checks, nothing more.
```

<details>
<summary>Superseded: the plan run #1 wrote for run #2 (kept for the trail)</summary>

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

Run #2 displaced this plan on the user's standing directive that every iteration ship
a feature. R-2 was not rejected — it carries forward to run #3 unchanged.

</details>

---

## Run Log

One line per run. Format:
`Run #N | task | rubric-iterations | score initial→final | rework? (cause) | gate failures`

```
Run #1 | BOOTSTRAP: loop machinery + token baseline | 0 iterations | rubric n/a (no user-facing slice) | rework: no | gate failures: 0 | 2×S1 found by qa-runner and fixed in-run (B-1 .gitignore, B-2 README install target)
Run #2 | F-1: /solodev:discover, the what-to-build teammate | 1 iteration | rubric 10→15 of 16 | rework: yes (seam-1 command was broken by a markdown table escape; transcript regenerated 3× as its own measurement drifted) | gate failures: 0 | 1 blocker + 4 majors from pr-reviewer, 2 blockers from ui-auditor, S2+S3 from qa-runner — all fixed pre-commit | deviated from the inherited plan on the user's standing directive, R-2 carried forward
```

Note on the S1s: neither overrode a cadence — run #1 is bootstrap, which has no
cadence to break — but both were fixed before the commit per §3 Phase 4. `B-1` is the
more instructive one: the failure mode was a **silent** one. `git commit` would have
succeeded, the report would have said the machinery was installed, and the next
session would have found an empty `specs/`. Only running the artifact caught it;
reading the diff would not have.
