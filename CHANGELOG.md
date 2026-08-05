# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **The quality gate now refuses to let the loop's own rules go backwards.** A repo
  running the loop keeps its protocol in `specs/`, which is deliberately not committed
  — so it accumulates across runs while the copy that ships with the plugin does not.
  Editing the shipped copy from an older starting point and putting it back over the
  live one reverted a rule that had been agreed one run earlier, and no diff looked
  wrong, because both files ended on the same version number. The gate now remembers
  the highest version it has seen and fails if the live protocol drops below it.

  `python3 scripts/validate.py --selfcheck` proves the check can fail: 40 assertions
  against real files, including every shape the bookkeeping file can take that would
  otherwise have let a regression through, or destroyed the protocol outright.

- **A hook that stops you committing the workspace.** Installing the plugin now
  installs one Claude Code hook (`PreToolUse`, on Bash). It blocks a `git commit` that
  would put `specs/` or `docs/evidence/` into git history — bookkeeping, and raw
  transcripts of whatever a run printed, which is an open-ended capture surface for a
  credential. Git history is permanent; this is the one rule worth enforcing in code
  rather than trusting an agent to remember it.

  It is quiet by design. A repository with no `specs/LOOP.md` never opted in and is
  never touched. **Your own `docs/` stays yours** — the hook blocks only on `specs/`
  and `docs/evidence/`, never on documentation you wrote, even in a repository running
  the loop. Anything it cannot parse is allowed through: a guard that blocks when it is
  confused is worse than the leak it prevents.

  It reads the command rather than pattern-matching it, so `cd elsewhere && git commit`
  and `git -C elsewhere commit` are checked against the repository they actually commit
  to, and `git log --author='git commit'` is not mistaken for a commit.
  `python3 hooks/guard-workspace.py --selfcheck` decides every case against throwaway
  repositories. Behaviour and limits: `docs/flows/hooks.md`.

  Set `SOLODEV_NO_GUARD=1` if a repository commits its workspace on purpose.

- **`token-cost.py --agents` — the bill, by agent type, across every session.** One
  command for the question "is this check worth what it costs": spawns, turns and
  total per agent type. Totals only, never averages — deciding whether to remove
  something is a question about the bill it removes, and an average cannot answer it,
  because dropping the dearest item lowers the bill while raising the mean.

  `--selfcheck` asserts the accounting on a fixture: dedup by message id, the
  streamed-output rule below, orphan counting, and the weights.

- **`scripts/token-cost.py` — what a session actually processed.** It reads the
  `usage` block Claude Code records for every assistant message in its own
  transcripts, including each subagent's, so the figure is measured rather than
  estimated. It reports turns, the three token classes separately, and an
  input-equivalent total — never a single number called "cost", because roughly nine
  tenths of the volume is cache reads billed at about a tenth of fresh input, and the
  ratio between volume and spend is not constant. `skills/autopilot/references/PROTOCOL.md`
  §4B now requires the figure in every Run Log line.

  Two things it makes visible that guesswork had hidden. A session's prompt tokens are
  the sum of the context at every turn, so a token admitted early is re-read by every
  turn after it — turn count, not file size, is what moves. And a subagent's context is
  its own: they run a fifth to two fifths of a session's tokens, which is far more than
  the size of the reports they hand back suggests.

  Figures live in the dated evidence directory rather than here, because transcripts
  keep growing and a number pasted into a changelog is wrong by the next session.

- **`/solodev:pr-review` now posts its findings to the pull request** as a `COMMENTED`
  review, instead of leaving the verdict in a session that ends. The review sits where
  the next reader finds it.

  It posts `COMMENTED` because that is the only state GitHub permits on a pull request
  you opened yourself — `--approve` and `--request-changes` are both rejected outright.
  So `approved` and `changes_requested` never appear on a solo developer's own PR, with
  or without this plugin, and the skill now says so rather than letting the absence read
  as a failure. On someone else's PR `--request-changes` is used when a blocker
  survives; approval is left to a human.

### Changed

- **A loop run no longer reviews its own work.** It used to spawn a reviewer over its
  own diff before every commit. It does not any more: it opens the pull request and
  stops there. Reviewing is `/solodev:pr-review`, which now runs only when you invoke
  it, and the PR a run opens should be treated as unreviewed until you have.

  This is a deliberate trade, so it is worth saying what is on both sides. The
  automatic pass was productive — every one of its invocations returned findings, none
  ever came back clean — and nothing replaces it. What it was not, is a review: a
  check a tool runs on itself and can act on alone is a step in a pipeline, and the
  point of a review is that a second party decides. Getting that back is one command.

