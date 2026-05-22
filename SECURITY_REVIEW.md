# Security & Safety Review — agent-skills-pro

Date: 2026-05-22
Reviewer: autonomous application-security / content-safety review
Scope: all 12 `skills/*/SKILL.md`, both `references/*.md`, `scripts/validate_skills.py`,
`.github/workflows/ci.yml`, and the repo metadata (README, CONTRIBUTING, LICENSE, gitignore,
gitattributes, PLAN).

## Summary

This repository is a content collection (Markdown agent Skills) plus a small, stdlib-only Python
validator and a single CI workflow. The overall safety and quality bar is high:

- No skill instructs an agent to perform destructive shell actions, exfiltrate data, harvest
  secrets, or run untrusted code silently.
- The three security-adjacent skills (`dockerfile-hardener`, `env-secrets-auditor`,
  `sql-query-optimizer`) themselves recommend correct, secure practices.
- The validator uses no `eval`, no `pickle`, and no third-party YAML — it is a small hand-rolled
  parser. There are no runtime dependencies, so there is no supply-chain dependency surface to
  audit with `pip-audit`/`bandit` beyond the stdlib.
- The CI workflow is minimal, uses least-privilege `permissions: contents: read`, and pins
  actions to major version tags.

No Critical or High issues were found. The findings below are Medium/Low/Info. All Medium and
actionable Low items have been fixed (see "Status").

## Findings

### M1 — `allowed-tools` does not match the commands the skills actually run (least-privilege)

- Severity: **Medium**
- Files:
  - `skills/changelog-writer/SKILL.md:9` and `:41`
  - `skills/conventional-commit-writer/SKILL.md:9` and `:32`
  - `skills/pr-description-writer/SKILL.md:9` and `:32-33`
- Impact: The skills declare a pre-approved `allowed-tools` list, but the dynamic
  `` !`...` `` command-injection lines they ship do **not** line up with that list, in two
  directions:
  1. **Undeclared subcommands run inside command substitution.** `changelog-writer` runs
     `` !`git log $(git describe --tags ...) ...` `` — the substitution executes `git describe`,
     which is **not** covered by the declared `Bash(git log:*) Bash(git tag:*)`.
     `pr-description-writer` runs `git merge-base` inside `$(...)`, which is **not** covered by
     `Bash(git diff:*) Bash(git log:*) Bash(gh pr diff:*)`. A permission matcher that evaluates
     the full command string will see an unapproved subcommand (defeating the point of the
     pre-approval and surprising the user with a prompt); a naive client that only checks the
     outer command would silently run an *undeclared* subcommand.
  2. **Declared-but-unused (over-broad) grants.** `conventional-commit-writer` declares
     `Bash(git status:*)` and `Bash(git log:*)` but the body only invokes `git diff`.
     `changelog-writer` declares `Bash(git tag:*)` but never invokes `git tag` directly.
     `pr-description-writer` declares `Bash(gh pr diff:*)` but never invokes it. Granting tools a
     skill does not use violates least-privilege.
- Recommended fix: make `allowed-tools` exactly cover the subcommands the dynamic lines run
  (including those inside `$(...)`), and drop unused grants. Specifically:
  - `conventional-commit-writer`: `Bash(git diff:*)` only.
  - `changelog-writer`: add `Bash(git describe:*)` (used in `$(...)`), drop unused `Bash(git tag:*)`.
  - `pr-description-writer`: add `Bash(git merge-base:*)` (used in `$(...)`), drop unused
    `Bash(gh pr diff:*)`.

### L1 — Validator silently drops tab-indented `metadata` entries

- Severity: **Low**
- File: `scripts/validate_skills.py:70` (`indent = len(raw) - len(raw.lstrip(" "))`)
- Impact: The indentation calculation strips spaces only. A `metadata:` block whose entries are
  indented with a **tab** is parsed as having `indent == 0`; the entries are treated as new
  top-level keys with empty values, which silently turns `metadata` into an empty mapping (or, if
  the tabbed line has a colon, registers a bogus top-level field). A malformed-but-tabbed file can
  pass or fail for the wrong reason. (YAML forbids tabs for indentation, so this should be a clear
  error, not silent acceptance.)
- Recommended fix: detect leading tabs and raise a clear `ValueError`.

### L2 — Validator silently accepts duplicate top-level frontmatter keys (last-wins)

- Severity: **Low**
- File: `scripts/validate_skills.py:78-84`
- Impact: A frontmatter block with two `name:` (or two `description:`) lines is accepted; the last
  value silently wins. This can mask an authoring mistake.
- Recommended fix: raise on a duplicate top-level key.

### L3 — Validator rejects files that start with a UTF-8 BOM

- Severity: **Low**
- File: `scripts/validate_skills.py:46-52`
- Impact: A `SKILL.md` saved with a UTF-8 BOM (common from some Windows editors) starts with
  `﻿---`, so `text.startswith("---")` is false and the file is rejected as "missing opening
  delimiter." This is fail-safe (it rejects rather than passes a bad file) but produces a
  confusing error for a file that is otherwise valid.
