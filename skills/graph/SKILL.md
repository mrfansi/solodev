---
name: graph
description: Build and query a greppable knowledge graph of the codebase — module cards, god nodes, and edges under specs/graph/, so questions about the code are answered from the map instead of re-exploring. Use to map a codebase, ask how something works or what calls what, or after big changes to refresh the map. Also consulted by the loop skill in Phases 0 and 3.
---

# graph

```
/solodev:graph               # build if no map exists, update if one does
/solodev:graph build         # force a full rebuild
/solodev:graph status        # freshness and stats, no changes
/solodev:graph <question>    # answer from the map, verified against live code
```

The teammate who has read the whole codebase so nobody else has to. The map is
plain markdown under `specs/graph/` — greppable, diffable, no runtime, no
database. `specs/` is already gitignored, so the map is workspace like the rest
of the loop's state; unlike the backlog, losing it costs nothing but a rebuild.

Anything that is not `build`, `status`, or empty is a **question**.

## The map

```
specs/graph/GRAPH.md         # the index — always read this first, never the cards blind
specs/graph/nodes/<module>.md# one card per module
```

`GRAPH.md` (≤100 lines — it is read often, so it stays small):

```markdown
# CODE GRAPH
Built-at: <commit sha> · <date> · scope: <path or "whole repo">
Modules: <n> · Files: <n> · Edges: <n>

## God nodes — highest fan-in; read before changing anything
| Node | Where | In-degree | Why load-bearing |

## Modules
| Module | Purpose (one line) | Files | Card |

## Module edges
a -> b : <one-line why>
```

A card (≤60 lines each):

```markdown
# <module>
Built-at: <commit sha>
Purpose: <one line>

## Files
`path` — role

## Public surface
`symbol` (`kind`) `file:line` — role

## Depends on
-> <module> — why  [EXTRACTED file:line]

## Used by
<- <module> — why

## Gotchas
- [EXTRACTED file:line | INFERRED] <invariant, trap, or assumption>
```

**EXTRACTED means you read it at that line; INFERRED means you concluded it.**
Never promote an inference by giving it a citation it does not have — the audit
trail is what makes the map trustworthy, and one fabricated citation poisons all
of them.

## Build

1. **Partition.** `git ls-files` (fall back to `find` outside git), group into
   modules by top-level directory or the language's package convention. Merge
   the smallest groups until there are **at most 10 modules**; a partition finer
   than that costs more cards than it saves reading.
2. **Fan out** — one `Agent` per module, `subagent_type: "solodev:code-mapper"`,
   all in a single message so they run concurrently. Each prompt carries: the
   module's file list, the repo root, the exact card path to write, the card
   format above, and the current commit sha. Each mapper **writes its own card**
   and returns only its index row and edge lines — the caller never relays card
   bodies.
3. **Assemble `GRAPH.md`** from the returned rows. Compute `Used by` and god
   nodes by reversing the edges (in-degree ≥3, or the clear hubs in a small
   repo), then append each module's `Used by` lines to its card.
4. **Verify before trusting:** every module row has a card on disk; every edge
   endpoint is a module that exists; `Built-at` is `git rev-parse HEAD`. A
   mapper that returned nothing → say so and map that module inline (same rule
   as the loop's Phase 4 fallback).

## Update (the default when a map exists)

```bash
git diff --name-only "$(sed -n 's/^Built-at: \([a-f0-9]*\).*/\1/p' specs/graph/GRAPH.md)"..HEAD
```

Map the changed files to modules, re-map **only those modules** (fan out as in
build), refresh their index rows, edges, and the god-node table, and stamp the
new sha. If the `Built-at` sha is gone (rebase, fresh clone), fall back to a
full build and say so. Untouched cards are not rewritten — churn on identical
content makes the map's own diff useless.

## Query

1. Read `GRAPH.md` only. Pick the 1–2 cards the question actually needs.
2. Answer from the cards, **then verify every claim you assert with one
   targeted grep or read against live code** — the map narrows the search;
   the code confirms it. A stale map answering unverified is worse than no map.
3. Cite as the graph does: `file:line` for EXTRACTED, "inferred" said plainly.
4. **Self-heal:** if the code disagrees with a card, fix the card in the same
   pass and note it in the answer. If the map cannot answer at all, say so,
   answer from live exploration, and add what you learned to the right card.

If `Built-at` is behind `HEAD`, say the map is stale, answer with extra
verification, and offer to update.

## When the loop skill invokes this

The protocol consults the map rather than invoking this skill wholesale:
Phase 0 reads `GRAPH.md` when it exists instead of re-exploring; Phase 3 starts
the call-site inventory from the `Used by` edges, verified with grep; §4B
refreshes the cards of modules the run touched. Building the map in the first
place is a chore (`C-`) filed and scored like any other work.
