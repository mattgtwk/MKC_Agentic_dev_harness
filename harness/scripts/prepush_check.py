"""Pre-push enforcement for repo-dev RULE ONE and RULE TWO. Stdlib + git only.

VENDORED into the harness kit from mkc_agentic_workflow_langchain/.claude/scripts/prepush_check.py
(2026-10-03) with two edits and nothing else: the two tunables below are named constants. Everything
after this block is the original file.

  SKIP  which paths are NOT production code (tests, docs, tooling, generated). Tune per repo layout.
  BASE  the branch a push is judged against. Default origin/main; env HARNESS_BASE overrides.

Prose did not stop PR #191 shipping the same two mistakes five rounds running, so these
are mechanical.

  RULE ONE  scope. Always prints the production churn per file, because the shape of the
            diff is the tell: a "composer" CR whose largest file is the stream provider
            grew a subsystem it never needed (#191). BLOCKS when a production file is
            outside the branch's first commit - that is a review finding you decided to
            fix instead of writing down. Override with `SCOPE-OK: <reason>` in a commit
            message, so the justification lands in the history rather than in a chat.

  RULE TWO  read before you write. Report-only:
            - every definition whose line you changed, with EVERY site that reads it,
              including sites in files already in your diff - which is exactly where
              #191's defect hid: `disabled={composerDisabled}` handed a flag to the
              kiosk composer, whose Cancel button then died with it;
            - the files where you MODIFIED existing lines rather than adding, with the
              command to read the incumbent (#191: main returned early on a failed
              refresh; the invented replacement fired an opener at a stale project).

HOW IT RUNS.  As git's own `pre-push` hook: `git config core.hooksPath .githooks`, once
per clone. Git runs it inside the repository, for the refs actually being pushed, which
it hands over on stdin - so there is nothing to detect and nothing to parse.

That is the whole design, and it is the second one. The first tried to recognise a push
by matching the shell command with a regex, from a PreToolUse hook. Four consecutive
review rounds found bugs in that matcher, and an adversarial pass then demonstrated six
more working push forms it missed (`git --% push`, an unquoted `cmd /c git push`, an
absolute path to git.exe, `--git-dir <d> push`, `-c "a b"`, and a bare refspec push from
another branch), plus `cd repo; git push` with a PowerShell semicolon, which it did not
merely miss: it ran the check against the WRONG repository and printed "RULE ONE clear".
A guard that attests to a tree the push never touches is worse than no guard. Shell
commands are not a regular language, and git already knows what is being pushed, so it
is asked instead of guessed.
"""

from __future__ import annotations

import os
import pathlib
import re
import subprocess
import sys

SKIP = re.compile(  # tunable 1: what is not production code
    r"(^|/)(tests?|__tests__|e2e)/|"
    r"\.(test|spec)\.[jt]sx?$|_test\.py$|(^|/)test_[^/]+\.py$|"
    r"^docs/|^\.claude/|^\.agents/|^\.agent/|^_bmad|^\.harness/|^\.githooks/|^\.github/|^scripts/|"
    r"\.md$|\.json$|\.toml$|^\.git(ignore|attributes)$|^infra/|(^|/)migrations/"
)
BASE = os.environ.get("HARNESS_BASE", "origin/main")  # tunable 2: the branch pushes are judged against
DEFN = re.compile(
    r"^\s*(?:export\s+)?(?:const|let|var|function|async\s+function|class)\s+([A-Za-z_$][\w$]*)"
    r"|^\s*(?:export\s+)?(?:async\s+)?def\s+([A-Za-z_][\w]*)"
)
CAP = 10
GENERIC = 40  # more sites than this and the name is too common to be a signal
ZERO = "0" * 40  # git's "no such ref" sha, used for a deletion


