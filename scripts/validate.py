#!/usr/bin/env python3
"""Validate the solodev plugin: manifests, frontmatter, and cross-references.

Run: python3 scripts/validate.py
Exits non-zero on any error. Warnings do not fail the run.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESC_MAX = 1024
VALID_MODELS = {"opus", "sonnet", "haiku", "inherit"}
BUILTIN_AGENTS = {"Explore", "Plan", "general-purpose"}

errors: list[str] = []
warnings: list[str] = []

# Anchored to the top of the document on purpose. `re.M` + `search` takes the
# LEFTMOST match, so a title-shaped line quoted in a code block — or left behind
# by an older version further down — would win over the real title, and a
# malformed real title would silently resolve to that stale number instead of
# being reported. Up to three leading spaces still render as an H1 in CommonMark.
VERSION_RE = re.compile(r"\A {0,3}#\s*LOOP PROTOCOL\s*[·-]\s*v(\d+)\.(\d+)\s*$", re.M)


def protocol_version(text: str):
    """(major, minor) from the protocol's title line, or None."""
    m = VERSION_RE.search(text)
    return (int(m.group(1)), int(m.group(2))) if m else None


def ratchet(live_text: str, floor_text):
    """Has the repo's protocol gone backwards? -> (error or None, floor to write or None)

    `specs/LOOP.md` accumulates patches; `references/PROTOCOL.md` ships them. A run
    that branches from a default branch predating a patch, edits the template, then
    copies it back over `specs/LOOP.md`, reverts that patch — and both files end on
    the same version number, so nothing in the diff looks wrong. That happened, and
    it undid a user-ordered behaviour change one run after it shipped.

    The floor is kept by this check rather than by a run, because the rule that
    should have prevented it already existed in prose and was broken twice anyway.
    """
    now = protocol_version(live_text)
    if now is None:
        return ("specs/LOOP.md has no `# LOOP PROTOCOL · vN.N` title, so a silent "
                "downgrade cannot be detected. Restore the title line.", None)
    seen = None
    if floor_text:
        try:
            major, minor = floor_text.strip().split(".")[:2]
            seen = (int(major), int(minor))
        except (ValueError, IndexError):
            seen = None          # unreadable floor is no floor, and gets rewritten
    if seen is not None and now < seen:
        # Almost always: a run branched from a default branch predating the patch,
        # edited references/PROTOCOL.md, and copied it back over specs/LOOP.md.
        return (f"specs/LOOP.md is v{now[0]}.{now[1]}, below the v{seen[0]}.{seen[1]} "
                f"this repo has run. A protocol patch was reverted; specs/ is "
                f"gitignored, so restore it from the patch entry in "
                f"skills/autopilot/references/PROTOCOL-HISTORY.md. If the downgrade is "
                f"deliberate: echo {now[0]}.{now[1]} > specs/.protocol-floor "
                f"(lowers the bar; deleting the file forgets it entirely).", None)
    if seen is None or now > seen:
        return (None, f"{now[0]}.{now[1]}\n")
    return (None, None)


def floor_verdict(live: Path, floor: Path):
    """Read both files and decide. -> ([(level, message), ...], floor text or None)

    The severity of each outcome is decided HERE, not at the call site, so
    `--selfcheck` can assert it. A demoted error or a promoted warning is one
    character of edit and breaks both rules this check is built on.

    Every filesystem shape `.protocol-floor` can take is handled here, because three
    of them were dangerous and all three came from audit:

    * A **symlink** must never be followed. Pointed at `specs/LOOP.md` it made an
      earlier version of this check truncate the live protocol to five bytes — a file
      git cannot restore, destroyed by the gate written to protect it. Pointed at
      `/dev/null` it read back empty, which was then taken for "nothing recorded yet".
    * A **hard link** to the protocol passes both `is_symlink()` and `is_file()`,
      because it *is* a plain file — the same inode under a second name. Only
      comparing inodes sees it.
    * A **directory or unreadable file** raised, taking the gate down over its own
      note-keeping.

    An unusable floor is an ERROR, not a note. CI does not fail on warnings, so
    "cannot detect a downgrade" would ship the same green as "checked, found none" —
    and this whole check exists because a silent revert went unnoticed for a run. The
    remedy is one command and the message carries it.
    """
    if not live.exists():
        return ([], None)
    if floor.is_symlink():
        return ([("error", "specs/.protocol-floor is a symlink, so a protocol "
                           "downgrade cannot be detected. Delete it and re-run.")], None)
    if floor.exists():
        if not floor.is_file():
            return ([("error", "specs/.protocol-floor is not a plain file, so a "
                               "protocol downgrade cannot be detected. Delete it and "
                               "re-run.")], None)
        try:
            if floor.samefile(live):
                return ([("error", "specs/.protocol-floor and specs/LOOP.md are the "
                                   "same file. Delete the floor and re-run.")], None)
        except OSError:
            pass          # reported by the read below, which fails the same way
    try:
        text = floor.read_text() if floor.exists() else None
    except OSError:
        return ([("error", "specs/.protocol-floor cannot be read, so a protocol "
                           "downgrade cannot be detected. Fix its permissions, or "
                           "delete it and re-run.")], None)
    if text is not None and not text.strip():
        return ([("error", "specs/.protocol-floor is empty, so a protocol downgrade "
                           "cannot be detected. Delete it and re-run to re-record.")], None)
    problem, new_floor = ratchet(live.read_text(), text)
    return ([("error", problem)] if problem else [], new_floor)


