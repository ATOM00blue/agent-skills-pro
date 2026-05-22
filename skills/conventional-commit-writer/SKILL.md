---
name: conventional-commit-writer
description: Writes Conventional Commits messages from a diff or change description, choosing the correct type and scope, writing an imperative subject, and flagging breaking changes. Use when the user asks for a commit message, wants to commit staged changes, or mentions conventional commits, semantic commits, or commit conventions.
license: MIT
metadata:
  author: ATOM00blue
  version: "1.0.0"
  category: development
allowed-tools: Bash(git diff:*)
---

# Conventional Commit Writer

Write a commit message that follows the [Conventional Commits 1.0.0](https://www.conventionalcommits.org)
spec, so history is readable and tools can derive versions and changelogs automatically.

## Format

```
<type>(<optional scope>): <subject>
<BLANK LINE>
<optional body — what and why, not how>
<BLANK LINE>
<optional footer(s) — BREAKING CHANGE, Refs, Closes>
```

## Step 1 — Inspect the change

If you have repo access, base the message on the actual diff, not assumptions:

```
Staged changes: !`git diff --cached --stat`
```

If the diff is empty, note there are no staged changes and ask what was changed (or read the
unstaged diff).

## Step 2 — Pick the type

| Type | Use for | SemVer impact |
| ---- | ------- | ------------- |
| `feat` | a new user-facing feature | MINOR |
| `fix` | a bug fix | PATCH |
| `docs` | documentation only | none |
| `style` | formatting, whitespace, no logic change | none |
| `refactor` | code change that is neither a fix nor a feature | none |
| `perf` | a change that improves performance | PATCH |
| `test` | adding or fixing tests | none |
| `build` | build system or dependencies (npm, cargo, docker) | none |
| `ci` | CI configuration and scripts | none |
| `chore` | maintenance that doesn't touch src or tests | none |
| `revert` | reverts a previous commit | varies |

Pick the single most important type. If a change is both a feature and a fix, prefer `feat`
and describe the fix in the body.

## Step 3 — Scope (optional but useful)

A noun in parentheses naming the affected area: `feat(auth):`, `fix(api):`, `docs(readme):`.
Keep scopes from a small, consistent set. Omit the scope rather than inventing a vague one.

## Step 4 — Write the subject

- **Imperative mood**: "add", "fix", "remove" — not "added", "fixes", "adding".
- No capital first letter after the colon, no trailing period.
- Aim for ≤50 characters; hard cap 72.
- Complete the sentence: "If applied, this commit will _<subject>_."

## Step 5 — Body and footers (when warranted)

Add a body when the *why* isn't obvious from the subject. Wrap at ~72 columns. Explain the
motivation and contrast with previous behavior; the code already shows the *how*.

Footers reference issues and declare breaking changes:

```
Closes #123
Refs #456
Reviewed-by: Jane Doe
```

## Step 6 — Breaking changes

Two equivalent ways to mark a breaking change; use the footer for tooling and the `!` for
visibility:

```
feat(api)!: drop support for legacy v1 auth tokens

BREAKING CHANGE: v1 bearer tokens are no longer accepted. Clients must
migrate to OAuth2 access tokens. See MIGRATION.md.
```

A `BREAKING CHANGE:` footer (or `!`) signals a MAJOR version bump regardless of type.

## Examples

**Input:** Added a `/healthz` endpoint that returns 200 when the DB is reachable.
**Output:**
```
feat(api): add /healthz readiness endpoint

Returns 200 when the database connection is live, 503 otherwise, so the
load balancer can route around unhealthy instances.
```

**Input:** Fixed dates rendering one day off due to timezone handling.
**Output:**
```
fix(reports): use UTC to prevent off-by-one dates

Report timestamps were formatted in local time, shifting dates across the
midnight boundary. Format consistently in UTC.

Closes #842
```

**Input:** Bumped lodash and removed an unused helper.
**Output:**
```
chore(deps): upgrade lodash to 4.17.21 and drop unused util

- Patches a prototype-pollution advisory
- Removes the now-unreferenced deepClone helper
```

## Common edge cases

- **Mixed unrelated changes:** recommend splitting into separate commits; if that's not
  possible, lead with the most significant type and enumerate the rest in the body.
- **Revert:** `revert: <subject of reverted commit>` with a body `This reverts commit <sha>.`
- **WIP/merge commits:** Conventional Commits is for meaningful history; squash WIP commits
  before merging.
- **No issue tracker:** omit footers rather than inventing references.
