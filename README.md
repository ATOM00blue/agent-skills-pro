<div align="center">

# agent-skills-pro

**A curated collection of production-ready agent Skills for Claude Code, Codex, Cursor, Gemini CLI, and every tool that supports the open [Agent Skills](https://agentskills.io) standard.**

[![CI](https://github.com/ATOM00blue/agent-skills-pro/actions/workflows/ci.yml/badge.svg)](https://github.com/ATOM00blue/agent-skills-pro/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-12-7c3aed.svg)](#-the-skills)
[![Spec](https://img.shields.io/badge/Agent%20Skills-spec%20compliant-0ea5e9.svg)](https://agentskills.io/specification)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-22c55e.svg)](CONTRIBUTING.md)

</div>

---

**Skills** are a lightweight, open format for teaching AI agents how to do real work. Each skill
is just a folder with a `SKILL.md` file: some YAML metadata plus Markdown instructions the agent
loads **only when it's relevant**. Write once, use across [dozens of agent tools](https://agentskills.io/clients).

`agent-skills-pro` is a hand-authored set of **12 genuinely useful, spec-compliant skills** for
everyday software work — query tuning, accessibility, container hardening, commit hygiene, and
more. Every skill is concise, third-person, keyword-rich for discovery, and validated in CI.

## Contents

- [Why this collection](#why-this-collection)
- [The skills](#-the-skills)
- [Install](#install)
  - [Claude Code](#claude-code)
  - [Claude.ai / Claude API](#claudeai--claude-api)
  - [OpenAI Codex](#openai-codex)
  - [Cursor](#cursor)
  - [Gemini CLI](#gemini-cli)
  - [Any other Agent Skills client](#any-other-agent-skills-client)
- [How skills work](#how-skills-work)
- [Validate](#validate)
- [Contributing](#contributing)
- [License](#license)

## Why this collection

- **Spec-compliant.** Every `SKILL.md` validates against the open
  [Agent Skills specification](https://agentskills.io/specification) — correct `name`/`description`
  rules, folder layout, and optional `license`/`metadata`. A CI gate enforces it on every commit.
- **Portable.** No Claude-only features required to run; these work in any Agent Skills client.
- **Concise by design.** Bodies stay well under the 500-line guidance, with deeper material moved
  to `references/` so context stays cheap (progressive disclosure).
- **Written for outcomes.** Each skill has a clear workflow, concrete input/output examples, and an
  edge-cases section — the things that actually change agent behavior.

## 🧩 The skills

| Skill | What it does | Triggers on |
| ----- | ------------ | ----------- |
| [`sql-query-optimizer`](skills/sql-query-optimizer/) | Diagnoses slow SQL from EXPLAIN plans; recommends indexes, rewrites, and schema fixes (PostgreSQL, MySQL, SQLite, SQL Server). | "optimize this query", slow DB, execution plan |
| [`regex-builder`](skills/regex-builder/) | Builds, explains, and tests regexes with a ReDoS (catastrophic-backtracking) safety check. | "write a regex", "what does this pattern mean" |
| [`conventional-commit-writer`](skills/conventional-commit-writer/) | Writes [Conventional Commits](https://www.conventionalcommits.org) messages from a diff, with breaking-change handling. | "write a commit message", "commit this" |
| [`changelog-writer`](skills/changelog-writer/) | Generates [Keep a Changelog](https://keepachangelog.com) entries and human-focused release notes from commits. | "changelog", "release notes", "what's new" |
| [`a11y-auditor`](skills/a11y-auditor/) | Audits HTML/JSX against WCAG 2.2 AA with severity, criterion, and a code fix per issue. | "check accessibility", a11y, WCAG, ARIA, contrast |
| [`dockerfile-hardener`](skills/dockerfile-hardener/) | Hardens Dockerfiles: non-root, pinned bases, multi-stage, no leaked secrets, healthcheck. | "harden/secure/shrink this image", Dockerfile |
| [`api-design-reviewer`](skills/api-design-reviewer/) | Reviews REST/JSON API design: naming, methods, status codes, errors, pagination, versioning. | "review this API", OpenAPI/endpoints |
| [`test-writer`](skills/test-writer/) | Writes focused, behavior-driven unit/integration tests in the project's existing framework. | "write tests", "add coverage", TDD |
| [`error-message-explainer`](skills/error-message-explainer/) | Explains stack traces and cryptic errors in plain language with the root cause and a fix. | pasted error/traceback, "what does this mean" |
| [`readme-generator`](skills/readme-generator/) | Generates a clear, accurate README grounded in the actual repository. | "write a README", "document this project" |
| [`pr-description-writer`](skills/pr-description-writer/) | Writes reviewer-friendly PR titles and descriptions from a branch diff. | "write a PR description", "open a pull request" |
| [`env-secrets-auditor`](skills/env-secrets-auditor/) | Scans code/config for leaked secrets and insecure env handling; gives a remediation plan. | "check for secrets", leaked API key, audit env |

> Skills with deeper reference material bundle a `references/` file
> (e.g. [SQL anti-patterns](skills/sql-query-optimizer/references/anti-patterns.md),
> [WCAG 2.2 AA checklist](skills/a11y-auditor/references/wcag-2.2-aa-checklist.md)) that the agent
> loads only when needed.

## Install

Pick the skills you want and copy their folders into your tool's skills directory. You can install
**one skill**, several, or all of them. Each folder is self-contained.

```bash
git clone https://github.com/ATOM00blue/agent-skills-pro.git
```

### Claude Code

Skills live in `~/.claude/skills/` (personal, all projects) or `.claude/skills/` (project-local).

```bash
# Personal (available everywhere)
mkdir -p ~/.claude/skills
cp -r agent-skills-pro/skills/* ~/.claude/skills/

# OR project-local (commit it with your repo)
mkdir -p .claude/skills
cp -r agent-skills-pro/skills/sql-query-optimizer .claude/skills/
```

Claude loads a skill automatically when your request matches its description, or you can invoke it
directly: `/sql-query-optimizer`. Run `claude` and ask "what skills are available?" to confirm.
See the [Claude Code skills docs](https://code.claude.com/docs/en/skills).

### Claude.ai / Claude API

Upload a skill folder as a Skill in the Claude.ai Skills UI, or via the API
[Skills endpoints](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).
The same `SKILL.md` format is used.

### OpenAI Codex

Codex reads skills from its skills directory. Copy a skill folder in and Codex discovers it by its
`name`/`description`:

```bash
mkdir -p ~/.codex/skills
cp -r agent-skills-pro/skills/* ~/.codex/skills/
```

See the [Codex skills docs](https://developers.openai.com/codex/skills/) for the exact path on your
version.

### Cursor

Cursor supports the Agent Skills standard. Place skill folders in your Cursor skills directory
(project `.cursor/skills/` or the global location shown in
[Cursor's skills docs](https://cursor.com/docs/context/skills)):

```bash
mkdir -p .cursor/skills
cp -r agent-skills-pro/skills/* .cursor/skills/
```

### Gemini CLI

```bash
mkdir -p ~/.gemini/skills
cp -r agent-skills-pro/skills/* ~/.gemini/skills/
```

See the [Gemini CLI skills docs](https://geminicli.com/docs/cli/skills/).

### Any other Agent Skills client

The format is portable across [40+ tools](https://agentskills.io/clients) — OpenCode, Goose, Amp,
Roo Code, GitHub Copilot, VS Code, Factory, and more. Drop the skill folder into that tool's skills
directory (check its docs for the path). Because each skill is a plain `SKILL.md` folder, no
conversion is needed.

## How skills work

Agents use **progressive disclosure** in three stages, so you can keep many skills installed for
almost no cost until one is needed:

1. **Discovery** — at startup the agent reads only each skill's `name` + `description` (~100 tokens).
2. **Activation** — when your task matches a description, it loads the full `SKILL.md` body.
3. **Execution** — it follows the instructions, loading `references/` or running `scripts/` on demand.

A skill folder:

```
sql-query-optimizer/
├── SKILL.md                      # required: frontmatter + instructions
└── references/
    └── anti-patterns.md          # loaded only when needed
```

The frontmatter follows the [open spec](https://agentskills.io/specification):

```yaml
---
name: sql-query-optimizer          # required: 1-64 chars, lowercase/numbers/hyphens, = folder name
description: Diagnoses slow SQL...  # required: 1-1024 chars, what it does + when to use it
license: MIT                       # optional
metadata:                          # optional: arbitrary string key/values
  author: ATOM00blue
  version: "1.0.0"
  category: data
---
```

## Validate

Every skill is checked against the spec by a zero-dependency Python validator (used in CI):

```bash
python scripts/validate_skills.py
```

```
Validating 12 skill(s) against the Agent Skills spec...

  PASS  a11y-auditor
  PASS  api-design-reviewer
  ...
  PASS  test-writer

All 12 skill(s) passed validation.
```

It verifies frontmatter delimiters, required fields, the `name` rules (and that `name` matches the
folder), length limits, `metadata` shape, that only spec fields are used, and a non-empty body.
[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs it on every push and PR.

## Contributing

New skills and improvements are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for the skill
format, quality bar, and how to add one. In short: create `skills/<your-skill>/SKILL.md`, follow
the authoring checklist, and make sure `python scripts/validate_skills.py` passes.

## License

[MIT](LICENSE) © 2026 ATOM00blue. The Agent Skills format is an open standard originally developed
by [Anthropic](https://www.anthropic.com/) and adopted across the ecosystem.
