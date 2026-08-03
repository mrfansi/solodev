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
drift and the reader cannot tell which one is current. That consolidation is the model
for every future one.

## Scheduling is the exception

`skills/loop/SKILL.md` owns scheduling — the interval grammar, `ScheduleWakeup` versus
`CronCreate`, and the one invariant that a failed run does not reschedule. This is
deliberately *not* in the protocol: the protocol governs what happens inside a run,
and scheduling is what happens between them. A repo can adopt the protocol without
adopting this plugin's scheduling.

## What is deliberately missing

Nothing in the plugin decides **what to build**. The loop can take a slice from
backlog to draft PR with verification, audit, and review along the way — but the
backlog is only ever fed by the user or by findings from a run's own verification.
The product-thinking member of the "team" is not implemented. This is tracked as
backlog item `F-1` rather than left as an unstated gap.
