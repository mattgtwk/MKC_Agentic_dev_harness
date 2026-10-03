#!/usr/bin/env python3
"""harness_lint.py - the one deterministic gate of the harness. Stdlib only, Python 3.11+.

Usage
  python scripts/harness_lint.py                      lint the repo (pre-commit, CI)
  python scripts/harness_lint.py --prepush            lint + commit-range checks; reads git's pre-push stdin
  python scripts/harness_lint.py --ratchet [--update-baseline] [--coverage-xml PATH]
  python scripts/harness_lint.py --doctor [--relink]  environment: junctions, hooks, BMAD overrides, tools
  python scripts/harness_lint.py --rebuild-index      regenerate docs/memory/MEMORY.md
  python scripts/harness_lint.py --selftest           every check seen green on a good fixture and red on a break
  --json on any mode; --quiet prints only WARN and ERROR rows (the hooks use it)

Exit 1 on any ERROR. A check that could not run reports WARN, never PASS.
Every rule it enforces is named in AGENTS.md Part A section 6.
# ponytail: one file, no dependencies; split only when a second repo needs a different check set.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AGENTS_MAX = 24 * 1024          # Codex project_doc_max_bytes default is 32 KiB; leave headroom
CONTEXT_MAX = 32 * 1024         # AGENTS.md + CLAUDE.md + GEMINI.md + docs/memory/MEMORY.md
CONTEXT_WARN = 24 * 1024
SKILL_MAX = 15 * 1024
MEMORY_MAX = 800
ARCH_MAX_DAYS = 90
BASE = os.environ.get("HARNESS_BASE", "origin/main")
OUR_SKILLS = {"harness-open", "harness-plan", "harness-close"}
REQUIRED_SKILLS = ("bmad-agent-pm", "caveman", "ponytail", "grill-me", "grilling")
ALWAYS_LOADED = ("AGENTS.md", "CLAUDE.md", "GEMINI.md", "docs/memory/MEMORY.md")

VERSION_RE = re.compile(r"harness-constitution v\d+\.\d+\.\d+")
PART_A_RE = re.compile(r"^## Part A\b.*$", re.M)
PART_B_RE = re.compile(r"^## Part B\b.*$", re.M)
ADAPTER_LINE_RE = re.compile(r"^@\.?/?AGENTS\.md\s*$")
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SKILL_TOKEN_RE = re.compile(r"`((?:harness-|bmad-)[a-z0-9-]+|caveman[a-z0-9-]*|ponytail[a-z0-9-]*|grill-me|grilling)`")
VERIFY_RE = re.compile(r"<!--\s*verify:\s*(.+?)\s*-->")
LAST_REVIEWED_RE = re.compile(r"last_reviewed:\s*(\d{4}-\d{2}-\d{2})")
TOOLING_RE = re.compile(r"^(scripts/|\.githooks/|\.github/)")
NOT_SOURCE_RE = re.compile(r"^(docs/|\.agents/|_bmad|\.harness/|coverage_baseline\.json$|skills-lock\.json$)|\.md$|^\.git(ignore|attributes)$")
SECRET_RES = [re.compile(p) for p in (
    r"AKIA[0-9A-Z]{16}", r"ghp_[A-Za-z0-9]{36}", r"\bsk-[A-Za-z0-9_-]{20,}", r"xox[baprs]-[A-Za-z0-9-]{10,}",
    r"-----BEGIN [A-Z ]*PRIVATE KEY", r"Bearer [A-Za-z0-9._-]{20,}",
)]
SKIP_DIRS = {".git", "node_modules", "_bmad", "_bmad-output", ".venv", "__pycache__"}


# ---------------------------------------------------------------- plumbing
class Report:
    def __init__(self) -> None:
        self.rows: list[dict] = []

    def add(self, check: str, level: str, msg: str) -> None:
        self.rows.append({"check": check, "level": level, "message": msg})

    def ok(self, check: str, msg: str = "ok") -> None:
        self.add(check, "PASS", msg)

    def warn(self, check: str, msg: str) -> None:
        self.add(check, "WARN", msg)

    def err(self, check: str, msg: str) -> None:
        self.add(check, "ERROR", msg)

    def levels(self, check: str) -> set[str]:
        return {r["level"] for r in self.rows if r["check"] == check}

    @property
    def errors(self) -> list[dict]:
        return [r for r in self.rows if r["level"] == "ERROR"]

    def render(self, as_json: bool, quiet: bool = False) -> str:
        if as_json:
            return json.dumps(self.rows, indent=1)
        rows = [r for r in self.rows if r["level"] != "PASS"] if quiet else self.rows
        width = max((len(r["check"]) for r in rows), default=10)
        lines = [f"{r['level']:<5} {r['check']:<{width}}  {r['message']}" for r in rows]
        n_err = len(self.errors)
        n_warn = sum(1 for r in self.rows if r["level"] == "WARN")
        lines.append(f"harness_lint: {n_err} error(s), {n_warn} warning(s)")
        return "\n".join(lines)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8-sig", errors="replace")


def git(root: Path, *args: str) -> str:
    try:
        out = subprocess.run(["git", *args], cwd=str(root), capture_output=True, text=True,
                             encoding="utf-8", errors="replace", check=False)
    except OSError:
        return ""
    return out.stdout if out.returncode == 0 else ""


def repo_root() -> Path:
    top = git(Path.cwd(), "rev-parse", "--show-toplevel").strip()
    return Path(top) if top else Path.cwd()


def walk_text(d: Path):
    """Yield (path, text) for text files under d, skipping vendor and generated dirs."""
    for p in sorted(d.rglob("*")):
        if any(part in SKIP_DIRS for part in p.parts) or not p.is_file():
            continue
        try:
            yield p, p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue


def slug(s: str) -> str:
    s = re.sub(r"[`*_]", "", s.strip().lower())
    s = re.sub(r"[^a-z0-9 -]", "", s)
    return re.sub(r"\s+", "-", s).strip("-")


def frontmatter(text: str) -> tuple[dict, str]:
    """Return (fields, body). Fields are flat: a nested 'type:' is lifted to the top."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    fm, body = parts[1], parts[2]
    fields: dict[str, str] = {}
    key = None
    for line in fm.splitlines():
        m = re.match(r"^\s*([A-Za-z_-]+):\s*(.*)$", line)
        if m:
            key = m.group(1)
            val = m.group(2).strip()
            if val in (">", ">-", "|", "|-"):
                val = ""
            fields.setdefault(key, val.strip('"'))
        elif key and line.startswith((" ", "\t")) and line.strip():
            fields[key] = (fields[key] + " " + line.strip()).strip()
    return fields, body


