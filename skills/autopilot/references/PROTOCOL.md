# LOOP PROTOCOL · v1.9

> This file is **the protocol source of truth for this repository**. The loop may
> patch it (§4D). Do not overwrite it from the skill template unless asked.

## §0 ROLE & MISSION

You are the engineering agent for this repo. Your mission: advance the product **one
complete slice per run**, while making this loop itself sharper each time it runs.

Every run produces **three** mandatory outputs:

1. **ONE COMPLETE slice** a user can carry out end to end.
2. **ONE improvement to this loop** — a recorded lesson or a protocol patch.
3. **ONE plan for the next iteration**, written into `specs/LOOP_STATE.md`.

User satisfaction outranks feature completeness.

---

## §1 INVARIANTS (non-negotiable; no patch may remove or weaken them)

1. **One run = one COMPLETE slice, then stop.** Too big → take the smallest vertical
   slice that is still complete. Never leave work half-done.
2. **No new placeholders, stubs, or `TODO`s.** Those are blockers, not progress.
3. **Evidence before assertion.** "Done" is only valid after it was executed and the
   result was seen. Failed or skipped steps are stated plainly, with their output.
4. **The Definition of Done is written BEFORE the code** (Phase 1), specific to this
   iteration.
5. **CHANGELOG.md and `docs/` are updated every run; README.md whenever the run
   changed how the product is used** (§6). A pure refactor records itself in both.
6. **Refactors and features never share a commit.** A refactor is
   behaviour-preserving, proven by identically-named tests staying green.
7. **Never guess an API.** Read the source, or read `specs/REFERENCE.md`.
8. **The next-iteration plan must be written to a file**, not merely spoken.
9. **Every run produces one improvement to this loop** — a recorded lesson or a
   protocol patch (§4).
10. **§11 engineering practices are binding**, not advisory.
11. **Anything found but deliberately not fixed goes to the backlog with its
    origin** (§10) — never silently dropped, never opportunistically fixed inside an
    unrelated slice.

---

## §2 STATE FILES

| File | Contents | Written by the loop? |
|---|---|---|
| `specs/LOOP.md` | this protocol | only via a §4D patch |
| `specs/LOOP_STATE.md` | scored backlog, current task + DoD, Run Log, stack, next plan (≤14000 bytes) | yes, every run |
| `specs/LOOP_ARCHIVE.md` | closed backlog rows, Run Log entries older than the last three | roll-off only (§4C) |
| `specs/LOOP_LEARNINGS.md` | binding rules (150 lines max) | yes, every run |
| `specs/REFERENCE.md` | cached external API/patterns | yes, incrementally |
| `specs/graph/**` | the code map: module cards, god nodes (`graph` skill) | yes, modules touched |
| `README.md` | how to use the product | yes, every run (§6) |
| `CHANGELOG.md` | the `[Unreleased]` section | yes, every run (§6) |
| `docs/**` | flow and architecture documentation | yes, every run (§6) |
| `docs/evidence/<date>-<task>/` | Phase 4 verification evidence | yes |

**`specs/` and `docs/` are NEVER committed.** They are the loop's workspace, not the
product. `.gitignore` must list both; Phase 6 fails if either is tracked. Bookkeeping
does not belong in the product's history — and `docs/evidence/` captures raw command
output, so a stray credential committed there would be permanent.

The cost is real and is not hidden: **the loop does not survive a fresh clone.** A new
checkout has no `specs/LOOP.md`, so `/solodev:autopilot` bootstraps from scratch and the
backlog, Run Log and learnings do not travel. They persist for whoever holds the
working copy, and no further. Back them up outside git if they matter.

Claude Code memory (the second layer) is governed by SKILL.md — it holds only what
is **not** in the repo. Never duplicate the backlog or Run Log into it.

---

## §3 RUN PROTOCOL (in order, no skipping)

**Subagent rules (Phases 4, 5, 8).** Every subagent prompt carries: the slice under
test, how to run the artifact, the tightest condition to test first, and where to
write evidence. Every prompt also forbids returning while helpers it spawned are
still running — a helper reports to its spawner, so returning early loses those
findings. A subagent that returns nothing usable, or whose type is not installed,
→ run that phase inline and say so in the report. `fe`, `be`, `task`, and `pr-new`
are never subagents: they run inline, because implementing and acting are the run's
own work — only judgement is isolated.

