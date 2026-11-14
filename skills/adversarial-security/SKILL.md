---
name: adversarial-security
description: Optional adversarial security check of a change before it ships - trace every new path from untrusted input to a dangerous sink, try to refute each finding, keep only what survives. Offered by harness-close step 1 and run when the person asks. Triggers - "security check", "adversarial security review", "is this change safe", "adversarial-security". Not a substitute for a professional audit.
---

# Adversarial security check

Tests prove the code does what it should. This check asks what an attacker can make it do instead. It runs over a change, reads like an attacker, then argues against itself, so what reaches the person is a short list of findings that survived a second look.

## NEVER

- Never run an exploit against a live, shared or production system. Reason from the code; a proof runs only in a local test.
- Never print a secret's value: not in a finding, log, commit or the conversation (the transcript is copied into the repository at close). Find secrets with `git grep -l <pattern>` (file names only); never print the matching text or a secret file's contents. Name the file; write `[REDACTED]`.
- Never report "no findings" without listing what was checked: the boundaries mapped and the classes hunted.
- Never fix a finding outside the plan's declared Surface. It becomes a BACKLOG line.

## Flow

1. **Scope.** The whole change, committed or not: `git diff --merge-base <base>` (base: `HARNESS_BASE` if set, else `origin/main` or the repository's base branch), plus the untracked files from `git ls-files --others --exclude-standard`. Read the changed files in full, not only the hunks, and every caller of a changed function (`git grep -w <name>`). Whole-repo only when the person asks.
2. **Map the boundaries.** List each place the change reads data it does not control (request, file, environment, CLI argument, queue, webhook, database row written by others, model output) and each sink it can reach (shell, SQL, filesystem path, HTML, URL fetch, `eval`/deserialise, log, outbound call, CI step with secrets).
3. **Hunt.** For each source-to-sink path, look for the classes below. Write each candidate as `source -> transformations -> sink`, with file:line at every hop.

   | Class | Look for |
   |---|---|
   | Injection | string-built shell, SQL, paths (`..`, absolute, symlink), templates, regex from input; XML entities (XXE); archive members extracted outside the target |
   | Agent and prompt injection | model output or fetched text that reaches a tool call, a shell, a file write or a commit without a human gate |
   | Access control | a handler with no authn/authz check; an object fetched by caller-supplied id without an owner check; mass assignment of fields the caller should not set |
   | Crypto and tokens | TLS verification off; MD5/SHA1 or unsalted password hashes; non-crypto `random` for tokens; non-constant-time compare; JWT accepted unverified or with `alg: none` |
   | Secrets | keys or tokens in code, config, fixtures, logs, error messages, transcripts |
   | Unsafe execution | `eval`, `exec`, `pickle`/`yaml.load`, dynamic import from input |
   | Outbound requests | SSRF: a URL taken from input; redirects followed to internal hosts |
   | Web | XSS through unescaped output; CSRF on a state-changing route; open redirect |
   | Insecure config | debug on in production; CORS `*` with credentials; permissive defaults |
   | Fail-open | an exception, a decode error or a missing value that skips a check and continues as allowed |
   | Races | check-then-use on files or records (TOCTOU) |
   | Supply chain | a new dependency (who publishes it, is it pinned, any known CVE: `pip-audit`, `npm audit`); CI using `pull_request_target`, unpinned actions or secrets on fork PRs |
   | Exhaustion | unbounded reads, loops, recursion or regex on input |

4. **Refute.** For each candidate, argue the defence: a validator upstream, a framework escape, an unreachable route, a trusted-only caller. Better: hand the code (not your conclusion) to a fresh agent or a second pass and ask it to break the claim. Keep a finding only if the path still stands. Mark it `CONFIRMED` (every hop traced, or a local test shows it) or `PLAUSIBLE` (one hop rests on an assumption, named).
5. **Rank.** `HIGH`: remote or unauthenticated, reaches code execution, data of other users, or secrets. `MEDIUM`: needs a foothold or a specific configuration. `LOW`: hardening, defence in depth.
6. **Act.** A finding inside the Surface: fix it with a regression test written first (red, then green), then rewrite the self-review gate and re-run the review over the new diff before `Review:` is written. Outside it: a BACKLOG line in the commit body. The person decides what blocks the push.
7. **Record.** Keep the record until `harness-close` step 8 writes the session log, then put it there under `## Security check`: scope, boundaries mapped, classes hunted, then one line per finding: `- <SEVERITY> <CONFIRMED|PLAUSIBLE> <file:line>: <one sentence> -> fixed | backlog | accepted by <person>`. In the commit body: `Security: <n> findings (<n> fixed, <n> backlog, <n> accepted)`.

## Deeper option on Claude Code

If the person runs Claude Code with Anthropic's Claude Security plugin installed, `/claude-security` then "scan changes" runs a multi-agent version of this check. Record its result the same way in step 7. It works only inside Claude Code; this skill works in any agent.