def should_write_floor(pending, error_count: int) -> bool:
    """The floor advances only on a run that passed.

    Raising it beside an unrelated failure strands the repo: the last known-good
    protocol becomes a "downgrade" the moment anyone reverts to it.
    """
    return bool(pending) and error_count == 0


def write_floor(floor: Path, text: str) -> str:
    """Replace the floor's directory entry. -> "" on success, else why not.

    Never `open(floor, "w")`. That writes *through* whatever the name resolves to, so
    a symlink or hard link aimed at `specs/LOOP.md` truncates the live protocol — and
    the shape check above happens once, a whole validator run before the write, which
    is a race anything touching the file can win. Writing a sibling and renaming over
    the name touches only the directory entry, so neither is reachable.
    """
    tmp = floor.with_name(floor.name + ".tmp")
    try:
        tmp.write_text(text)
        os.replace(tmp, floor)
        return ""
    except OSError as e:
        try:
            tmp.unlink()
        except OSError:
            pass
        return e.strerror or str(e)


def selfcheck() -> int:
    """The smallest thing that fails if the ratchet breaks. `--selfcheck`.

    Verdicts, not parses: every case asserts whether an error was raised and what the
    floor becomes, because a check that confirms its own plumbing is how two of this
    repo's other gates stayed green over real holes.
    """
    v = lambda s: f"# LOOP PROTOCOL · v{s}\n\nbody\n"

    # No floor yet: anything is acceptable, and the floor starts here.
    assert ratchet(v("1.13"), None) == (None, "1.13\n")
    assert ratchet(v("1.13"), "") == (None, "1.13\n")

    # The case this exists for: v1.13 was live, a run put v1.12 back.
    problem, floor = ratchet(v("1.12"), "1.13\n")
    assert problem and "below the v1.13" in problem, problem
    assert floor is None, "a rejected downgrade must not become the new floor"

    # Equal holds without rewriting; higher advances. Minor and major both count,
    # and 1.9 -> 1.10 must read as forward, which a string compare gets wrong.
    assert ratchet(v("1.13"), "1.13\n") == (None, None)
    assert ratchet(v("1.14"), "1.13\n") == (None, "1.14\n")
    assert ratchet(v("2.0"), "1.13\n") == (None, "2.0\n")
    assert ratchet(v("1.10"), "1.9\n") == (None, "1.10\n"), "1.10 is after 1.9"
    assert ratchet(v("1.9"), "1.10\n")[0], "1.9 is before 1.10"
    assert ratchet(v("1.9"), "2.0\n")[0], "a major downgrade is a downgrade"

    # A title that cannot be read is reported, never skipped — silence here would
    # mean deleting one line disables the check.
    assert ratchet("no title at all\n", "1.13\n")[0], "a missing title must be an error"
    assert ratchet(v("1.13").replace("·", "-"), "1.12\n") == (None, "1.13\n"), \
        "the separator is cosmetic and both forms exist in the wild"

    # An unreadable floor is no floor: it is rewritten rather than trusted, because
    # a floor nobody can parse must not silently veto every future run.
    for junk in ("garbage\n", "1\n", "x.y\n", "\n", "1.2.3.4.5\n"):
        problem, floor = ratchet(v("1.13"), junk)
        assert problem is None, f"junk floor {junk!r} must not raise: {problem}"
        assert floor == "1.13\n", f"junk floor {junk!r} must be replaced, got {floor}"
    # ...except one that parses to a real, higher version, which still vetoes.
    assert ratchet(v("1.13"), "1.20.7\n")[0], "extra components are ignored, not the version"

    # A title-shaped line that is not the title must never be mistaken for one:
    # leftmost-match would take a code-block example or a stale heading further down.
    assert protocol_version("# LOOP PROTOCOL · v1.13\n") == (1, 13)
    assert protocol_version("   # LOOP PROTOCOL · v1.13\n") == (1, 13), "3 spaces is still an H1"
    assert protocol_version("# LOOP PROTOCOL - v1.13\n") == (1, 13)
    assert protocol_version("# LOOP PROTOCOL | v1.13\n") is None, "| is not a separator"
    assert protocol_version("## LOOP PROTOCOL · v1.13\n") is None, "H2 is not the title"
    assert protocol_version("# LOOP PROTOCOL · V1.13\n") is None, "capital V is not the form"
    assert protocol_version("intro\n\n# LOOP PROTOCOL · v1.9\n") is None, \
        "a heading below the top of the file is not the title"
    assert protocol_version("```\n# LOOP PROTOCOL · v1.0\n```\n# LOOP PROTOCOL · v1.13\n") is None, \
        "an example inside a code block must not win over the real title"

    # The wiring, not just the arithmetic. Every mutant that survived an earlier
    # version of this check lived here rather than in the sums.
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        live, floor = Path(d) / "LOOP.md", Path(d) / ".protocol-floor"
        lvl = lambda r: [x[0] for x in r[0]]
        msg = lambda r: " ".join(x[1] for x in r[0])

        assert floor_verdict(live, floor) == ([], None), "no protocol, nothing to check"

        live.write_text(v("1.13"))
        assert floor_verdict(live, floor) == ([], "1.13\n"), "first sight records the floor"
        floor.write_text("1.13\n")

        live.write_text(v("1.12"))
        r = floor_verdict(live, floor)
        assert lvl(r) == ["error"], f"a downgrade is an error, not a note: {r}"
        assert "below the v1.13" in msg(r) and r[1] is None, r

        # Every unusable floor is an ERROR: CI does not fail on warnings, so a
        # warning here ships the same green as a clean check.
        live.write_text(v("1.13"))
        for stage in ("symlink", "symlink_elsewhere", "dirlink", "hardlink",
                      "dir", "empty", "unreadable"):
            if floor.is_symlink():
                floor.unlink()          # a symlink to a dir is not a dir to rmdir
            elif floor.is_dir():
                floor.rmdir()
            elif floor.exists():
                floor.unlink()
            if stage == "symlink":
                floor.symlink_to(live)
            elif stage == "symlink_elsewhere":
                # A symlink to an unrelated, perfectly valid floor file. `samefile`
                # does not catch this one, so it isolates the symlink guard: without
                # it the write would silently replace the user's link.
                other = Path(d) / "elsewhere"
                other.write_text("1.13\n")
                floor.symlink_to(other)
            elif stage == "dirlink":
                floor.symlink_to(Path(d))
            elif stage == "hardlink":
                os.link(live, floor)          # a plain file, same inode — is_file() is True
            elif stage == "dir":
                floor.mkdir()
            elif stage == "empty":
                floor.write_text("   \n")
            else:
                floor.write_text("1.13\n")
                floor.chmod(0o000)
                if os.access(floor, os.R_OK):
                    floor.chmod(0o644)
                    continue                  # running as root: cannot stage this
            before = live.read_text()
            r = floor_verdict(live, floor)
            if stage == "unreadable":
                floor.chmod(0o644)
            assert lvl(r) == ["error"], f"{stage}: expected an error, got {r}"
            assert r[1] is None, f"{stage}: an unusable floor must not be re-armed"
            assert live.read_text() == before, f"{stage}: the live protocol was touched"

        # The write replaces the name, never follows it. A hard link at the floor
        # shares an inode with the protocol; open(floor,'w') truncates both.
        if floor.exists() or floor.is_symlink():
            floor.unlink()
        os.link(live, floor)
        before = live.read_text()
        assert write_floor(floor, "9.9\n") == "", "the write must succeed"
        assert live.read_text() == before, "write_floor must not write through a hard link"
        assert floor.read_text() == "9.9\n"
        assert not floor.with_name(floor.name + ".tmp").exists(), "no temp file left behind"

        floor.unlink()
        floor.symlink_to(live)
        before = live.read_text()
        assert write_floor(floor, "9.9\n") == "", "the write must succeed"
        assert live.read_text() == before, "write_floor must not write through a symlink"

    # The floor advances only on a passing run.
    assert should_write_floor("1.14\n", 0) is True
    assert should_write_floor("1.14\n", 1) is False, "a failed run must not raise the floor"
    assert should_write_floor(None, 0) is False
    assert should_write_floor("", 0) is False

    print("selfcheck OK — 40 assertions on real files:\n"
          "  version compare, title anchoring, floor init and advance,\n"
          "  downgrade refused, symlink / hard link / directory / empty / unreadable,\n"
          "  the write never follows a link, the floor never rises on a failed run")
    return 0


