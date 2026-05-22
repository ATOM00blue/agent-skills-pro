---
name: api-design-reviewer
description: Reviews REST/HTTP and JSON API designs for consistency, correctness, and evolvability — resource naming, HTTP methods and status codes, pagination, filtering, errors, versioning, idempotency, and auth. Use when the user shares an API spec, OpenAPI/Swagger doc, endpoint list, or route handlers, or asks to review, critique, or design an API.
license: MIT
metadata:
  author: ATOM00blue
  version: "1.0.0"
  category: backend
---

# API Design Reviewer

Review an HTTP/JSON API for the things that make it pleasant, predictable, and safe to evolve.
Give actionable feedback grouped by area, with the corrected shape.

## Workflow

```
- [ ] 1. Inventory the resources, endpoints, methods, and payloads
- [ ] 2. Review against the checklist below
- [ ] 3. Report findings by area with severity and a concrete fix
- [ ] 4. Show the corrected request/response where it helps
```

## Review checklist

### 1. Resources & URLs
- Nouns, not verbs: `POST /orders` not `POST /createOrder`. The HTTP method is the verb.
- Plural collection names: `/users`, `/users/{id}`, `/users/{id}/orders`.
- Lowercase, hyphenated paths; no file extensions; no trailing slashes inconsistency.
- Nest only to express ownership, and not more than ~2 levels deep. Prefer
  `/orders?customer_id=42` over `/customers/42/orders/7/items/9/...`.
- Use IDs in the path, filters in the query string.

### 2. HTTP methods & semantics
- `GET` (safe, no side effects, cacheable), `POST` (create / non-idempotent action),
  `PUT` (full replace, idempotent), `PATCH` (partial update), `DELETE` (idempotent).
- `GET` must never mutate state. `PUT`/`DELETE` must be idempotent (calling twice = calling
  once). Support an `Idempotency-Key` header for `POST` that creates resources.

### 3. Status codes (use the specific one)
| Code | When |
| ---- | ---- |
| 200 | OK with body |
| 201 | Created (include a `Location` header to the new resource) |
| 202 | Accepted (async work queued) |
| 204 | Success, no body (e.g. `DELETE`) |
| 400 | Malformed request / validation error |
| 401 | Not authenticated |
| 403 | Authenticated but not authorized |
| 404 | Resource not found |
| 409 | Conflict (duplicate, version mismatch) |
| 422 | Semantically invalid (valid syntax, bad values) |
| 429 | Rate limited (include `Retry-After`) |
| 500 / 503 | Server error / unavailable |

Avoid "200 with `{ "error": ... }`" — let the status code carry the outcome.

### 4. Errors (consistent, machine-readable)
Adopt one error envelope everywhere. [RFC 9457 Problem Details](https://www.rfc-editor.org/rfc/rfc9457)
is a good default:
```json
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation failed",
  "status": 422,
  "detail": "email must be a valid address",
  "errors": [{ "field": "email", "code": "invalid_format" }]
}
```
Include a stable machine-readable `code`, a human `detail`, and per-field errors for forms.
Never leak stack traces, SQL, or internal hostnames.

### 5. Collections: pagination, filtering, sorting
- Paginate every list endpoint by default; document the cap.
- Prefer **cursor pagination** (`?limit=20&cursor=...`) over offset for large/append-heavy
  data; return the next cursor in the body or a `Link` header.
- Filtering and sorting via query params: `?status=open&sort=-created_at`.
- Return total counts only when cheap; they're often expensive at scale.

### 6. Payload conventions
- Pick one case style (`snake_case` or `camelCase`) and use it everywhere.
- Timestamps in ISO 8601 UTC (`2026-05-22T14:30:00Z`). Money as integer minor units +
  currency code, never floats.
- Be liberal in what you accept, conservative in what you return; don't break clients by
  removing fields — deprecate first.
- Wrap list responses in an object (`{ "data": [...], "next_cursor": "..." }`) so you can add
  metadata without breaking clients.

### 7. Versioning & evolution
- Version from day one: URL (`/v1/...`) is simplest and most visible; header-based works too.
- Additive changes (new optional field, new endpoint) are non-breaking. Removing/renaming a
  field or changing a type **is** breaking — version it.
- Document a deprecation policy and use the `Deprecation`/`Sunset` headers.

### 8. Security & limits
- Authenticate with `Authorization: Bearer <token>`; never put credentials in the URL.
- Enforce authorization per resource (object-level), not just per route.
- Validate and bound all inputs (string length, array size, numeric ranges).
- Rate-limit and return `429` + `Retry-After`; expose `RateLimit-*` headers.
- Use HTTPS only; set sensible CORS; never trust client-supplied IDs for ownership.

## Severity guide
- **Critical:** broken auth/authorization, `GET` with side effects, no input validation.
- **High:** wrong/ambiguous status codes, inconsistent errors, no pagination on large lists.
- **Medium:** verb-in-URL naming, mixed casing, missing versioning strategy.
- **Low:** naming polish, optional metadata, documentation gaps.

## Example finding

**Endpoint:** `POST /getUserOrders` returns `200 { "error": "not found" }` for unknown users.

**Findings:**
```
[High] Verb in URL + wrong method. Use: GET /users/{id}/orders
[High] Wrong status. Unknown user should be 404, not 200-with-error.
[Medium] No pagination on a potentially large collection. Add ?limit & ?cursor.
```
**Corrected:**
```
GET /v1/users/42/orders?limit=20&cursor=eyJpZCI6N30
200 OK
{ "data": [ ... ], "next_cursor": "eyJpZCI6Mjd9" }

# unknown user:
404 Not Found
{ "type": ".../errors/not-found", "title": "User not found", "status": 404 }
```

## Common edge cases
- **Bulk operations:** define a clear partial-success contract (e.g. `207 Multi-Status` or a
  per-item results array) rather than all-or-nothing ambiguity.
- **Long-running actions:** return `202` + a status resource to poll, or a webhook.
- **Search:** complex queries that don't fit a URL can use `POST /resource/search`; document
  why it's a `POST`.
- **GraphQL/gRPC:** these conventions are REST-specific; note when the API isn't REST.