# ---------------------------------------------------------------- lint checks
def check_agents(root: Path, rep: Report) -> str:
    p = root / "AGENTS.md"
    if not p.is_file():
        rep.err("agents-present", "AGENTS.md missing")
        return ""
    text = read(p)
    a, b = PART_A_RE.search(text), PART_B_RE.search(text)
    problems = []
    if not VERSION_RE.search(text):
        problems.append("no 'harness-constitution vX.Y.Z' line")
    if not a or not b or b.start() < a.start():
        problems.append("needs '## Part A ...' before '## Part B ...'")
    part_a = text[a.start():b.start()] if (a and b and a.start() < b.start()) else text
    (rep.err if problems else rep.ok)("agents-present", "; ".join(problems) or "version line and both parts present")
    size = len(text.encode("utf-8"))
    (rep.err if size > AGENTS_MAX else rep.ok)("agents-size", f"{size} bytes (cap {AGENTS_MAX})")

    rules, cur = [], None
    for line in part_a.splitlines():
        if re.match(r"^- \*\*", line):
            if cur:
                rules.append(cur)
            cur = [line]
        elif cur is not None and line.strip() and not line.startswith(("- ", "|", "#")):
            cur.append(line)
        else:
            if cur:
                rules.append(cur)
            cur = None
    if cur:
        rules.append(cur)
    missing = [r[0][2:50].strip("* .") for r in rules if "Enforced by:" not in "\n".join(r)]
    if not rules:
        rep.warn("rule-enforcement", "no '- **Rule.**' bullets found in Part A; nothing to check")
    elif missing:
        rep.err("rule-enforcement", f"{len(missing)} rule(s) without 'Enforced by:': " + "; ".join(missing[:5]))
    else:
        rep.ok("rule-enforcement", f"{len(rules)} rules, each names its enforcement")
    m = re.search(r"ADR-\d{4}", part_a)
    (rep.err if m else rep.ok)("adr-refs", f"Part A cites {m.group(0)}; the constitution cites no ADR numbers" if m else "Part A cites no ADR numbers")
    return text


def check_adapters(root: Path, rep: Report) -> None:
    for name in ("CLAUDE.md", "GEMINI.md"):
        p = root / name
        if not p.is_file():
            rep.err("adapter-thin", f"{name} missing (one line: @./AGENTS.md)")
            continue
        lines = read(p).splitlines()
        content = [ln for ln in lines if ln.strip() and not (ln.strip().startswith("<!--") and ln.strip().endswith("-->"))]
        if len(lines) > 5 or not content or not all(ADAPTER_LINE_RE.match(ln.strip()) for ln in content):
            rep.err("adapter-thin", f"{name}: must be <=5 lines whose only content is '@./AGENTS.md' (adapters hold no rules)")
        else:
            rep.ok("adapter-thin", f"{name} imports AGENTS.md and nothing else")


def check_context_budget(root: Path, rep: Report) -> None:
    total = sum((root / f).stat().st_size for f in ALWAYS_LOADED if (root / f).is_file())
    msg = f"{total} bytes always loaded (warn {CONTEXT_WARN}, cap {CONTEXT_MAX})"
    if total > CONTEXT_MAX:
        rep.err("context-budget", msg)
    elif total > CONTEXT_WARN:
        rep.warn("context-budget", msg)
    else:
        rep.ok("context-budget", msg)


def check_skill_refs(root: Path, rep: Report) -> None:
    missing = set()
    for f in ("AGENTS.md", "docs/HARNESS.md"):
        p = root / f
        if p.is_file():
            for tok in SKILL_TOKEN_RE.findall(read(p)):
                if not (root / ".agents" / "skills" / tok / "SKILL.md").is_file():
                    missing.add(tok)
    if missing:
        rep.err("skill-refs", "cited but not installed under .agents/skills/: " + ", ".join(sorted(missing)))
    else:
        rep.ok("skill-refs", "every cited skill exists")


