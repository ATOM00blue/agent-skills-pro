---
name: readme-generator
description: Generates a clear, well-structured project README from the codebase — title, badges, description, features, install, usage, configuration, contributing, and license. Use when the user asks to write, create, generate, or improve a README, project documentation, or docs for a repository.
license: MIT
metadata:
  author: ATOM00blue
  version: "1.0.0"
  category: documentation
---

# README Generator

Write a README that lets a newcomer understand the project and get it running in minutes.
Base it on the actual repository, not assumptions.

## Workflow

```
- [ ] 1. Learn the project (manifest, entry point, scripts, existing docs)
- [ ] 2. Draft sections in priority order
- [ ] 3. Make every command copy-pasteable and accurate
- [ ] 4. Trim filler; keep it scannable
```

## Step 1 — Read the repo first

Ground the README in evidence. Inspect:
- The package manifest (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`) for name,
  description, scripts, dependencies, and entry point.
- The main entry file and CLI/flags for real usage.
- Existing config files, `.env.example`, and any docs to reuse.
- The license file for the license name.

Never invent install commands, options, or badges that aren't true.

## Step 2 — Structure (most-read sections first)

```markdown
# Project Name

> One-sentence description of what it does and who it's for.

[badges: build, version, license, etc.]

Short paragraph: the problem it solves and why someone would use it.

## Features
- Key capability 1
- Key capability 2

## Quick start / Installation
\`\`\`bash
<exact install command>
\`\`\`

## Usage
\`\`\`bash
<minimal working example with expected output>
\`\`\`

## Configuration
| Option | Default | Description |
| ------ | ------- | ----------- |

## API / Commands        (if applicable)

## Contributing          (link to CONTRIBUTING.md if it exists)

## License
```

Add a Table of Contents only for long READMEs. Add Screenshots/Demo near the top for anything
with a UI. Omit sections that don't apply rather than padding them.

## Step 3 — Writing rules

- **Lead with value.** The first two lines must answer "what is this and why do I care?"
- **Show, don't tell.** A 5-line working example beats a paragraph of prose.
- **Make commands real.** Every command should run as written; include the expected output
  for the key one.
- **Be honest about status** (alpha/beta, supported platforms, requirements/versions).
- **Use relative links** for in-repo files; check headings are unique for anchor links.

## Badges (only true ones)

Use shields.io. Common, accurate badges:
```markdown
![Build](https://github.com/OWNER/REPO/actions/workflows/ci.yml/badge.svg)
![npm](https://img.shields.io/npm/v/PACKAGE)
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
```
Don't add badges for services the project doesn't use.

## Example skeleton (CLI tool)

```markdown
# wc-rs

> A fast, drop-in `wc` replacement written in Rust.

![Build](https://github.com/me/wc-rs/actions/workflows/ci.yml/badge.svg)
![Crates.io](https://img.shields.io/crates/v/wc-rs)
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)

`wc-rs` counts lines, words, and bytes 4–6x faster than GNU `wc` on large files,
with the same flags you already know.

## Features
- Drop-in compatible flags (`-l`, `-w`, `-c`, `-m`)
- Parallel processing for multiple files
- Zero dependencies, single static binary

## Installation
\`\`\`bash
cargo install wc-rs
\`\`\`

## Usage
\`\`\`bash
wc-rs -l README.md
#   42 README.md
\`\`\`

## License
MIT — see [LICENSE](LICENSE).
```

## Common edge cases
- **Library vs application:** libraries lead with install + import + a minimal code snippet;
  apps lead with run instructions and a screenshot.
- **Monorepo:** keep a top-level README that orients, plus a focused README per package.
- **Existing README:** improve in place — preserve accurate content and structure; don't
  discard project-specific details.
- **Sparse repo:** ask for or infer the missing pieces (purpose, audience) rather than
  fabricating features.
