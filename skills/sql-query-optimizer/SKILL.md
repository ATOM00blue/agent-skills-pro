---
name: sql-query-optimizer
description: Diagnoses slow SQL queries and recommends concrete fixes — indexes, query rewrites, and schema changes. Reads EXPLAIN/EXPLAIN ANALYZE plans for PostgreSQL, MySQL, SQLite, and SQL Server. Use when a query is slow, a database is under load, the user shares an execution plan, or asks to optimize, tune, or speed up SQL.
license: MIT
metadata:
  author: ATOM00blue
  version: "1.0.0"
  category: data
---

# SQL Query Optimizer

Turn a slow query into a fast one with evidence-based changes. Always measure first,
change one thing at a time, and re-measure.

## Workflow

```
- [ ] 1. Capture the plan (EXPLAIN ANALYZE) and the slowest operators
- [ ] 2. Identify the dominant cost (scan, sort, join, or row estimate error)
- [ ] 3. Form one hypothesis and the smallest change that tests it
- [ ] 4. Recommend the change with the expected effect
- [ ] 5. State how to verify (re-run plan, compare actual time/rows)
```

## Step 1 — Get the real plan, not the estimate

Ask for or run the analyzed plan so you see actual rows and time, not just estimates:

- PostgreSQL: `EXPLAIN (ANALYZE, BUFFERS, VERBOSE) <query>;`
- MySQL 8+: `EXPLAIN ANALYZE <query>;` (or `EXPLAIN FORMAT=JSON`)
- SQLite: `EXPLAIN QUERY PLAN <query>;`
- SQL Server: enable "Include Actual Execution Plan", or `SET STATISTICS IO, TIME ON;`

If you only have the query, reason from the schema and predicates but say the estimate is
unverified until a plan is captured.

## Step 2 — Read the plan top-down, fix bottom-up

Find the operator that consumes the most actual time, and check the row-estimate accuracy
(estimated vs actual rows). A large gap (e.g. estimate 10, actual 1,000,000) means stale
statistics or a non-sargable predicate is misleading the planner.

| Signal in the plan | Likely cause | First thing to try |
| ------------------ | ------------ | ------------------ |
| `Seq Scan` / `Full Table Scan` on a large table with a selective `WHERE` | Missing index | Add an index on the filter/join columns |
| Estimated rows ≪ actual rows | Stale statistics | `ANALYZE table;` (PG) / `ANALYZE TABLE` (MySQL) / `UPDATE STATISTICS` (MSSQL) |
| Index exists but unused | Non-sargable predicate (function/cast on the column) | Rewrite so the column is bare on one side |
| Expensive `Sort` / `Hash` spilling to disk | `ORDER BY` / `GROUP BY` / large hash join | Covering/sorted index, or raise `work_mem` |
| `Nested Loop` over many rows | Bad join order from wrong estimates | Refresh stats; consider a hash/merge join |
| Same subquery evaluated per row | Correlated subquery | Rewrite as a `JOIN` or window function |

## Step 3 — The highest-impact fixes (in order)

### 1. Make predicates sargable (index-usable)

A predicate is sargable when the indexed column appears bare on one side. Wrapping it in a
function or applying a math/cast prevents index use.

```sql
-- Not sargable: function on the column blocks the index
WHERE DATE(created_at) = '2026-05-22'
WHERE LOWER(email) = 'a@b.com'
WHERE price * 1.2 > 100

-- Sargable: column stays bare; transform the constant or add an expression index
WHERE created_at >= '2026-05-22' AND created_at < '2026-05-23'
WHERE email = 'a@b.com'                       -- or add an index on LOWER(email)
WHERE price > 100 / 1.2
```

### 2. Add the right index — order matters

For a composite index, put **equality columns first, then the range/sort column**. An index
on `(status, created_at)` serves `WHERE status = 'open' ORDER BY created_at`; reversing the
columns does not.

```sql
-- Query: WHERE status = 'open' AND created_at > now() - interval '7 days'
CREATE INDEX idx_orders_status_created ON orders (status, created_at);
```

Prefer a **covering index** (include the selected columns) so the query is index-only and
never touches the heap:

```sql
-- PostgreSQL
CREATE INDEX idx_orders_lookup ON orders (status, created_at) INCLUDE (total, customer_id);
```

Use a **partial index** when you only ever query a slice of the table:

```sql
CREATE INDEX idx_active_users ON users (last_login) WHERE deleted_at IS NULL;
```

### 3. Avoid `SELECT *`

Select only the columns you need. It reduces I/O and makes covering indexes possible.

### 4. Replace `OFFSET` pagination with keyset (seek) pagination

`OFFSET 100000` still reads and discards 100,000 rows. Page by the last seen key instead:

```sql
-- Slow on deep pages
SELECT * FROM events ORDER BY id LIMIT 20 OFFSET 100000;

-- Keyset: O(log n) regardless of page depth
SELECT * FROM events WHERE id > :last_id ORDER BY id LIMIT 20;
```

### 5. Fix N+1 query patterns

If the application loops issuing one query per row, collapse it into a single `JOIN` or an
`IN (...)` / `= ANY(...)` batch. This is usually the single biggest application-level win.

## Examples

**Input:** `SELECT * FROM orders WHERE YEAR(created_at) = 2026;` is slow.

**Output:**
- Cause: `YEAR(created_at)` is non-sargable, forcing a full scan.
- Fix: rewrite as a half-open range and index the column.
  ```sql
  CREATE INDEX idx_orders_created ON orders (created_at);
  SELECT id, customer_id, total
  FROM orders
  WHERE created_at >= '2026-01-01' AND created_at < '2027-01-01';
  ```
- Verify: re-run `EXPLAIN ANALYZE`; expect an Index Range Scan and far fewer rows read.

## Common edge cases

- **Tiny tables:** a sequential scan can be faster than an index; don't add indexes blindly.
- **Write-heavy tables:** every index slows `INSERT`/`UPDATE`/`DELETE`; justify each one.
- **Low-cardinality columns** (e.g. boolean `is_active`): a plain b-tree index rarely helps;
  consider a partial index on the rare value instead.
- **`OR` across different columns:** can defeat indexes; a `UNION ALL` of two indexed queries
  is often faster.
- **Parameter sniffing (SQL Server):** one plan cached for skewed parameters can be slow for
  others; consider `OPTION (RECOMPILE)` or optimizing for a typical value.

## Additional resources

- For a fuller catalog of anti-patterns and engine-specific notes, see
  [references/anti-patterns.md](references/anti-patterns.md).