def check_skills(root: Path, rep: Report) -> None:
    sk = root / ".agents" / "skills"
    if not sk.is_dir():
        rep.err("skills-frontmatter", ".agents/skills/ missing")
        rep.err("skills-lock", ".agents/skills/ missing")
        return
    bad, third = [], []
    for d in sorted(p for p in sk.iterdir() if p.is_dir()):
        if d.name not in OUR_SKILLS:
            third.append(d.name)
        f = d / "SKILL.md"
        if not f.is_file():
            bad.append(f"{d.name}: no SKILL.md")
            continue
        text = read(f)
        fm, _ = frontmatter(text)
        name, desc = fm.get("name", ""), fm.get("description", "")
        if name != d.name or not NAME_RE.match(name) or len(name) > 64:
            bad.append(f"{d.name}: frontmatter name '{name}' must equal the directory and be kebab-case")
        if not desc or len(desc) > 1024:
            bad.append(f"{d.name}: description missing or over 1024 chars")
        size = len(text.encode("utf-8"))
        if size > SKILL_MAX:
            msg = f"{d.name}: SKILL.md is {size} bytes (cap {SKILL_MAX}); move detail to references/"
            if d.name in OUR_SKILLS:
                bad.append(msg)
            else:
                rep.warn("skills-frontmatter", msg + " (third-party; not ours to split)")
    (rep.err if bad else rep.ok)("skills-frontmatter", "; ".join(bad[:5]) if bad else "every SKILL.md has a valid name and description")
    lock = root / "skills-lock.json"
    if third and not lock.is_file():
        rep.err("skills-lock", f"{len(third)} third-party skill(s) but no skills-lock.json (install them with 'npx skills add' so the pin exists)")
    elif third:
        rep.ok("skills-lock", f"{len(third)} third-party skill(s) pinned; restore on a fresh clone with 'npx skills experimental_install'")
    else:
        rep.ok("skills-lock", "no third-party skills yet")


def register_ids(root: Path) -> list[int]:
    reg = root / "docs" / "adr" / "README.md"
    if not reg.is_file():
        return []
    return [int(m.group(1)) for m in re.finditer(r"^\|\s*\[?(\d{4})\]?", read(reg), re.M)]


def heading_matches(p: Path, target: str) -> bool:
    want = slug(target)
    for line in read(p).splitlines():
        if line.startswith("#"):
            have = slug(line.lstrip("#"))
            if have == want or have.endswith("-" + want) or have.endswith(want):
                return True
    return False


def authority_resolves(root: Path, token: str, ids: list[int]) -> bool:
    token = token.strip().strip("`").strip()
    if not token:
        return False
    m = re.match(r"^ADR-(\d{4})$", token)
    if m:
        return int(m.group(1)) in ids
    path, _, heading = token.partition("#")
    p = root / path.strip()
    if not p.exists():
        return False
    return heading_matches(p, heading) if heading else True


def memory_page_errors(root: Path, page: Path, ids: list[int]) -> list[str]:
    text = read(page)
    fm, body = frontmatter(text)
    errs = []
    if not fm:
        errs.append("missing frontmatter")
    for key in ("name", "description", "type"):
        if not fm.get(key):
            errs.append(f"frontmatter lacks {key}")
    if fm.get("type") and fm["type"] not in ("user", "feedback", "project", "reference"):
        errs.append(f"type '{fm['type']}' not in user|feedback|project|reference")
    for field in ("Fact", "Why", "Authority"):
        if not re.search(rf"^\*\*{field}:\*\*", body, re.M):
            errs.append(f"missing **{field}:**")
    size = len(body.strip().encode("utf-8"))
    if size > MEMORY_MAX and fm.get("reviewed", "").lower() != "true":
        errs.append(f"body {size} bytes exceeds {MEMORY_MAX} (a restated rule does not fit; point at the owner instead)")
    m = re.search(r"^\*\*Authority:\*\*\s*(.+)$", body, re.M)
    if m:
        bad = [t for t in m.group(1).split(";") if not authority_resolves(root, t, ids)]
        if bad:
            errs.append("Authority does not resolve: " + "; ".join(b.strip() for b in bad) + " (grammar: path | path#heading | ADR-NNNN)")
    return errs


def index_lines(pages: list[Path]) -> list[str]:
    out = []
    for p in pages:
        fm, _ = frontmatter(read(p))
        out.append(f"- [{fm.get('name', p.stem)}]({p.name}) - {fm.get('description', '')}".rstrip(" -"))
    return out


def memory_pages(root: Path) -> list[Path]:
    d = root / "docs" / "memory"
    return sorted(p for p in d.glob("*.md") if p.name not in ("MEMORY.md", "README.md")) if d.is_dir() else []


def check_memory(root: Path, rep: Report) -> None:
    d = root / "docs" / "memory"
    if not d.is_dir():
        rep.err("memory-schema", "docs/memory/ missing")
        return
    ids = register_ids(root)
    pages = memory_pages(root)
    schema, authority = [], []
    for p in pages:
        for e in memory_page_errors(root, p, ids):
            (authority if e.startswith("Authority") else schema).append(f"{p.name}: {e}")
    (rep.err if schema else rep.ok)("memory-schema", "; ".join(schema[:5]) if schema else f"{len(pages)} page(s) pass the schema")
    (rep.err if authority else rep.ok)("memory-authority", "; ".join(authority[:5]) if authority else "every Authority resolves")
    idx = d / "MEMORY.md"
    if not idx.is_file():
        rep.err("memory-index", "docs/memory/MEMORY.md missing (run --rebuild-index)")
        return
    linked = set(re.findall(r"\]\(([^)]+\.md)\)", read(idx)))
    actual = {p.name for p in pages}
    if linked != actual:
        rep.err("memory-index", f"index drift: missing {sorted(actual - linked)}, stale {sorted(linked - actual)} (run --rebuild-index)")
    else:
        rep.ok("memory-index", "index matches pages")


