#!/usr/bin/env python3
"""Block a `git commit` that would carry the loop's workspace into git history.

PreToolUse hook. The loop's protocol (§2) says `specs/` and `docs/` are never
committed: `specs/` is the loop's bookkeeping, and `docs/evidence/` holds raw
transcripts of whatever a run happened to print — an env dump, a curl with an auth
header. A credential reaching git history is permanent, so this is the one rule worth
enforcing in code rather than trusting an agent to remember. `scripts/validate.py`
runs the identical check over this repo in CI; this runs it in the user's repo at the
moment it still matters.

It stays out of the way otherwise. A repo with no `specs/LOOP.md` never opted into the
loop, so the guard exits silently there — installing this plugin must not start
blocking commits in repos that have a perfectly ordinary tracked `docs/`.

Self-check: `python3 hooks/guard-workspace.py --selfcheck`
"""
# Annotations stay unevaluated: this runs on whatever python3 the user's machine has,
# and `str | None` is a syntax error before 3.10.
from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

BLOCK = 2  # PreToolUse: exit 2 blocks the call and feeds stderr back to Claude
ALLOW = 0

GIT_TIMEOUT = 2  # two git calls per candidate root, inside hooks.json's 5s budget

# The only two paths this hook blocks on. See the comment in `verdict()` for why it is
# narrower than protocol §2, which covers all of `docs/`.
OWNED = ("specs/", "docs/evidence/")

# Set this to anything to switch the guard off. `specs/LOOP.md` existing is a strong
# hint that a repo runs the loop, but it is not consent — somebody may have decided to
# commit their workspace on purpose, and a hook with no exit is a hook that gets the
# whole plugin uninstalled.
OPT_OUT = "SOLODEV_NO_GUARD"

# A `git` token only starts a command at position 0 or after one of these. Without the
# check, `grep -rn git commit .`, `man git commit`, and any heredoc body mentioning a
# commit are all read as invocations.
CMD_START = frozenset(("&&", "||", ";", "|", "(", "{", "!", "then", "do", "else"))

# git options that take a SEPARATE value; the walk must step over both tokens or the
# value gets mistaken for the subcommand.
GIT_VALUE_OPTS = frozenset(
    ("-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path")
)

MAX_ROOTS = 4  # two git calls each, at 2s — keeps the worst case inside the 5s budget

# Cheap pre-filter, used ONLY when the command cannot be tokenised. The real decision
# is made on tokens — a regex over raw shell text cannot survive quoting.
COMMIT_TEXT = re.compile(r"\bgit\b(?:\s+\S+)*?\s+commit\b")


def git(root: str, *args: str) -> "subprocess.CompletedProcess[str]":
    return subprocess.run(
        ["git", "-C", root, *args],
        capture_output=True, text=True, timeout=GIT_TIMEOUT,
    )


def _resolve(base: str, path: str) -> str:
    path = os.path.expanduser(path)
    return path if os.path.isabs(path) else os.path.join(base, path)


def commit_roots(command: str, cwd: str) -> list[str]:
    """Directories a `git commit` in this command could land in; empty means no commit.

    Tokenising is what makes `"git" commit` and `git"" commit` visible and
    `git log --author='git commit'` invisible — quotes vanish, and `commit` inside an
    argument stays one token rather than becoming a subcommand.

    ponytail: shlex does not expand `$VAR` or `$(...)`, so `$GIT commit` and
    `$(which git) commit` are not recognised. That hole is unbounded by construction —
    `python -c` can commit too — and this is a guard rail against a careless commit,
    not a sandbox against a determined one. Raising the ceiling means intercepting git
    itself, not parsing harder.
    """
    try:
        tokens = shlex.split(command, comments=True)
    except ValueError:
        # Unbalanced quotes: shlex cannot tell us anything. If the pre-filter thinks a
        # commit is in there, check cwd rather than waving it through.
        return [cwd] if COMMIT_TEXT.search(command) else []

    # `cd` anywhere in the command is another directory the commit might run in.
    # ponytail: each `cd` is resolved against cwd, not against the one before it —
    # chained relative `cd a && cd b` resolves to `a` and `b`, not `a/b`. Over-broad,
    # never under-broad, and the extra candidate costs one `git rev-parse`.
    bases = [cwd] + [
        _resolve(cwd, tokens[i + 1])
        for i, tok in enumerate(tokens[:-1]) if tok == "cd"
    ]

    roots: list[str] = []
    for i, tok in enumerate(tokens):
        if PurePosixPath(tok).name != "git":
            continue
        if i and tokens[i - 1] not in CMD_START:
            continue  # an argument to something else, or prose in a heredoc
        dash_c, j = None, i + 1
        while j < len(tokens):  # walk past git's own options to the subcommand
            if tokens[j] in GIT_VALUE_OPTS and j + 1 < len(tokens):
                if tokens[j] == "-C":
                    dash_c = tokens[j + 1]
                j += 2
            elif tokens[j].startswith("-"):
                j += 1
            else:
                break
        if j < len(tokens) and tokens[j] == "commit":
            roots.extend([_resolve(b, dash_c) for b in bases] if dash_c else bases)

    return list(dict.fromkeys(roots))[:MAX_ROOTS]  # dedupe, keep order, stay in budget