if "--selfcheck" in sys.argv[1:]:
    sys.exit(selfcheck())


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

# --- hooks ----------------------------------------------------------------

# hooks/hooks.json is discovered by convention — no `hooks` key in plugin.json, same
# as agents/. Nothing at runtime reports a hook that failed to load, and a hook that
# never fires is indistinguishable from one that works, so the manifest is checked
# here. Event names are the 31 in Claude Code's hooks reference (specs/REFERENCE.md).
HOOK_EVENTS = {
    "SessionStart", "Setup", "UserPromptSubmit", "UserPromptExpansion", "PreToolUse",
    "PermissionRequest", "PermissionDenied", "PostToolUse", "PostToolUseFailure",
    "PostToolBatch", "Notification", "MessageDisplay", "SubagentStart", "SubagentStop",
    "TaskCreated", "TaskCompleted", "Stop", "StopFailure", "TeammateIdle",
    "InstructionsLoaded", "ConfigChange", "CwdChanged", "DirectoryAdded", "FileChanged",
    "WorktreeCreate", "WorktreeRemove", "PreCompact", "PostCompact", "Elicitation",
    "ElicitationResult", "SessionEnd",
}

hooks_path = ROOT / "hooks/hooks.json"
hooks_manifest = {}
if not hooks_path.exists():
    # Required, not optional: deleting the manifest is the narrowest way to stop every
    # hook this plugin ships, and it left the gate green until a review said so.
    err("hooks/hooks.json does not exist; the plugin ships a hook and this is the file "
        "Claude Code discovers it by")