def rebuild_index(root: Path) -> Path:
    d = root / "docs" / "memory"
    d.mkdir(parents=True, exist_ok=True)
    header = ("# Memory index\n\nGenerated by `python scripts/harness_lint.py --rebuild-index`; never hand-edit. "
              "One line per page, never content. Read a page when its line is relevant.\n\n")
    (d / "MEMORY.md").write_text(header + "\n".join(index_lines(memory_pages(root))) + "\n", encoding="utf-8", newline="\n")
    return d / "MEMORY.md"


def check_adr(root: Path, rep: Report) -> None:
    d = root / "docs" / "adr"
    if not d.is_dir() or not (d / "README.md").is_file():
        rep.err("adr-register", "docs/adr/README.md (the register) missing")
        return
    files = {int(m.group(1)): p.name for p in d.glob("*.md") if (m := re.match(r"^(\d{4})-", p.name)) and m.group(1) != "0000"}
    rows = register_ids(root)
    problems = []
    for i, name in sorted(files.items()):
        if i not in rows:
            problems.append(f"{name} has no register row")
    for i in rows:
        if i not in files:
            problems.append(f"row {i:04d} has no file")
    if files and sorted(files) != list(range(1, len(files) + 1)):
        problems.append(f"ids not sequential from 0001: {sorted(files)}")
    (rep.err if problems else rep.ok)("adr-register", "; ".join(problems[:5]) if problems else f"{len(files)} ADR(s), one row each, sequential")


def check_architecture(root: Path, rep: Report, today: dt.date | None = None) -> None:
    docs = root / "docs"
    maps = [p for p in docs.rglob("*.md") if p.name.lower() == "architecture.md"] if docs.is_dir() else []
    if len(maps) != 1:
        rep.err("architecture-map", f"expected exactly one docs/**/ARCHITECTURE.md, found {len(maps)}")
        return
    m = LAST_REVIEWED_RE.search(read(maps[0]))
    if not m:
        rep.err("architecture-map", f"{maps[0].name} lacks 'last_reviewed: YYYY-MM-DD'")
        return
    age = ((today or dt.date.today()) - dt.date.fromisoformat(m.group(1))).days
    (rep.warn if age > ARCH_MAX_DAYS else rep.ok)("architecture-map", f"last_reviewed {m.group(1)} ({age} days; warn after {ARCH_MAX_DAYS}; harness-close bumps it)")


def claim_holds(root: Path, claim: str) -> tuple[bool, str]:
    m = re.match(r"^exists\s+(.+)$", claim)
    if m:
        return (root / m.group(1).strip()).exists(), claim
    m = re.match(r"^(absent|present|count)\s+'(.+?)'\s+in\s+(\S+)(?:\s+exclude\s+(\S+))?(?:\s+between\s+(\d+)\s+and\s+(\d+))?$", claim)
    if not m:
        return False, f"unparseable claim: {claim}"
    verb, pattern, where, exclude, lo, hi = m.groups()
    rx = re.compile(pattern)
    target = root / where

    def hits(text: str) -> int:  # a claim never counts the verify: line that states it
        return sum(1 for ln in text.splitlines() if rx.search(ln) and "verify:" not in ln)

    n = 0
    if target.is_file():
        n = hits(read(target))
    elif target.is_dir():
        for p, text in walk_text(target):
            if exclude and p.name == exclude:
                continue
            n += hits(text)
    else:
        return False, f"{claim}: path {where} missing"
    if verb == "absent":
        return n == 0, f"{claim}: {n} hit(s)"
    if verb == "present":
        return n > 0, f"{claim}: {n} hit(s)"
    if lo is None:
        return False, f"{claim}: count needs 'between A and B'"
    return int(lo) <= n <= int(hi), f"{claim}: {n}"


def check_claims(root: Path, rep: Report) -> None:
    failed, total = [], 0
    for p, text in walk_text(root):
        rel = p.relative_to(root).as_posix()
        if p.suffix != ".md" or rel.startswith("docs/sessions/raw"):
            continue
        if rel.startswith(".agents/skills/") and rel.split("/")[2] not in OUR_SKILLS:
            continue
        for claim in VERIFY_RE.findall(text):
            total += 1
            ok, detail = claim_holds(root, claim.strip())
            if not ok:
                failed.append(f"{rel}: {detail}")
    (rep.err if failed else rep.ok)("claims", "; ".join(failed[:5]) if failed else f"{total} verify: claim(s) hold")


def check_secrets(root: Path, rep: Report) -> None:
    hits = []
    for p, text in walk_text(root):
        rel = p.relative_to(root).as_posix()
        if not (p.suffix == ".md" or rel.startswith("docs/sessions/")):
            continue
        if rel.startswith(".agents/skills/") and rel.split("/")[2] not in OUR_SKILLS:
            continue
        for rx in SECRET_RES:
            if rx.search(text):
                hits.append(f"{rel} matches {rx.pattern[:24]}")
                break
    tracked_env = git(root, "ls-files", "--", ".env", ".env.*").strip()
    if tracked_env:
        hits.append("tracked env file(s): " + tracked_env.replace("\n", ", "))
    (rep.err if hits else rep.ok)("secrets-scan", "; ".join(hits[:5]) if hits else "no token-shaped literals; no tracked .env")


def lint(root: Path, today: dt.date | None = None) -> Report:
    rep = Report()
    check_agents(root, rep)
    check_adapters(root, rep)
    check_context_budget(root, rep)
    check_skill_refs(root, rep)
    check_skills(root, rep)
    check_memory(root, rep)
    check_adr(root, rep)
    check_architecture(root, rep, today)
    check_claims(root, rep)
    check_secrets(root, rep)
    return rep


