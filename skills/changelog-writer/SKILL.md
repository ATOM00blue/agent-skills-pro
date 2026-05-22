---
name: changelog-writer
description: Generates and maintains a CHANGELOG following the Keep a Changelog format, grouping changes into Added/Changed/Fixed/etc. and writing human-focused release notes from commits or a list of changes. Use when the user asks for a changelog, release notes, what's new, or wants to cut a release or prepare an Unreleased section.
license: MIT
metadata:
  author: ATOM00blue
  version: "1.0.0"
  category: development
allowed-tools: Bash(git log:*) Bash(git tag:*)
---

# Changelog Writer

Write a changelog **for humans**, following [Keep a Changelog 1.1.0](https://keepachangelog.com)
and [Semantic Versioning](https://semver.org). A changelog is curated release notes, not a
raw `git log` dump.

## Core principles

- Write for the person upgrading, not the person who wrote the code.
- Group by the kind of change, newest version on top.
- Each entry is one line, plain language, describing the user-visible effect.
- Keep an `## [Unreleased]` section at the top and add to it as you go.

## Change groups (use only the ones with entries)

| Group | For |
| ----- | --- |
| `Added` | new features |
| `Changed` | changes in existing behavior |
| `Deprecated` | features slated for removal |
| `Removed` | features removed in this release |
| `Fixed` | bug fixes |
| `Security` | vulnerability fixes (always call these out) |

## Step 1 — Gather changes

From git, list commits since the last tag:

```
Commits since last release: !`git log $(git describe --tags --abbrev=0 2>/dev/null)..HEAD --pretty=format:"%s" 2>/dev/null || git log --pretty=format:"%s"`
```

Map Conventional Commit types to groups: `feat` → Added, `fix` → Fixed, `perf`/`refactor`
that change behavior → Changed, anything with `BREAKING CHANGE`/`!` → Changed (and bump
MAJOR). Drop `chore`, `ci`, `test`, `style`, and internal `docs` unless they affect users.

## Step 2 — Rewrite commits as user-facing notes

A commit subject is for developers; a changelog entry is for users. Translate jargon, add the
"so what," and merge related commits into one entry.

| Commit | Changelog entry |
| ------ | --------------- |
| `fix(parser): handle CRLF in csv` | Fixed CSV import failing on Windows line endings |
| `feat(api): add cursor pagination` | Added cursor-based pagination to the list endpoints |
| `perf(db): batch the writes` | Improved bulk-import speed by ~5x |

## Step 3 — Choose the version (SemVer)

- **MAJOR** (`X.0.0`): any breaking change.
- **MINOR** (`x.Y.0`): backward-compatible new features.
- **PATCH** (`x.y.Z`): backward-compatible bug fixes only.

Lead the release notes with breaking changes and a short migration note when relevant.

## Step 4 — Emit the entry

Use this exact structure. Date is ISO 8601 (`YYYY-MM-DD`). Add comparison links at the bottom.

```markdown
# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.4.0] - 2026-05-22
### Added
- Cursor-based pagination on all list endpoints.
- `--dry-run` flag to preview changes without writing.

### Changed
- Default request timeout raised from 10s to 30s.

### Fixed
- CSV import no longer fails on Windows (CRLF) line endings.

### Security
- Patched a path-traversal issue in the file upload handler.

[Unreleased]: https://github.com/OWNER/REPO/compare/v1.4.0...HEAD
[1.4.0]: https://github.com/OWNER/REPO/compare/v1.3.0...v1.4.0
```

## Examples

**Input:** commits `feat: dark mode`, `fix: crash on empty input`, `chore: bump eslint`.
**Output:** version MINOR; `chore` dropped.
```markdown
## [2.1.0] - 2026-05-22
### Added
- Dark mode, toggled from Settings or the system preference.

### Fixed
- No longer crashes when the input field is empty.
```

## Common edge cases

- **Pre-1.0 projects:** breaking changes bump MINOR (`0.x.0`); document them prominently.
- **No prior changelog:** create the file with the structure above and an `[Unreleased]`
  section; optionally backfill notable past releases.
- **Yanked release:** mark it `## [1.2.1] - 2026-05-01 [YANKED]` with a one-line reason.
- **Monorepo:** keep a changelog per published package, not one global file.
- **Pure-internal release:** if nothing is user-facing, say so rather than padding the notes.
