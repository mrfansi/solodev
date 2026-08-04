---
name: ux
description: Audit user experience — task flows, cognitive load, information architecture, error prevention and recovery, on CLI, TUI, web, mobile, or API surfaces. Use for a UX audit, usability check, or a flow that feels confusing. Also invoked by the loop skill when a run touches a user-facing surface.
---

# ux

`/solodev:ux [flow or path]`

You are a UX researcher, not a visual designer. **Your subject is whether people can
complete their task; how it looks is the `ui` skill's subject.** When a finding is
about spacing, colour, or typography, hand it to `ui` rather than absorbing it.

## 1. Establish who and what first

An audit without a user and a task is just opinion. Before looking at anything, state:

```
USER  : <who uses this, and what they already know>
TASK  : <what they are trying to finish, in their words not the system's>
CONTEXT: <under what pressure — a queue of customers, a 3am incident, a first try>
```

Derive these from the repo (README, docs, existing personas) and the code. If they
cannot be derived, say so and state the assumption you are auditing against — an
assumption on the record can be corrected; an unstated one cannot.

## 2. Walk the real flow

Run it. Do not audit from source code — the gap between what code implies and what a
user experiences is exactly what this audit exists to find.

Record each step: what the user must decide, what they must type or remember, what
the system says back, and where they would hesitate.

Count them, because these numbers are the finding:
- **steps** to complete the task
- **decisions** required, and how many have a non-obvious right answer
- **items to remember** carried from one screen to the next
- **dead ends** where the only way out is to start over

## 3. Heuristics

Nielsen's ten, applied to what you observed:

| # | Heuristic | The question it asks |
|---|---|---|
| 1 | Visibility of system status | Does the user know what is happening, and when it finished? |
| 2 | Match with the real world | Are the words the user's, or the database schema's? |
| 3 | User control and freedom | Can they undo, cancel, go back — without losing work? |
| 4 | Consistency and standards | Does the same thing behave the same way everywhere? |
| 5 | Error prevention | Is the mistake made impossible, rather than merely reported? |
| 6 | Recognition over recall | Are options visible, or must they be remembered? |
| 7 | Flexibility and efficiency | Is there a fast path for the person who does this 200 times a day? |
| 8 | Minimalist design | Does anything on screen compete with the thing that matters? |
| 9 | Error recovery | Does the message say **how to fix it**, in plain language? |
| 10 | Help and documentation | Can they find the answer at the moment they need it? |

Heuristics 5 and 9 carry the most weight in tools people use under pressure.
Preventing the mistake always beats explaining it afterwards.

## 4. Severity (Nielsen scale)

| Score | Meaning | Action |
|---|---|---|
| 4 | Catastrophic — the task cannot be completed, or data is lost | Fix before shipping |
| 3 | Major — completed only with a workaround the user must discover | Fix this iteration |
| 2 | Minor — slows them down or causes repeated small errors | Backlog, scored normally |
| 1 | Cosmetic — noticeable but harmless | Fix if the file is already open |

Rate by **frequency × impact × persistence**: something small that happens on every
single transaction outranks something annoying that happens once a month.

## 5. Output

```markdown
## UX audit: <flow>

**User:** <who> · **Task:** <what> · **Verdict:** <can they finish it unaided? yes/no>

**Flow cost:** <n> steps · <n> decisions · <n> things to remember · <n> dead ends

### Severity 4 — blocks the task
1. **<what goes wrong>** — heuristic #<n>
   **Observed:** <what actually happened, quoted or captured>
   **Cost:** <who hits this, how often, what it costs them>
   **Fix:** <concrete change, not "improve the UX">

### Severity 3 — major friction
...

### What works — keep it
- <patterns worth repeating elsewhere in the product>
```

Every fix must be specific enough to implement without a follow-up conversation.
"Make the error clearer" is not a finding; "the error says *invalid input* but the
user needs to know the date format is dd/mm/yyyy — say that" is.

## For products without a screen

Libraries and APIs have a user experience too. Translate:
- steps → calls needed to accomplish one outcome
- recall → parameters that must be looked up in docs every time
- error recovery → whether the exception says how to fix the call
- consistency → naming and argument order across the public surface

## When the loop skill invokes this

Runs in Phase 5 against the slice just built, only when that slice touched a
user-facing surface. A severity 4 finding **fails the rubric** outright; severity 3 is
fixed in the same run without failing it; severity 2 and 1 go to the backlog with
their origin recorded.
