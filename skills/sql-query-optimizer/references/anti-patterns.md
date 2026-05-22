# SQL Anti-Patterns and Engine Notes

## Contents
- Predicate anti-patterns
- Join anti-patterns
- Aggregation and window anti-patterns
- Engine-specific tuning notes
- Statistics and maintenance

## Predicate anti-patterns

| Anti-pattern | Why it hurts | Fix |
| ------------ | ------------ | --- |
| `WHERE func(col) = x` | Non-sargable, index unusable | Transform the constant, or add an expression/functional index |
| `WHERE col LIKE '%term%'` | Leading wildcard can't use a b-tree index | Full-text index, trigram index (PG `pg_trgm`), or a search engine |
| `WHERE col != x` / `NOT IN` | Often forces a scan; `NOT IN` with NULLs returns no rows | Use `NOT EXISTS`, or rethink the predicate |
| Implicit type cast (`WHERE varchar_col = 123`) | Cast on the column blocks the index | Compare same types; bind parameters with the column's type |
| `OR` across columns | Planner may scan instead of using either index | `UNION ALL` of indexed branches |

## Join anti-patterns

- **Cartesian product:** a missing or wrong join condition multiplies rows. Verify the join
  keys and expected cardinality.
- **Joining then filtering** when you could filter then join: push selective `WHERE` clauses
  down so fewer rows enter the join.
- **`DISTINCT` to paper over a fan-out join:** the join is producing duplicates; fix the join
  grain (e.g. aggregate the child table first) instead of de-duplicating after.

## Aggregation and window anti-patterns

- **Correlated subquery per row** (`SELECT ..., (SELECT MAX(x) FROM t2 WHERE t2.id=t1.id)`):
  rewrite with a `JOIN` to a pre-aggregated set, or a window function
  (`MAX(x) OVER (PARTITION BY id)`).
- **`GROUP BY` on an unindexed expression:** may force a sort/hash spill; index the grouping
  columns or precompute.
- **`COUNT(*)` on huge tables for "is there any":** use `EXISTS` / `LIMIT 1` instead.

## Engine-specific tuning notes

### PostgreSQL
- `EXPLAIN (ANALYZE, BUFFERS)` shows shared/read buffers — high `read=` means cold cache or
  missing index.
- Raise `work_mem` per session for big sorts/hashes; lower it back afterward.
- Use `CREATE INDEX CONCURRENTLY` on production to avoid locking writes.
- Check `pg_stat_user_indexes` to find unused indexes; drop them to speed writes.

### MySQL / InnoDB
- The clustered primary key is appended to every secondary index; keep the PK narrow.
- `EXPLAIN FORMAT=JSON` exposes `used_key_parts` and filtered percentages.
- Watch for `Using filesort` and `Using temporary` in the Extra column — both signal a sort
  or temp table that an index could remove.

### SQLite
- `EXPLAIN QUERY PLAN` reports `SCAN` vs `SEARCH`; aim for `SEARCH ... USING INDEX`.
- Run `ANALYZE` so the query planner has statistics; SQLite skips many optimizations without.

### SQL Server
- Read the actual plan's thick arrows (high row counts) and missing-index hints (use as a
  starting point, not gospel).
- Beware parameter sniffing; `OPTION (RECOMPILE)` or `OPTIMIZE FOR` can stabilize plans.

## Statistics and maintenance

Stale statistics are the most common cause of "the index exists but isn't used." Refresh
them before concluding an index is wrong:

- PostgreSQL: `ANALYZE table;` (autovacuum usually handles this)
- MySQL: `ANALYZE TABLE table;`
- SQLite: `ANALYZE;`
- SQL Server: `UPDATE STATISTICS table;`

Rebuild/reorganize fragmented indexes on write-heavy tables periodically.
