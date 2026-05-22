---
name: test-writer
description: Writes focused, behavior-driven unit and integration tests for a given function, module, or change, covering happy paths, edge cases, and error conditions using the project's existing test framework and conventions. Use when the user asks to write or add tests, improve coverage, write a unit/integration test, or do test-driven development.
license: MIT
metadata:
  author: ATOM00blue
  version: "1.0.0"
  category: development
---

# Test Writer

Write tests that document behavior and catch regressions — not tests that just chase a
coverage number. Match the project's existing framework and style.

## Workflow

```
- [ ] 1. Detect the test framework and conventions already in use
- [ ] 2. Identify the unit under test and its observable behavior
- [ ] 3. Enumerate cases: happy path, edges, errors, boundaries
- [ ] 4. Write each test: Arrange–Act–Assert, one behavior per test
- [ ] 5. Make tests deterministic and isolated
- [ ] 6. Run them; ensure they pass and actually exercise the code
```

## Step 1 — Match the project

**Do not introduce a new test framework.** Detect and reuse what exists:
- JS/TS: `vitest`, `jest`, `node:test`, `mocha` (check `package.json` and existing `*.test.*`).
- Python: `pytest` (default), `unittest`.
- Go: `testing` + table-driven tests.
- Rust: `#[cfg(test)]` modules; Java: JUnit 5.

Follow the existing file location, naming, and assertion style. Reuse existing fixtures and
helpers instead of inventing parallel ones.

## Step 2 — Test behavior, not implementation

Assert on observable outputs and side effects (return values, thrown errors, emitted events,
DB rows) — not private internals. A good test survives a refactor that preserves behavior.

## Step 3 — Enumerate cases

For each unit, cover:
- **Happy path:** typical valid input → expected output.
- **Boundaries:** empty, single element, max size, zero, negative, off-by-one.
- **Edge values:** null/undefined/None, empty string, whitespace, unicode, very large input.
- **Error conditions:** invalid input raises/returns the right error; failures are handled.
- **State/idempotency:** calling twice, ordering, concurrency where relevant.

Prefer a few high-value cases over many trivial ones. Every test should be able to fail for a
real reason.

## Step 4 — Structure each test

- **Arrange–Act–Assert** with a blank line between phases.
- **One behavior per test.** Multiple assertions are fine if they describe the same behavior.
- **Descriptive names** that read as a sentence: `returns 0 for an empty cart`,
  `throws when the user is not found`.

## Step 5 — Determinism and isolation

- No real network, clock, randomness, or filesystem unless that *is* the unit under test —
  inject or mock them. Freeze time; seed RNG.
- Each test sets up and tears down its own state; tests must pass in any order and in
  parallel. No shared mutable globals.
- **Mock at the boundary** (HTTP client, DB driver), not your own domain logic. Over-mocking
  produces tests that pass while the app is broken.

## Step 6 — Verify

Run the suite. A test that can't fail is worthless: if unsure, temporarily break the code and
confirm the test goes red, then restore it.

## Examples

**Vitest / TypeScript** for `function discount(total, code)`:
```ts
import { describe, it, expect } from "vitest";
import { discount } from "./pricing";

describe("discount", () => {
  it("applies a known 10% code", () => {
    expect(discount(100, "SAVE10")).toBe(90);
  });

  it("returns the original total for an unknown code", () => {
    expect(discount(100, "NOPE")).toBe(100);
  });

  it("never returns a negative total", () => {
    expect(discount(5, "SAVE10")).toBeGreaterThanOrEqual(0);
  });

  it("throws on a negative total", () => {
    expect(() => discount(-1, "SAVE10")).toThrow(/total/i);
  });
});
```

**pytest** table-driven style:
```python
import pytest
from app.pricing import discount

@pytest.mark.parametrize("total, code, expected", [
    (100, "SAVE10", 90),     # happy path
    (100, "NOPE", 100),      # unknown code -> no change
    (0, "SAVE10", 0),        # boundary: zero total
])
def test_discount(total, code, expected):
    assert discount(total, code) == expected

def test_discount_rejects_negative_total():
    with pytest.raises(ValueError, match="total"):
        discount(-1, "SAVE10")
```

## Anti-patterns to avoid
- Asserting on log output or call counts instead of real behavior.
- Tests coupled to implementation details (private methods, internal call order).
- One giant test covering ten things — failures become undiagnosable.
- Snapshot tests for logic that should have explicit assertions.
- Mocking the thing you're trying to test.

## Common edge cases
- **Async code:** await/return promises; assert on rejections; avoid arbitrary `sleep`.
- **Time-dependent logic:** inject a clock or use fake timers; never assert on `now()`.
- **Floating point:** compare with a tolerance, not `==`.
- **Integration tests:** use an ephemeral DB/container or transaction rollback per test for
  isolation; keep them separate from fast unit tests.
