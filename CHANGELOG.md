# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Security
- Tightened `allowed-tools` to least-privilege in `conventional-commit-writer`,
  `changelog-writer`, and `pr-description-writer`: each skill now declares exactly the
  git subcommands its dynamic commands run (including subcommands used inside `$(...)`
  command substitution, e.g. `git describe`, `git merge-base`) and no longer grants
  unused tools (`git status`, `git tag`, `gh pr diff`).

### Changed
- `validate_skills.py` now rejects malformed frontmatter that previously parsed silently:
  tab indentation, duplicate top-level or nested keys, and non-string `metadata` values.
- `validate_skills.py` now tolerates a leading UTF-8 BOM so BOM-prefixed `SKILL.md` files
  validate correctly.

### Fixed
- Clarified the `description` length guidance in `CONTRIBUTING.md` to reference the spec's
  1,024-character cap.

### Added
- `SECURITY_REVIEW.md` documenting a full security and content-safety audit of the skills,
  validator, and CI.
