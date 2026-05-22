---
name: regex-builder
description: Builds, explains, and tests regular expressions, and flags catastrophic-backtracking (ReDoS) risks. Translates plain-English requirements into a correct pattern with a token-by-token explanation and test cases. Use when the user needs a regex, asks what a pattern means, wants to validate/extract/replace text, or mentions regex, pattern matching, or ReDoS.
license: MIT
metadata:
  author: ATOM00blue
  version: "1.0.0"
  category: development
---

# Regex Builder

Produce a correct, readable, safe regular expression — and prove it works.

## Workflow

```
- [ ] 1. Restate the requirement: what must match, what must NOT match
- [ ] 2. Confirm the flavor (PCRE/Python/JS/Go/RE2) and flags
- [ ] 3. Build the pattern from anchored, named pieces
- [ ] 4. Explain it token by token
- [ ] 5. Give passing and failing test cases
- [ ] 6. Check for catastrophic backtracking (ReDoS)
```

## Step 1 — Pin down the spec

Ambiguity is the main source of wrong regexes. Before writing anything, state explicitly:

- Three to five strings that **must match**.
- Three to five strings that **must NOT match** (the near-misses matter most).
- Whether you're matching the whole string (anchor with `^...$`) or finding substrings.

## Step 2 — Know the flavor

Syntax and capabilities differ. Confirm which engine the regex runs in:

| Engine | Notes |
| ------ | ----- |
| JavaScript | `\d` is Unicode-unaware by default; use `u` flag; lookbehind in modern engines only |
| Python `re` | Named groups `(?P<name>...)`; `re.VERBOSE` allows whitespace/comments |
| PCRE / PHP / Java | Richest feature set; supports atomic groups and possessive quantifiers |
| Go / RE2 / Rust | **Linear time, no backtracking** — no backreferences or lookaround, but ReDoS-immune |

Prefer RE2-style engines for untrusted input when the feature set allows.

## Step 3 — Build from named, anchored pieces

Default to anchoring (`^...$`) when validating a full value, and use the smallest character
classes that satisfy the spec. Build complex patterns from labeled sub-expressions rather
than one dense line.

### Reliable building blocks

```
\d              one digit (ASCII)            [A-Za-z]   one ASCII letter
\w              word char [A-Za-z0-9_]       \s         whitespace
.               any char except newline      [^...]     negated class
a?  a*  a+      0-1, 0+, 1+ (greedy)         a*?  a+?    lazy variants
{2,4}           between 2 and 4              (?:...)    non-capturing group
(?<name>...)    named capture group         \1 / \k<n> backreference
^   $   \b      start, end, word boundary    (?i)       case-insensitive (inline)
(?=...) (?!...) lookahead / negative lookahead
```

## Step 4 — Always explain the pattern

Break the final regex into a token-by-token table so the user can verify and maintain it.

## Step 5 — Provide test cases

List concrete strings that should match and should fail, including tricky near-misses.

## Step 6 — ReDoS safety check (do this every time)

Catastrophic backtracking can hang a server on a short malicious input. **Flag and fix** any
pattern where the input can be parsed many ways. The danger signs:

- **Nested quantifiers:** `(a+)+`, `(a*)*`, `(.*)*`
- **Quantified group with overlapping alternation:** `(a|a)*`, `(\d+|\w+)*`
- **Adjacent overlapping quantifiers:** `\d+\d+`, `.*.*`

```
Dangerous:  ^(\w+\s?)*$        on "aaaaaaaaaaaaaaaaaaaa!"  -> exponential blowup
Safer:      ^\w+(?:\s\w+)*$    no overlap between the repeated pieces
```

Fixes: remove overlap so each character has one parse path; make a quantifier possessive
(`\w++`) or wrap in an atomic group (`(?>\w+)`) in PCRE/Java; or switch to an RE2 engine.
For "match up to a delimiter," prefer a negated class `[^"]*` over `.*?`.

## Examples

**Requirement:** validate a US ZIP code (`12345` or `12345-6789`), full-string.

**Pattern (JS/PCRE):**
```
^\d{5}(?:-\d{4})?$
```

**Explanation:**

| Token | Meaning |
| ----- | ------- |
| `^` | start of string |
| `\d{5}` | exactly five digits |
| `(?:-\d{4})?` | optionally, a hyphen and four more digits (non-capturing) |
| `$` | end of string |

**Tests:** match `12345`, `12345-6789`; reject `1234`, `123456`, `12345-67`, `abcde`.

---

**Requirement:** capture the host from an `http(s)` URL.

**Pattern (Python, `re.VERBOSE`):**
```python
import re
url_re = re.compile(r"""
    ^https?://          # scheme
    (?P<host>[^/:\s]+)  # host: up to a slash, colon, or whitespace
    (?::\d+)?           # optional :port
    (?:/\S*)?$          # optional path
""", re.VERBOSE)
m = url_re.match("https://example.com:8080/path")
m.group("host")  # -> "example.com"
```

Note the host uses a negated class `[^/:\s]+` rather than `.+`, which keeps it linear-time
and stops at the right boundary.

## Common edge cases

- **Email/URL "validation":** no regex fully validates these; validate format loosely, then
  verify by sending a confirmation. Don't ship a 200-character email regex.
- **Unicode:** `\w` and `\d` are ASCII-only in many engines; use `\p{L}` / `\p{N}` with the
  Unicode flag when you need international text.
- **Multiline:** `^`/`$` match line boundaries only with the multiline flag; `.` excludes
  newlines unless the dotall/single-line flag is set.
- **Escaping in code:** in most languages backslashes must be doubled in string literals, or
  use raw strings (`r"..."` in Python, backtick strings in Go).