- `scripts/validate.py` now checks `hooks/hooks.json`: that the file exists, that it
  parses, that every event name is a real Claude Code hook event, and that every
  `${CLAUDE_PLUGIN_ROOT}` script path resolves. Nothing at runtime reports a hook that
  failed to load, so a hook that never fires is indistinguishable from one that works.

- **Protocol v1.12: orientation checks that past work actually landed.** A change can
  be committed, reviewed and written up as finished while its branch never reaches the
  default one, and nothing looked. Orientation now does, in a single command, and
  distinguishes the two cases that matter: a branch carrying work the default branch
  lacks is a real gap, while an unmerged branch whose diff is empty is a stale pointer
  and is ignored. Each gap either lands or gets recorded, so the check cannot decay
  into noise nobody reads.

- **`/solodev:pr-new` carries the one exception to its own rule.** It forbids workflow
  detail in a PR body — run numbers, phases, patch arithmetic — but the ban had no
  exception written beside it, which made it simultaneously too strict to follow in a
  repo whose product *is* the workflow tooling and too vague to catch the real leak.
  The exception is now stated where the rule is, with the by-hand test that decides it.

- **Protocol v1.11: prune before you add.** §4C used to say pruning is what you do
  when a cap fails. That turned every cap into a mid-edit interruption — check the
  budget first, make room, then write. The §4D bloat guardrail is also explicit now
  that its five-line allowance is measured net, which it had never said.

- **`/solodev:discover` runs in a subagent.** A whole-repo sweep is thousands of lines
  of grep output mined down to at most five backlog rows, and until now every one of
  those lines landed in the context of whoever asked. The skill now sets
  `context: fork` with `agent: general-purpose`, so the sweep happens in its own
  context and only the report comes back. `background: false` keeps that report
  arriving in the same turn — nothing changes for the person typing the command, and
  it is why `/solodev:discover` now needs **Claude Code 2.1.218 or later**. How much
  output this keeps out of your context is not yet measured against a real forked run,
  so no figure is claimed here.

### Fixed

- **A run no longer leaves you standing on the branch it just proposed.** After
  opening the pull request it returns to your default branch and pulls it. Staying put
  meant the next run cut its branch from work that was not merged yet, so each run
  carried the previous one's changes inside its own diff and the two drifted further
  apart with every iteration — until a pull request that had been clean turned
  conflicted because others had landed ahead of it.

- **Token figures were undercounting output by roughly sixteen times.** Claude Code
  repeats a message's `usage` on every content-block line, and while the three prompt
  fields are identical across those copies, `output_tokens` grows as the message
  streams — the first copy is partial, the last is the total. Deduplicating by message
  id kept the first. Since output carries the heaviest weight, every input-equivalent
  figure came out about 1.3x low, and unevenly enough (1.11x to 1.54x) that it did not
  cancel in any comparison between agents.

- **`discover`'s seams could not see the loop's own workspace on a machine where
  `grep` is wrapped.** Ripgrep and token-proxy wrappers honour `.gitignore`, and the
  two directories the loop keeps its evidence in are gitignored by design — so seam 1
  returned 4 hits where the real answer is 22, and seams 2 and 3 read trees that came
  back empty. The skill now carries a probe that detects it before the sweep starts.
  The probe has to recurse from `.` and list paths only: naming the ignored directory
  directly returns the same result either way, and asking for line numbers prints
  matched text containing the very filename you were told to look for.

### Internal

- **The validator checks the three forking keys.** `context` must be `fork` if
  present; `agent` and `background` are errors without it; `background` must be a
  boolean; and a forked skill's `agent` must be a built-in or resolve to an
  `agents/*.md` file. Forking into an agent that cannot edit files warns rather than
  fails — correct for a read-only skill, wrong for one that writes its own output.
  A typo in any of these keys is otherwise silent: the skill simply keeps running
  inline, which is the exact behaviour the key was set to stop.

- **Every skill prints a score the same way.** `task` and the two loop templates wrote
  `(Value 5 × Frequency 3 ÷ Size 1)` while `discover` wrote `(V5 x F3 / S1)` for the
  same number, so two teammates reporting the same backlog row disagreed on how it
  looked. All four output templates now use the ASCII form, which is the safer one in
  a terminal. The formula *definitions* keep `×` and `÷` — those are read, not printed.

## [0.3.0] - 2026-08-04

### Added