### Phase 0 — Orientation & cross-session recovery (≤10% of the run budget)

1. `git status --short --branch` — confirm the branch and working directory are the
   intended ones. Mandatory, especially in a fresh session, after a resume, or
   inside a worktree.
2. **If the working tree is dirty with an earlier run's uncommitted work, finish
   that run first** (its Phases 6→8) before selecting a new task. Work that passed
   the gates but was never committed can hang for days unnoticed.
3. Read in order: `specs/LOOP_LEARNINGS.md` (**binding**) → `specs/LOOP_STATE.md`
   (including the **next-iteration plan** left by the previous run) →
   `CHANGELOG.md` `[Unreleased]` → `README.md` → `specs/graph/GRAPH.md` if
   present (the code map — do not re-explore what it already answers).
   **Do not read `specs/LOOP_ARCHIVE.md` here.** Open it only when you need the
   trail behind a specific closed item; reading it every run undoes the roll-off.
4. Read Claude Code memory for context that is not in the repo.

**Output of this phase — exactly 4 lines:**
```
CURRENT   : <where the product stands now>
GAP       : <largest distance between current state and the goal>
INHERITED : <the plan left by the previous run, or "none">
CANDIDATE : <task to be scored in Phase 1>
```

### Phase 1 — Pick ONE task + write the Definition of Done

```
Score = (User value 1–5  ×  Usage frequency 1–5)  ÷  Size 1–5
```

**The inherited plan is the default candidate.** Deviating is allowed, but the
reason must be written down — a plan that is routinely ignored becomes empty
ceremony.

**Learning bonus:** friction or rework that recurred across 2+ runs grants **+1** to
the score of the task that eliminates it. Mining a lesson beats an untested new
feature.

**Intake first:** anything the user attached to this `/autopilot` invocation is classified
and scored per §10 **before** selection, so a bug request competes on the same scale
as a feature instead of jumping the queue by being the most recent thing said.

