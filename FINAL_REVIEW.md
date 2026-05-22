# Final Independent Security & Content-Safety Review — agent-skills-pro

Date: 2026-05-22
Reviewer: autonomous senior application-security / content-safety reviewer (independent second-opinion sign-off)
Scope reviewed at commit: `33da234` (`docs: record CI Node.js runtime bump in review and changelog`)
Method: skeptical re-verification of every prior fix from first principles — re-read all 12
`skills/*/SKILL.md`, both `references/*.md`, `scripts/validate_skills.py`,
`.github/workflows/ci.yml`, and all repo metadata (README, CONTRIBUTING, LICENSE, PLAN,
CHANGELOG, SECURITY_REVIEW, .gitignore, .gitattributes). Ran the validator, exercised it against
deliberately broken inputs, audited links, scanned for insecure-code / prompt-injection /
exfiltration patterns, and checked CI status on the latest commit.

## Verdict

**PASS — APPROVED. No residual or new issues.** The prior fix pass is correct and complete.
All claimed fixes were independently reproduced and confirmed. No code or content changes were
required during this review (this `FINAL_REVIEW.md` is the only addition). No Critical/High/Medium
issues exist; no actionable Low/Info items remain open.

## Per-item confirmation of prior fixes

| ID | Claim | Independent verification | Held? |
| -- | ----- | ------------------------ | ----- |
| M1 | `allowed-tools` tightened to least-privilege in the 3 git skills | Re-derived every `` !`...` `` line and the subcommands inside `$(...)`. See per-skill analysis below. Grants now match invoked subcommands exactly — no over- or under-grant. | YES |
| L1 | Validator rejects tab indentation | Fed `metadata:\n\tauthor: a` → raises `tab indentation is not allowed in frontmatter`. | YES |
| L2 | Validator rejects duplicate keys | Duplicate top-level `name:` → `duplicate frontmatter key: 'name'`; duplicate nested `author:` → `duplicate metadata key: 'author'`. Both raise. | YES |
| L3 | Validator tolerates a leading UTF-8 BOM | BOM-prefixed `﻿---\n...` parses successfully with correct `name`. | YES |
| L4 | Validator enforces non-empty string `metadata` values | Empty `author:` value → `metadata.author must be a non-empty string value`. | YES |
| L5 | CI bumped to `checkout@v5` / `setup-python@v6` (Node 24) | `.github/workflows/ci.yml:18,21` confirm `actions/checkout@v5` and `actions/setup-python@v6`. Latest CI run green on Node 24 runtime. | YES |
| I1 | CONTRIBUTING description-cap wording clarified | `CONTRIBUTING.md:71` now references the spec's 1,024-char cap. | YES |
| I2 | README "broken link" false positive | `readme-generator/SKILL.md:125` `[LICENSE](LICENSE)` is inside a fenced code block (an illustrative README skeleton), not a real link. Confirmed false positive. | YES (no action) |

### M1 — least-privilege `allowed-tools`, re-derived independently

- **conventional-commit-writer** — declares `Bash(git diff:*)`. Body invokes only
  `` !`git diff --cached --stat` ``. Exact match. No unused grant.
- **changelog-writer** — declares `Bash(git log:*) Bash(git describe:*)`. Body invokes
  `` !`git log $(git describe --tags --abbrev=0 ...)..HEAD ... || git log ...` ``: outer `git log`
  (declared), `git describe` inside `$(...)` (declared), `git log` fallback (declared). Exact match;
  the previously-unused `Bash(git tag:*)` grant is gone.
- **pr-description-writer** — declares `Bash(git diff:*) Bash(git log:*) Bash(git merge-base:*)`.
  Body invokes `git diff` / `git log` (outer) each with `git merge-base` inside `$(...)`. All three
  declared and all three used; the previously-unused `Bash(gh pr diff:*)` grant is gone. The
  `echo origin/main` fallback runs as a shell builtin inside command substitution (like the
  `2>/dev/null` redirections), so it correctly needs no separate `Bash(...)` grant.

## Independent verification results

- **Validator, full run (real repo):** `python scripts/validate_skills.py` → all 12 skills PASS,
  exit code 0. ("Validating 12 skill(s)… All 12 skill(s) passed validation.")
- **Validator, deliberately broken inputs (negative tests):** A broken skill dropped into
  `skills/` (empty `description`, tab-indented `metadata`, unknown field) was reported as
  `FAIL` with the tab-indentation error and the runner exited 1. Parser- and skill-level unit
  probes additionally confirmed catches for: missing/closing delimiter, no-colon line, duplicate
  top-level + nested keys, non-empty-string `metadata`, unknown top-level field, bad/uppercase
  `name`, name≠folder, over-length (1025-char) `description`, missing required field, empty body,
  and missing `SKILL.md`. A valid control skill passed cleanly. The broken test artifacts were
  removed; working tree is clean.
- **CI:** `gh run list` shows the latest run on `main` (`33da234`) **completed / success**; job
  "Validate SKILL.md files" succeeded in ~4s on the Node 24 runtime. No deprecated-runtime
  annotation.
- **Links:** all in-repo relative links (README, CONTRIBUTING, LICENSE, ci.yml, SKILL/reference
  files) resolve to existing files. External links point only to legitimate, well-known domains
  (agentskills.io, w3.org, rfc-editor.org, conventionalcommits.org, keepachangelog.com,
  semver.org, and official Claude/Codex/Cursor/Gemini docs). Placeholder links
  (`OWNER/REPO`, `me/wc-rs`, `PACKAGE`) appear only inside illustrative code blocks.
- **Content-safety / insecure-guidance scan:** no matches for `curl … | sh`, disabled TLS/cert
  verification (`verify=false`, `InsecureSkipVerify`, `rejectUnauthorized:false`), `--no-verify`,
  `chmod 777`, `eval(`, weak crypto recommendations, `sudo rm`, or prompt-injection /
  exfiltration patterns (ignore-previous-instructions, send-secret-to-URL, webhook.site,
  pastebin, etc.). The three security-adjacent skills (`dockerfile-hardener`,
  `env-secrets-auditor`, `sql-query-optimizer`) give correct, security-positive guidance
  (non-root, pinned/digest bases, BuildKit secrets, redaction + mandatory rotation, parameter
  binding, ReDoS-aware regex). `regex-builder` actively teaches ReDoS avoidance.
- **Validator safety:** stdlib-only; no `eval`/`exec`/`pickle`/third-party YAML. Reads files only
  under a fixed `SKILLS_DIR` derived from the script location; bounded, simple grammar. No
  dependency supply-chain surface.
- **CI safety:** `permissions: contents: read` (least privilege), no secrets, no third-party
  install step. Actions pinned to major version tags — an accepted trade-off for a read-only,
  secret-free validation workflow (full-SHA pinning optional, not required).

## New findings

None. The fresh audit (skills misleading an agent into insecure code, broken links, license, CI
workflow safety, validator file-handling) surfaced nothing actionable. The MIT `LICENSE` is
present and consistent across README/CONTRIBUTING/frontmatter.

## Disposition

No changes made to skills, validator, CI, or docs — every prior fix is correct and complete, and
no new issue warranted a change. Only this `FINAL_REVIEW.md` was added.