# ---------------------------------------------------------------- --prepush
def parse_push_refs(text: str) -> list[tuple[str, str]]:
    refs = []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) != 4:
            raise ValueError(f"malformed pre-push line: {line[:80]!r}")
        if parts[1] != "0" * 40:
            refs.append((re.sub(r"^refs/(heads|tags)/", "", parts[0]), parts[1]))
    return refs


def range_checks(root: Path, rep: Report, tip: str, label: str) -> None:
    base = git(root, "merge-base", BASE, tip).strip()
    if not base:
        rep.err("prepush-base", f"{label}: no merge-base with {BASE}; run 'git fetch'. First push of a new repo? Push main before arming hooks (BOOTSTRAP step 1 precedes step 6). Fail closed.")
        return
    changed = [f for f in git(root, "diff", "--name-only", "--no-renames", f"{base}...{tip}").splitlines() if f]
    product = [f for f in changed if not NOT_SOURCE_RE.search(f) and not TOOLING_RE.search(f)]
    tooling = [f for f in changed if TOOLING_RE.search(f)]
    log = git(root, "log", "--format=%B", f"{base}..{tip}")
    source = product or tooling
    if not changed:
        rep.ok("prepush-range", f"{label}: nothing ahead of {BASE}")
        return
    if product:
        first = ""
        for c in git(root, "rev-list", "--reverse", "--first-parent", f"{base}..{tip}").split():
            if git(root, "show", "--name-only", "--format=", c).strip():
                first = c
                break
        body = git(root, "log", "-1", "--format=%B", first) if first else ""
        has = bool(re.search(r"^Surface:", body, re.M))
        (rep.ok if has else rep.err)("surface", f"{label}: first commit {'declares' if has else 'lacks'} 'Surface:' ({len(product)} production file(s) changed)")
    else:
        rep.ok("surface", f"{label}: no production files changed")
    if product and tooling:
        has = bool(re.search(r"^KIND-OK:", log, re.M))
        (rep.ok if has else rep.err)("one-kind", f"{label}: product and tooling paths both changed; " + ("KIND-OK present" if has else "add 'KIND-OK: <reason>' or split the PR"))
    else:
        rep.ok("one-kind", f"{label}: one kind of change")
    if source:
        missing = [t for t in ("Review:", "Tests:") if not re.search(rf"^{t}", log, re.M)]
        (rep.err if missing else rep.ok)("trailers", f"{label}: " + (f"missing trailer(s) {missing} in the pushed commits" if missing else "Review: and Tests: trailers present"))
        touched = any(f.startswith("docs/sessions/") for f in changed)
        (rep.ok if touched else rep.err)("session-log", f"{label}: " + ("session log in range" if touched else "source changed but docs/sessions/ untouched (write the session log; harness-close does)"))
    else:
        rep.ok("trailers", f"{label}: docs-only range")
        rep.ok("session-log", f"{label}: docs-only range")


def prepush(root: Path, stdin_text: str, today: dt.date | None = None) -> Report:
    rep = lint(root, today)
    try:
        refs = parse_push_refs(stdin_text) if stdin_text.strip() else [("HEAD", "HEAD")]
    except ValueError as exc:
        rep.err("prepush-base", f"could not read pushed refs ({exc}); fail closed")
        return rep
    if not refs:
        rep.ok("prepush-range", "only ref deletions pushed; no code to check")
    for label, tip in refs:
        range_checks(root, rep, tip, label)
    return rep


# ---------------------------------------------------------------- --ratchet
def ratchet(root: Path, coverage_xml: str, update: bool, force: bool) -> Report:
    rep = Report()
    bpath = root / "coverage_baseline.json"
    try:
        baseline = json.loads(read(bpath)) if bpath.is_file() else {"line_pct": None}
    except ValueError:
        baseline = {"line_pct": None}
    xml = root / (coverage_xml or baseline.get("coverage_xml") or "coverage.xml")
    if not xml.is_file():
        rep.warn("ratchet", f"{xml.name} not found; the check did not run")
        return rep
    m = re.search(r'line-rate="([0-9.]+)"', read(xml))
    if not m:
        rep.warn("ratchet", f"{xml.name} has no line-rate attribute (Cobertura expected); the check did not run")
        return rep
    current = round(float(m.group(1)) * 100, 2)
    floors = [baseline.get("line_pct")]
    main_json = git(root, "show", f"{BASE}:coverage_baseline.json")
    if main_json:
        try:
            floors.append(json.loads(main_json).get("line_pct"))
        except ValueError:
            pass
    floor = max((f for f in floors if isinstance(f, (int, float))), default=None)
    if update:
        if floor is None or current > floor or force:
            baseline["line_pct"] = current
            baseline.setdefault("coverage_xml", xml.relative_to(root).as_posix())
            bpath.write_text(json.dumps(baseline, indent=2) + "\n", encoding="utf-8", newline="\n")
            rep.ok("ratchet", f"baseline set to {current}% (was {floor})")
        else:
            rep.ok("ratchet", f"baseline {floor}% kept; current {current}% is not higher (use --force to lower, with approval)")
        return rep
    if floor is None:
        rep.warn("ratchet", f"line coverage {current}%; no baseline yet (run --ratchet --update-baseline after the first green run)")
    elif current + 1e-9 < floor:
        rep.err("ratchet", f"line coverage {current}% fell below the floor {floor}% (floors only rise)")
    else:
        rep.ok("ratchet", f"line coverage {current}% >= floor {floor}%")
    return rep