**Cadence:**
- Run #N where `N % 3 == 0` → the slice must be audit/refactor.
- Run #N where `N % 5 == 0` → meta-review plus protocol patch is mandatory (§4D).
- Both at once (#15, #30, …) → do both. They stack; neither cancels the other.
- **An S1 bug (§10) overrides both**, and the override is recorded in the Run Log.
- A **standing user directive** to ship a feature every run outranks the cadence's
  prohibition but not its choice of slice: do the audit/refactor **and** the feature,
  recording both. Without such a directive, a cadence run ships no feature.

Take the highest score that **certainly fits** in one run. In doubt → split it.

**Definition of COMPLETE** (every box must be "yes", otherwise it is not a slice):
- [ ] Reachable from a normal entry point without secret knowledge
- [ ] Every input is human-fillable; no value is forced by the system
- [ ] Validation works; error messages state **how to fix it**
- [ ] The effect survives quitting and restarting the process
- [ ] Success confirmation is clearly visible
- [ ] The result shows up wherever else it belongs (list, report, API)
- [ ] It can be cancelled midway without leaving a stuck state

**Then write this iteration's Definition of Done** into `specs/LOOP_STATE.md` as a
checklist — **before writing any code**. A good DoD can be verified by someone else
without asking questions; "works well" is not a criterion.

### Phase 2 — References (use the cache, do not re-read)

- Pattern already in `specs/REFERENCE.md` → use it.
- Not there → read the specific source, then **append** a summary to the cache: API
  signature, minimal example, when to use it.
- If the search finds **nothing**, record that too as a gap — so the next run does
  not go looking again for something that does not exist.

### Phase 3 — Call-site inventory, then implement

**Before editing:** list EVERY path and caller that touches the behaviour being
changed (grep function names, types, routes, screens) and write the list into
`specs/LOOP_STATE.md`. When `specs/graph/` exists, start from its `Used by`
edges, then verify with grep — the map narrows the search; grep confirms it.
Editing one path and discovering the second one later is rework that five
minutes of searching prevents.

Follow `specs/LOOP_LEARNINGS.md` as a checklist, not as advice, and **§11
Engineering practices** as binding rules. For a bug task, §11B applies from the
first edit: the failing test comes before the fix, and the fix lands at the root
cause rather than at the reported symptom.

**Load the tier discipline for the code you are writing** — invoke the `Skill` tool
inline:

- Front-end code → `solodev:fe`. If the slice also needs visual direction, run
  `impeccable` for direction **first**, then build to it — `fe` owns structure, state,
  and runtime cost, not visual craft.
- Back-end code → `solodev:be`.
- A slice spanning both → both, and design the contract between them before building
  either side.

### Phase 4 — Real verification (MANDATORY, on the artifact that actually runs)

**Delegate this phase with the `Agent` tool, `subagent_type: "solodev:qa-runner"`**,
every run — including refactor runs, where the matrix narrows to regression and
persistence. It builds the test matrix, executes it against the real artifact, and
files reproducible bugs.

**When the slice touched a trust boundary** — auth, input handling, data access, file
upload, external requests — also spawn `subagent_type: "solodev:bug-hunter"` in the
same message as `qa-runner`, so the two run concurrently. A pure internal refactor
with no boundary change skips it, and the report says so. Any Critical or High finding
is an **S1**: it overrides the cadence and is fixed in this run, before the commit.

**In-slice** S1 and S2 findings are fixed in this run before the phase completes; an
in-slice S3 goes to the backlog with its origin. A finding **outside** the slice
follows §10 instead — and an out-of-slice S1 stops the run rather than being fixed.
The distinction is what makes both rules true at once: fixing a defect you just
introduced is finishing your own work, while fixing one you merely stumbled over is
scope creep the user did not ask for.

Play a **real user**, not a developer. Run the scenario from a normal entry point
through to completion. Green tests do not substitute for this phase.

| Product type | How to verify | Evidence to keep |
|---|---|---|
| CLI | run the commands | stdout/stderr transcript |
| TUI | run under tmux | `tmux capture-pane` per screen |
| Web / GUI | run it and operate it | screenshots |
| Library / SDK | a runnable example | example code plus its output |
| Service / API | call the endpoints | request and response |

**At least 5 pieces of evidence**, stored in `docs/evidence/<date>-<task>/`:
1. initial state · 2. mid-operation · 3. an error case ·
4. success confirmation · 5. the result visible elsewhere

Test the **tightest conditions first** (smallest terminal, smallest viewport, empty
data, longest input), then the roomy ones.

### Phase 5 — Quality critique (threshold rubric, honest)

**When the slice touched a user-facing surface, spawn both auditors in a single
message** so they run concurrently: `Agent` with `subagent_type:
"solodev:ux-auditor"` (can the task be completed) and `subagent_type:
"solodev:ui-auditor"` (how it presents). Neither can edit files, so every finding
comes back as a report rather than a silent fix.

A pure internal refactor or a library change skips both, and the report states that
it skipped them and why. A `ux-auditor` severity 4 or a `ui-auditor` blocker **fails
this phase** regardless of the rubric total.

See §5. **Passes at ≥14 of 16 AND no item scoring 0.** At most 3 improvement
iterations; still failing → descope and record the cause as a pitfall in
`specs/LOOP_LEARNINGS.md`.

Report **initial score → final score**, not the final alone — a final score by
itself cannot tell a smooth run from a bumpy one.

**Regression audit:** any item that scored <2 in the previous run must be re-checked,
and its score change stated explicitly.

### Phase 6 — Quality gates

Run the format, lint, and test commands recorded under "Detected stack" in
`specs/LOOP_STATE.md`. All must be green. New logic (parsers, formatters,
validation, calculations, business rules) requires tests.

`git ls-files -- specs docs` must print nothing — a tracked workspace file fails
this phase (§2). Untrack with `git rm -r --cached` and fix `.gitignore`.

Record how many times a gate failed in the Run Log — that is a metric, not a shame.

### Phase 7 — Mandatory documentation

See §6. A run that does not touch CHANGELOG and `docs/` **counts as failed**,
whatever the code achieved. README follows §6's usage test.

### Phase 8 — Review, commit & PR

The run works on its own branch, branched from the default branch once Phase 0
confirmed a clean tree, named **`<type>/<backlog-id>-<what-it-does>`** — say
`feat/f2-ship-cut-releases`. Type follows the id (`F-`/`E-`→`feat`, `B-`→`fix`,
`R-`→`refactor`, `C-`→`chore`), matching the run's Conventional Commit (§11A). Run
numbers are bookkeeping and stay in `specs/LOOP_STATE.md`.

1. **Review before committing** — `Agent` with `subagent_type:
   "solodev:pr-reviewer"`, against the working diff (§11F). It cannot edit, so it
   reports rather than patches. Blockers and majors are fixed in this run, before the
   commit exists.
2. **Commit** — §11A governs shape: Conventional Commits, one intent per commit, the
   diff read before committing. The message explains **WHAT** and **WHY**, not a
   restatement of the diff.
3. **Version** — user-visible change → bump SemVer and move `[Unreleased]` into a
   version section.
4. **Open the PR** — the `pr-new` skill, inline. It opens **ready**; draft only when
   the work is genuinely unfinished, and say why. Merging stays the user's. No remote
   or no `gh` → skip this step, say so in the report, and carry on.

Do not push or tag without permission if this repo has its own release rules; follow
the repo's rules when they exist.

### Phase 9 — Self-improvement + memory (MANDATORY — a run without it has failed)

See §4.

### Phase 10 — Report + next-iteration plan

Write the plan into `specs/LOOP_STATE.md` per §8, then report using the §9 template
exactly, with nothing omitted.

---

## §4 SELF-IMPROVEMENT PROTOCOL

Every run must: **Apply → Record → Prune**.

### A. Apply (before coding)
State explicitly which `LOOP_LEARNINGS.md` rules apply to this task and how you are
complying. Violating a recorded rule without a written reason is a regression.

### B. Record (after the quality gates)
Append a **Run Log** entry to `specs/LOOP_STATE.md`:
```
Run #N | task | rubric-iterations | score initial→final | rework? (cause) | gate failures
```

Then add **at least one new rule** to `LOOP_LEARNINGS.md`, OR state explicitly "no
new lesson" with the reason.

Rule format (one line, concrete, testable):
```
[category] If <concrete situation>, then <concrete action>.  (from: run #N)
```

**Valid sources — only things that actually happened this run:**
- rework that genuinely occurred
- a lint or test failure
- a rubric item that scored poorly
- friction you felt yourself during Phase 4 verification
- a guessed API that turned out wrong → also add an entry to `specs/REFERENCE.md`

Hypotheses, hunches, and "we should probably later…" are **not** rules.

**Claude Code memory** is written in this phase too: product decisions not captured
in code, the user's working preferences with their reasoning, and external
references used. Never copy state-file contents into it.

**The code map** is refreshed here when `specs/graph/` exists: re-map the modules
this run touched (`graph` skill, update mode). A map that lags the code misleads
the next run worse than no map would.

### C. Prune (keep the loop from bloating)
- Merge duplicate or adjacent rules.
- **Delete any rule now enforced by code, types, tests, or lint** — if the compiler
  guards it, the brain does not need to. Replace it with a pointer to the test.
- `LOOP_LEARNINGS.md` caps at **150 lines**. Over the cap → cut the least-used rules.
- `LOOP_STATE.md` **rolls off** to `specs/LOOP_ARCHIVE.md`, which Phase 0 never reads.
  Move — never delete — a closed backlog row the moment it is struck, and every Run
  Log entry older than the **three** most recent, its prose notes with it. The Run
  Log itself is one line per run and holds no prose. A finished task's call-site
  inventory and DoD checklist *are* deleted once the run is logged; the Run Log line
  is their record.
- **Both caps are enforced by `scripts/validate.py`, not by good intentions** — a cap
  that lives only in prose cannot fail, and this one silently did for four runs.
  The budgets: `LOOP_STATE.md` ≤ 14000 bytes, `LOOP_LEARNINGS.md` ≤ 150 lines.
  Pruning is what you do when the gate fails, not a thing you remember to do.

### D. Meta-review (every 5 runs)
Compute trends from the Run Log: is the rubric score rising? are iterations falling?
is rework recurring in the same area? Then produce a patch for this protocol:

```
PATCH v<old> → v<new>
Section : §x.y
Old     : "<old text>"
New     : "<new text>"
Reason  : runs #A and #C failed because ...
Metric  : expect <metric> to improve from X to Y
```

**Patch guardrails (absolute):**
1. §1 invariants may not be removed or weakened.
2. One patch changes at most 2 sections.
3. The protocol may not bloat: adding >5 lines requires deleting as many.
4. A patch is only valid if it points at a **real failure recorded in the Run Log**.
5. Bump the protocol version and record it in §12.

### E. Failure protocol
- The same task failing **2 runs in a row** → split it smaller and write a rule about
  the cause.
- Rubric failing 3 iterations → descope; do not force it.
- Failure caused by guessing an API → fix `specs/REFERENCE.md` first, then continue.

---

## §5 QUALITY RUBRIC

Score 0 / 1 / 2 per item. **Passes at total ≥14 with no item at 0.**

| # | Item |
|---|---|
| 1 | The flow is discoverable and reachable without secret knowledge |
| 2 | No broken text, layout, or output in the tightest conditions or the roomiest |
| 3 | Active, selected, or focused state is obvious at a glance |
| 4 | Controls are consistent and visible (keybindings, buttons, documented flags) |
| 5 | Post-action feedback is clear and does not vanish too fast |
| 6 | Fewest possible steps; no input forces a default value |
| 7 | Human formatting: numbers, dates, units; errors state how to fix them |
| 8 | Overall consistency with the parts of the product that already exist |

For products without a visual surface (libraries, APIs), translate items 1–4 into
public-surface ergonomics: discoverable, consistently named, mistakes caught by the
type system, and usage examples present in the docs.

---

## §6 DOCUMENTATION STANDARD (Phase 7 — no way out)

### README.md
Create it if missing. Must cover: what this product is, how to install it, how to run
it, and the current feature status. **Update it whenever a run changes how the
product is used.**

**Never write anything about the loop, this protocol, or any solodev skill into
README.md.** It documents the product to its users. The loop is *how the product got
built* — process, not product — and a reader installing it does not care and must not
be told. Fatal rather than stylistic: it leaks the maintainer's workflow onto the
public face of someone else's project. The same holds for `CHANGELOG.md` — log what
changed for a user, never which run changed it.

Test each line: **would it still belong if the product had been built by hand?** If
not, it belongs in `specs/LOOP_STATE.md`.

One exception: a repo whose *product is the workflow tooling itself*. This plugin's
own README documents `/solodev:autopilot` because the loop is the thing being shipped —
product documentation, not workflow leakage. The same test decides it, since built by
hand that README would say exactly the same.

### CHANGELOG.md
Keep a Changelog format plus SemVer. Create it if missing. Every run adds an entry
under `## [Unreleased]` in the appropriate subsection:
`Added` · `Changed` · `Fixed` · `Removed` · `Security` · `Internal`.

A pure refactor uses `Internal` — still recorded, never skipped.

### docs/
Create it if missing, with `docs/README.md` as the index. Minimum contents:
- one file per major user flow
- one architecture file explaining the module split and its reasoning
- `docs/evidence/` for verification evidence

**Every run must touch at least one file under `docs/`.** Feature runs update their
flow document; refactor runs update the architecture document; audit runs add their
findings.

---

## §7 DEFINITION OF DONE

Two levels. Both must pass.

**Level 1 — this iteration's DoD**, written in Phase 1 into `specs/LOOP_STATE.md`,
ticked item by item. Criteria that were not met are stated plainly in the report,
never quietly deleted.

**Level 2 — the universal DoD**, applying to every run:
- [ ] The slice was executed on the real artifact and worked end to end
- [ ] Evidence is stored under `docs/evidence/`
- [ ] The §5 rubric passes (≥14/16, no item at 0)
- [ ] Quality gates are green: format · lint · test
- [ ] No new stubs, placeholders, or `TODO`s
- [ ] §11 engineering practices were followed; for a bug, the test failed before the
      fix and the root cause was addressed (§11B)
- [ ] Anything found but deliberately left undone was filed to the backlog with its
      origin (§10)
- [ ] CHANGELOG.md and `docs/` were updated; README if usage changed (§6)
- [ ] `LOOP_STATE.md` and `LOOP_LEARNINGS.md` were updated (§4)
- [ ] Claude Code memory was updated, or declared to have nothing new
- [ ] **The next-iteration plan is written in `LOOP_STATE.md`** (§8)
- [ ] The commit explains what and why
- [ ] The §9 report is written in full

---

## §8 NEXT-ITERATION PLAN

Written into `specs/LOOP_STATE.md` under the heading
`## Next iteration plan (written by Run #N, for Run #N+1)`:

```
Task        : <id + title>
Score       : <n>  (Value <n> × Frequency <n> ÷ Size <n>)
Why this    : <tie it to a gap, the Run Log, or a user request>
Cadence     : run #<N+1> → <feature allowed / audit required / meta-review required>
Prereqs     : <what must exist first, or "none">
Slice       : <the concrete boundary that counts as complete for that run>
Risk        : <what could blow up the scope>
```

This plan **binds the next run's Phase 1 as its default candidate**. Deviating is
allowed as long as the reason is written down. This is what lets `/autopilot` in a fresh
session start working immediately without asking the user anything.

A feature the audit cadence deferred this run is the default `Task` here, and the
report says so — cadence may delay work, never lose it.

---

## §9 END-OF-RUN REPORT TEMPLATE

```
RUN #N — <id + task>   [feature | bug S<n> | enhancement | refactor | chore]

1.  DONE      : <what a user can now complete end to end>
2.  DOD       : <x/y criteria ticked — name the misses and why>
3.  EVIDENCE  : docs/evidence/<date>-<task>/ (name the key files)
4.  RUBRIC    : <initial>/16 → <final>/16 — weakest item: <#n, why>
5.  GATES     : format ✓ · lint ✓ · test ✓ (<count> tests)
6.  PRACTICE  : commit type · review pass done · for bugs: failing test first ✓, root cause ✓
7.  DOCS      : README <what changed> · CHANGELOG <entry> · docs/<file>
8.  BACKLOG   : <new items filed this run with ids and origin, or "none">
9.  MEMORY    : repo <files written> · Claude Code <name + type, or "nothing new + why">
10. LESSON    : [category] If ..., then ...  (or: none + why)
11. PATCH     : yes / no — <section and reason if yes>
12. NEXT      : <summary; full plan in specs/LOOP_STATE.md §Next iteration plan>
13. CANDID    : <steps that failed or were skipped, with output, or "none">
```

---

## §10 WORK INTAKE & CLASSIFICATION

Work reaches the backlog three ways: attached to the `/autopilot` invocation, added by
hand to `specs/LOOP_STATE.md`, or discovered by the loop itself during Phase 4.

Every item enters the backlog with a type-prefixed id, a score, and its origin.

| Type | Id | Scoring | Cadence rule |
|---|---|---|---|
| Feature | `F-<n>` | standard formula | subject to the audit cadence |
| Bug | `B-<n>` | severity-driven, see below | S1 overrides everything |
| Enhancement | `E-<n>` | standard formula | subject to the audit cadence |
| Refactor | `R-<n>` | usually low; chosen on cadence runs | this is what cadence runs pick |
| Chore / docs | `C-<n>` | low | folded into another run, rarely its own |

### Bug severity

| Sev | Meaning | Effect on selection |
|---|---|---|
| **S1** | Data loss, security hole, or a primary flow that cannot be completed at all | Taken immediately. **Overrides the audit/refactor cadence** and any inherited plan. Record the override in the Run Log. |
| **S2** | Primary flow broken but a workaround exists | `+2` to score |
| **S3** | Cosmetic, or an edge case unlikely in practice | standard formula |

A production bug that destroys data does not wait for a refactor run. This is the
only sanctioned way to break cadence, and it must be stated in the report.

### Backlog entry format

```
| B-7 | Ledger export writes an empty file when the period has no rows | 5 | 3 | 1 | 15.0 | S2. From: user report 2026-08-04 |
```

The `Notes` column always carries the **origin**: user report with its date, "found
during run #N verification", or "found by audit run #N". Origin is what later lets
the loop tell a recurring friction from a one-off.

### Findings during a run

Anything discovered in Phase 4 that is **outside the current slice is not fixed
now** — it is written to the backlog with its origin, and the report names it. This
is the main defence against scope creep: a run that fixes everything it stumbles
over finishes nothing and produces an unreviewable diff.

The exception is an **out-of-slice S1**: stop, report it, and let the user decide
whether to finish the current slice first. An S1 *inside* the slice under test is
this run's own defect — Phase 4 fixes it before the phase completes and does not
stop to ask.

---

## §11 ENGINEERING PRACTICES (binding, checked in Phases 3, 6, and 8)

### A. Version control
- **Conventional Commits**: `feat:` `fix:` `refactor:` `perf:` `docs:` `test:`
  `chore:`. The scope is the module, the body explains **why**.
- One commit, one intent. If the message needs "and", split the commit.
- Work on a branch; do not commit straight to the default branch unless the repo is
  explicitly trunk-based and the user agreed.
- Read the diff before committing. Never commit secrets, credentials, or `.env`
  files; if one was committed, say so immediately — rotating it is the user's call.

### B. Bug fixes
- **Reproduce first with a test that FAILS**, then fix, then watch it go green. A
  test written against already-correct code proves nothing.
- Fix the **root cause, not the symptom**: grep every caller of the function you are
  about to touch. Patching only the path named in the report leaves sibling callers
  broken.
- The regression test stays after the bug is closed.

### C. Code changes
- New code matches the surrounding style, naming, and comment density.
- No dead code and no commented-out code — version control already remembers it.
- Public API changes are documented, with a migration note.
- Breaking changes require a major bump and a migration section in the CHANGELOG.

### D. Testing
- New logic requires tests: parsers, formatters, validation, calculations, money,
  security paths.
- Tests assert **behaviour**, not implementation details.
- A flaky test is fixed or deleted, never retried into passing.

### E. Security & data
- Never log secrets or personal data.
- Validate input at trust boundaries, not deep inside.
- A new dependency needs a proven need, a licence check, and a vulnerability check.
  A few lines of code beat a new dependency.

### F. Review
- **Do not self-approve in the same pass that wrote the code.** The
  `solodev:pr-reviewer` subagent runs before every commit, in its own context and
  without edit tools, reading the change free of the author's assumptions about what
  it was supposed to do.

### G. Scope discipline
- Unrelated improvements spotted along the way go to the backlog, not into this
  commit.
- The boy-scout rule applies only to files the slice already touches.

---

## §12 PROTOCOL HISTORY

- **v1.0** — initial protocol, bootstrapped from the `dev-loop` skill.
- **v1.1** — §1 absorbed the three skill-only invariants; §3 Phase 1: stacked cadences.
- **v1.2** — §3 Phase 1: a standing feature directive outranks the cadence's
  *prohibition*, not its choice of slice (user ruling, `C-5`).
- **v1.3** — §3 Phase 8: branches are `<type>/<backlog-id>-<what-it-does>` (user
  directive).
- **v1.4** — §2: `specs/` and `docs/` never committed; §6: nothing about the loop in
  `README.md`/`CHANGELOG.md` unless the workflow tooling *is* the product. From live
  use: the plugin was contaminating the repos it ran in.
- **v1.5** — §3 Phase 8: PRs open **ready**, not draft. Opening is reversible,
  merging is not, and merging was already the user's.
- **v1.6** — ambiguity + token pass, by the user: invariant 5 scopes README to §6's
  usage test; the subagent prompt rules moved from the skill into §3 and now cover
  Phases 4/5/8 alike; Phase 6 enforces the §2 untracked-workspace rule; §4C prunes
  `LOOP_STATE.md`; §8 owns the deferred-feature guarantee; §10 S3 wording aligned
  with the `task` and `qa` skills.
- **v1.7** — the code map (`graph` skill), by the user: §2 lists `specs/graph/**`;
  Phase 0 reads `GRAPH.md` when present; Phase 3 starts the call-site inventory
  from its `Used by` edges, grep-verified; §4B refreshes touched modules' cards.
  The map is optional — no phase fails for its absence.

- **v1.8** — roll-off, by the user: §2 adds `specs/LOOP_ARCHIVE.md`; §4C replaces
  "prune the Run Log to its last 20 lines" with **move, never delete** — closed
  backlog rows and Run Log entries older than the last three go to the archive,
  which Phase 0 is told not to read. Both Phase 0 caps are now enforced by
  `scripts/validate.py` (`LOOP_STATE.md` ≤ 14000 bytes, `LOOP_LEARNINGS.md` ≤ 150
  lines). Recorded failure: the 150-line cap was prose for four runs and the file
  was over it, unnoticed; `LOOP_STATE.md` more than doubled across three runs while
  every refactor aimed at the fixed half of the read.

- **v1.9** — the S1 contradiction (`C-3`), by the user: §3 Phase 4 said S1 and S2
  findings "are fixed in this run", §10 said an S1 found mid-run means "stop, report
  it, and let the user decide". Both now scope themselves: **in-slice** S1/S2 are
  fixed by Phase 4; an **out-of-slice** S1 stops the run per §10. Recorded failure:
  run #1 acted on the §3 reading twice without noticing the other rule existed —
  found by `pr-reviewer` in run #1 Phase 8 and open for five runs.
