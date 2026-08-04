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

Plugin `solodev` v0.2.0. **Twelve skills**, five agents, one structure validator.

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

**Where the work physically is:** published as of the run #3 ruling. `main` and all
three loop branches are on `github.com/mrfansi/solodev`, with a stacked draft PR per
run: **#1** run-1 → main, **#3** run-2 → run-1, **#4** run-3 → run-2. Merge in that
order. All three stay drafts; promoting and merging are the user's.

`main` itself still contains no `specs/` — it is the pre-loop tree until PR #1 merges.

**Unrelated PR on the repo: #2**, opened by the `ecc-tools` GitHub App, not by this
loop. It adds 741 lines of `.claude/`, `.codex/`, and `.agents/` config and is **not**
a draft. The loop has not touched it and will not.

**Branch the next run from the newest branch above, not from `main`.** From `main` the
loop skill sees no `specs/LOOP.md`, selects BOOTSTRAP, and overwrites this file from
the template — losing the backlog, the Run Log, and every learning.

**Protocol is at v1.2** as of the C-5 ruling. From run #4 on, a cadence run ships a
feature *alongside* its refactor rather than instead of one — the streak run #3 broke
does not repeat.

Confirm the base carries the latest run before Phase 1:

```bash
git log --oneline -1 --format='%h %s'                        # newest commit here
sed -n '/^## Run Log/,$p' specs/LOOP_STATE.md | grep -c '^Run #[0-9]* |'
```

The second command must equal the last run number. It counts **only** Run Log entries:
scoped to the section, and anchored on the `Run #N |` pipe that every entry carries and
no prose does.

Two earlier versions of this check were wrong, both shipped:

- `git log -- specs/LOOP.md` — that file barely changes, so every loop branch returns
  the same commit. It could distinguish a loop branch from `main` and nothing else.
  Caught by `pr-reviewer` in run #3.