- Recommended fix: strip a leading BOM before parsing.

### L4 — Validator does not enforce that `metadata` values are strings

- Severity: **Low**
- File: `scripts/validate_skills.py:158-160`
- Impact: The spec defines `metadata` as a map from string keys to **string** values. The
  validator only checks that `metadata` is a mapping, not that each value is a scalar/string. A
  nested mapping or empty value would pass. (In practice the tiny parser only produces string
  scalars for nested keys, so the blast radius is small.)
- Recommended fix: validate that every `metadata` value is a non-empty string.

### L5 — CI actions run on the deprecated Node.js 20 runtime

- Severity: **Low**
- File: `.github/workflows/ci.yml:18` and `:21`
- Impact: `actions/checkout@v4` and `actions/setup-python@v5` execute on Node.js 20, which GitHub
  is removing from runners (forced off in June 2026, removed September 2026). Left unchanged, CI
  would eventually break. Surfaced as a GitHub workflow annotation on the first push.
- Recommended fix: bump to `actions/checkout@v5` and `actions/setup-python@v6` (Node.js 24).

### I1 — CONTRIBUTING description-length note can read as inconsistent with the 1024 cap

- Severity: **Info**
- File: `CONTRIBUTING.md:71`
- Note: The guidance mentions descriptions are "truncated around 1,536 chars in some clients,"
  while the spec/validator hard cap on `description` alone is 1024. The 1,536 figure refers to the
  combined discovery text (name + description) in some clients, so it is not strictly wrong, but it
  can confuse contributors. Clarified to reference the 1024 hard cap. Low value; left as a wording
  tweak.

### I2 — README "broken link" false positive (verified safe)

- Severity: **Info (no action)**
- File: `skills/readme-generator/SKILL.md:125`
- Note: An automated link check flags `[LICENSE](LICENSE)`. This occurs **inside a fenced code
  block** as an illustrative README skeleton, not as a real repository link. No fix needed.

## Things checked and found clean

- **Prompt injection / data exfiltration / destructive commands:** none. No skill tells an agent
  to pipe to `curl`, post data anywhere, `rm -rf`, force-push without warning, or disable safety.
  Where a skill discusses destructive operations (e.g. `env-secrets-auditor` mentioning
  `git filter-repo`/BFG history purge and force-push), it explicitly labels them as disruptive.
- **Secret handling guidance:** `env-secrets-auditor` correctly says never to print a full live
  secret, to redact matches, and that rotation is mandatory once a secret is committed. Sound.
- **Dockerfile guidance:** `dockerfile-hardener` recommends non-root, pinned/digest bases,
  BuildKit secrets (not baked `ENV`/`ARG`), minimal images, `--cap-drop=ALL`,
  `no-new-privileges`, read-only rootfs, and image scanning. All correct.
- **SQL guidance:** uses parameter binding language ("bind parameters with the column's type")
  and never recommends string-concatenated SQL; no injection-encouraging advice.
- **Regex guidance:** `regex-builder` has a dedicated, accurate ReDoS section and recommends RE2
  for untrusted input — actively a security-positive skill.
- **Validator parser safety:** no `eval`/`exec`/`pickle`/`yaml.load`; reads files as UTF-8 with a
  bounded, simple grammar. Spec rules for `name`, `description`, `compatibility`, unknown-field
  rejection, and folder-name match are all enforced correctly.
- **CI / supply chain:** `permissions: contents: read` (least privilege), no secrets used, no
  third-party install step, actions pinned to major tags. Pinning to a full commit SHA would be
  marginally stricter but is not warranted for this low-risk, read-only workflow. The actions were
  bumped to `actions/checkout@v5` / `actions/setup-python@v6` (Node.js 24) to clear GitHub's
  deprecated-Node.js-20 runner warning (see L5).
- **Spec conformance:** all 12 skills pass the validator; `name` == folder for every skill; all
  descriptions are well within 1024 chars (286-357); only spec-defined frontmatter fields are
  used.

## Status of fixes (Phase 2)

| ID | Severity | Status |
| -- | -------- | ------ |
| M1 | Medium | Fixed — `allowed-tools` tightened to match actual commands in all 3 skills |
| L1 | Low | Fixed — validator rejects tab indentation |
| L2 | Low | Fixed — validator rejects duplicate top-level keys |
| L3 | Low | Fixed — validator strips a leading UTF-8 BOM |
| L4 | Low | Fixed — validator enforces non-empty string `metadata` values |
| L5 | Low | Fixed — CI actions bumped to checkout@v5 / setup-python@v6 (Node 24) |
| I1 | Info | Fixed — CONTRIBUTING wording clarified |
| I2 | Info | No action — false positive (link is inside a code block) |

### Intentionally not changed

- CI actions are pinned to major version tags (`@v4`/`@v5`) rather than full commit SHAs. For a
  read-only validation workflow with no secrets, tag pinning is an acceptable, common trade-off;
  full-SHA pinning was considered and judged unnecessary.
