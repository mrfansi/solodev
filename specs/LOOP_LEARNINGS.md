# LOOP LEARNINGS

> Rules here are **BINDING** for every run. Read in Phase 0, written in Phase 9.
>
> Format: `[category] If <concrete situation>, then <concrete action>. (from: run #N)`
>
> **150 lines maximum.** Any rule now enforced by code, types, tests, or lint MUST be
> deleted and replaced with a pointer to the test — if the compiler guards it, the
> brain does not need to.
>
> Valid sources are only things that actually happened: rework, gate failures, poor
> rubric items, friction felt during verification, a guessed API that was wrong.
> Hypotheses and "we should probably later" are not rules.

## Rules

- `[backlog]` If a backlog candidate is phrased as "X duplicates Y", then open both
  files and read them before scoring it. (from: run #1 — "agent definitions duplicate
  their skills" was drafted, scored, and about to be filed; reading
  `agents/qa-runner.md` showed the agents already delegate via the Skill tool and only
  add a return contract. There was nothing to deduplicate.)

- `[measurement]` If a run's task is justified by a cost — tokens, time, size — then
  measure the cost and store the number as evidence before proposing the fix. (from:
  run #1 — "the protocol is a token eater" was the premise; measuring it produced
  ~6,151 tokens with a per-section breakdown, which is what turned a 40% cut into a
  concrete plan instead of a hunch.)

- `[verification]` If a run's deliverable is files, then before Phase 8 run
  `git add -n` on every directory the run created and confirm git would actually stage
  them. (from: run #1 — `.gitignore` had grown `specs/` and `docs/` mid-run. `git
  commit` would have exited 0 with those directories absent, the report would have
  claimed success, and the next session would have found an empty `specs/`. The whole
  run's output, lost silently. Reading the diff would not have caught it; only running
  git did.)

- `[docs]` If documentation states a command a user is expected to run, then run the
  command itself — not a check that its arguments look plausible. (from: run #1 —
  `README.md` told users `/plugin marketplace add mrfansi/claude-solodev`, which does
  not exist. The fix pointed it at `mrfansi/solodev` and verified with `gh repo view`,
  which passed. `pr-reviewer` then found that repo is **empty**, so the documented
  command still fails. Checking that the name resolves is not checking that the
  command works, and the run had already written this rule when it made that exact
  mistake.)

- `[claims]` If a run reports a measured number as its headline finding, then list the
  inputs to that measurement explicitly and check them against the spec that defines
  what gets read. (from: run #1 — the per-run token cost was reported as ~9,071 from
  two files. Protocol §3 Phase 0.3, in the very file being measured, mandates six.
  The real figure is ~14,240, and the four uncounted files include the two that grow
  without any cap — which was the more important half of the problem.)

- `[authoring]` If a shell command is going into a markdown file, then put it in a
  fenced block, never in a table cell. (from: run #2 — a table cell must escape `|` as
  `\|`, and that escape survives being copied into the shell. Inside `grep -E`, `\|`
  is a *literal pipe*, so `(TODO\|FIXME\|HACK\|XXX)` searched for that exact string
  and returned 2 hits where the working command returns 19. The flagship seam of a
  brand-new skill could not have found anything, and the skill's own raw-hit-count
  rule could not catch it, because the raw count really was 2. Note the sibling case:
  the same escape in a *BRE* command — no `-E` — is correct alternation, so this fails
  only in the ERE half.)

- `[evidence]` If a transcript measures a repo that will contain that transcript, then
  regenerate it as the last step before commit and say the number is a snapshot.
  (from: run #2 — the seam-1 raw count moved 15 → 19 across three edits, because every
  new sentence discussing `TODO` became a hit for the seam searching for `TODO`. Two
  transcripts disagreed until the last one was regenerated.)

## Recurring pitfalls

_(filled when the rubric fails 3 iterations, or the same task fails 2 runs in a row)_

## Agreed patterns

- **One rule lives in exactly one file.** The protocol owns what a run must obey;
  skills own how to do the work; agent files own the return contract; scheduling is
  the loop skill's alone. Consolidation precedent: the eleven invariants moved out of
  `skills/loop/SKILL.md` into protocol §1. See `docs/architecture.md`.

- **The protocol is the expensive file.** `specs/LOOP.md` is read in full at Phase 0
  of every run. Anything added to it is paid for forever. Guidance a run does not
  strictly have to obey belongs in a skill, loaded on demand.