- `grep -c "^Run #"` over the whole file — matched prose like *"Run #1 installed the
  loop machinery"* and returned **7** where the true answer was 3. Caught in run #4
  Phase 0, by the check misleading the very run it was written for. Filed as `B-3`.

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
| ~~C-5~~ | ~~The standing directive contradicts protocol §3 Phase 1 (`N % 3 == 0` → audit/refactor mandatory, **not** a new feature)~~ | 4 | 3 | 1 | 12.0 | **Ruled by the user after run #3: the directive wins.** Protocol patched to **v1.2** — a standing directive now outranks the cadence's *prohibition* on features but not its *choice of slice*, so a cadence run does the refactor **and** ships a feature. §1 untouched. Run #3's Run Log entry is the recorded failure §4D requires. Template synced |
| ~~C-4~~ | ~~`scripts/validate.py` cannot catch the class of bug that nearly sank run #1. Add a `git check-ignore` check and scan `docs/architecture.md` for the agent-count claim~~ | 3 | 4 | 1 | 12.0 | **Done in run #3**, folded in per §10. Took three attempts to build a check that could actually fail — see the Run Log note. Covers `specs/`, `docs/`, and every directory beneath them |
| C-1 | `README.md` and `docs/` were created before the loop existed and have never been checked against a live install. Walk the documented install path end to end once the remote has content | 2 | 2 | 1 | 4.0 | Blocked on `B-2`. Recorded so the id is not reused and the dependency is visible |
| C-6 | `pr-review` is the one skill named in no `docs/flows/` file. Give it a flow doc, or state in `docs/README.md` why the review flow does not need one | 1 | 3 | 1 | 3.0 | **Found by discovery, run #2, seam 2.** Cite: `docs/evidence/2026-08-04-discover/03-seam-2-corrected.txt`, "skills with no flow doc mentioning them: pr-review". **Narrowed after run #2 review:** originally filed as "11 skills, 1 flow doc" against §6's "one file per major user flow". `pr-reviewer` rejected the framing — a skill is not a flow, and reading it as one would commission ten always-resident documents in a repo whose three top refactors all exist to cut per-run read cost. The one-skill gap is what the evidence actually supports |
| C-7 | `skills/task/SKILL.md:88` writes a report score with the `×` and `÷` glyphs; `discover` writes the same score in ASCII. ASCII is the safer choice in a terminal, so `task` is the side that should move | 1 | 3 | 1 | 3.0 | Found during run #2 Phase 5 by `ui-auditor` (major 2). Deliberately **not** fixed in run #2: `task` is outside the slice, and §11G sends unrelated improvements to the backlog rather than into this commit |
| ~~B-1~~ | ~~`.gitignore` listed `specs/` and `docs/`, so every bootstrap commit would have silently contained nothing but `.gitignore` and `CHANGELOG.md`~~ | — | — | — | — | **S1. Fixed in run #1.** Found by `qa-runner` in Phase 4. Origin: the two lines were absent at Phase 0 and present by Phase 4 — added mid-run by something outside this run's edits |
| ~~B-2~~ | ~~`README.md` install command named a repo that does not exist, then a repo that was empty, so `/plugin marketplace add` failed either way~~ | 5 | 4 | 1 | 20.0 | **S1, CLOSED after run #3 on the user's authorisation to publish.** `main` and all three loop branches pushed to `github.com/mrfansi/solodev`; `.claude-plugin/marketplace.json` now resolves on `main`, so the documented install command works. Open for two runs because closing it required an outward-facing first publication the loop must not do unasked |
| R-3 | `specs/LOOP_STATE.md` and `CHANGELOG.md` are read every run and grow every run, with no cap on either. Give the Run Log and the backlog a roll-off rule the way `LOOP_LEARNINGS.md` has its 150-line cap | 5 | 5 | 1.25 | 20.0 | Found run #1 by `pr-reviewer`. **Rescored 10.0 → 20.0 in run #3 on three runs of measurement.** `LOOP_STATE.md` more than doubled in two runs and is now the second-largest Phase 0 read, close behind the protocol itself. Despite run #3 shrinking `SKILL.md`, the total Phase 0 read **rose** by roughly 30%. The growing half dominates the fixed half. Figures regenerate each run — see `docs/evidence/2026-08-04-skill-dedup/03-token-delta.txt` rather than any number retyped here |
| C-3 | Protocol §3 Phase 4 and §10 give **contradictory** S1 rules: §3 says "S1 and S2 findings are fixed in this run before the phase completes"; §10 says an S1 found mid-run means "stop, report it, and let the user decide". Run #1 acted on the §3 reading twice without noticing | 3 | 3 | 1 | 9.0 | Found during run #1 Phase 8 by `pr-reviewer`. This is a real Run Log failure, so it is a valid target for a §4D protocol patch on the run #5 meta-review |

**Considered and rejected this run:** "agent definitions duplicate their skills."
Reading `agents/qa-runner.md` and `agents/ux-auditor.md` showed they already delegate
(`invoke the Skill tool with skill: "solodev:qa"`) and only add the isolation framing
and the return contract. There is nothing to deduplicate. Recorded so a later run does
not re-open it.

---

## Current task

**Run #4 — F-2: `/solodev:ship`, the teammate that cuts a release**

Score: `10.0` (Value 5 × Frequency 4 ÷ Size 2). Highest-scoring **feature**; `R-3`
scores 20.0 but is a refactor, and its CHANGELOG half is delivered as a side effect of
this slice. Folds in `B-3` and `B-4` per §10.

Cadence: run #4 → `4 % 3 != 0`, `4 % 5 != 0` → no cadence constraint. Protocol **v1.2**
plus the standing directive → ship a feature. No conflict; `C-5` is closed.

**Why this, on evidence rather than on the backlog being empty of features.** Protocol
§3 Phase 8 step 3 mandates: *"user-visible change → bump SemVer and move `[Unreleased]`
into a version section."* Three runs have shipped user-visible changes. There are **zero
version sections, zero tags, and the version is still 0.1.0.** The protocol has been
mandating a step that no skill supports and no run has performed — `discover` seam 2,
"a promise with no keeper", found in the plugin's own protocol.

