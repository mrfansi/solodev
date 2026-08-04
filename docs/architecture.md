# Architecture

The plugin has three kinds of parts, and the split is about **who reads what, and
when**. Getting a rule into the wrong part is the main way this codebase degrades.

## The three parts

| Part | Lives in | Loaded when | Owns |
|---|---|---|---|
| **Skills** | `skills/<name>/SKILL.md` | on invocation, into the current context | how to do one kind of work |
| **Agents** | `agents/<name>.md` | when spawned as a subagent, into a *fresh* context | isolation framing + the return contract |
| **Protocol** | `specs/LOOP.md` | at Phase 0 of every loop run | the rules a run must obey |

### Skills carry the craft

A skill is a body of technique — how to audit a flow, how to build a test matrix, how
to write a PR body. It is written to be read by whoever is doing that work, whether
that is the main session or a subagent.

### Agents are thin on purpose

An agent file does **not** restate its skill. It delegates:

```
**First action:** invoke the Skill tool with `skill: "solodev:qa"` and follow it in
full. Everything below is the contract you must satisfy regardless.
```

What it adds is the part that only makes sense from inside a subagent: why this runs
in a separate context, and the exact shape of the value it must return. An agent file
that grew a copy of its skill would be paying twice for one set of instructions and
would drift within a few edits.

**Four of the five auditors have no edit tools at all** (`disallowedTools: Write,
Edit, NotebookEdit`). This is the load-bearing decision of the whole audit tier: an
auditor that can patch what it finds will patch instead of report, and the finding
never reaches the Run Log where it could become a lesson. Only `qa-runner` can write,
and only so it can save evidence.

### The protocol is the rulebook, and it is the expensive one

`specs/LOOP.md` is read in full at Phase 0 of every run. At v1.1 that is roughly
6,150 tokens before a single line of work happens — the single largest fixed cost the
loop carries. Anything added to it is paid for on every future run, forever.

The corollary: **a rule belongs in the protocol only if a run must obey it.** Guidance
about how to do the work belongs in a skill, which is loaded on demand.

## Where each rule goes

When adding a rule, ask which of these it is:

| The rule is about… | It goes in |
|---|---|
| what a run must do or must not do | protocol §1 or §3 |
| how to perform one kind of work well | the relevant skill |
| what a subagent must return | the agent file |
| something that went wrong in a real run | `specs/LOOP_LEARNINGS.md` |
| an external API that had to be looked up | `specs/REFERENCE.md` |

**Never in two places.** The invariants used to live in both `skills/loop/SKILL.md`
and the protocol; they were consolidated into protocol §1 because two copies of a rule
drift and the reader cannot tell which one is current.

Run #3 finished that job: the agent-per-phase table, the work-intake and severity
table, the branch-and-draft-PR rules, and the layer-1 state-file table all moved to
pointers. **Five clauses survived** because they exist nowhere else.

**The method needs a warning attached, because run #3's own execution of it failed
twice.** The rule is: grep every candidate against `specs/LOOP.md` before deleting it,
and keep anything absent. Two rules were deleted anyway, and neither was caught by the
grep:

- A **two-clause table row** was checked as one claim. Its first half was in §3
  Phase 1; its second half — a feature deferred by the cadence becomes the next run's
  first candidate — was nowhere. `qa-runner` filed it S1.
- A **quantifier** was not read. The skill said "**each agent's** prompt must carry…";
  the protocol says "**its** prompt", scoped to one agent. A phrase match found the
  sentence and certified the deletion. `pr-reviewer` caught it.

So: **split multi-clause rows before grepping, and match the quantifier, not just the
phrase.** A grep that finds similar words is not proof the rule survives. Both rules
were restored; both failures are recorded in `specs/LOOP_LEARNINGS.md`.

`skills/loop/SKILL.md` now holds only what the protocol does not: scheduling, argument
parsing, the bootstrap sequence, stack detection, layer-2 memory, and the five orphans
above.

## Scheduling is the exception

`skills/loop/SKILL.md` owns scheduling — the interval grammar, `ScheduleWakeup` versus
`CronCreate`, and the one invariant that a failed run does not reschedule. This is
deliberately *not* in the protocol: the protocol governs what happens inside a run,
and scheduling is what happens between them. A repo can adopt the protocol without
adopting this plugin's scheduling.

## Two ways work enters the backlog

`task` and `discover` look adjacent and are not. The difference is who decided the
work exists:

| Skill | Input | The decision it makes |
|---|---|---|
| `task` | a request a human already formed | how to classify, score, and queue it |
| `discover` | the repository itself | **that a piece of work exists at all** |

`task` cannot find anything — it files what you bring it. `discover` reads the seams
where unfiled work accumulates (abandoned markers, documentation describing absent
behaviour, findings named in evidence but never queued, blind spots in the quality
gate, friction repeating in the Run Log, work git shows was abandoned) and turns the
evidence into rows.

They share one rulebook: `task` owns the type table, the id sequence, bug severity,
the scoring formula, and the row format. `discover` points at those rules rather than
carrying a second copy, for the same reason the invariants live only in protocol §1.

## Where the boundary sits

`ship` moved it, but did not remove it. The plugin now takes work all the way from an
unfiled idea to a cut release: `discover` finds it, `task` files it, `loop` builds and
verifies it, the audit tier judges it, `pr-new` proposes it, `ship` versions it.

**Two steps remain deliberately outside**: tagging and pushing. Those are where a
mistake reaches other people and stops being recallable. `ship` prepares everything, then
prints the exact commands and stops — the person accountable for a public release
should be the one who types it. `pr-new` draws the same line by opening PRs as drafts.

This is the plugin's one consistent rule about power: **it will do any amount of work,
and it will not take an irreversible outward-facing action on your behalf.** Run #1
found the README's install command broken and could not fix it, because fixing it meant
publishing the repo. It stayed an open S1 for two runs until the user authorised it.
That is the boundary working, not the loop failing.

What is still missing: nothing *notices* when a release is due. Protocol §3 Phase 8
step 3 already requires one — "user-visible change → bump SemVer and move
`[Unreleased]` into a version section" — but no gate enforces it, which is exactly how
three runs shipped user-visible changes while the version sat at `0.1.0`. `ship` gives
that rule a keeper; nothing yet reminds a run to call it.