def verdict(command: str, cwd: str) -> tuple[int, str]:
    """Return (exit code, stderr). Unreadable input allows the commit through: a guard
    that cannot read its own input must not become the thing that breaks committing.
    The one exception is documented at `ls-files` below."""
    if os.environ.get(OPT_OUT):
        return ALLOW, ""
    for candidate in commit_roots(command, cwd):
        top = git(candidate, "rev-parse", "--show-toplevel")
        if top.returncode != 0:
            continue  # not a git repo; git itself will say so
        root = top.stdout.rstrip("\n")  # only the terminator — a path may end in a space

        if not (Path(root) / "specs" / "LOOP.md").exists():
            continue  # never opted into the loop

        tracked = git(root, "ls-files", "-z", "--", "specs", "docs")
        if tracked.returncode != 0:
            # Fails CLOSED, alone among the exits here. By this point the repo is known
            # to be a loop repo — the precondition held and only the verification
            # failed, so allowing would turn a known-sensitive repo into an unguarded one.
            return BLOCK, (
                f"solodev: could not check whether the loop's workspace is tracked in\n"
                f"  {root}\n\n"
                f"git ls-files failed: {tracked.stderr.strip() or '(no output)'}\n\n"
                f"specs/LOOP.md §2 forbids committing that workspace, so this commit is\n"
                f"held rather than guessed at. Run this yourself in that repository —\n"
                f"the same command the guard just failed to run:\n"
                f"  $ git ls-files -- specs docs\n"
                f"and fix whatever it reports before committing again."
            )
        found = sorted(f for f in tracked.stdout.split("\0") if f.strip())
        leaked = [f for f in found if f.startswith(OWNED)]
        if not leaked:
            continue

        # Only `specs/` and `docs/evidence/` block. §2 covers all of `docs/`, but this
        # hook runs in repositories that never heard of the loop, where a tracked
        # `docs/guide.md` is somebody's product and untracking it would be the damage.
        # Those two are the ones §2's own reasoning names: bookkeeping, and raw
        # transcripts that can carry a credential. `scripts/validate.py` keeps the wide
        # check for THIS repo, where all of `docs/` really is the workspace.
        # ponytail: a loop-written `docs/architecture.md` in a user's repo is therefore
        # only mentioned, never blocked on — it is indistinguishable from their own.
        others = [f for f in found if not f.startswith(OWNED)]
        also = (
            f"\nAlso tracked under docs/: {len(others)} "
            f"{'file' if len(others) == 1 else 'files'}, left alone by the fix above —\n"
            f"the guard cannot tell the loop's documentation from your own.\n"
            if others else ""
        )
        shown = "\n  ".join(leaked[:5])
        more = f"\n  ...and {len(leaked) - 5} more" if len(leaked) > 5 else ""
        count = "1 file is" if len(leaked) == 1 else f"{len(leaked)} files are"
        # Only the paths that actually matched: `git rm` aborts on a pathspec matching
        # nothing, so naming both when only one is tracked prints a fix that cannot run.
        targets = " ".join(
            p.rstrip("/") for p in OWNED if any(f.startswith(p) for f in leaked)
        )
        return BLOCK, (
            f"solodev: this commit would put the loop's workspace into git history.\n\n"
            f"{count} tracked in\n"
            f"  {root}\n\n"
            f"--- file names, quoted from the repository ---\n"
            f"  {shown}{more}\n"
            f"--- end ---\n\n"
            f"Why: docs/evidence/ holds raw transcripts of whatever a run printed, so a\n"
            f"credential committed there is permanent; specs/ is bookkeeping that belongs\n"
            f"to whoever runs the loop, not to the product. See specs/LOOP.md §2, and §3\n"
            f"Phase 6, which fails on the same thing.\n\n"
            f"Fix, in that repository:\n"
            f"  $ git rm -r --cached -- {targets}\n"
            # The leading \n matters: a .gitignore with no trailing newline would
            # otherwise get `node_modulesspecs/`, silently un-ignoring the last rule.
            # ponytail: still appends unconditionally, so a second block-and-fix cycle
            # leaves a duplicate line. A conditional form runs past 80 columns and wraps
            # mid-command, and a command you cannot copy in one piece is the worse bug.
            f"  $ printf '\\nspecs/\\ndocs/evidence/\\n' >> .gitignore\n"
            f"Then commit again. The files stay on disk; only git stops tracking them.\n"
            f"{also}"
            f"\nIf this repository commits its workspace on purpose, set {OPT_OUT}=1 in\n"
            f"the environment and the guard stays out of the way.\n"
        )

    return ALLOW, ""


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        tool_input = payload.get("tool_input") or {}
        command = tool_input.get("command")
        cwd = payload.get("cwd") or "."
    except (ValueError, AttributeError):
        return ALLOW
    # Another PreToolUse hook may have rewritten `updatedInput`, so the types are not
    # guaranteed by Claude Code's own Bash tool alone.
    if not isinstance(command, str) or not isinstance(cwd, str):
        return ALLOW

    try:
        code, message = verdict(command, cwd)
    except (OSError, ValueError, subprocess.SubprocessError):
        return ALLOW

    if message:
        print(message, file=sys.stderr)
    return code


