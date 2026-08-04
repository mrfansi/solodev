# REFERENCE

> Incremental cache of external APIs and patterns, filled in during Phase 2. A run
> that needs something already here **uses it without re-reading the source**. A run
> that has to look something up **appends it here**, including lookups that came back
> empty — an empty answer recorded once saves the next run the same dead end.
>
> Entry format: what it is · the signature or shape · a minimal example · when to use
> it · where it was read from.

## Claude Code — agent definition frontmatter

**Read from:** this repo's own `agents/*.md`, verified against the five agents
loading correctly as `solodev:<name>` in a live session on 2026-08-04.

```yaml
---
name: qa-runner              # required; the plugin prefixes it, so it resolves as solodev:qa-runner
description: <one line>      # required; this is what the orchestrator matches against
model: sonnet                # optional; omit to inherit
disallowedTools: Write, Edit, NotebookEdit   # optional deny-list
---
```

`disallowedTools` is a **deny-list**: everything else stays available. The alternative
is a `tools:` allow-list, which must then enumerate every tool the agent needs. This
repo uses the deny-list for the four read-only auditors, because an auditor needs to
read, run, and search freely — only writing is forbidden.

Use `disallowedTools` when the restriction is narrow; use `tools` when the agent
should have a small, explicitly enumerated surface.

## Claude Code — plugin manifests

**Read from:** `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` in
this repo, both loading correctly.

`plugin.json` declares `"skills": "./skills/"` and **does not declare an agents
path** — `agents/` at the plugin root is discovered by convention. Verified: all five
agents resolve without the key. Do not add an `agents` key on the assumption it is
missing.

## Gap — the authoritative plugin schema was not consulted

Run #1 derived the frontmatter shapes above from **working examples in this repo**,
not from Anthropic's published schema. That is enough to keep the plugin loading, but
it cannot tell us which optional keys exist and are unused.

Recorded so a later run does not re-derive the same partial answer from the same
files. Closing this is backlog item `C-2`: read the installed plugin cache at
`~/.claude/plugins/cache/solodev/solodev/<version>/` and Anthropic's schema, then
replace this section with the full key list.
