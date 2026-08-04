---
name: pr-new
description: Open a pull request whose title and body follow GitHub best practice. Use when asked to create or open a PR, or when a finished slice is ready for review. Also invoked by the loop skill after a run commits. Optional title argument; the rest derives from the branch.
---

# pr-new

`/solodev:pr-new [title]`

Produce a PR a reviewer can act on without asking questions. The title is derived
from the commits when no argument is given.

## 1. Preflight

Stop and report instead of guessing if any of these fail:

```bash
gh auth status                          # authenticated?
git rev-parse --abbrev-ref HEAD         # not the default branch?
git status --short                      # nothing uncommitted left behind?
gh pr view --json number,url 2>/dev/null   # a PR already open for this branch?
```

- On the default branch → create a topic branch first, never open a PR from it.
- Uncommitted changes → commit or stash them; a PR that omits local work misleads
  the reviewer.
- PR already open → **update it** (`gh pr edit`) instead of opening a duplicate.

## 2. Gather context

```bash
BASE=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name)
git log --oneline "origin/$BASE..HEAD"
git diff --stat "origin/$BASE...HEAD"
```

Read the actual diff, not just the stat. A PR description written from commit
subjects alone repeats what the reviewer can already see and explains nothing.

**Size check:** if the diff exceeds ~400 changed lines excluding generated files and
lockfiles, say so and recommend splitting. Review quality falls off a cliff past
that size. Proceed if the user insists, but note it in the body.

## 3. Title

Conventional Commits, imperative mood, no trailing period, ≤72 characters:

```
feat(ledger): export account statement as PDF
fix(auth): reject expired tokens on refresh
refactor(ui): extract render layer into its own module
perf(db): batch invoice lookups to remove the N+1
```

The title names the **outcome**, not the activity. `feat(export): add ledger PDF` is
useful; `update export module` is not — every PR updates some module.

Breaking change → add `!` after the scope: `feat(api)!: rename balance field`.

## 4. Body

```markdown
## Summary

<Two or three sentences: what changed and WHY. The why is the part the diff
cannot show, so it carries the most weight.>

## Changes

- <change stated as an outcome, not a filename>
- <...>

## How to test

1. <exact steps a reviewer can follow>
2. <...>

Expected: <what they should see>

## Evidence

<screenshots, terminal output, or a link to the evidence directory>

## Breaking changes

<None. — or: what breaks, and the migration path.>

## Related

Closes #<issue>
```

Rules that decide whether the body is worth reading:

- **Never paste the diff into the body.** GitHub already renders it.
- Drop empty sections rather than leaving them with "N/A" — noise costs attention.
- "How to test" must be runnable by someone who did not write the code. "Run the
  tests" is not a step; name the command and the expected result.
- Use `Closes #n` / `Fixes #n` so the issue closes on merge. `Related to #n` when it
  should stay open.
- Anything you deliberately left undone belongs in the body, not in the reviewer's
  discovery process.

## 5. Create

Show the rendered title and body to the user first, then create:

```bash
gh pr create --title "<title>" --body-file <file> --base "$BASE"
```

- **Open it ready, not draft.** A draft PR is for work that is genuinely unfinished:
  CI has not run, a dependency is unmerged, you want early eyes on a direction. Add
  `--draft` for those and say which one applies. Opening a PR is not an irreversible
  act — merging is — so defaulting to draft buys no safety and costs the author a
  click before anything can happen.
- Add `--reviewer` only when the user names reviewers; do not guess who should review.
- **Do not merge.** Opening a PR and merging it are separate decisions, and the
  second one is the user's.

Report the PR URL when done.

## Never leak the workflow

A PR body is read by whoever reviews the product. **Do not name the loop, a run
number, a backlog id, a phase, or patch arithmetic in it.** The loop's bookkeeping
lives in `specs/LOOP_STATE.md`, which is not committed.

The test is protocol §6's: **would this line still belong if the change had been made
by hand?** "PRs now open ready for review instead of as drafts" passes — the product
changed.
"Guardrails: §1 untouched, net +5 lines" does not; that is proof you followed your own
process, and no reviewer asked for it.

§6's exception applies here too. In a repo whose *product is the workflow tooling*, a
PR that changes the protocol describes the protocol, because the protocol is what
ships. The by-hand test still decides line by line, and it still rejects the
bookkeeping — which is how a real PR on this repo shipped a guardrail tally before an
audit caught it.

## When the loop skill invokes this

Runs unattended after a run commits, so:

- Ready by default, exactly as when invoked by hand. Draft only for the reasons in
  step 5, and the report names the reason.
- Title comes from the run's task and type; body's Summary comes from the run report.
- "Evidence" links to `docs/evidence/<date>-<task>/` from that run.
- "How to test" reuses the verification steps QA already executed, so the reviewer
  repeats a path that is known to work.
