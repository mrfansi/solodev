---
name: pr-review
description: Review a pull request and report findings ranked by severity. Use when the user asks to review a PR, check a PR, or asks whether a PR is safe to merge. Also invoked by the loop skill before committing. Takes an optional PR link or number; with no argument it reviews the PR for the current branch.
---

# pr-review

`/solodev:pr-review [pr-url-or-number]`

No argument → review the PR for the current branch. No PR for the branch → review
the diff against the default branch and say that is what you did.

## 1. Load the PR

```bash
gh pr view <ref> --json title,body,author,files,additions,deletions,baseRefName,url
gh pr diff <ref>
gh pr checks <ref>
```

**Read the PR description before the diff.** Review means judging whether the change
achieves its stated intent — without the intent, you are only reading code.

Then read enough of the surrounding code to judge the change in context. A diff read
in isolation produces findings that are locally right and globally wrong.

## 2. Review in this order

Stop-the-line issues first; taste last. Reviews that open with style notes bury the
bug that matters.

| Order | Dimension | Look for |
|---|---|---|
| 1 | **Correctness** | edge cases, empty/null, off-by-one, error paths, wrong operator, unreachable branches |
| 2 | **Security** | unvalidated input at trust boundaries, injection, secrets in code or logs, missing authorisation, unsafe deserialisation |
| 3 | **Data** | migrations, backward compatibility, anything that can destroy or corrupt existing data |
| 4 | **Concurrency** | shared mutable state, races, lock ordering, non-atomic read-modify-write |
| 5 | **Tests** | does new logic have tests, do they assert behaviour, would they fail if the bug returned |
| 6 | **Performance** | N+1 queries, nested loops over unbounded input, work inside a hot path |
| 7 | **Design** | duplication of something that already exists, wrong layer, leaked abstraction |
| 8 | **Docs** | README, CHANGELOG, public API docs updated when behaviour changed |
| 9 | **Style** | only what a formatter or linter does not already enforce |

## 3. Verify before reporting

Every finding must survive this test: **can you state concrete inputs or state that
produce a wrong result?** If not, it is a question, not a finding — phrase it as one.

Do not report:
- what the formatter or linter already enforces
- personal preference dressed up as a defect
- speculation about code the diff does not touch
- "consider extracting this" with no defect behind it

Where a claim in the PR description is checkable, check it rather than trusting it.

## 4. Severity

| Level | Meaning | Merge? |
|---|---|---|
| **Blocker** | Data loss, security hole, or the feature does not work | No |
| **Major** | Wrong behaviour in a real scenario, or a missing test for risky logic | Not until resolved or consciously accepted |
| **Minor** | Real but low impact; edge case unlikely in practice | Can merge, fix later |
| **Nit** | Preference, naming, phrasing | Never blocks; prefix with `nit:` |

## 5. Output

```markdown
## Review: <PR title>

**Verdict:** approve / approve with comments / request changes
**Scope:** <n> files, +<a>/-<b> · CI: <status>

### Blockers
1. `path/file.ext:42` — <one sentence: the defect>
   **Fails when:** <concrete inputs → wrong output>
   **Fix:** <what to do>

### Major
...

### Minor / Nits
- `nit:` ...

### What works well
- <name it — a review that only finds fault teaches nothing about what to repeat>
```

The verdict is a **recommendation**. Do not run `gh pr review --approve` or merge;
approving is the user's call, and an automated approval defeats the purpose of
review.

Posting the review as a PR comment requires the user to ask — it is outward-facing
and visible to everyone on the repo.

## When the loop skill invokes this

Runs before the commit, on the working diff rather than an open PR:

```bash
git diff HEAD          # staged and unstaged
```

Blockers and majors are fixed **before** the commit, in that same run. This is what
satisfies the protocol's rule against approving code in the same pass that wrote it:
the review runs as a separate agent with its own context, so it reads the code
without the author's assumptions about what it was supposed to do.