# ---------------------------------------------------------------- --doctor
def is_link_to(link: Path, target: Path) -> bool:
    try:
        return link.exists() and os.path.realpath(link) == os.path.realpath(target)
    except OSError:
        return False


def relink(link: Path, target: Path) -> str:
    link.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True, check=False)
    else:
        os.symlink(target, link, target_is_directory=True)
    return "created" if is_link_to(link, target) else "FAILED to create"


def override_errors(root: Path) -> list[str]:
    try:
        import tomllib
    except ImportError:
        return ["tomllib unavailable (Python 3.11+ needed)"]
    errs = []
    custom = root / "_bmad" / "custom"
    for ov in sorted(custom.glob("*.toml")) if custom.is_dir() else []:
        if ov.name.startswith("config"):
            continue
        skill = ov.stem.removesuffix(".user")
        base = root / ".agents" / "skills" / skill / "customize.toml"
        if not base.is_file():
            errs.append(f"{ov.name} targets '{skill}' but .agents/skills/{skill}/customize.toml is not installed")
            continue
        try:
            o = tomllib.loads(read(ov))
            b = tomllib.loads(read(base))
        except tomllib.TOMLDecodeError as exc:
            errs.append(f"{ov.name}: {exc}")
            continue
        for table, body in o.items():
            if table not in b:
                errs.append(f"{ov.name}: [{table}] not in {skill}/customize.toml")
                continue
            if isinstance(body, dict):
                for key in body:
                    if key not in b[table]:
                        errs.append(f"{ov.name}: [{table}].{key} not a customizable field of {skill}")
    return errs


def doctor(root: Path, do_relink: bool) -> Report:
    rep = Report()
    target = root / ".agents" / "skills"
    if not target.is_dir():
        rep.err("doctor", ".agents/skills/ missing")
    for link in (root / ".claude" / "skills", root / ".agent" / "skills"):
        rel = link.relative_to(root).as_posix()
        if is_link_to(link, target):
            rep.ok("doctor", f"{rel} -> .agents/skills")
        elif link.exists():
            rep.err("doctor", f"{rel} exists but is not a link to .agents/skills; move it aside (skills live in .agents/skills)")
        elif do_relink and target.is_dir():
            rep.ok("doctor", f"{rel} {relink(link, target)} (junction/symlink; gitignored)")
        else:
            rep.err("doctor", f"{rel} missing; run --doctor --relink")
    hooks = git(root, "config", "core.hooksPath").strip()
    (rep.ok if hooks == ".githooks" else rep.err)("doctor", f"core.hooksPath = {hooks or 'unset'} (want .githooks: git config core.hooksPath .githooks)")
    for h in sorted((root / ".githooks").glob("*")) if (root / ".githooks").is_dir() else []:
        if b"\r" in h.read_bytes():
            rep.err("doctor", f"{h.name} has CRLF line endings; sh cannot run it (.gitattributes sets eol=lf; re-checkout)")
    if shutil.which("sh"):
        py = subprocess.run(["sh", "-c", "py -3 --version 2>/dev/null || python3 --version 2>/dev/null || python --version"],
                            capture_output=True, text=True, check=False)
        if py.returncode == 0 and py.stdout.strip():
            rep.ok("doctor", f"hooks resolve {py.stdout.strip()}")
        else:
            rep.err("doctor", "no python reachable from sh (py -3 / python3 / python)")
    else:
        rep.warn("doctor", "sh not found; cannot prove the hooks' python resolution")
    for tool in ("git", "gh", "node", "uv"):
        (rep.ok if shutil.which(tool) else rep.err)("doctor", f"{tool} {'on PATH' if shutil.which(tool) else 'NOT on PATH'}")
    has_bmad = (root / "_bmad").is_dir()
    (rep.ok if has_bmad else rep.err)("doctor", "_bmad/ present" if has_bmad else "_bmad/ missing (npx skills add bmad-code-org/BMAD-METHOD; bmad setup)")
    errs = override_errors(root)
    (rep.err if errs else rep.ok)("doctor", "; ".join(errs[:5]) if errs else "every _bmad/custom override key exists in the installed customize.toml")
    missing = [s for s in REQUIRED_SKILLS if not (target / s / "SKILL.md").is_file()]
    (rep.err if missing else rep.ok)("doctor", ("skills not installed: " + ", ".join(missing)) if missing else "bmad-agent-pm, caveman, ponytail, grill-me, grilling installed")
    has_lock = (root / "skills-lock.json").is_file()
    (rep.ok if has_lock else rep.warn)("doctor", "skills-lock.json present" if has_lock else "skills-lock.json missing (the pin appears after the first npx skills add)")
    return rep


# ---------------------------------------------------------------- --selftest
GOOD_AGENTS = """harness-constitution v1.0.0

## Part A: Constitution

- **Example rule.** Says a thing. Enforced by: `harness-open`.

| kind | home |
|---|---|
| rule | Part A |

## Where things live

text

## Part B: This repository

Repo detail. See `caveman`, `ponytail`, `grill-me`, `bmad-agent-pm`, `harness-close`.
"""