else:
    try:
        hooks_manifest = json.loads(hooks_path.read_text())
    except json.JSONDecodeError as exc:
        err(f"hooks/hooks.json is not valid JSON: {exc}")
if not (hooks_manifest.get("hooks") if isinstance(hooks_manifest, dict) else None):
    if hooks_path.exists():
        err("hooks/hooks.json declares no `hooks` object, so nothing is registered")
for event, matchers in (hooks_manifest.get("hooks") or {}).items():
    if event not in HOOK_EVENTS:
        err(f"hooks/hooks.json: {event!r} is not a Claude Code hook event; "
            f"an unknown event never fires and reports nothing")
    for matcher in matchers if isinstance(matchers, list) else []:
        for hook in matcher.get("hooks", []):
            cmd = hook.get("command", "")
            if not cmd:
                err(f"hooks/hooks.json: a {event} entry has no `command`")
            for rel in re.findall(r"\$\{?CLAUDE_PLUGIN_ROOT\}?/([^\"'\s]+)", cmd):
                if not (ROOT / rel).exists():
                    err(f"hooks/hooks.json: {event} runs {rel!r}, which does not "
                        f"exist. The hook would fail on every fire")

# --- skills ---------------------------------------------------------------

skill_dirs = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
skills = set()
forked: dict[str, str] = {}  # skill -> the agent type it forks into, checked below
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

    # forking keys. A typo here fails silently at runtime: the skill just keeps
    # running inline, which is the exact behaviour `context: fork` was set to stop.
    where = f"skills/{d.name}/SKILL.md"
    context = fm.get("context")
    if context is not None and context != "fork":
        err(f"{where}: context is {context!r}; `fork` is the only documented value")
    for key in ("agent", "background"):
        if key in fm and context is None:
            err(f"{where}: {key!r} only applies with `context: fork`, which is not set")
    if fm.get("background") not in (None, "true", "false"):
        err(f"{where}: background is {fm['background']!r}, must be `true` or `false`")
    if context == "fork":
        forked[d.name] = fm.get("agent", "general-purpose")

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

