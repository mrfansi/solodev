# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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

### Fixed

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

### Changed

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
  tracked. Run #1 found both directories ignored in its working tree, which would
  have produced a bootstrap commit containing none of the machinery it installed —
  with no error. The bad lines were never committed, so this is a guard, not a fix.
- The eleven invariants now live only in protocol §1. `skills/loop/SKILL.md` points
  at them instead of keeping a second copy that could drift.
- Protocol §3 Phase 1 states what happens when the audit cadence and the meta-review
  cadence land on the same run: they stack, neither cancels the other.

[Unreleased]: https://github.com/mrfansi/solodev/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/mrfansi/solodev/releases/tag/v0.2.0