def git(*args: str) -> str:
    out = subprocess.run(
        ["git", *args], capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return out.stdout if out.returncode == 0 else ""


def verdict(message: str) -> int:
    """Say something on EVERY exit. A checker that printed nothing when it found nothing
    was indistinguishable from one that printed nothing because it was broken - which is
    how a self-inflicted fail-open rode along for a whole round (2026-09-16)."""
    sys.stderr.write(f"pre-push check: {message}\n")
    return 0


def refusal(unread: int, surface: set[str], overridden: bool) -> str | None:
    """Why this run must NOT report a clean result, or None if it may.

    Both reasons are the rule this file enforces, turned on itself: do not vouch for a
    diff you could not read. Saying "some of this was not understood" and then "RULE ONE
    clear" in the next breath is a fail-open with a disclaimer attached."""
    if unread:
        return (
            f"{unread} numstat row(s) could not be read, so this check covered less than"
            " the whole\ndiff and cannot report it clear. Run `git diff --numstat"
            " origin/main...HEAD` and look\nat the rows it prints."
        )
    if not surface and not overridden:
        return (
            "the CR's first commit has no file list, so there is no surface to judge"
            " scope\nagainst. That happens when the branch's first commit is a MERGE"
            " (git prints a\ncombined diff for one). Put the branch's own first commit"
            " before the merge, or\nrecord a SCOPE-OK: reason for what the merge brings"
            " in."
        )
    return None


def parse_numstat(rows: list[str]) -> tuple[list[tuple[int, int, str]], int, int]:
    """(production churn, files excluded, rows not understood). Binary files count: git
    writes `-` for their line counts, and dropping those rows made a branch whose only
    production change was a binary report itself clean, in a confident sentence.

    A row that is not three tab-separated fields is COUNTED and reported rather than
    dropped. It should never happen, which is exactly why it has to be loud: a silently
    discarded row shrinks the surface RULE ONE is computed over, and the report would
    still read as a confident clean result - the same shape as every other bug in this
    file's history."""
    churn: list[tuple[int, int, str]] = []
    skipped = 0
    unread = 0
    for row in rows:
        parts = row.split("\t")
        if len(parts) != 3:
            unread += 1
            continue
        if SKIP.search(parts[2]):
            skipped += 1
            continue
        added, deleted = (int(p) if p.isdigit() else 0 for p in parts[:2])
        churn.append((added, deleted, parts[2]))
    return churn, skipped, unread


def surface_of(base: str, tip: str) -> tuple[set[str], list[str]]:
    """The files the CR's first REAL commit touched, plus the commit list. A branch that
    starts by merging main - routine here - used to get an EMPTY surface, because
    `git show --name-only` prints nothing for a merge, and then every file it owned, the
    feature included, was reported as a stray. Skipping file-less commits fixes that;
    `--first-parent` fixes the other half, where merging a sibling branch pulled in a
    commit older than mine and made MY OWN first commit look like the stray."""
    # `--first-parent`: only this branch's own commits. Merging a SIBLING branch pulls
    # its commits into the range, and one of them is usually older than mine, so it was
    # picked as the surface and my own first commit was reported as the stray.
    commits = git("rev-list", "--reverse", "--first-parent", f"{base}..{tip}").split()
    for commit in commits:
        # A merge prints no file list at all (git shows a combined diff), so it falls
        # through the empty-list check below. A merge CAN be the first commit on the
        # first-parent line - branch from main, then immediately merge a sibling - and
        # when it is the ONLY one the surface comes back empty. `report` refuses to
        # vouch in that case rather than calling it clear.
        files = {
            p
            # `--no-renames` on BOTH sides or they cannot agree: the churn list sees a
            # rename as a delete plus an add, while `show` with detection on names only
            # the new path, so the old one looked like a file the CR never touched.
            for p in git("show", "--name-only", "--no-renames", "--format=", commit).splitlines()
            if p and not SKIP.search(p)
        }
        if files:
            return files, commits
    return set(), commits


def report(base: str, tip: str, label: str) -> int:
    # `--no-renames` matters: the default compact form `src/{old.py => new.py}` can never
    # equal the plain path `git show` prints, so a renamed file was ALWAYS a stray, and
    # the only way past it was a SCOPE-OK for a file that was never out of scope.
    churn, skipped, unread = parse_numstat(
        git("diff", "--numstat", "--no-renames", f"{base}...{tip}").splitlines()
    )
    surface, ordered = surface_of(base, tip)
    if not ordered:
        return verdict(f"{label}: no commits ahead of the baseline - nothing to check.")
    if not churn:
        return verdict(
            f"{label}: {len(ordered)} commit(s), no production files changed"
            f"{f' ({skipped} excluded by the skip list)' if skipped else ''}."
        )
    churn.sort(key=lambda r: -(r[0] + r[1]))
    strays = [r for r in churn if r[2] not in surface] if len(ordered) > 1 else []
    override = re.search(
        r"^SCOPE-OK:\s*(.+)$", git("log", "--format=%B", f"{base}..{tip}"), re.MULTILINE
    )

    out: list[str] = [f"RULE ONE - production churn on {label}, largest first:"]
    total = sum(a + d for a, d, _ in churn)
    for added, deleted, path in churn:
        share = (added + deleted) * 100 // max(total, 1)
        mark = (
            "  <-- outside the CR's first commit"
            if path not in surface and len(ordered) > 1
            else ""
        )
        size = "      binary  " if added + deleted == 0 else f"+{added:>5} -{deleted:>5}"
        out.append(f"    {size}  {share:>3}%  {path}{mark}")
    if skipped:
        # Name what was NOT looked at, so the skip list is a visible choice rather than
        # a blind spot. It covers *.json and infra/, which is where the signed admin
        # allowlists and the deployment tfvars live.
        out.append(f"    ({skipped} changed file(s) excluded: tests, docs, *.json, infra/)")
    if unread:
        out.append(
            f"    ({unread} numstat row(s) NOT UNDERSTOOD and left out - this report"
            " covers less than the whole diff)"
        )
    biggest = churn[0]
    if len(churn) > 1 and (biggest[0] + biggest[1]) > total / 2:
        out.append(
            f"  {biggest[2]} is more than half this CR's production churn."
            "  Is it the feature, or a review finding you grew?"
        )
    if strays:
        out.append("  A review finding in a file the CR never needed is a BACKLOG item: an ADL")
        out.append("  'surfaced, NOT fixed' bullet, a PR line, a follow-up CR. Fix it here only")
        out.append("  for a security hole, data loss, or a defect this CR creates. Ask: would it")
        out.append("  exist if the CR were reverted? Yes = backlog.")
        out.append(
            f"  {'OVERRIDDEN by SCOPE-OK: ' + override.group(1).strip() if override else 'To proceed: put SCOPE-OK: <reason> in a commit message.'}"
        )

    # Definitions whose line you changed, and EVERY site that reads them - including
    # sites in files already in your diff, which is where #191's Cancel-button defect
    # hid (`disabled={composerDisabled}`, a prop pass in a file that was 'already read').
    touched: dict[str, str] = {}
    for _, _, path in churn:
        for line in git("diff", "-U0", f"{base}...{tip}", "--", path).splitlines():
            if not line.startswith(("+", "-")) or line.startswith(("+++", "---")):
                continue
            m = DEFN.match(line[1:])
            if m:
                name = next(g for g in m.groups() if g)
                if len(name) > 4:
                    touched.setdefault(name, path)
    sites: list[str] = []
    for name, path in sorted(touched.items()):
        segments = path.split("/")
        # A root-level file has no directory to search in: the pathspec `toolbox.py/*`
        # matches nothing, `git grep` exits 1, and that empty result read as "no sites".
        if len(segments) == 1:
            tree, spec = ".", ["--", "."]
        else:
            tree = "/".join(segments[:3]) if len(segments) > 3 else segments[0]
            spec = ["--", f"{tree}/*"]
        # Grep the REF BEING PUSHED, not the working tree. `tip` can be any branch on a
        # pre-push line, and a working-tree grep then lists consumers from a different
        # branch and misses the real ones - the same "attests to a tree the push never
        # touched" failure the command matcher was replaced for. With a revision, git
        # prefixes each hit with `<rev>:`, so the path is the SECOND field.
        hits = git("grep", "-n", "-w", name, tip, *spec).splitlines()
        # Grepping a revision prefixes every hit with `<40-char sha>:`, which is noise
        # that eats the line budget below - the point of this list is the call site.
        hits = [h[len(tip) + 1:] if h.startswith(f"{tip}:") else h for h in hits]
        hits = [h for h in hits if not SKIP.search(h.split(":", 1)[0])]
        if not hits or len(hits) > GENERIC:
            continue  # no hits, or a name so common the list would be noise
        sites.append(f"    {name}  ({len(hits)} sites in {tree})")
        sites.extend(f"        {h.strip()[:110]}" for h in hits[:CAP])
        if len(hits) > CAP:
            sites.append(f"        ... and {len(hits) - CAP} more")
    if sites:
        out.append("")
        out.append("RULE TWO - definitions you changed, and every site that reads them:")
        out.extend(sites)
        out.append("  Read them ALL, including the ones in files you already edited. A value")
        out.append("  handed to a component as a prop is consumed by code you did not write.")

    modified = [(a, d, p) for a, d, p in churn if d > 0]
    if modified:
        out.append("")
        out.append("RULE TWO - these change EXISTING behaviour. Read the incumbent first:")
        for added, deleted, path in modified:
            out.append(f"    git show {BASE}:{path}    (+{added} -{deleted})")
        out.append("  The incumbent is usually right: it has been in production.")

    bar = "=" * 72
    sys.stderr.write(f"{bar}\npre-push check (.claude/scripts/prepush_check.py)\n{bar}\n")
    sys.stderr.write("\n".join(out) + "\n")
    if strays and not override:
        sys.stderr.write("\nPUSH BLOCKED by RULE ONE (see above).\n")
        return 2
    why = refusal(unread, surface, bool(override))
    if why:
        sys.stderr.write(f"\nPUSH BLOCKED: {why}\n")
        return 2
    return verdict(f"{label}: RULE ONE clear.")


def main(tips: list[tuple[str, str]] | None = None) -> int:
    """tips: (label, sha) for each ref being pushed, from git's pre-push stdin. None
    means the script was run by hand, which checks HEAD."""
    if not git("rev-parse", "--is-inside-work-tree").strip():
        return verdict("not a git worktree - nothing checked.")
    worst = 0
    for label, tip in tips or [("HEAD", "HEAD")]:
        base = (git("merge-base", BASE, tip) or "").strip()
        if not base:
            # FAIL CLOSED. A guard that waves the push through exactly when it cannot
            # establish its baseline (a fresh clone, a shallow checkout, origin/main
            # never fetched) is a guard with a one-command bypass.
            sys.stderr.write(
                f"pre-push check: cannot resolve a baseline for {label} (no merge-base "
                "with origin/main).\nRun `git fetch origin main`, or run the checks by "
                "hand before pushing.\nPUSH BLOCKED.\n"
            )
            return 2
        worst = max(worst, report(base, tip, label))
    return worst


def parse_push_refs(text: str) -> list[tuple[str, str]]:
    """git's pre-push protocol: one `<local ref> <local sha> <remote ref> <remote sha>`
    per line. A deletion carries the all-zero local sha and changes no code, so it is
    skipped. This is the whole reason the command no longer needs parsing: `git push
    --all`, a bare refspec, a push of a branch that is not even checked out - every one
    of them arrives here already named.

    A non-blank line that is NOT four fields RAISES. Skipping it row by row left `refs`
    empty on a truncated payload, and the caller then exited through the "nothing to
    check" path - a clean exit on input this could not read, under a comment promising
    to fail closed. Not understanding the input is not the same as there being nothing
    to check, and a guard must never confuse the two."""
    refs: list[tuple[str, str]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 4:
            raise ValueError(f"malformed pre-push line: {line[:80]!r}")
        if parts[1] != ZERO:
            # Keep the whole branch name: `feat/a` and `fix/a` both printed as "a".
            refs.append((re.sub(r"^refs/(heads|tags)/", "", parts[0]), parts[1]))
    return refs


def self_test() -> int:
    """`--self-test`: the parsing everything else is built on, over git's real output
    shapes. The command matcher these cases used to cover is gone; what is left is where
    the silent wrong answers actually came from."""
    bad = 0
    for label, rows, want in [
        ("a plain modification", ["12\t3\tapp/backend/src/a.py"], [(12, 3, "app/backend/src/a.py")]),
        ("a BINARY file - git prints - -", ["-\t-\tapp/frontend/public/logo.png"],
         [(0, 0, "app/frontend/public/logo.png")]),
        ("an added file", ["40\t0\tapp/backend/src/new.py"], [(40, 0, "app/backend/src/new.py")]),
        ("a test file is excluded", ["5\t0\tapp/backend/tests/test_a.py"], []),
        ("a docs file is excluded", ["5\t0\tdocs/plan.md"], []),
        ("infra is excluded", ["5\t0\tinfra/terraform/main.tf"], []),
        ("a malformed row is left out of the churn", ["nonsense"], []),
    ]:
        got, _, _ = parse_numstat(rows)
        bad += got != want
        print(f"{'ok  ' if got == want else 'FAIL'} {got!s:<46} {label}")
    for label, rows, want in [
        ("excluded files are COUNTED, not silently dropped",
         ["5\t0\tdocs/a.md", "1\t1\tapp/backend/src/a.py"], 1),
    ]:
        _, got_skipped, _ = parse_numstat(rows)
        bad += got_skipped != want
        print(f"{'ok  ' if got_skipped == want else 'FAIL'} skipped={got_skipped!s:<38} {label}")
    for label, args, want_refusal in [
        ("a readable diff with a surface may be reported clean", (0, {"a.py"}, False), False),
        ("an unreadable row refuses to attest", (1, {"a.py"}, False), True),
        ("...even with SCOPE-OK, which is about scope and not about reading it",
         (1, {"a.py"}, True), True),
        ("an EMPTY surface refuses to attest", (0, set(), False), True),
        ("...and SCOPE-OK releases that one", (0, set(), True), False),
    ]:
        got = refusal(*args) is not None
        bad += got != want_refusal
        print(f"{'ok  ' if got == want_refusal else 'FAIL'} refuses={got!s:<38} {label}")

    # ...and a row it could not read is COUNTED, so the report can say its surface was
    # incomplete instead of quietly shrinking and still reading as clean.
    _, _, got_unread = parse_numstat(["nonsense", "1\t1\tapp/backend/src/a.py"])
    bad += got_unread != 1
    print(f"{'ok  ' if got_unread == 1 else 'FAIL'} unread={got_unread!s:<39} a row it cannot read is COUNTED")

    for label, text, want in [
        ("a push of one branch", "refs/heads/feat abc123 refs/heads/feat def456",
         [("feat", "abc123")]),
        ("a branch DELETION is skipped", f"(delete) {ZERO} refs/heads/old def456", []),
        ("--all pushes several refs at once",
         "refs/heads/a aaa refs/heads/a 111\nrefs/heads/b bbb refs/heads/b 222",
         [("a", "aaa"), ("b", "bbb")]),
        ("blank lines are not an error", "\n  \n", []),
        ("nothing on stdin", "", []),
    ]:
        got = parse_push_refs(text)
        bad += got != want
        print(f"{'ok  ' if got == want else 'FAIL'} {got!s:<46} {label}")
    for label, text in [
        ("a malformed line RAISES, never skipped", "garbage"),
        ("a truncated protocol line RAISES", "refs/heads/feat abc123"),
        ("a good line beside a bad one still RAISES", "refs/heads/a aaa refs/heads/a 1\nbad"),
    ]:
        try:
            parse_push_refs(text)
            raised = False
        except ValueError:
            raised = True
        bad += not raised
        print(f"{'ok  ' if raised else 'FAIL'} raised={raised!s:<39} {label}")
    bad += live_test()
    print("SELF-TEST-OK" if not bad else f"SELF-TEST-FAILURES: {bad}")
    return 1 if bad else 0


def live_test() -> int:
    """The cases no amount of string parsing can reach, each built as a throwaway
    repository. Two of them were FALSE BLOCKS - the guard stopping honest work - and one
    was a false clear, and all three were invisible to a parsing-only suite."""
    import shutil
    import tempfile

    def run(repo, *args, stdin=None):
        return subprocess.run(
            args, cwd=repo, capture_output=True, text=True,
            encoding="utf-8", errors="replace", input=stdin,
        )

    def make(repo):
        for cmd in (
            ("git", "init", "-q", "-b", "main"),
            ("git", "config", "user.email", "t@t"),
            ("git", "config", "user.name", "t"),
            ("git", "config", "commit.gpgsign", "false"),
        ):
            run(repo, *cmd)
        (repo / "app/backend/src").mkdir(parents=True)

    def commit(repo, msg):
        run(repo, "git", "add", "-A")
        run(repo, "git", "commit", "-q", "-m", msg)

    def case(label, repo, want, names=None, says=None, silent=None, push=None):
        # `push`: a ref line, fed through the real pre-push stdin protocol. Otherwise
        # the script is run by hand, which checks HEAD.
        me = str(pathlib.Path(__file__).resolve())
        out = (
            run(repo, sys.executable, me, "--git-hook", stdin=push)
            if push
            else run(repo, sys.executable, me)
        )
        got = out.returncode
        # The exit code alone cannot tell a correct block from one that blamed the
        # wrong file, or a report about the right tree from one about another tree.
        checks = (
            names is None or f"{names}  <--" in out.stderr,
            says is None or says in out.stderr,
            silent is None or silent not in out.stderr,
        )
        ok = got == want and all(checks)
        detail = "" if all(checks) else "  [the report named the wrong thing]"
        print(f"{'ok  ' if ok else 'FAIL'} exit={got} (want {want})   {label}{detail}")
        return not ok

    bad = 0
    root = pathlib.Path(tempfile.mkdtemp())
    try:
        # A rename IS the feature. numstat splits it into a delete and an add, so the
        # surface has to be read the same way or the old path is always a stray, and
        # the only way past it is a SCOPE-OK for a file that was never out of scope.
        repo = root / "rename"
        repo.mkdir()
        make(repo)
        (repo / "app/backend/src/old_name.py").write_text("x = 1\n")
        commit(repo, "base")
        run(repo, "git", "branch", "-f", "origin/main", "main")
        run(repo, "git", "checkout", "-q", "-b", "feat")
        run(repo, "git", "mv", "app/backend/src/old_name.py", "app/backend/src/new_name.py")
        commit(repo, "feat: rename it")
        (repo / "app/backend/src/new_name.py").write_text("x = 1\ny = 2\n")
        commit(repo, "feat: extend it")
        bad += case("a RENAME as the CR's own first commit", repo, 0)

        # Merging main into a feature branch is routine here, and `git show` prints no
        # file list for a merge, which used to empty the surface and strand every file
        # the branch owns, the feature included.
        repo = root / "merge"
        repo.mkdir()
        make(repo)
        (repo / "app/backend/src/base.py").write_text("x = 1\n")
        commit(repo, "base")
        run(repo, "git", "checkout", "-q", "-b", "feat")
        run(repo, "git", "checkout", "-q", "main")
        (repo / "app/backend/src/other.py").write_text("z = 1\n")
        commit(repo, "main moves on")
        run(repo, "git", "branch", "-f", "origin/main", "main")
        run(repo, "git", "checkout", "-q", "feat")
        run(repo, "git", "merge", "-q", "--no-ff", "-m", "sync main", "main")
        (repo / "app/backend/src/keep.py").write_text("k = 1\n")
        commit(repo, "feat: the actual feature")
        bad += case("a MERGE of main as the branch's first act", repo, 0)

        # A branch whose FIRST first-parent commit is a merge has no surface at all -
        # git prints no file list for a merge - and when it is the only commit the
        # stray test is disabled too, so a colleague's production changes used to ride
        # in reported clean. It refuses to vouch instead.
        repo = root / "mergeonly"
        repo.mkdir()
        make(repo)
        (repo / "app/backend/src/base.py").write_text("x = 1\n")
        commit(repo, "base")
        run(repo, "git", "branch", "-f", "origin/main", "main")
        run(repo, "git", "checkout", "-q", "-b", "colleague")
        (repo / "app/backend/src/theirs.py").write_text("t = 1\n")
        commit(repo, "theirs")
        run(repo, "git", "checkout", "-q", "-b", "feat", "main")
        run(repo, "git", "merge", "-q", "--no-ff", "-m", "take theirs", "colleague")
        bad += case("a branch whose ONLY commit is a merge", repo, 2)
        # ...and SCOPE-OK releases it, or a sync-first branch has no way past.
        run(repo, "git", "commit", "-q", "--allow-empty", "-m",
            "chore: note\n\nSCOPE-OK: the merge is a colleague's reviewed work")
        bad += case("...released by SCOPE-OK", repo, 0)

        # Merging a SIBLING branch pulls its commits into the range, and one of them
        # is usually older than mine - so it was chosen as the surface and my own
        # first commit was reported as the stray.
        repo = root / "sibling"
        repo.mkdir()
        make(repo)
        (repo / "app/backend/src/base.py").write_text("x = 1\n")
        commit(repo, "base")
        run(repo, "git", "branch", "-f", "origin/main", "main")
        run(repo, "git", "checkout", "-q", "-b", "colleague")
        (repo / "app/backend/src/theirs.py").write_text("t = 1\n")
        commit(repo, "theirs: older than mine")
        run(repo, "git", "checkout", "-q", "-b", "feat", "main")
        (repo / "app/backend/src/mine.py").write_text("m = 1\n")
        commit(repo, "feat: mine")
        run(repo, "git", "merge", "-q", "--no-ff", "-m", "take theirs", "colleague")
        # Correct to block - the branch carries a colleague's commit into the PR -
        # but it must blame THEIR file. Their commit is older, so it used to be taken
        # as the surface and my own first commit was reported as the stray.
        bad += case(
            "a MERGE of a sibling branch blames THEIR file",
            repo, 2, names="app/backend/src/theirs.py",
        )

        # RULE TWO must read the REF BEING PUSHED. Pushing `feat` by refspec while
        # `other` is checked out used to list `other`'s consumers and miss `feat`'s -
        # a report about a tree the push never touches, which is the exact failure the
        # command matcher was replaced for.
        repo = root / "refspec"
        repo.mkdir()
        make(repo)
        (repo / "app/backend/src/base.py").write_text("x = 1\n")
        commit(repo, "base")
        run(repo, "git", "branch", "-f", "origin/main", "main")
        run(repo, "git", "checkout", "-q", "-b", "feat")
        (repo / "app/backend/src/defs.py").write_text(
            "def shared_helper():\n    return 1\n"
        )
        (repo / "app/backend/src/on_feat.py").write_text(
            "from defs import shared_helper\n"
        )
        commit(repo, "feat: add it together with its consumer")
        run(repo, "git", "checkout", "-q", "-b", "other", "main")
        (repo / "app/backend/src/on_other.py").write_text(
            "from defs import shared_helper\n"
        )
        commit(repo, "other: a consumer that is NOT on feat")
        sha = run(repo, "git", "rev-parse", "feat").stdout.strip()
        bad += case(
            "RULE TWO reads the PUSHED ref, not the checkout",
            repo, 0, says="        app/backend/src/on_feat.py:", silent="on_other.py",
            push=f"refs/heads/feat {sha} refs/heads/feat {'0' * 40}\n",
        )

        # Binary files have no line counts, so dropping those rows made a branch with a
        # genuine stray report itself clean, in a confident sentence.
        repo = root / "binary"
        repo.mkdir()
        make(repo)
        (repo / "app/backend/src/model.bin").write_bytes(bytes(range(256)))
        commit(repo, "base")
        run(repo, "git", "branch", "-f", "origin/main", "main")
        run(repo, "git", "checkout", "-q", "-b", "feat")
        (repo / "app/backend/src/model.bin").write_bytes(bytes(range(255, -1, -1)))
        commit(repo, "feat: retrain")
        (repo / "app/backend/other").mkdir()
        (repo / "app/backend/other/stray.bin").write_bytes(bytes([0, 1, 2]))
        commit(repo, "fix: an unrelated binary")
        bad += case("a BINARY-only branch with a genuine stray", repo, 2)

        # And the guard still blocks the thing it exists for.
        repo = root / "stray"
        repo.mkdir()
        make(repo)
        (repo / "app/backend/src/base.py").write_text("x = 1\n")
        commit(repo, "base")
        run(repo, "git", "branch", "-f", "origin/main", "main")
        run(repo, "git", "checkout", "-q", "-b", "feat")
        (repo / "app/backend/src/base.py").write_text("x = 2\n")
        commit(repo, "feat: the feature")
        (repo / "app/backend/src/elsewhere.py").write_text("y = 1\n")
        commit(repo, "fix: a review finding I grew")
        bad += case("a stray outside the first commit", repo, 2)

        # ...unless the reason is written into the history.
        run(repo, "git", "commit", "-q", "--allow-empty", "-m",
            "docs: note\n\nSCOPE-OK: it is a data-loss fix")
        bad += case("...and a SCOPE-OK in a commit message releases it", repo, 0)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    return bad


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    if "--git-hook" in sys.argv:
        try:
            payload = sys.stdin.read()
            refs = parse_push_refs(payload)
        except Exception as exc:
            # FAIL CLOSED, and deliberately broad. `ValueError` is the malformed-row
            # case, but a decode error or a read error on stdin must block too. Git
            # itself aborts a push on ANY non-zero pre-push exit, so an uncaught
            # exception would still block HERE - the reason to catch it is to say WHY,
            # rather than dumping a traceback and leaving the cause to be guessed, and
            # to keep the behaviour right for any non-git caller that distinguishes
            # exit codes. Narrowing it would drop that explanation.
            sys.stderr.write(
                f"pre-push check: could not read the pushed refs ({exc}).\n"
                "PUSH BLOCKED - run `python .claude/scripts/prepush_check.py` by hand.\n"
            )
            sys.exit(2)
        if refs:
            sys.exit(main(refs))
        # Empty stdin means git found nothing to send; lines with an all-zero local sha
        # mean the push only DELETES refs. Neither changes code, but they are different
        # situations and saying the wrong one is how a report stops being trusted.
        sys.exit(
            verdict(
                "only ref deletions pushed - no code to check."
                if payload.strip()
                else "nothing to push - no code to check."
            )
        )
    sys.exit(main())
