#!/usr/bin/env python3
"""Validate the solodev plugin: manifests, frontmatter, and cross-references.

Run: python3 scripts/validate.py
Exits non-zero on any error. Warnings do not fail the run.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESC_MAX = 1024
VALID_MODELS = {"opus", "sonnet", "haiku", "inherit"}

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def frontmatter(path: Path) -> dict[str, str]:
    """Parse the leading --- block. Flat key: value only, which is all these files use."""
    text = path.read_text()
    if not text.startswith("---\n"):
        err(f"{path.relative_to(ROOT)}: no frontmatter block at line 1")
        return {}
    end = text.find("\n---\n", 3)
    if end == -1:
        err(f"{path.relative_to(ROOT)}: frontmatter is never closed")
        return {}
    fields = {}
    for line in text[4:end].split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            err(f"{path.relative_to(ROOT)}: frontmatter line is not key: value — {line!r}")
            continue
        fields[key.strip()] = value.strip()
    return fields


# --- manifests ------------------------------------------------------------

plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())

entries = [p for p in market["plugins"] if p["name"] == plugin["name"]]
if not entries:
    err(f"marketplace.json lists no plugin named {plugin['name']!r}")
else:
    entry = entries[0]
    if entry.get("version") != plugin.get("version"):
        err(
            f"version drift: plugin.json {plugin.get('version')!r} vs "
            f"marketplace.json {entry.get('version')!r}. plugin.json wins at runtime, "
            f"so this misleads readers rather than breaking installs — but a release "
            f"that moved one file and not the other is a half-cut release"
        )
    # The version is the cache key Claude Code uses to decide whether an update
    # exists. A version that never moves means installed users never receive
    # anything, silently — /plugin update reports success. So it must at least be
    # well-formed SemVer, and the CHANGELOG must have a matching section.
    ver = plugin.get("version", "")
    if not re.fullmatch(r"\d+\.\d+\.\d+", ver):
        err(f"plugin.json version {ver!r} is not MAJOR.MINOR.PATCH")
    elif ver != "0.1.0":  # 0.1.0 predates this repo's changelog convention
        cl_path = ROOT / "CHANGELOG.md"
        if not cl_path.exists():
            err(f"version {ver} is set but CHANGELOG.md does not exist")
        else:
            changelog = cl_path.read_text()
            # A bare substring test passes on a section that is empty, undated, or
            # merely quoted in prose. All three shipped a green gate once; each of
            # these three assertions kills one of them.
            m = re.search(
                rf"^## \[{re.escape(ver)}\][^\n]*$(.*?)(?=^## \[|\Z)",
                changelog, re.M | re.S,
            )
            if not m:
                err(
                    f"version {ver} has no `## [{ver}]` section heading in "
                    f"CHANGELOG.md. Bumping without cutting the changelog leaves "
                    f"users no way to see what they received"
                )
            elif not re.search(r"^\s*[-*] ", m.group(1), re.M):
                err(
                    f"CHANGELOG.md's `## [{ver}]` section is empty. The version was "
                    f"cut but the entries were left behind"
                )
            if not re.search(r"^## \[Unreleased\]", changelog, re.M):
                err(
                    "CHANGELOG.md has no `## [Unreleased]` section. Cutting a release "
                    "must leave a fresh empty one for the next run to write into"
                )
    if entry.get("description") != plugin.get("description"):
        warn("description differs between plugin.json and marketplace.json")

# --- skills ---------------------------------------------------------------

skill_dirs = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
skills = set()
for d in skill_dirs:
    md = d / "SKILL.md"
    if not md.exists():
        err(f"skills/{d.name}/: no SKILL.md")
        continue
    fm = frontmatter(md)
    skills.add(d.name)
    if fm.get("name") != d.name:
        err(f"skills/{d.name}/SKILL.md: name is {fm.get('name')!r}, must match the directory")
    desc = fm.get("description", "")
    if not desc:
        err(f"skills/{d.name}/SKILL.md: no description")
    elif len(desc) > DESC_MAX:
        err(f"skills/{d.name}/SKILL.md: description is {len(desc)} chars, max {DESC_MAX}")

# --- agents ---------------------------------------------------------------

agents = set()
for md in sorted((ROOT / "agents").glob("*.md")):
    fm = frontmatter(md)
    agents.add(md.stem)
    if fm.get("name") != md.stem:
        err(f"agents/{md.name}: name is {fm.get('name')!r}, must match the filename")
    if not fm.get("description"):
        err(f"agents/{md.name}: no description")
    elif len(fm["description"]) > DESC_MAX:
        err(f"agents/{md.name}: description is {len(fm['description'])} chars, max {DESC_MAX}")
    model = fm.get("model")
    if model and model not in VALID_MODELS:
        err(f"agents/{md.name}: model {model!r} is not one of {sorted(VALID_MODELS)}")

# --- cross-references -----------------------------------------------------

md_files = sorted(ROOT.glob("**/*.md"))
md_files = [p for p in md_files if ".git" not in p.parts]

# `solodev:<x>` must resolve to a skill or an agent
for path in md_files:
    for ref in set(re.findall(r"solodev:([a-z0-9-]+)", path.read_text())):
        if ref not in skills and ref not in agents:
            err(f"{path.relative_to(ROOT)}: references solodev:{ref}, which is neither a skill nor an agent")

# files the loop skill copies at bootstrap must exist
loop = ROOT / "skills/loop/SKILL.md"
for ref in set(re.findall(r"`references/([A-Za-z0-9_.-]+)`", loop.read_text())):
    if not (loop.parent / "references" / ref).exists():
        err(f"skills/loop/SKILL.md: references/{ref} does not exist")

# README table must list exactly the shipped skills and agents
readme = (ROOT / "README.md").read_text()
documented_skills = set(re.findall(r"`/solodev:([a-z0-9-]+)", readme))
if documented_skills != skills:
    for name in sorted(skills - documented_skills):
        err(f"README.md: skill {name!r} ships but is not documented")
    for name in sorted(documented_skills - skills):
        err(f"README.md: documents {name!r}, which does not ship")

documented_agents = set(re.findall(r"`solodev:([a-z0-9-]+)`", readme)) & set(agents) | {
    n for n in agents if f"`solodev:{n}`" in readme
}
for name in sorted(agents - documented_agents):
    err(f"README.md: agent {name!r} ships but is not documented")

# the loop's deliverable must be committable. Run #1 shipped a .gitignore listing
# specs/ and docs/; git commit would have exited 0 with the whole run's output absent.
# Files AND directories. A directory-only check misses `*.txt`, which is enough to
# swallow every evidence transcript while the two roots still look clean.
roots = [r for r in ("specs", "docs") if (ROOT / r).exists()]
if roots:
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--", *roots],
        cwd=ROOT, capture_output=True, text=True,
    )
    deliverable = sorted({
        *roots,
        *(str(p.relative_to(ROOT)) for r in roots for p in (ROOT / r).rglob("*") if p.is_dir()),
        *(l for l in listed.stdout.split("\n") if l.strip()),
    })
    # --no-index is load-bearing: without it git skips any path already in the
    # index, so once specs/ is tracked the check silently passes forever. We are
    # testing the ignore rule, not the current index state — a newly ignored path
    # keeps its tracked files but swallows every new one in silence.
    # --stdin keeps argv bounded; docs/evidence/ gains a directory every run.
    found = subprocess.run(
        ["git", "check-ignore", "--no-index", "--stdin"],
        cwd=ROOT, capture_output=True, text=True, input="\n".join(deliverable),
    )
    # 0 = something matched, 1 = nothing matched. Anything else (128 outside a git
    # repo) means the check did not run, which must not read as a pass.
    if found.returncode not in (0, 1):
        err(f"git check-ignore could not run ({found.stderr.strip() or 'unknown'}); "
            f"the deliverable-not-ignored check did NOT execute")
    for path in sorted({p for p in found.stdout.split("\n") if p.strip()}):
        err(
            f".gitignore excludes {path}, which protocol §2 and §6 require every "
            f"run to commit. A commit would succeed with it missing, and say nothing"
        )

# a claim about how many agents cannot edit must match the frontmatter
no_edit = {n for n in agents if "Edit" in frontmatter(ROOT / "agents" / f"{n}.md").get("disallowedTools", "")}
for path in (ROOT / "README.md", ROOT / "skills/loop/SKILL.md", ROOT / "docs/architecture.md"):
    if not path.exists():
        continue
    text = path.read_text()
    words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
    pat = r"(one|two|three|four|five) of the (one|two|three|four|five)"
    for claim, whole in re.findall(pat, text, re.IGNORECASE):
        if words[claim.lower()] != len(no_edit) or words[whole] != len(agents):
            err(
                f"{path.relative_to(ROOT)}: claims '{claim} of the {whole}' agents cannot edit, "
                f"but {len(no_edit)} of the {len(agents)} have no edit tools"
            )

# Branch naming, per protocol §3 Phase 8: <type>/<backlog-id>-<what-it-does>.
# A WARNING, not an error: the validator runs on main, on release branches, and in
# repos that never adopted the loop, none of which should fail the gate for this.
branch = subprocess.run(
    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
    cwd=ROOT, capture_output=True, text=True,
)
name = branch.stdout.strip()
TYPES = ("feat", "fix", "refactor", "chore", "docs", "perf", "test")
if branch.returncode == 0 and name not in ("main", "master", "HEAD"):
    if not re.fullmatch(rf"({'|'.join(TYPES)})/[a-z]-?\d+-[a-z0-9-]+|({'|'.join(TYPES)})/[a-z0-9-]+", name):
        warn(
            f"branch {name!r} does not match <type>/<backlog-id>-<what-it-does> "
            f"(§3 Phase 8). Types: {', '.join(TYPES)}"
        )
    elif not re.match(rf"({'|'.join(TYPES)})/[a-z]-?\d+-", name):
        warn(f"branch {name!r} has no backlog id — it cannot be traced to a row")

# --- report ---------------------------------------------------------------

print(f"skills: {len(skills)}  agents: {len(agents)} ({len(no_edit)} without edit tools)")
for w in warnings:
    print(f"WARN  {w}")
for e in errors:
    print(f"ERROR {e}")
print("FAIL" if errors else "OK")
sys.exit(1 if errors else 0)