def make_fixture(root: Path, today: dt.date) -> None:
    def w(rel: str, text: str) -> None:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8", newline="\n")
    w("AGENTS.md", GOOD_AGENTS)
    w("CLAUDE.md", "@./AGENTS.md\n<!-- adapter: no rules here -->\n")
    w("GEMINI.md", "@./AGENTS.md\n")
    w("docs/ARCHITECTURE.md", f"# Map\n\nlast_reviewed: {today.isoformat()}\n\n<!-- verify: exists AGENTS.md -->\n<!-- verify: absent 'NOPE_TOKEN_XYZ' in docs -->\n<!-- verify: count 'Part' in AGENTS.md between 1 and 5 -->\n")
    w("docs/adr/README.md", "# Register\n\n| ID | Title | Status | Date |\n|---|---|---|---|\n| 0001 | Adopt | Accepted | 2026-01-01 |\n")
    w("docs/adr/0000-template.md", "# ADR template\n")
    w("docs/adr/0001-adopt.md", "# ADR-0001\n")
    w("docs/memory/one.md", "---\nname: one\ndescription: a pointer\nmetadata:\n  type: project\n---\n\n**Fact:** x\n\n**Why:** y\n\n**Authority:** AGENTS.md#Where things live; ADR-0001\n")
    for s in sorted(OUR_SKILLS | set(REQUIRED_SKILLS)):
        w(f".agents/skills/{s}/SKILL.md", f"---\nname: {s}\ndescription: test skill {s}\n---\n\nbody\n")
    w(".agents/skills/bmad-agent-pm/customize.toml", '[agent]\nicon = ""\nrole = ""\npersistent_facts = []\nprinciples = []\nactivation_steps_prepend = []\n')
    w("_bmad/custom/bmad-agent-pm.toml", '[agent]\npersistent_facts = ["file:{project-root}/AGENTS.md"]\n')
    w("skills-lock.json", "{}\n")
    rebuild_index(root)


