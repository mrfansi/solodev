---
name: discover
description: Find work the repo already proves is needed but nobody filed — abandoned markers, doc promises no code keeps, findings never queued. Use when the backlog is thin, before planning, or when asking what to build next. Files what it finds; every item cites evidence.
context: fork
agent: general-purpose
background: false
---

# discover

`/solodev:discover [area]`

The teammate who decides **what to build**. Every other solodev skill acts on work
someone already decided on; this one finds the work nobody has written down yet.

It is not a brainstorm. A repo that has been worked on carries evidence of its own
unfinished business — abandoned markers, promises the documentation makes that no code
keeps, findings a past run named and then dropped. This skill reads that evidence and
turns it into backlog rows.

**The contract: no item without a citation.** A file and line, a command and its
output, a log entry. An item you cannot point at is an opinion, and opinions filed as
tasks are how a backlog stops being trusted.

Give it an `[area]` — a directory, a subsystem, a theme — to narrow the sweep. With no
argument it sweeps the whole repo.

## 1. Read what is already known

Before looking for anything, load what must not be re-filed:

```bash
sed -n '/## Scored backlog/,/^---$/p' specs/LOOP_STATE.md
```

That one range covers the open rows, the struck-through rows, **and** the "Considered
and rejected" block, which sits inside the same section. Do not add a second `sed` for
the rejected block: its address re-arms and matches the phrase again further down the
file, printing unrelated checklist lines as though they were settled decisions.

Struck-through rows and the "Considered and rejected" block are **decisions**.
Re-filing something that was deliberately closed reopens an argument the repo already
settled, and it is the fastest way to make this skill unwelcome.

No `specs/LOOP_STATE.md` → the loop has not been bootstrapped. Say so, and file into
the format `/solodev:task` describes so `/solodev:autopilot` picks the items up on its
first run.

## 2. Work the seams

Six places where unfiled work accumulates. Work them in order — the early ones are
cheap and specific, the later ones need judgement.

| # | Seam | A hit means | `[area]` narrows it? |
|---|---|---|---|
| 1 | Abandoned markers | Someone named the work, then stopped | yes |
| 2 | Promises with no keeper | Docs describe behaviour no code implements | yes |
| 3 | Findings that leaked | A finding was named but never filed, against §1 invariant 11 | yes |
| 4 | Gate blind spots | The gate cannot fail the way the product breaks | no |
| 5 | Repeats in the Run Log | Recurring friction — worth **+1** on the score of whatever kills it (§3 Phase 1) | no |
| 6 | Work git abandoned | A revert, a stale branch, or a "temporarily" commit is unfinished work | no |

**Every command lives in the block below, never in the table above.** A markdown table
cell must escape `|` as `\|`, and that escape does not survive being copied into a
shell: inside `grep -E`, `\|` is a *literal pipe*, so an alternation written in a table
cell silently matches nothing. Run #2 shipped seam 1 that way and it returned 2 hits
where the working command returns 25.

**Check your `grep` before you trust any seam.** On many machines the `grep` on PATH
is a wrapper — ripgrep, or a token-saving proxy — and those honour `.gitignore`. The
loop's own `specs/` and `docs/` are gitignored by design, and they are exactly the
trees seams 2 and 3 read, so a wrapped grep reports a clean sweep of the files that
hold the evidence. This is the same hazard as the `ls` aliasing named below, and it is
quieter. Prove it once per machine, **recursing from `.` exactly as the seams do**:

```bash
grep -rl 'Scored backlog' .    # must list specs/LOOP_STATE.md
```

If `specs/LOOP_STATE.md` exists but is missing from that list, the sweep cannot see
the workspace: bypass the wrapper — `/usr/bin/grep`, `command grep`, or whatever
no-ignore flag it takes — and run every seam through the bypass. Measured on this
repo, seam 1 returned 4 hits wrapped against 22 unwrapped, with every file under
`specs/` and `docs/` missing from the wrapped result. In a repo that never bootstrapped
the loop there is no `specs/LOOP_STATE.md` to find, and its absence proves nothing.

Two ways this probe has already been written wrong. **`-l`, never `-n`:** with line
numbers the output carries matched *text*, and four of this repo's own hits contain
the string `specs/LOOP_STATE.md` inside the line — a wrapped grep then shows you the
filename you were told to look for while having reached no such file. **Do not name
the ignored directory:** `grep -r '...' specs/` returns the same result either way,
because the filtering applies to the recursive walk, not to a path you hand it.