Research turned that from an oversight into a defect. Claude Code's plugin reference
states it verbatim: *"Users get updates **only when you bump this field**. Pushing new
commits without bumping it has no effect, and `/plugin update` reports 'already at the
latest version'."* Because `version` is set and pinned at 0.1.0, **everything runs #1–#3
shipped is unreachable to anyone who installs solodev**, and the update command reports
success while doing nothing. Filed as `B-4`, S2.

It also delivers the CHANGELOG half of `R-3`: cutting `[Unreleased]` into a version
section removes ~1,175 tokens from the per-run Phase 0 read. Run #3's plan said this
half *"is not roll-off material — it is release material"*, so a release concept was
always its prerequisite.

Binding `LOOP_LEARNINGS.md` rules, and how this run complies:
- `[claims]` measured headline → name the inputs. **Applied:** the version-pin claim is
  quoted from the fetched reference, not inferred, and cached in `specs/REFERENCE.md`.
- `[gates]` break a new check the narrowest way. **Applies:** the validator gains a
  version-consistency check; it must be shown failing on a *partial* bump, not just a
  mismatched one.
- `[authoring]` shell commands into fenced blocks, never table cells.
- `[claims]`/`[evidence]` no retyped numbers; regenerate measurements last.
- `[refactor]` split multi-clause candidates — applies to the CHANGELOG cut.

### Call-site inventory (Phase 3 — filled in before editing)

| File | Change |
|---|---|
| `skills/ship/SKILL.md` | new — the skill |
| `.claude-plugin/plugin.json` | version 0.1.0 → the bump this run cuts |
| `.claude-plugin/marketplace.json` | same version; the validator already enforces they match |
| `CHANGELOG.md` | `[Unreleased]` cut into a dated version section + link refs |
| `scripts/validate.py` | version-consistency check; fix `B-3`'s broken base check is **not** here — it is in LOOP_STATE prose |
| `specs/LOOP_STATE.md` | `B-3` fix: the base-verification command |
| `specs/REFERENCE.md` | cache the version-management spec |
| `README.md`, `docs/` | §6 |

`grep -rn "version" scripts/validate.py specs/LOOP.md` established that the only
existing version rule is the manifest-drift check and §3 Phase 8 step 3. No skill
references releasing, so there are no callers to update.

### Definition of Done for this iteration (Phase 1 — before any code)

- [ ] `skills/ship/SKILL.md` exists and uses only frontmatter keys confirmed in
      `specs/REFERENCE.md`
- [ ] It bumps **both** manifests and never lets them diverge — the validator proves
      this by failing on a deliberate partial bump
- [ ] It derives the bump from the `[Unreleased]` content per SemVer, and states its
      reasoning rather than asking the user to pick a number blind
- [ ] It **stops before tagging or pushing**, printing the exact commands instead —
      §11A forbids tagging without permission, and `docs/architecture.md` names
      shipping as the boundary the plugin deliberately hands over
- [ ] The skill is **executed against this repo**: a real release is cut, `B-4` closed,
      and `[Unreleased]` emptied
- [ ] The Phase 0 read total is re-measured and the CHANGELOG reduction shown
- [ ] `B-3` fixed: the base-verification command in this file returns the true run
      count, demonstrated against the current file
- [ ] `python3 scripts/validate.py` green, 12 skills, README cross-reference satisfied
- [ ] `docs/architecture.md`'s "What is deliberately missing" updated — it currently
      says nothing ships, which this run partly changes
- [ ] README, CHANGELOG, and `docs/` updated (§6)

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
Run #4 | F-2 /solodev:ship + B-3 + B-4 | rubric n/a (see note) | rework: yes (bump clause ambiguous; version search missed a file, then a file type; changelog gate passed 3 narrow breaks) | gate failures: 0 | qa-runner: S1+S2+2xS3. pr-reviewer: 2 blockers + 2 majors | SHIPPED A FEATURE and cut release 0.2.0, the repo's first
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
