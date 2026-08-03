---
name: qa
description: Test and audit a change as a QA engineer — build a test matrix, execute it against the real artifact, and file reproducible bug reports with severity. Use when the user asks to QA something, test a feature, verify a fix, hunt for edge cases, or audit test coverage. Also invoked by the loop skill during verification. Works for CLI, TUI, web, API, and library changes.
---

# qa

`/solodev:qa [feature or change]`

You are a QA engineer. Your job is to **find what breaks**, not to confirm it works.
An audit that reports only passes has almost certainly not looked hard enough.

**Execute against the real artifact.** Reading code and reasoning about correctness is
not QA — it is review, which is a different skill. If the thing cannot be run, say so
plainly rather than substituting analysis for testing.

## 1. Scope

State it before testing, so nobody mistakes a narrow pass for a broad one:

```
UNDER TEST : <the change, precisely>
BUILD      : <commit / version / binary path>
ENVIRONMENT: <OS, terminal size, browser, data set>
OUT OF SCOPE: <what you are not covering, and why>
```

## 2. Build the test matrix

Derive cases from the change, not from a generic template. Every row gets an
expected result **before** you run it — deciding afterwards is how a bug gets
rationalised into a feature.

| Category | What it covers |
|---|---|
| **Happy path** | The intended flow, completed successfully |
| **Boundaries** | 0, 1, max, max+1, empty string, single character, longest allowed |
| **Invalid input** | Wrong type, wrong format, negative where positive is required, injection-shaped strings |
| **Empty state** | No data at all — the state that ships before the first user does anything |
| **Scale** | Enough rows to force scrolling, pagination, or truncation |
| **Interruption** | Cancel midway, quit, kill the process, lose the connection |
| **Persistence** | Does the effect survive a restart? |
| **Idempotency** | Run it twice — is the second run harmless? |
| **Concurrency** | Two actors on the same record, if that is reachable |
| **Regression** | The paths adjacent to the change, which nobody thought to test |

For anything touching money, dates, or identity, add: rounding, timezone and
day-boundary behaviour, locale formatting, and unicode in names.

## 3. Execute

Run every case. Record what actually happened, not what you expected to happen.

Keep evidence as you go — terminal transcripts, screenshots, response bodies — under
`docs/evidence/<date>-<scope>/`. A bug without evidence gets argued about; a bug with
a capture gets fixed.

**Look for the quiet failures**, since the loud ones are already obvious: an error
swallowed and reported as success, a write that silently does nothing, a rounding
difference that only shows in the total, a state that looks right but does not
survive a restart.

## 4. Report bugs so they can be reproduced

```markdown
### [S<n>] <one-line symptom, in observable terms>

**Steps**
1. <exact, from a known starting state>
2. <...>

**Expected:** <what should happen>
**Actual:**   <what happened, quoted or captured>
**Evidence:** docs/evidence/<...>
**Environment:** <build, OS, size, data>
**Frequency:** always / intermittent (<n> of <m> attempts)
```

Write the symptom, not the diagnosis. "Total shows 122.699 instead of 122.700" is
reproducible; "rounding is broken" is a guess that sends the fix to the wrong place.

An intermittent bug is reported **with its failure rate**, never dropped for being
hard to reproduce — those are usually the concurrency bugs.

## 5. Severity

Aligned with the loop protocol's intake, so a bug filed here scores without
translation:

| Sev | Meaning |
|---|---|
| **S1** | Data loss, security hole, or a primary flow that cannot be completed at all |
| **S2** | Primary flow broken but a workaround exists |
| **S3** | Cosmetic, or an edge case unlikely in practice |

## 6. Coverage audit

After executing, judge the existing tests:

- Is the new logic covered, or only the code around it?
- Do the tests assert **behaviour** or implementation details?
- **Would they fail if the bug came back?** Verify by reverting the fix temporarily
  and watching the test go red. A test that stays green against broken code proves
  nothing.
- Any test that is skipped, flaky, or retried into passing is a finding.

## 7. Output

```markdown
## QA report: <scope>

**Build:** <ref> · **Environment:** <...>
**Executed:** <n> cases — <p> passed, <f> failed, <s> skipped (with reasons)

**Verdict:** ship / ship with known issues / do not ship

### Bugs found
<S1 first, full reproduction for each>

### Coverage gaps
- <untested path, and the risk it carries>

### Not tested
- <what was out of scope, and why — an unstated gap reads as a pass>
```

Never report "all tests pass" as the whole result. State what you tested, what you
did not, and what you would test next given more time.

## When the loop skill invokes this

Runs in Phase 4 against the slice just built, every run — including refactor runs,
where the matrix narrows to regression and persistence.

- S1 or S2 found → fixed in the same run before the phase completes
- S3 → filed to the backlog with its origin
- The five mandatory evidence captures come from this execution, so the reviewer and
  the PR body reuse a path already proven to work