# --- self-check ------------------------------------------------------------

def _repo(parent: str, name: str, *, loop: bool, tracked: str | None) -> str:
    """A throwaway git repo. `tracked` is a path staged with -f, ignore rules and all."""
    root = os.path.join(parent, name)
    os.makedirs(root)
    subprocess.run(["git", "init", "-q", root], check=True, capture_output=True)
    if loop:
        os.makedirs(os.path.join(root, "specs"), exist_ok=True)
        Path(root, "specs/LOOP.md").write_text("# LOOP PROTOCOL\n")
    if tracked:
        os.makedirs(os.path.dirname(os.path.join(root, tracked)), exist_ok=True)
        Path(root, tracked).write_text("AWS_SECRET=hunter2\n")
        subprocess.run(["git", "-C", root, "add", "-f", tracked],
                       check=True, capture_output=True)
    return root


def selfcheck() -> int:
    """Oracle: every answer below is known by hand, and asserts the VERDICT, not the
    parse. An earlier draft asserted only that the matcher fired, and shipped two
    High-severity holes underneath a green check (a review found two High-severity holes under a
    green check that asserted only the parse)."""
    checks = 0

    def eq(got, want, what):
        nonlocal checks
        checks += 1
        assert got == want, f"{what}: got {got!r}, want {want!r}"

    with tempfile.TemporaryDirectory() as tmp:
        plain = _repo(tmp, "plain", loop=False, tracked=None)
        ordinary = _repo(tmp, "ordinary", loop=False, tracked="docs/guide.md")
        clean = _repo(tmp, "clean", loop=True, tracked=None)
        dirty = _repo(tmp, "dirty", loop=True, tracked="docs/evidence/run.txt")
        authored = _repo(tmp, "authored", loop=True, tracked="docs/api-reference.md")

        # The four quadrants. (b) is the one that matters most: an ordinary repo with a
        # tracked docs/ belongs to someone who never asked for this plugin's opinion.
        eq(verdict("git commit -m x", plain)[0], ALLOW, "(a) non-loop, clean")
        eq(verdict("git commit -m x", ordinary)[0], ALLOW, "(b) non-loop, tracked docs/")
        eq(verdict("git commit -m x", clean)[0], ALLOW, "(c) loop repo, clean workspace")
        code, msg = verdict("git commit -m x", dirty)
        eq(code, BLOCK, "(d) loop repo, tracked workspace")
        assert "docs/evidence/run.txt" in msg, "the blocking message must name the file"
        assert "git rm -r --cached -- docs/evidence\n" in msg, "must state a runnable fix"
        assert "hunter2" not in msg, "names only — never file content"
        checks += 3

        # (e) A loop repo whose tracked docs/ file is the AUTHOR'S, not the loop's. The
        # guard must not hold their commit hostage, and must never name their file in a
        # `git rm --cached`. An audit rated this severity 4: untracking
        # someone else's documentation is damage, not a fix.
        eq(verdict("git commit -m x", authored)[0], ALLOW, "(e) loop repo, author's docs/")

        # The repo the commit lands in is not always the session's cwd.
        eq(verdict(f"cd {dirty} && git commit -m x", plain)[0], BLOCK, "cd into a loop repo")
        eq(verdict(f"git -C {dirty} commit -m x", plain)[0], BLOCK, "-C into a loop repo")
        eq(verdict(f"cd {clean} && git commit -m x", plain)[0], ALLOW, "cd into a clean one")

        # Quoting is punctuation, not permission.
        for form in ('"git" commit -m x', "git'' commit -m x", "/usr/bin/git commit"):
            eq(verdict(form, dirty)[0], BLOCK, f"quoted form {form!r}")

        # Reading history is not committing, and neither is saying the word. Every case
        # below runs against `dirty`, where a block is possible — asserting ALLOW in a
        # repo that can never block proves nothing.
        for form in ("git log --grep=commit", "git log --author='git commit'",
                     "echo 'remember to git commit later'", "git status",
                     "git log --oneline | grep 'git commit'", "git show HEAD --stat",
                     "grep -rn git commit .", "man git commit",
                     "python3 scripts/validate.py", ""):
            eq(verdict(form, dirty)[0], ALLOW, f"non-commit {form!r}")

        # A command shlex cannot parse does not run, but it is checked anyway: shlex is
        # not bash, and guessing ALLOW on the guard's own confusion is how a leak ships.
        eq(verdict("git commit -m 'unbalanced", dirty)[0], BLOCK, "unparseable, cwd checked")
        eq(verdict("git commit -m 'unbalanced", plain)[0], ALLOW, "unparseable, clean cwd")
        eq(verdict("git commit", os.path.join(tmp, "does-not-exist"))[0], ALLOW,
           "cwd that does not exist")

        # The escape hatch works, and it is the whole reason the guard is installable.
        os.environ[OPT_OUT] = "1"
        try:
            eq(verdict("git commit -m x", dirty)[0], ALLOW, f"{OPT_OUT} disables the guard")
        finally:
            del os.environ[OPT_OUT]

        # The printed fix must be runnable. `git rm` aborts on a pathspec matching
        # nothing, so a repo leaking only one of the two must not be told to name both.
        specs_only = _repo(tmp, "specs-only", loop=True, tracked="specs/LOOP_STATE.md")
        code, msg = verdict("git commit -m x", specs_only)
        eq(code, BLOCK, "specs/ alone still blocks")
        assert "git rm -r --cached -- specs\n" in msg, f"fix names only specs/: {msg!r}"
        checks += 1
        both = _repo(tmp, "both", loop=True, tracked="specs/LOOP_STATE.md")
        Path(both, "docs/evidence").mkdir(parents=True)
        Path(both, "docs/evidence/run.txt").write_text("x\n")
        subprocess.run(["git", "-C", both, "add", "-f", "docs/evidence/run.txt"],
                       check=True, capture_output=True)
        assert "git rm -r --cached -- specs docs/evidence\n" in verdict("git commit", both)[1]
        checks += 1

    print(f"selfcheck OK — {checks} assertions on real throwaway repos:\n"
          f"  four quadrants + the author's own docs/, cd and -C retargeting,\n"
          f"  quoted invocations, history reads, unreadable input")
    return 0


if __name__ == "__main__":
    sys.exit(selfcheck() if "--selfcheck" in sys.argv else main())
