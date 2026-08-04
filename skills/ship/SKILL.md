---
name: ship
description: Cut a release — work out the SemVer bump from what actually changed, move CHANGELOG [Unreleased] into a dated version section, and keep every version field in step. Use before publishing, when asked to release or bump a version, or when users are not receiving updates. Prepares everything and stops before tagging or pushing; those stay yours.
---

# ship

`/solodev:ship [major|minor|patch]`

The teammate who cuts the release. Everything else in solodev takes work from an idea
to a reviewed, merged change; nothing turns that into something a user can actually
receive. This does — up to the point where a mistake would reach other people.

**It stops before tagging and before pushing.** Those are the two irreversible steps,
and they stay the user's. What you get is a repository in a state where one command
completes the release, and a printed list of exactly which commands.

With no argument the bump is derived from the changelog. Pass one to override, and say
why in the release notes.

## 1. Refuse to release a repo that is not ready

Check all of these first and stop on the first failure. A half-cut release is worse
than none, because the version number then lies about what the code contains.

```bash
git status --porcelain          # must be empty — never release a dirty tree
git rev-parse --abbrev-ref HEAD # note the branch; releasing off a feature branch
                                # is legal but must be stated
```

Then run the repo's own quality gate — whatever `specs/LOOP_STATE.md` records under
"Detected stack". **A release cut over a red gate is a bug you have version-numbered.**

If `CHANGELOG.md` has no `## [Unreleased]` section, or that section is empty, there is
nothing to release. Say so and stop rather than cutting an empty version.

## 2. Derive the bump from what actually changed

Read the `[Unreleased]` section and map its subsections to SemVer:

| Present in `[Unreleased]` | Bump | Because |
|---|---|---|
| `Removed`, or any entry marked breaking | **MAJOR** | existing usage stops working |
| `Added` | **MINOR** | new capability, old usage intact |
| only `Fixed`, `Security`, `Internal`, `Changed` | **PATCH** | behaviour corrected, surface unchanged |

**Below `1.0.0`, only the MAJOR row shifts.** A breaking change becomes a MINOR bump
(`0.4.2` → `0.5.0`); `Added` still gives MINOR and everything else still gives PATCH.
SemVer puts no compatibility promise on `0.x` at all, so there is nothing for a MAJOR
bump to signal until `1.0.0` exists.

Worked, because the ambiguous version of this rule shipped once and had to be fixed:
`[Unreleased]` containing `Added`, `Changed`, `Fixed` and `Internal`, with the project
at `0.1.0`, gives **`0.2.0`** — MINOR, driven by `Added`, unshifted.

Say which convention you applied; do not leave the reader to reverse-engineer it from
the number.

**State the reasoning in one line before writing anything**: *"MINOR — `Added` names a
new skill, nothing was removed."* A version number nobody can argue with is a number
nobody checked.

## 3. Move the version everywhere it lives, in one step

Version strings rot by drifting apart. Find every place the version appears before
editing any of them:

```bash
# Search for the CURRENT version string itself, not for the word "version".
# Manifests are the obvious half; prose is the half that silently rots.
CUR=$(python3 -c "import json;print(json.load(open('.claude-plugin/plugin.json'))['version'])")
grep -rn --fixed-strings "$CUR" . \
  --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=evidence --exclude-dir=dist
```

Two things are deliberate here. **Search for the literal current version**, not for
the word "version" — the latter finds the manifests and stops, and missed a `v0.1.0`
sitting in a state file read on every run. **Do not filter by extension**: a version
lives in `__init__.py`, `Cargo.toml`, `build.gradle`, a workflow YAML, or a README
badge depending on the project, and an allow-list is a promise to miss whichever one
you did not think of. Exclude directories instead — that is a much shorter list.

Then **read the hits and sort them into three piles before editing anything**:

| pile | what to do |
|---|---|
| the version *is* this file's subject | change it — manifests, a state file's inventory line |
| a historical record | leave it — changelog sections, evidence, past release notes |
| documentation *about* versioning | leave it — a worked example that names a version is not a version |

The third pile is the trap. On the next release this command will match the changelog
section this release just cut, and any prose that quotes a version number. "Move the
version everywhere it lives" means everywhere it *claims to be current*, not everywhere
the digits appear.

For a **Claude Code plugin** specifically, two files carry it and both must move
together: `.claude-plugin/plugin.json` and the matching entry in
`.claude-plugin/marketplace.json`. At runtime `plugin.json` wins, so a stale
marketplace entry does not break installs — it misleads every human who reads it. See
`specs/REFERENCE.md` for the exact mechanism.

**Why this matters more than it looks.** Claude Code's plugin reference states that
when `version` is set, *users receive updates only when you bump it* — pushing commits
alone has no effect, and `/plugin update` will report "already at the latest version"
while doing nothing. A plugin that ships work without bumping is invisible to everyone
who installed it.

## 4. Cut the changelog

Rename `## [Unreleased]` to `## [<version>] - <YYYY-MM-DD>`, then open a fresh empty
`[Unreleased]` above it. Keep a Changelog also expects link references at the bottom:

```markdown
[Unreleased]: https://github.com/<owner>/<repo>/compare/v<version>...HEAD
[<version>]: https://github.com/<owner>/<repo>/compare/v<previous>...v<version>
```

**The oldest release is the exception**: it has no predecessor to compare against, so
it alone uses `/releases/tag/v<version>`. Check with `git tag --list 'v*'` — empty means
you are cutting that first one. Emitting a `releases/tag` link for a later version is
the easy mistake, because it looks right on a repo that has never been tagged.

Derive `<owner>/<repo>` from `git remote get-url origin` rather than assuming it
matches the directory name — those differ more often than people expect.

**Do not edit the entries while moving them.** Rewriting history at release time is how
a changelog stops being a record and starts being marketing. If an entry is wrong, fix
it in its own commit, before the release.

## 5. Commit, then hand over

Commit the bump on its own — `chore(release): <version>` — with nothing else in it. A
release commit that also changes code cannot be reverted cleanly.

Then **stop**, and print exactly what remains:

```
RELEASED : <version>  (was <previous>)
BUMP     : <major|minor|patch> — <the one-line reasoning from step 2>
GATE     : <command> — <result>
MOVED    : <each file and the field that changed>
CHANGELOG: <n> entries cut into [<version>]; [Unreleased] is now empty
COMMIT   : <sha> <message>

NOT DONE — yours to run:
  git tag -a v<version> -m "<title>"
  git push origin <branch> --follow-tags
  gh release create v<version> --notes-file <path>   # if this repo publishes releases
```

Never run those three yourself, and never offer to. Tagging and pushing are how a
release becomes public and unrecallable; the person accountable for that should be the
one who types it.

If the repo has its own release rules — a `RELEASING.md`, a CI workflow that tags, a
protected branch — **follow them and say which one you followed.** They outrank this
skill.
