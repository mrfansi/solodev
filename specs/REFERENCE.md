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

## Claude Code — SKILL.md frontmatter, full key list

**Read from:** <https://code.claude.com/docs/en/skills> on 2026-08-04 (note:
`docs.claude.com/en/docs/claude-code/skills` 301-redirects there). Cross-checked
against 226 installed `SKILL.md` files in `~/.claude/plugins/cache/`.

**Provenance:** every row in both tables below is quoted from those two pages, not
inferred. What that does *not* establish is whether a claim still holds in the
installed version here — the version gates (`background` needs ≥ 2.1.218, the `:`
ban on subagent names needs ≥ 2.1.218), the 1,536-character truncation, and
`permissionMode` being ignored for plugin subagents were all read off the page and
**none of them can be checked locally**. Treat them as the docs' word. The two claims
this repo did verify against its own installation are noted inline below.

| Key | Required | What it does |
|---|---|---|
| `name` | No | Display name. **Defaults to the directory name** |
| `description` | Recommended | What it does and when to use it. Falls back to the first paragraph of the body |
| `argument-hint` | No | Autocomplete hint, e.g. `[issue-number]` |
| `disable-model-invocation` | No | `true` keeps the description **out of context**; the skill loads only when typed as `/name`. Also blocks preloading into subagents |
| `user-invocable` | No | `false` hides it from the `/` menu; the description stays in context |
| `allowed-tools` | No | Pre-approved for the invoking turn only. String or YAML list |
| `model` | No | Same values as `/model`, or `inherit` |
| `effort` | No | `low`/`medium`/`high`/`xhigh`/`max` |
| `context` | No | `fork` runs the skill in a forked subagent context |
| `agent` | No | Which subagent type `context: fork` uses |
| `background` | No | Only with `context: fork`. `false` waits for the result in the invoking turn. **Default `true`**. Needs Claude Code ≥ 2.1.218 |
| `hooks` | No | Hooks scoped to the skill's lifecycle |
| `shell` | No | `bash` (default) or `powershell` |

**The token fact that matters here:** `description` is **always resident in
context** — it is what Claude matches against to decide whether to load the skill.
The combined `description` + `when_to_use` text is truncated at **1,536 characters**
in the skill listing. **Eleven skills cost ~1,042 tokens** of permanently resident
context in this plugin. That is 4,169 description characters ÷ 4 — the character
count is exact, the division is the usual English-prose approximation, so treat the
token figure as an estimate. Ten skills cost 3,816 chars (~954 tok) before `discover`
shipped. Mean is **~95 resident tokens per skill**; `discover` itself added 88.
`scripts/validate.py` caps descriptions at 1024 chars, stricter than the platform's
1,536 and therefore safe.

`disable-model-invocation: true` is the only key that **removes** a skill's
description from context. It costs automatic invocation in exchange, so it suits
skills that are only ever typed deliberately.

**Not yet used, and deliberately not guessed:** the docs state `agent` selects the
subagent type for `context: fork` but do not state what `context: fork` defaults to
when `agent` is omitted; the worked example passes `agent: Explore` explicitly. Run #2
declined to use `context: fork` for that reason — see backlog `E-3`.

## Claude Code — subagent frontmatter, full key list

**Read from:** <https://code.claude.com/docs/en/sub-agents> on 2026-08-04.

| Key | Required | What it does |
|---|---|---|
| `name` | **Yes** | Lowercase and hyphens. **May not contain `:`** — that is reserved for plugin scoping (`solodev:qa-runner`). Since v2.1.218 a file with `:` in the name fails to load. The filename need not match |
| `description` | **Yes** | When Claude should delegate here |
| `tools` | No | Allow-list. Omitted → inherits every tool available to subagents. An entry resolving to nothing usually makes the subagent **fail to launch** |
| `disallowedTools` | No | Deny-list, removed from the inherited or specified list |
| `model` | No | `sonnet`/`opus`/`haiku`/`fable`, a full id, or `inherit`. **Defaults to `inherit`** |
| `permissionMode` | No | `default`/`acceptEdits`/`auto`/`dontAsk`/`bypassPermissions`/`plan`. **Ignored for plugin subagents** — which is what this repo ships, so setting it here would do nothing |

To preload skills into a subagent use the `skills` field, **not** `Skill` in `tools`.

This closes backlog item `C-2`.