```bash
# seam 1 — abandoned markers. Substitute [area] for the final `.`
grep -rnE '(TODO|FIXME|HACK|XXX)' .

# seam 2 — promises with no keeper. Compare what the docs NAME against what the
# code SHIPS: commands, flags, endpoints, config keys, skill names. Adapt both
# sides to this repo's layout — a CLI compares its README flags against the
# argument parser; a plugin compares documented skill names against skills/*/.
# Use `find`, never `ls`: ls is aliased to eza/exa/lsd on many machines and its
# colour codes corrupt sort and comm.
grep -rhoE '<pattern the docs use to name things>' README.md docs/ \
  | LC_ALL=C sort -u > /tmp/named
<list what actually ships, one per line> | LC_ALL=C sort -u > /tmp/ships
comm -23 /tmp/named /tmp/ships   # named in docs, does not ship
comm -13 /tmp/named /tmp/ships   # ships, never documented

# seam 2, second half — requirements the docs state about themselves. The protocol
# and README make countable promises ("one file per major user flow", "every run
# updates X"). Count what they promise against what exists. This is where run #2
# found C-6, and it is not the same check as the two comms above.
grep -rn 'must\|requires\|minimum contents' specs/LOOP.md | head -40

# seam 3 — findings that leaked. Substitute [area] for docs/evidence/
grep -rn 'backlog\|deferred\|out of scope' docs/evidence/
grep -oE '[A-Z]-[0-9]+' docs/evidence/*/*.txt | LC_ALL=C sort -u   # cited ids
grep -oE '^\| ~?~?[A-Z]-[0-9]+' specs/LOOP_STATE.md | grep -oE '[A-Z]-[0-9]+' \
  | LC_ALL=C sort -u                                              # filed ids

# seam 6 — work git abandoned
git log --oneline -40
git branch --no-merged
git log --grep=revert -i --oneline
```

Seams 4 and 5 have no command: seam 4 reads the Detected stack table and asks what
could break that those commands would still pass, and seam 5 reads the Run Log for the
same friction across 2+ runs. Both are judgement, and both must still cite what they
read.

**Outside a git repo, seam 6 is UNAVAILABLE, not clean** — the same distinction seam 5
draws when the Run Log is too short. A seam that could not run has told you nothing,
and recording it as clean claims otherwise.

**Run each seam command unfiltered, and disclose every exclusion.** Piping a seam
through `grep -v` to hide self-matches or known-clean paths is fine — reporting the
filtered count as if it were the raw output is not. State the raw hit count, then name
each false positive and why it is one. A sweep that quietly trims its own output is
doing the thing this skill exists to catch.

**Record the empty seams too.** "Seam 3 clean — every evidence finding traced to a
backlog row" is a real result, and it stops the next sweep re-walking it blind.

Never invent a seventh seam from intuition. If something feels wrong but no seam
produces evidence for it, say that plainly rather than filing a hunch with a score
attached.

## 3. Classify, score, and write the rows

**Use `/solodev:task`'s rules — do not restate them here.** It owns the type table,
the id sequence, bug severity, the scoring formula, and the row format. Two copies of
a scoring rule drift, and then the same work scores differently depending on which
skill filed it.

Two things this skill adds on top:

- **The origin is `found by discovery, run #N, seam <n>`** plus the citation itself.
  A row whose Notes column has no file, line, or hash is not finished.
- **Write the observable gap, never the fix.** "`docs/architecture.md` describes a
  fork-based audit tier that no agent file implements" is a task. "Refactor the audit
  tier" has already chosen the answer before anyone looked at the question.

## 4. Deduplicate, then cap

Against the rows loaded in step 1, drop anything that is:

- already open in the backlog, even under different wording
- struck through as finished
- in "Considered and rejected"

Then **file at most 5 items**, highest score first. A sweep that files fifteen rows
has not found fifteen things worth doing; it has moved the problem from "no backlog"
to "no signal". Name what you dropped and why, so the next sweep can pick it up
knowing it was seen and ranked, not missed.

## 5. Report

**Wrap every line at 80 columns**, on word boundaries, never inside a filename.
Continuations indent to column 12 — the value column, flat. Do not open a second
alignment column for sub-items; it does not survive an 80-column terminal.

```
SWEPT    : <area, or "whole repo"> — <n> seams worked
SEAMS    : seam <n>: <r> raw hits -> <n> candidates, <k> false positives
           (name each false positive and why), or "clean, <r> raw, all
           false positives", or "UNAVAILABLE" with the reason
FILED    : <n> items, highest first
           <id> - <title>
           score <n> (V<n> x F<n> / S<n>)
           cite: <file:line, hash, or command>
DROPPED  : <what was found but not filed, and which rule dropped it>
BACKLOG  : <n> open, was <n>. Top of queue: <id> (<score>)
NEXT RUN : run #<N+1> is <a feature run / an audit run per cadence>, so
           <which filed item is picked up, or which waits and why>
GAPS     : <seams that produced nothing or could not run, so the next
           sweep can skip or vary them>
```

**A seam is never reported as "clean" without its raw hit count beside it.** That is
the field that makes undisclosed filtering visible; without it a reader cannot tell a
seam that found nothing from a seam whose output was quietly trimmed.

If the sweep files nothing, say so and name every seam you worked. A discovery pass
that returns empty against a repo it has already swept is a **good** result — it means
the backlog is current. Manufacturing a row to look productive is the one failure this
skill cannot recover from, because every later run will trust the row.
