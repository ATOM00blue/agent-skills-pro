---
name: pr-description-writer
description: Writes clear, reviewer-friendly pull request titles and descriptions from a diff or branch — summary of what and why, key changes, testing notes, and a review checklist. Use when the user asks to write a PR description, open a pull request, summarize a branch for review, or fill in a PR template.
license: MIT
metadata:
  author: ATOM00blue
  version: "1.0.0"
  category: development
allowed-tools: Bash(git diff:*) Bash(git log:*) Bash(gh pr diff:*)
---

# PR Description Writer

Write a pull request description that respects the reviewer's time: they should grasp the
*what* and *why* in 30 seconds and know exactly what to scrutinize.

## Workflow

```
- [ ] 1. Read the diff and commits on the branch
- [ ] 2. If a PR template exists, fill it; otherwise use the structure below
- [ ] 3. Write a precise title and a why-focused summary
- [ ] 4. List the meaningful changes; call out risk and how it was tested
- [ ] 5. Link issues; add screenshots for UI; flag follow-ups
```

## Step 1 — Read the actual change

Base the description on the diff, not the branch name:

```
Changes vs base: !`git diff $(git merge-base HEAD origin/main 2>/dev/null || echo origin/main)...HEAD --stat`
Commits: !`git log $(git merge-base HEAD origin/main 2>/dev/null || echo origin/main)..HEAD --pretty=format:"%s"`
```

Respect an existing template if the repo has `.github/PULL_REQUEST_TEMPLATE.md`.

## Step 2 — Title

Use the Conventional Commit form so it reads well in history and release tooling:
`type(scope): imperative summary`, ≤ ~70 chars, no trailing period.
Example: `fix(auth): refresh expired tokens before retrying requests`.

## Step 3 — Description structure

```markdown
## Summary
<1–3 sentences: what this PR does and WHY. Lead with the motivation/problem.>

## Changes
- <Meaningful change 1 (group by area; describe behavior, not every file)>
- <Meaningful change 2>

## Why
<Context a reviewer needs: the bug's root cause, the design decision and alternatives
considered, links to the issue or discussion.>

## Testing
- <How you verified it: tests added, manual steps, edge cases checked>
- <How a reviewer can reproduce/verify>

## Screenshots / Recordings
<Before/after for any UI change>

## Notes for reviewers
- <Where to focus; known limitations; follow-up work; anything intentionally out of scope>

Closes #<issue>
```

Drop sections that don't apply (e.g. no Screenshots for a backend-only change).

## Writing rules

- **Why over what.** The diff already shows *what* changed; the description must explain *why*
  and the decisions behind it.
- **Summarize, don't transcribe.** Group changes by area and describe behavior; don't list
  every file — that's what the diff is for.
- **Surface risk.** Explicitly call out anything risky: migrations, data backfills, config or
  env changes, feature flags, breaking changes, performance-sensitive paths.
- **Make it reviewable.** Tell the reviewer where to look first and what to verify. If the PR
  is large, suggest a reading order or note it could be split.
- **Link, don't repeat.** Reference the issue/RFC instead of re-explaining it.

## Example

**Branch diff:** adds retry-with-refresh to the API client; touches `client.ts`, `auth.ts`,
plus tests.

**Output:**
```markdown
fix(auth): refresh expired tokens before retrying failed requests

## Summary
API calls were failing with 401s right after a token expired, surfacing as random logout
errors. This refreshes the access token once and retries the request transparently.

## Changes
- Add a response interceptor that catches 401s, refreshes the token, and replays the request.
- Deduplicate concurrent refreshes so a burst of 401s triggers a single token refresh.
- Add unit tests for the single-flight refresh and the no-infinite-loop guard.

## Why
Root cause: the client treated every 401 as fatal. We chose interceptor-level handling over
per-call retry logic to keep call sites unchanged. A refresh lock prevents a thundering herd.

## Testing
- New tests: refresh-and-retry succeeds; second 401 after refresh does NOT loop.
- Manual: forced token expiry locally; confirmed seamless recovery, one /refresh call.

## Notes for reviewers
- Focus on the single-flight lock in `auth.ts` — concurrency is the tricky part.
- Out of scope: refresh-token rotation (tracked in #512).

Closes #498
```

## Common edge cases
- **Huge PR:** recommend splitting; if not feasible, provide a guided reading order and call
  out the few files that carry the real logic.
- **Pure refactor / no behavior change:** say so explicitly and explain how you confirmed
  behavior is unchanged (e.g. tests untouched and passing).
- **Dependency bumps:** note what changed, why, and whether anything is breaking.
- **Draft PR:** state what's done, what's left, and what feedback you're seeking.
