---
name: error-message-explainer
description: Explains errors, stack traces, exceptions, and cryptic build/runtime messages in plain language, identifies the root cause, and gives a concrete fix. Use when the user pastes an error, stack trace, traceback, panic, compiler error, or failing log and asks what it means, why it happens, or how to fix it.
license: MIT
metadata:
  author: ATOM00blue
  version: "1.0.0"
  category: development
---

# Error Message Explainer

Turn a confusing error into: what it means, why it happened *here*, and the exact fix.
Be specific to the user's code, not generic.

## Workflow

```
- [ ] 1. Read the WHOLE trace — find the real error and the relevant frame
- [ ] 2. State in one sentence what the error means
- [ ] 3. Pinpoint the root cause in the user's code/config
- [ ] 4. Give the concrete fix (and a verification step)
- [ ] 5. Note how to prevent it recurring
```

## Step 1 — Read the trace correctly

The most useful information is often not the last line:

- **Read the actual exception type and message**, then find the **first frame in the user's
  own code** (not library/framework internals). That's usually where to look.
- **Follow "caused by" / chained exceptions to the bottom** — the root cause is the innermost
  one; the outer wrappers are symptoms.
- Language order differs: Python tracebacks read top-down (oldest call first, error last);
  JS stacks read newest-first; Java "Caused by" chains go outer→inner.
- Note line numbers and the values involved; reproduce the failing input mentally.

## Step 2 — Explain plainly

One sentence, no jargon dump: e.g. "`undefined is not a function` means you called something
that isn't a function — usually a typo'd method name or an import that resolved to `undefined`."

## Step 3 — Root cause in *their* context

Tie the generic error to the specific code. "Generic cause: X. In your case, line 42 does Y,
so Z is null when you call `.map` on it." Don't stop at the textbook definition.

## Step 4 — Concrete fix

Show the corrected code or command. If there are multiple plausible causes, give the most
likely first with how to confirm it, then the alternatives — don't dump ten possibilities.

## Common errors — quick reference

| Error (any language) | Usual root cause | First check |
| -------------------- | ---------------- | ----------- |
| Null/undefined access (`NoneType`, `NullPointerException`, `Cannot read properties of undefined`) | A value you assumed exists is missing | Trace where it's assigned; guard or fix the source |
| `ModuleNotFound` / `Cannot find module` / `ImportError` | Not installed, wrong name, or wrong path/venv | Install it; check the import path and active environment |
| `Address already in use` (`EADDRINUSE`) | Port held by another/old process | Kill the process or change the port |
| `Connection refused` (`ECONNREFUSED`) | Target not running or wrong host/port | Confirm the service is up and reachable |
| Permission denied (`EACCES`, `Errno 13`) | File perms, privileged port, or wrong user | Fix ownership/perms; avoid running as root to "fix" it |
| `CORS` / preflight blocked | Server isn't sending allow headers for this origin | Configure CORS on the server, not the browser |
| Type errors (compiler) | Mismatch between expected and actual type | Read "expected X, got Y"; fix at the boundary |
| Timeout / hang | Slow dependency, deadlock, or missing await | Add logging/timeouts; check for unresolved promises |
| `OOMKilled` / heap out of memory | Leak or unbounded data load | Profile memory; stream/paginate; raise limits last |
| Segfault / panic | Bad pointer, nil deref, index out of range | Check the failing index/pointer and bounds |

## Examples

**Input:**
```
TypeError: Cannot read properties of undefined (reading 'name')
    at renderUser (app/user.js:14:23)
```
**Output:**
- **Means:** you read `.name` on something that is `undefined`.
- **Cause:** at `user.js:14`, the `user` object is undefined when `renderUser` runs — likely
  the fetch hasn't resolved yet, or the API returned no user.
- **Fix:** guard before access and handle the empty state.
  ```js
  if (!user) return renderEmptyState();
  return `<h1>${user.name}</h1>`;
  ```
- **Prevent:** type the API response and handle loading/empty states explicitly.

---

**Input:**
```
django.db.utils.OperationalError: could not connect to server: Connection refused
    Is the server running on host "localhost" (127.0.0.1) and accepting TCP/IP connections on port 5432?
```
**Output:**
- **Means:** the app can't reach PostgreSQL at `localhost:5432`.
- **Most likely:** Postgres isn't running (or, in Docker, "localhost" points at the app
  container, not the DB).
- **Fix:** start the DB (`pg_ctl start` / `docker compose up db`); in Docker set the host to
  the DB service name (`db`), not `localhost`. Confirm with `pg_isready -h <host> -p 5432`.
- **Prevent:** add a startup healthcheck/retry and a clear error if the DB is unreachable.

## Common edge cases
- **Minified/bundled stack traces:** ask for source maps; line numbers in built code are
  meaningless without them.
- **Truncated logs:** the shown line may be a downstream symptom; request the full trace and
  the first error in the log, not the last.
- **Flaky/intermittent errors:** suspect timing, ordering, network, or shared state; suggest
  reproducing with logging around the boundary rather than guessing.
- **Error in a dependency:** check the version and known issues before assuming it's the
  user's bug, but verify the inputs they pass first.