- **CI runs the validator.** `.github/workflows/validate.yml` executes
  `python3 scripts/validate.py` on every push and pull request. It was the repo's
  only executable gate and it fired only when someone remembered to type it. No
  dependencies to install — the runner already has Python 3. Verified against a
  clean detached-HEAD clone, which is what `actions/checkout` produces and the one
  place a locally-green run could still fail: no `specs/`, no `docs/`, no branch
  name, all three special-cased by the validator.

- **`/solodev:graph` — the teammate who has read the whole codebase.** Builds a
  greppable knowledge graph under `specs/graph/` (inspired by
  [graphify](https://github.com/Graphify-Labs/graphify)): a ≤100-line index with god
  nodes and module edges, one ≤60-line card per module, every claim marked
  `EXTRACTED` with a `file:line` or `INFERRED` — never one dressed as the other.
  Builds fan out one `solodev:code-mapper` subagent per module (at most 10),
  each writing its own card and returning only its index row; updates re-map only
  the modules `git diff` says changed since the stamped `Built-at` commit. Queries
  read the index, open 1–2 cards, and verify every asserted claim against live code
  before answering — the map narrows the search, grep confirms it — and fix any card
  the code contradicts in the same pass.
- **Protocol v1.7 wires the map into the loop, optionally.** Phase 0 reads
  `GRAPH.md` when it exists instead of re-exploring; Phase 3 starts the call-site
  inventory from the `Used by` edges, grep-verified; §4B refreshes the cards of
  modules the run touched. No phase fails when the map is absent.

### Changed

- **The protocol's patch history moved out of the protocol — v1.10.** §12 is now a
  five-line pointer; the entries live in `skills/autopilot/references/PROTOCOL-HISTORY.md`,
  and a patch made in your own repo appends to `specs/LOOP_ARCHIVE.md` instead. The
  history had reached a tenth of the whole protocol while governing no phase — every
  run read it, and only a §4D run (one in five) had any use for it.

  This is `R-1` in part. **The rest of `R-1` was measured and rejected**: the plan was
  to move §5–§12 out of the start-of-run read entirely, on a claim that it would cut
  40%. Remeasuring showed the claim counted the *size* of those sections and never
  their *frequency* — six of the eight are needed by every single run, four because an
  invariant says so. Moving them relocates tokens between phases instead of removing
  them. Only §12 was genuinely cold, and only §12 moved.

- **The loop's state file rolls off instead of growing forever — protocol v1.8.**
  Closed backlog rows and Run Log entries older than the three most recent now
  **move** to `specs/LOOP_ARCHIVE.md`, which the start of a run never reads. Moving,
  not deleting: the decision trail behind a closed item is why the backlog keeps
  closed rows at all. The Run Log itself is one line per run and carries no prose.
  This replaces §4C's old "keep the last 20 lines" prune, which deleted what it
  trimmed and contradicted the backlog's own rule.

- **The two read-every-run caps are enforced by `scripts/validate.py`, not by prose.**
  `specs/LOOP_STATE.md` fails the gate over 14000 bytes; `specs/LOOP_LEARNINGS.md`
  over 150 lines. The 150-line cap had been claimed in a file header since the first
  run and the file had been over it for four runs, unnoticed — a cap that cannot fail
  is not a cap. Both budgets come from measurement, and both are skipped silently in
  a repo where the loop has never run.

- **The loop skill is now `/solodev:autopilot`.** `skills/loop/` renamed to
  `skills/autopilot/`; every invocation and path reference updated. Behaviour is
  unchanged — same protocol, same state files in `specs/`.

- **Protocol v1.6 — the ambiguity and token pass.** Invariant 5 no longer forces a
  README edit on every run: CHANGELOG and `docs/` move every run, README moves when
  the run changed how the product is used (§6's test already said so; the invariant
  contradicted it). The subagent prompt rules — what every prompt carries, the
  wait-for-helpers rule, what runs inline, the fallback when an agent type is missing
  — moved from `skills/loop/SKILL.md` into protocol §3, so one file owns them and the
  skill no longer argues with the protocol. Phase 6 now actually enforces §2's claim
  that a tracked `specs/` or `docs/` fails the gate. §4C prunes `LOOP_STATE.md` (Run
  Log caps at 20 lines, finished tasks collapse to their log line) so the file the
  loop reads every run stops growing without bound. §8 owns the guarantee that a
  cadence-deferred feature becomes the next run's default task.
- **Agent files no longer restate their skill's rules.** Each agent loads its skill
  and now states the precedence explicitly: the skill owns the method and severity
  scale, the agent owns the return shape. One copy of each rule, and roughly a third
  less text loaded on every agent invocation.
- **Every skill and agent description was cut to its triggers.** Descriptions load
  into every session whether or not the skill runs; the justification prose they
  carried belongs in the skill body, which loads only on use.

- **Branch naming follows `<type>/<backlog-id>-<what-it-does>`** instead of
  `loop/run-<N>-<slug>`. The type matches the Conventional Commit the run will write,
  so branch and commit cannot disagree; the backlog id makes the branch traceable
  without opening anything; the description says what the branch does rather than
  which run made it. Protocol v1.3. `scripts/validate.py` warns on a branch that does
  not conform — a warning, not an error, so it never fails the gate on `main` or in a
  repo that has not adopted the loop.

### Fixed

- **The two contradictory S1 rules now scope themselves — protocol v1.9.** Phase 4
  said an S1 finding "is fixed in this run"; §10 said an S1 found mid-run means
  "stop, report it, and let the user decide". Both are true, of different things, and
  neither said which: an S1 **in** the slice under test is the run's own defect and
  Phase 4 fixes it, while an S1 **outside** the slice stops the run and goes to the
  user. Run #1 acted on the Phase 4 reading twice without noticing the other rule
  existed; the ambiguity stood for five runs.

- **An agent's findings could vanish if it spawned helpers of its own.** A helper
  reports to the agent that spawned it, not to that agent's caller — so an agent
  returning before its helpers finished left their findings reaching nobody, while the
  caller saw only an idle notification with no report attached. Every agent now carries
  an explicit instruction to wait and fold helper findings into its own report, or not
  to spawn at all, and the quality gate fails if any agent is missing it.

- **Pull requests open ready for review instead of as drafts.** The rule said "always
  draft" in five places while `pr-new` itself said draft was conditional; the "always"
  won. Opening a PR is reversible and merging is not — merging was already the user's
  decision, so the draft default bought no safety, notified nobody on a solo
  repository, and cost a click before anything could happen. Draft is still there for
  work that is genuinely unfinished, and the report now names the reason.

- **The loop no longer contaminates the repository it runs in.** `specs/` and `docs/`
  are added to `.gitignore` at bootstrap and are never committed; the quality gate
  fails if either is tracked. `docs/evidence/` stores raw transcripts of whatever
  commands a run executed, which is an open-ended capture surface — an environment
  dump, an API response, a request with an auth header — and anything committed to git
  history is permanent.
- **Nothing about the loop is written into `README.md`, `CHANGELOG.md`, or a PR body.**
  Those describe the product to its users; the loop is how the product was built. The
  exception is a repo whose product *is* the workflow tooling, which is why this file
  documents the skills themselves.

  Reported from live use in another repository. Protocol v1.4.

  **Trade-off, stated rather than hidden:** the loop's memory no longer survives a
  fresh clone. A new checkout has no `specs/LOOP.md`, so it bootstraps from scratch.
  Back the directory up outside git if the backlog and Run Log matter to you.

- **`/solodev:discover` seam 2 only worked inside this plugin's own repository.** Its
  commands grepped `skills/*/` and `agents/*.md`, which exist nowhere else, while the
  skill claims to sweep any repo. The seam now states the generic shape — compare what
  the docs name against what the code ships — with the layout-specific halves marked
  for substitution.
- **README claimed `qa-runner` edits "evidence only".** Nothing enforces that; the
  agent keeps full edit access because QA must write evidence and temporarily revert
  a fix to prove a test catches it. The table now says so.
- **`CHANGELOG.md` had two `### Fixed` headings under `[Unreleased]`.** Merged.

### Internal

- `scripts/validate.py` now fails if the S1/S2/S3 severity definitions in the
  protocol, `task`, and `qa` drift apart — they are duplicated by design so each
  skill works standalone, and the check is what keeps the copies identical.

## [0.2.0] - 2026-08-04

### Added

- **`/solodev:ship` — the teammate who cuts a release.** Derives the SemVer bump from
  what `[Unreleased]` actually contains, moves the version everywhere it lives, cuts
  the changelog into a dated section with the right link references, and commits the
  bump alone. It **stops before tagging and pushing** and prints those commands
  instead — the two irreversible steps stay the user's.
- **`/solodev:be` and `/solodev:fe` — the implementation tiers.** Back-end engineering
  (boundaries, API and data design, transactions) and front-end engineering
  (architecture, state, runtime cost, code-level accessibility). The loop loads them
  inline in Phase 3; each also works standalone.
- **`/solodev:task` — files work into the backlog without starting a run.** Classifies,
  scores, and queues a feature, bug, enhancement, refactor, or chore, and says where it
  landed and when the cadence will reach it.
- **`/solodev:bug-hunter` — the security audit.** Thinks like an attacker against your
  own code: injection, broken access control, auth flaws, secrets exposure, SSRF, and
  logic-level abuse. Ships as a subagent too, spawned in Phase 4 when a slice touches a
  trust boundary.
- **`/solodev:discover` — the teammate who decides what to build.** Every other skill
  acts on work someone already decided on; this one finds work the repo proves is
  needed but nobody filed. It works six seams — abandoned `TODO`/`FIXME` markers,
  documentation describing behaviour no code implements, findings named in past
  evidence but never queued, blind spots the quality gate cannot fail on, friction
  repeating across the Run Log, and work `git` shows was abandoned — then classifies,
  scores, deduplicates against decisions already made, and files at most five rows.
  Every row must cite a file, a line, a hash, or a command; an item that cannot be
  pointed at is an opinion, not a task. It reuses `/solodev:task`'s scoring and row
  format rather than carrying a second copy.

- `specs/` — the loop's own state now lives in this repo: `LOOP.md` (protocol v1.1),
  `LOOP_STATE.md` (detected stack, scored backlog, Run Log, next-iteration plan),
  `LOOP_LEARNINGS.md`, and `REFERENCE.md`.
- `CHANGELOG.md` and `docs/` — the protocol requires both of every repo the loop runs
  in, and this repo had not applied that rule to itself.
- `docs/architecture.md` — why the plugin splits into skills, agents, and a protocol,
  and which of the three owns each rule.
- `docs/evidence/2026-08-04-bootstrap/` — the measured per-run token cost, kept so
  later runs can diff against it rather than re-argue from impressions.
- `scripts/validate.py` — checks both manifests, every skill and agent frontmatter
  block, and every cross-reference between skills, agents, and the README. Now wired
  in as the repo's lint and test gate.

### Changed

- **`scripts/validate.py` gained two checks it should always have had.** It now fails when
  `.gitignore` would exclude any file or directory under `specs/` or `docs/` — what
  the protocol requires every run to commit, and the exact bug that would have
  silently emptied the first bootstrap commit. It also scans `docs/architecture.md`
  for the agent-count claim. **The check took four attempts**: the first could never
  fire (`git check-ignore` skips tracked paths), the second missed `docs/evidence/`,
  the third missed `*.txt`. Each passed the obvious injection and failed a narrower
  one. Every version was demonstrated failing on broken input before being trusted.

### Fixed

- **Install command pointed at a repository that does not exist.** `README.md` said
  `/plugin marketplace add mrfansi/claude-solodev`; the published repository is
  `mrfansi/solodev`. Anyone following the README could not install the plugin at all.
- Agent-count claims in `README.md` and `skills/loop/SKILL.md` said "three of the
  four" after `bug-hunter` shipped as the fifth agent.
- The UX severity rule was ambiguous about severity 3: severity 4 fails the rubric
  outright, severity 3 is fixed in the same run without failing it.

### Internal

- **`skills/loop/SKILL.md` no longer restates the protocol.** The agent-per-phase
  table, the work-intake and bug-severity table, the branch-and-draft-PR rules, and
  the layer-1 state-file table each existed in both the skill and `specs/LOOP.md`;
  the skill now points at the section that owns them. Roughly 500 tokens saved on
  every run; exact figures in `docs/evidence/2026-08-04-skill-dedup/`. Five clauses survived because they exist nowhere else:
  that `task` loads inline, that `pr-new` runs inline rather than as a subagent, what
  to do when a subagent type is unavailable, that every agent's prompt must carry its
  slice and evidence path, and that a feature deferred by the cadence becomes the next
  run's first candidate.
  **The last two were deleted first and restored after review** — one because a
  two-clause table row was checked as a single claim, one because a phrase match
  ignored the quantifier ("each agent's" against the protocol's "its"). The
  grep-before-delete method needs both guards; see `docs/architecture.md`.
- `.gitignore` now carries a comment stating that `specs/` and `docs/` must stay
  tracked. They had been ignored in a working tree, which would have produced a
  commit containing none of the machinery it claimed to install — with no error. The
  bad lines were never committed, so this is a guard, not a fix.
- The eleven invariants now live only in protocol §1. `skills/loop/SKILL.md` points
  at them instead of keeping a second copy that could drift.
- Protocol §3 Phase 1 states what happens when the audit cadence and the meta-review
  cadence land on the same run: they stack, neither cancels the other.

[Unreleased]: https://github.com/mrfansi/solodev/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/mrfansi/solodev/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/mrfansi/solodev/releases/tag/v0.2.0
