#!/usr/bin/env python3
"""save_transcript.py - copy this project's agent conversations out of vendor folders into the repo.

The conversation record lives in the repo (AGENTS.md Part A section 8). Each host keeps transcripts
in its own home folder; this copies the ones that belong to this project into
docs/sessions/raw/<host>/<YYMMDDhhmm>-<basename>.

Hosts and where they write:
  claude       ~/.claude/projects/<slug>/*.jsonl          slug = cwd with every non-alphanumeric char -> '-'
  codex        ~/.codex/sessions/**/rollout-*.jsonl        filtered by mention of this repo's path
  gemini       ~/.gemini/tmp/*/chats/*                     filtered by mention of this repo's path
  antigravity  ~/.gemini/antigravity-cli/brain/**, ~/.gemini/antigravity/conversations/**,
               ~/.gemini/antigravity-ide/brain/**          filtered by mention of this repo's path
  cursor       SQLite workspace storage; no file export. Printed as a reminder, nothing copied.

A file is copied when it was modified after .harness/last_transcript_sync (epoch seconds; absent = 0)
and belongs to this project. Nothing is ever deleted at the source. Run by harness-close step 9.

Usage: python scripts/save_transcript.py [--home DIR] [--dry-run] [--selftest]
# ponytail: mtime + substring filter, no JSONL parsing. Upgrade when a host changes its layout.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HOSTS: dict[str, list[str]] = {
    "claude": [".claude/projects/<slug>/*.jsonl"],
    "codex": [".codex/sessions/**/rollout-*.jsonl"],
    "gemini": [".gemini/tmp/*/chats/*"],
    "antigravity": [".gemini/antigravity-cli/brain/**/*", ".gemini/antigravity/conversations/**/*",
                    ".gemini/antigravity-ide/brain/**/*"],
}
MARKER = Path(".harness") / "last_transcript_sync"


def repo_root() -> Path:
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False).stdout.strip()
    except OSError:
        top = ""
    return Path(top) if top else Path.cwd()


def slugs(root: Path) -> set[str]:
    """Claude's per-project folder name; the drive letter's case varies with how the tool was launched."""
    s = str(root)
    out = {re.sub(r"[^A-Za-z0-9]", "-", s)}
    if len(s) > 1 and s[1] == ":":
        out.add(re.sub(r"[^A-Za-z0-9]", "-", s[0].swapcase() + s[1:]))
    return out


def mentions_repo(p: Path, root: Path) -> bool:
    needles = {str(root), root.as_posix(), str(root).replace("\\", "\\\\")}
    try:
        with p.open("r", encoding="utf-8", errors="ignore") as fh:
            head = fh.read(2_000_000)
    except OSError:
        return False
    return any(n in head for n in needles)


def candidates(home: Path, root: Path) -> list[tuple[str, Path, bool]]:
    """(host, path, needs_content_filter) for every file a host pattern matches."""
    out = []
    for host, patterns in HOSTS.items():
        for pat in patterns:
            if "<slug>" in pat:
                for sl in slugs(root):
                    out += [(host, p, False) for p in home.glob(pat.replace("<slug>", sl)) if p.is_file()]
            else:
                out += [(host, p, True) for p in home.glob(pat) if p.is_file()]
    return out


def stamp(ts: float) -> str:
    return dt.datetime.fromtimestamp(ts).strftime("%y%m%d%H%M")


def sync(root: Path, home: Path, dry_run: bool, now: float | None = None) -> tuple[list[str], list[str]]:
    marker = root / MARKER
    since = float(marker.read_text().strip()) if marker.is_file() else 0.0
    copied, skipped = [], []
    for host, p, needs_filter in sorted(candidates(home, root), key=lambda t: (t[0], str(t[1]))):
        mtime = p.stat().st_mtime
        if mtime <= since:
            skipped.append(f"{host}: {p.name} older than last sync")
            continue
        if needs_filter and not mentions_repo(p, root):
            skipped.append(f"{host}: {p.name} does not mention this repo")
            continue
        dest = root / "docs" / "sessions" / "raw" / host / f"{stamp(mtime)}-{p.name}"
        if dest.exists() and dest.stat().st_size == p.stat().st_size:
            skipped.append(f"{host}: {p.name} already copied")
            continue
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)
        copied.append(f"{host}: {p.name} -> {dest.relative_to(root).as_posix()}")
    if not dry_run:
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(str(now if now is not None else time.time()), encoding="utf-8")
    return copied, skipped


def selftest() -> int:
    bad = 0

    def case(label: str, ok: bool) -> None:
        nonlocal bad
        bad += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {label}")

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        root = base / "repo"
        home = base / "home"
        root.mkdir()
        sl = next(iter(slugs(root)))
        (home / ".claude/projects" / sl).mkdir(parents=True)
        (home / ".claude/projects" / sl / "abc.jsonl").write_text('{"type":"user"}\n', encoding="utf-8")
        (home / ".claude/projects/other-project").mkdir(parents=True)
        (home / ".claude/projects/other-project/zzz.jsonl").write_text("{}\n", encoding="utf-8")
        (home / ".codex/sessions/2026/10/03").mkdir(parents=True)
        (home / ".codex/sessions/2026/10/03/rollout-mine.jsonl").write_text(f'{{"cwd":"{root.as_posix()}"}}\n', encoding="utf-8")
        (home / ".codex/sessions/2026/10/03/rollout-theirs.jsonl").write_text('{"cwd":"/elsewhere"}\n', encoding="utf-8")
        (home / ".gemini/antigravity-ide/brain/123").mkdir(parents=True)
        (home / ".gemini/antigravity-ide/brain/123/conv.md").write_text(f"work in {root}\n", encoding="utf-8")
        copied, skipped = sync(root, home, dry_run=False, now=time.time() + 5)
        names = " ".join(copied)
        case("claude transcript in this project's slug folder copied", "abc.jsonl" in names)
        case("claude transcript of another project not copied", "zzz.jsonl" not in names)
        case("codex rollout mentioning the repo copied", "rollout-mine.jsonl" in names)
        case("codex rollout of another repo skipped", any("rollout-theirs" in s for s in skipped))
        case("antigravity brain file mentioning the repo copied", "conv.md" in names)
        case("copies land under docs/sessions/raw/<host>/", (root / "docs/sessions/raw/claude").is_dir() and (root / "docs/sessions/raw/codex").is_dir())
        case("marker written", (root / MARKER).is_file())
        copied2, skipped2 = sync(root, home, dry_run=False)
        case("second run copies nothing new", not copied2 and any("older than last sync" in s for s in skipped2))
        case("sources untouched", (home / ".claude/projects" / sl / "abc.jsonl").is_file())
    print("SELFTEST-OK" if not bad else f"SELFTEST-FAILURES: {bad}")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--home", default="", help="override the home directory (tests)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    root = repo_root()
    home = Path(a.home) if a.home else Path(os.environ.get("HARNESS_HOME") or Path.home())
    copied, skipped = sync(root, home, a.dry_run)
    for line in copied:
        print(("would copy " if a.dry_run else "copied ") + line)
    print(f"save_transcript: {len(copied)} copied, {len(skipped)} skipped. cursor: no file export; attach manually if used.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
