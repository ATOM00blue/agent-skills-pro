# PLAN — agent-skills-pro

A curated collection of production-ready agent Skills for Claude Code, Codex, Cursor,
Gemini CLI, and any other tool that supports the open [Agent Skills](https://agentskills.io)
standard.

## Research summary (authoritative spec)

A skill is a directory containing a `SKILL.md` file with YAML frontmatter + Markdown body.

**Frontmatter fields (per the open Agent Skills spec at agentskills.io/specification):**

| Field           | Required | Constraints |
| --------------- | -------- | ----------- |
| `name`          | Yes      | 1–64 chars, lowercase `a-z0-9` + hyphens, no leading/trailing hyphen, no `--`, must match folder name |
| `description`   | Yes      | 1–1024 chars, non-empty, says *what* it does and *when* to use it (third person) |
| `license`       | No       | License name or reference |
| `compatibility` | No       | ≤500 chars, environment requirements |
| `metadata`      | No       | string→string map (we use `author`, `version`, `category`) |
| `allowed-tools` | No       | space-separated pre-approved tools (experimental) |

**Layout:** `skill-name/SKILL.md` (required) + optional `scripts/`, `references/`, `assets/`.

**Best practices applied:**
- Description is third person, leads with the key use case, packs trigger keywords.
- SKILL.md body kept concise (< 500 lines); deep material pushed to `references/`.
- References kept one level deep; forward-slash paths only.
- Concrete input/output examples; explicit step-by-step workflows with checklists.
- No time-sensitive content; consistent terminology.

## Skills to ship (12)

Each lives in `skills/<name>/SKILL.md`. Names use noun-phrase / action style, hyphenated.

| # | Folder | What it does |
|---|--------|--------------|
| 1 | `sql-query-optimizer`        | Diagnose slow SQL, read EXPLAIN plans, recommend indexes/rewrites |
| 2 | `regex-builder`              | Build, explain, and test regular expressions safely (ReDoS-aware) |
| 3 | `conventional-commit-writer` | Write Conventional Commits messages from a diff |
| 4 | `changelog-writer`           | Generate Keep a Changelog entries / release notes from commits |
| 5 | `a11y-auditor`               | Audit UI/markup for WCAG 2.2 AA accessibility issues + fixes |
| 6 | `dockerfile-hardener`        | Harden Dockerfiles (non-root, pinned, multi-stage, small, secure) |
| 7 | `api-design-reviewer`        | Review REST/HTTP API designs for consistency and correctness |
| 8 | `test-writer`                | Write focused, behavior-driven unit/integration tests |
| 9 | `error-message-explainer`    | Explain stack traces / errors and propose concrete fixes |
| 10 | `readme-generator`          | Generate a high-quality project README from the repo |
| 11 | `pr-description-writer`      | Write clear, reviewable pull request descriptions from a diff |
| 12 | `env-secrets-auditor`       | Scan code/config for leaked secrets and insecure env handling |

Skills that benefit from supporting files get a `references/` doc (e.g. SQL anti-pattern
catalog, WCAG checklist, commit-type table) to demonstrate progressive disclosure, and a
couple ship a small helper `scripts/` file where deterministic logic helps.

## Repo layout

```
agent-skills-pro/
├── README.md                # pitch, badges, skill index table, install per client, contributing, license
├── CONTRIBUTING.md          # the skill format + how to add a skill
├── LICENSE                  # MIT, Copyright (c) 2026 ATOM00blue
├── PLAN.md
├── .gitignore
├── .github/workflows/ci.yml # runs the validator on push/PR
├── scripts/
│   └── validate_skills.py   # validates every SKILL.md against the spec
└── skills/
    └── <12 skill folders>/SKILL.md (+ references/ / scripts/ where useful)
```

## Validator

`scripts/validate_skills.py` (Python 3, stdlib only):
- Finds every `skills/*/SKILL.md`.
- Parses YAML frontmatter (minimal hand-rolled parser — no third-party deps so CI is zero-install).
- Checks: frontmatter present; `name` + `description` exist; `name` matches all spec rules
  and equals the folder name; `description` 1–1024 chars; `compatibility` ≤500 if present;
  `metadata` is a map; no unknown top-level fields; body non-empty.
- Exits non-zero on any failure with a clear per-file report; prints a green summary on pass.

CI: `.github/workflows/ci.yml` runs `python scripts/validate_skills.py` on push + PR.

## Publish

`git init` → commits → `gh repo create agent-skills-pro --public --source . --remote origin --push`
→ add topics → verify public with `gh repo view`.