# a forked skill must name an agent type that exists — a missing one is a launch error
no_edit = {n for n in agents if "Edit" in frontmatter(ROOT / "agents" / f"{n}.md").get("disallowedTools", "")}
# `no_edit` is also the count README claims; keep it to repo agents. Explore and Plan
# are read-only built-ins, so they belong in the fork check and nowhere else.
cannot_write = no_edit | {"Explore", "Plan"}
for skill, agent in sorted(forked.items()):
    bare = agent.removeprefix("solodev:")
    if agent not in BUILTIN_AGENTS and bare not in agents:
        err(
            f"skills/{skill}/SKILL.md: agent {agent!r} is not a built-in "
            f"({', '.join(sorted(BUILTIN_AGENTS))}) and no agents/*.md defines it"
        )
        continue
    if agent in cannot_write or bare in cannot_write:
        warn(
            f"skills/{skill}/SKILL.md forks into {agent!r}, which cannot edit files. "
            "Correct for a read-only skill; wrong for one that writes its own output"
        )
    if bare in agents and agent == bare:
        warn(
            f"skills/{skill}/SKILL.md forks into {agent!r} unscoped. This plugin's "
            f"agents register as `solodev:{bare}`; the bare name may not resolve"
        )

# --- cross-references -----------------------------------------------------

md_files = sorted(ROOT.glob("**/*.md"))
md_files = [p for p in md_files if ".git" not in p.parts]

# `solodev:<x>` must resolve to a skill or an agent
for path in md_files:
    for ref in set(re.findall(r"solodev:([a-z0-9-]+)", path.read_text())):
        if ref not in skills and ref not in agents:
            err(f"{path.relative_to(ROOT)}: references solodev:{ref}, which is neither a skill nor an agent")

# files the loop skill copies at bootstrap must exist
loop = ROOT / "skills/autopilot/SKILL.md"
for ref in set(re.findall(r"`references/([A-Za-z0-9_.-]+)`", loop.read_text())):
    if not (loop.parent / "references" / ref).exists():
        err(f"skills/autopilot/SKILL.md: references/{ref} does not exist")

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

# The loop's workspace must NOT be committed. specs/ and docs/ hold workflow
# bookkeeping and raw command transcripts; a transcript captures whatever a run
# happened to print, and a credential in git history is permanent.
# This check asserted the exact opposite until 2026-08-04. Run #1 read a
# .gitignore listing these directories as a bug and deleted the lines. It was
# the rule, not a bug, and removing it made the plugin contaminate every repo
# it ran in — confirmed by the user from live use in another project.
tracked = subprocess.run(
    ["git", "ls-files", "--", "specs", "docs"],
    cwd=ROOT, capture_output=True, text=True,
)
if tracked.returncode != 0:
    err(f"git ls-files could not run ({tracked.stderr.strip() or 'unknown'}); the "
        f"workspace-not-committed check did NOT execute")
else:
    leaked = sorted(f for f in tracked.stdout.split("\n") if f.strip())
    if leaked:
        err(
            f"{len(leaked)} file(s) under specs/ or docs/ are tracked by git; these "
            f"never ship. First: {leaked[0]}. Untrack with "
            f"`git rm -r --cached specs docs`, and confirm .gitignore lists both"
        )

# a claim about how many agents cannot edit must match the frontmatter (`no_edit` above)
for path in (ROOT / "README.md", ROOT / "skills/autopilot/SKILL.md", ROOT / "docs/architecture.md"):
    if not path.exists():
        continue
    text = path.read_text()
    words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7}
    pat = r"(one|two|three|four|five|six|seven) of the (one|two|three|four|five|six|seven)"
    for claim, whole in re.findall(pat, text, re.IGNORECASE):
        if words[claim.lower()] != len(no_edit) or words[whole] != len(agents):
            err(
                f"{path.relative_to(ROOT)}: claims '{claim} of the {whole}' agents cannot edit, "
                f"but {len(no_edit)} of the {len(agents)} have no edit tools"
            )

