# Contributing to agent-skills-pro

Thanks for contributing! This repo curates **high-quality, spec-compliant** agent Skills. The bar
is "could realistically earn GitHub stars" — useful, correct, concise, and validated. This guide
covers the skill format and how to add or improve one.

## Quick start

1. Fork and clone the repo.
2. Create a folder under `skills/` named exactly like your skill (the folder name **is** the skill
   name): `skills/<skill-name>/`.
3. Add a `SKILL.md` with valid frontmatter and a focused body (see below).
4. Run the validator: `python scripts/validate_skills.py` — it must pass.
5. Add a row to the skill table in [`README.md`](README.md).
6. Open a PR using a clear, conventional title (e.g. `feat(skills): add yaml-linter`).

No build tools or dependencies are required — the validator uses only the Python 3.8+ standard
library.

## The skill format

A skill is a directory containing a `SKILL.md` file, following the open
[Agent Skills specification](https://agentskills.io/specification):

```
skills/
└── your-skill-name/
    ├── SKILL.md          # required
    ├── references/       # optional: docs the agent loads on demand
    │   └── DETAIL.md
    ├── scripts/          # optional: executable helpers the agent can run
    └── assets/           # optional: templates, schemas, examples
```

### Frontmatter

`SKILL.md` begins with YAML frontmatter between `---` markers.

| Field | Required | Rules |
| ----- | -------- | ----- |
| `name` | **Yes** | 1–64 chars; lowercase `a-z`, `0-9`, hyphens; no leading/trailing hyphen; no `--`; **must equal the folder name**. |
| `description` | **Yes** | 1–1024 chars. Third person. Say *what it does* AND *when to use it*; pack in trigger keywords. |
| `license` | No | A license name (we use `MIT`). |
| `compatibility` | No | ≤500 chars, only if the skill needs specific tools/runtime/network. |
| `metadata` | No | String key/value map. We use `author`, `version`, `category`. |
| `allowed-tools` | No | Space-separated pre-approved tools (experimental; e.g. `Bash(git diff:*)`). |

Do **not** add frontmatter keys outside this set — the validator rejects unknown top-level fields.

Example:

```yaml
---
name: yaml-linter
description: Lints YAML files for syntax errors, indentation problems, and common pitfalls (tabs, duplicate keys, ambiguous types), and suggests fixes. Use when the user shares YAML, a CI/k8s/compose config, or asks to validate or lint YAML.
license: MIT
metadata:
  author: your-handle
  version: "1.0.0"
  category: devops
---
```

### Writing the `description` (most important field)

The agent decides whether to load your skill from the description alone, so it carries most of the
weight:

- **Third person**, not "I/you": ✅ "Lints YAML files…" ❌ "I can help you lint YAML."
- **Lead with the key use case**, then list triggers. The combined description text is truncated
  around 1,536 chars in some clients, so front-load the important words.
- **Include the words users actually type** ("slow query", "accessibility", "leaked API key").
- Be specific. ❌ "Helps with files." ✅ "Extracts text and tables from PDF files… Use when…"

### Writing the body

Keep it concise — assume the model is already smart; only add what it doesn't know.

- **Under ~500 lines.** Move deep reference material to `references/` and link it (one level deep).
- Prefer a **clear workflow** (numbered steps, optionally a copyable checklist).
- Include **concrete input → output examples**, not abstract descriptions.
- Add a **common edge cases** section — this is where skills earn their keep.
- Use **consistent terminology** and **forward-slash paths** (`references/x.md`, never `\`).
- No time-sensitive content ("after August 2025…"); use an "old patterns" note if needed.
- Don't offer five alternatives — give a sensible default with an escape hatch.

See any existing skill (e.g. [`sql-query-optimizer`](skills/sql-query-optimizer/SKILL.md)) as a
reference implementation.

## Authoring checklist

Before opening a PR, confirm:

- [ ] Folder name = `name` field, and both follow the naming rules.
- [ ] `description` is third person, specific, and keyword-rich.
- [ ] Body is concise, has a workflow, concrete examples, and edge cases.
- [ ] Deep material lives in `references/`, linked one level deep.
- [ ] All file paths use forward slashes.
- [ ] No unknown frontmatter fields.
- [ ] `python scripts/validate_skills.py` passes locally.
- [ ] Added a row to the README skill table.

## Validating

```bash
python scripts/validate_skills.py
```

The same check runs in CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) on every push
and pull request. PRs must be green to merge.

## Improving an existing skill

Fixes, sharper descriptions, better examples, and new edge cases are very welcome. Keep changes
focused, preserve the existing structure, and re-run the validator.

## Code of conduct

Be respectful and constructive. Assume good intent, give specific feedback, and keep discussion
focused on making the skills more useful.

## License

By contributing, you agree your contributions are licensed under the [MIT License](LICENSE).
