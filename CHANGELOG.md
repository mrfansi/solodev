# Changelog

All notable changes to this project are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

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

### Fixed

- **Install command pointed at a repository that does not exist.** `README.md` said
  `/plugin marketplace add mrfansi/claude-solodev`; the published repository is
  `mrfansi/solodev`. Anyone following the README could not install the plugin at all.
- Agent-count claims in `README.md` and `skills/loop/SKILL.md` said "three of the
  four" after `bug-hunter` shipped as the fifth agent.
- The UX severity rule was ambiguous about severity 3: severity 4 fails the rubric
  outright, severity 3 is fixed in the same run without failing it.

### Internal

- `.gitignore` now carries a comment stating that `specs/` and `docs/` must stay
  tracked. Run #1 found both directories ignored in its working tree, which would
  have produced a bootstrap commit containing none of the machinery it installed —
  with no error. The bad lines were never committed, so this is a guard, not a fix.
- The eleven invariants now live only in protocol §1. `skills/loop/SKILL.md` points
  at them instead of keeping a second copy that could drift.
- Protocol §3 Phase 1 states what happens when the audit cadence and the meta-review
  cadence land on the same run: they stack, neither cancels the other.

[Unreleased]: https://github.com/mrfansi/solodev/compare/HEAD...HEAD