# Every agent may spawn subagents — none of them disallow `Agent`. A helper reports
# to the agent that spawned it, so an agent returning early orphans its helpers'
# findings. The rule has to live in each agent file because there is no shared
# include; this check is what stops five copies drifting apart.
SPAWN_RULE = "If you spawn helpers, wait for them"
missing = sorted(
    md.stem for md in (ROOT / "agents").glob("*.md")
    if SPAWN_RULE not in md.read_text()
)
if missing:
    err(
        f"agents missing the spawn-and-wait rule: {', '.join(missing)}. A helper "
        f"reports to its spawner, so an agent that returns early loses those findings "
        f"entirely — the caller gets an idle notification and no report"
    )

# Severity definitions are duplicated by design — standalone skills must be
# self-contained in a repo that never bootstrapped the loop. This check is what
# stops the copies drifting into different meanings.
SEV_CANON = {
    "S1": "data loss, security hole, or a primary flow that cannot be completed",
    "S2": "primary flow broken but a workaround exists",
    "S3": "cosmetic, or an edge case unlikely in practice",
}
for rel in ("skills/autopilot/references/PROTOCOL.md", "skills/task/SKILL.md", "skills/qa/SKILL.md"):
    text = (ROOT / rel).read_text().lower()
    for sev, phrase in SEV_CANON.items():
        if phrase not in text:
            err(f"{rel}: {sev} definition drifted from the canonical phrase {phrase!r}")

# Phase 0 read budget. These two files are read before any work happens on every
# single run, and both grew without a cap until 2026-08-04: LOOP_STATE.md more than
# doubled across three runs and became the second-largest read in the set, while
# LOOP_LEARNINGS.md quietly passed the 150-line cap its own header has always
# claimed — a cap that was prose, and prose cannot fail.
#
# Budgets come from the measurement in docs/evidence/2026-08-04-r3-roll-off/, not
# from taste. Roll-off took LOOP_STATE.md from 23774 B to 11463 B; 14000 B leaves
# roughly one run of normal growth (a Run Log line, a few backlog rows, a rewritten
# task section) before the gate tells the next run to roll off again.
#
# specs/ is gitignored, so these files exist only where the loop has actually run.
# Absent is not a failure — the validator also runs on main and in repos that never
# bootstrapped the loop.
BUDGETS = {
    "specs/LOOP_STATE.md": ("bytes", 14000,
        "Roll off to specs/LOOP_ARCHIVE.md: move closed backlog rows and Run Log "
        "entries older than the three most recent. MOVE them — deleting loses the "
        "decision trail"),
    "specs/LOOP_LEARNINGS.md": ("lines", 150,
        "Delete rules the compiler, tests or lint now enforce and leave a one-line "
        "pointer to the check, per §4C. A rule guarded by code does not need a brain"),
}
for rel, (unit, cap, fix) in BUDGETS.items():
    path = ROOT / rel
    if not path.exists():
        continue
    text = path.read_text()
    size = len(text.encode()) if unit == "bytes" else len(text.splitlines())
    if size > cap:
        err(f"{rel} is {size} {unit}, over its {cap}-{unit[:-1]} Phase 0 budget by "
            f"{size - cap}. {fix}")

# Protocol version ratchet. specs/ is gitignored, so this only fires where the loop
# has actually run; a repo that never bootstrapped has no specs/LOOP.md and no floor.
LIVE = ROOT / "specs" / "LOOP.md"
FLOOR = ROOT / "specs" / ".protocol-floor"
_floor_problems, PENDING_FLOOR = floor_verdict(LIVE, FLOOR)
for _level, _msg in _floor_problems:
    (err if _level == "error" else warn)(_msg)

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

if should_write_floor(PENDING_FLOOR, len(errors)):
    _was = FLOOR.read_text().strip() if FLOOR.is_file() else None
    _why = write_floor(FLOOR, PENDING_FLOOR)
    if not _why and _was != PENDING_FLOOR.strip():
        # Say it out loud when the bar moves. The one destructive path left is a
        # hand-lowered floor, and it used to happen in complete silence.
        print(f"protocol floor {'recorded at' if _was is None else _was + ' ->'} "
              f"v{PENDING_FLOOR.strip()}")
    if _why:
        # Read-only checkout. A gate must not fail the build over its own
        # note-keeping; a floor it cannot raise simply stays where it is.
        warnings.append(f"could not write specs/.protocol-floor ({_why})")

print(f"skills: {len(skills)}  agents: {len(agents)} ({len(no_edit)} without edit tools)")
for w in warnings:
    print(f"WARN  {w}")
for e in errors:
    print(f"ERROR {e}")
print("FAIL" if errors else "OK")
sys.exit(1 if errors else 0)