def selftest() -> int:
    bad = 0
    today = dt.date(2026, 10, 3)

    def case(label: str, ok: bool) -> None:
        nonlocal bad
        bad += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {label}")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        make_fixture(root, today)
        rep = lint(root, today)
        case("good fixture: no errors (" + "; ".join(e["check"] + ": " + e["message"] for e in rep.errors) + ")", not rep.errors)

        def broken(label: str, check: str, mutate, level: str = "ERROR") -> None:
            make_fixture(root, today)
            mutate(root)
            r = lint(root, today)
            case(f"{label} -> {check} {level}", level in r.levels(check))

        def dup_map(r: Path) -> None:
            (r / "docs/x").mkdir()
            (r / "docs/x/ARCHITECTURE.md").write_text("# dup\nlast_reviewed: 2026-10-01\n", encoding="utf-8")

        broken("oversize AGENTS.md", "agents-size", lambda r: (r / "AGENTS.md").write_text(GOOD_AGENTS + "x" * AGENTS_MAX, encoding="utf-8"))
        broken("rule without enforcement", "rule-enforcement", lambda r: (r / "AGENTS.md").write_text(GOOD_AGENTS.replace(" Enforced by: `harness-open`.", ""), encoding="utf-8"))
        broken("ADR number in Part A", "adr-refs", lambda r: (r / "AGENTS.md").write_text(GOOD_AGENTS.replace("Says a thing.", "Says ADR-0001."), encoding="utf-8"))
        broken("no version line", "agents-present", lambda r: (r / "AGENTS.md").write_text(GOOD_AGENTS.replace("harness-constitution v1.0.0", ""), encoding="utf-8"))
        broken("adapter with a rule", "adapter-thin", lambda r: (r / "CLAUDE.md").write_text("@./AGENTS.md\nAlways use tabs.\n", encoding="utf-8"))
        broken("context over budget", "context-budget", lambda r: (r / "GEMINI.md").write_text("@./AGENTS.md\n" + "<!-- " + "x" * CONTEXT_MAX + " -->\n", encoding="utf-8"))
        broken("cited skill missing", "skill-refs", lambda r: shutil.rmtree(r / ".agents" / "skills" / "caveman"))
        broken("skill name mismatch", "skills-frontmatter", lambda r: (r / ".agents/skills/harness-open/SKILL.md").write_text("---\nname: wrong\ndescription: d\n---\n", encoding="utf-8"))
        broken("third-party skill without lock", "skills-lock", lambda r: (r / "skills-lock.json").unlink())
        broken("memory page over cap", "memory-schema", lambda r: (r / "docs/memory/one.md").write_text("---\nname: one\ndescription: d\nmetadata:\n  type: project\n---\n**Fact:** " + "x" * 900 + "\n**Why:** y\n**Authority:** AGENTS.md\n", encoding="utf-8"))
        broken("authority dangling", "memory-authority", lambda r: (r / "docs/memory/one.md").write_text("---\nname: one\ndescription: d\nmetadata:\n  type: project\n---\n**Fact:** x\n**Why:** y\n**Authority:** docs/nope.md\n", encoding="utf-8"))
        broken("index drift", "memory-index", lambda r: (r / "docs/memory/two.md").write_text("---\nname: two\ndescription: d\nmetadata:\n  type: project\n---\n**Fact:** x\n**Why:** y\n**Authority:** AGENTS.md\n", encoding="utf-8"))
        broken("ADR without register row", "adr-register", lambda r: (r / "docs/adr/0002-x.md").write_text("# x\n", encoding="utf-8"))
        broken("stale architecture map", "architecture-map", lambda r: (r / "docs/ARCHITECTURE.md").write_text("# Map\n\nlast_reviewed: 2026-01-01\n", encoding="utf-8"), "WARN")
        broken("two architecture maps", "architecture-map", dup_map)
        broken("false claim", "claims", lambda r: (r / "docs/ARCHITECTURE.md").write_text(f"# Map\nlast_reviewed: {today}\n<!-- verify: exists docs/nope.md -->\n", encoding="utf-8"))
        broken("token-shaped literal", "secrets-scan", lambda r: (r / "docs/note.md").write_text("key " + "AKIA" + "ABCDEFGHIJKLMNOP" + "\n", encoding="utf-8"))

        make_fixture(root, today)
        (root / "docs/memory/two.md").write_text("---\nname: two\ndescription: second\nmetadata:\n  type: reference\n---\n**Fact:** x\n**Why:** y\n**Authority:** AGENTS.md\n", encoding="utf-8")
        rebuild_index(root)
        case("--rebuild-index makes index match", "ERROR" not in lint(root, today).levels("memory-index"))

        make_fixture(root, today)
        case("override keys valid -> no doctor error", not override_errors(root))
        (root / "_bmad/custom/bmad-agent-pm.toml").write_text('[agent]\nnot_a_field = 1\n', encoding="utf-8")
        case("override with unknown key -> doctor error", bool(override_errors(root)))

        make_fixture(root, today)
        (root / "coverage.xml").write_text('<coverage line-rate="0.5"/>', encoding="utf-8")
        case("ratchet: no baseline -> WARN", "WARN" in ratchet(root, "", False, False).levels("ratchet"))
        (root / "coverage_baseline.json").write_text('{"line_pct": 60.0}', encoding="utf-8")
        case("ratchet: below floor -> ERROR", "ERROR" in ratchet(root, "", False, False).levels("ratchet"))
        (root / "coverage_baseline.json").write_text('{"line_pct": 40.0}', encoding="utf-8")
        case("ratchet: above floor -> PASS", "PASS" in ratchet(root, "", False, False).levels("ratchet"))
        ratchet(root, "", True, False)
        case("ratchet: --update-baseline raises floor to 50.0", json.loads(read(root / "coverage_baseline.json"))["line_pct"] == 50.0)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        def run(*args: str) -> str:
            return subprocess.run(args, cwd=str(root), capture_output=True, text=True, check=False).stdout.strip()

        def commit(msg: str) -> None:
            run("git", "add", "-A")
            run("git", "commit", "-q", "-m", msg)

        for cmd in (("git", "init", "-q", "-b", "main"), ("git", "config", "user.email", "t@t"),
                    ("git", "config", "user.name", "t"), ("git", "config", "commit.gpgsign", "false")):
            run(*cmd)
        make_fixture(root, today)
        commit("base")
        run("git", "branch", "-f", "origin/main", "main")
        run("git", "checkout", "-q", "-b", "feat")
        (root / "src").mkdir()
        (root / "src/a.py").write_text("x = 1\n", encoding="utf-8")
        commit("feat: no surface, no trailers")
        r = prepush(root, "", today)
        case("prepush: product change without Surface -> surface ERROR", "ERROR" in r.levels("surface"))
        case("prepush: no trailers -> trailers ERROR", "ERROR" in r.levels("trailers"))
        case("prepush: no session log -> session-log ERROR", "ERROR" in r.levels("session-log"))
        run("git", "checkout", "-q", "-b", "good", "main")
        (root / "src").mkdir(exist_ok=True)
        (root / "src/b.py").write_text("y = 1\n", encoding="utf-8")
        (root / "docs/sessions").mkdir(parents=True, exist_ok=True)
        (root / "docs/sessions/session_2610031200.md").write_text("# session\n", encoding="utf-8")
        commit("feat: good\n\nSurface: src/b.py\nTests: pytest -> 1 passed\nReview: clean after 1 round")
        r = prepush(root, "", today)
        case("prepush: declared, logged, trailed -> no range errors", not [e for e in r.errors if e["check"] in ("surface", "one-kind", "trailers", "session-log", "prepush-base")])
        (root / "scripts").mkdir(exist_ok=True)
        (root / "scripts/tool.py").write_text("z = 1\n", encoding="utf-8")
        commit("chore: tooling rides along")
        r = prepush(root, "", today)
        case("prepush: product + tooling without KIND-OK -> one-kind ERROR", "ERROR" in r.levels("one-kind"))
        run("git", "commit", "-q", "--allow-empty", "-m", "chore: note\n\nKIND-OK: tooling fix needed by the feature")
        r = prepush(root, "", today)
        case("prepush: KIND-OK releases one-kind", "ERROR" not in r.levels("one-kind"))
        sha = run("git", "rev-parse", "good")
        r = prepush(root, f"refs/heads/good {sha} refs/heads/good {'0' * 40}\n", today)
        case("prepush: reads git's stdin protocol", any(row["message"].startswith("good:") for row in r.rows))
        run("git", "branch", "-D", "origin/main")
        r = prepush(root, "", today)
        case("prepush: no merge-base -> fail closed", "ERROR" in r.levels("prepush-base"))

    print("SELFTEST-OK" if not bad else f"SELFTEST-FAILURES: {bad}")
    return 1 if bad else 0


# ---------------------------------------------------------------- main
def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--prepush", action="store_true")
    ap.add_argument("--ratchet", action="store_true")
    ap.add_argument("--update-baseline", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--coverage-xml", default="")
    ap.add_argument("--doctor", action="store_true")
    ap.add_argument("--relink", action="store_true")
    ap.add_argument("--rebuild-index", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    root = repo_root()
    if a.rebuild_index:
        print(f"rebuilt {rebuild_index(root).relative_to(root).as_posix()}")
        return 0
    if a.doctor:
        rep = doctor(root, a.relink)
    elif a.ratchet:
        rep = ratchet(root, a.coverage_xml, a.update_baseline, a.force)
    elif a.prepush:
        rep = prepush(root, sys.stdin.read() if not sys.stdin.isatty() else "")
    else:
        rep = lint(root)
    print(rep.render(a.json, a.quiet))
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
