## Additional focus: DATA INTEGRITY

Add cases that prove the system does not lose, duplicate, or corrupt data.

- **Read-your-writes** — after every write, read the resource back through every
  operation that exposes it (detail, list, search, export) and assert they
  agree. Divergence between a detail view and a search index is a classic
  production defect that unit tests never catch.
- **Atomicity** — an operation that fails partway leaves no partial record. Test
  with an input that passes early validation and fails late.
- **Concurrent update** — two callers update the same resource; assert the loser
  gets a conflict and the winner's data is intact. Silent last-write-wins on a
  resource with an optimistic-locking field is a bug.
- **Duplicate submission** — the same create request sent twice (same
  idempotency key, or the same natural key) produces one record, not two.
- **Referential integrity** — deleting a parent with children behaves as
  documented (cascade, restrict, or soft-delete), and no orphan is readable
  afterwards.
- **Round-trip fidelity** — write and read back every field type at its limits:
  maximum-length strings, unicode and emoji, very large and negative numbers,
  high-precision decimals, null vs empty, and timestamps across a DST boundary.
- **Soft delete** — a soft-deleted record disappears from reads, does not
  collide with a new record using the same unique key, and stays excluded from
  aggregates and exports.
- **Aggregates** — counts, totals, and balances recomputed after a sequence of
  writes match the sum of the individual operations.
