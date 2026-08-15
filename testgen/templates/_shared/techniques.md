## Test design techniques to apply

Derive cases systematically. For every input you identify, walk this list and
keep the cases that are actually reachable — do not invent inputs the system
under test does not accept.

1. **Equivalence partitioning** — one representative case per class of input
   that the system should treat identically. Do not write ten cases that all
   exercise the same branch.
2. **Boundary value analysis** — for every bounded value (length, range, count,
   page size, date window) test `min-1`, `min`, `min+1`, `max-1`, `max`,
   `max+1`. Boundaries are where defects live; prefer them over interior values.
3. **Negative and malformed input** — wrong type, null, empty string, missing
   required field, unexpected extra field, oversized payload, wrong content
   type, malformed encoding.
4. **State transitions** — exercise the object lifecycle in order (create →
   read → update → delete → read-after-delete) and the illegal transitions
   (update-after-delete, double-delete, cancel-an-already-cancelled order).
5. **Authorization matrix** — for each protected operation, cross every role
   (anonymous, authenticated non-owner, owner, admin) against the expected
   outcome. Missing-token, expired-token, malformed-token, and
   token-for-another-tenant are separate cases.
6. **Idempotency and repetition** — repeat safe operations and assert
   invariance; repeat unsafe operations and assert the documented behaviour
   (duplicate rejected, or same result returned).
7. **Concurrency** — where two callers can touch one resource, assert the
   losing writer gets a conflict rather than silent data loss.
8. **Pagination, sorting, filtering** — first page, last page, page past the
   end, page size 0, page size above the cap, unstable sort keys, filter that
   matches nothing, filter that matches everything.
9. **Error contract** — every failure path asserts status code *and* the shape
   of the error body (code, message, field pointer). A test that only asserts
   "not 200" is not a test.
10. **Data isolation** — each case creates the data it needs and cleans up after
    itself, so the suite passes in any order and on a re-run against a dirty
    environment.

## Anti-patterns to avoid

- Assertions on the whole response body when only two fields matter — that
  produces a suite that breaks on every unrelated change.
- Tests that depend on execution order or on data left behind by a previous
  test.
- `sleep()` as a synchronisation strategy; poll with a timeout instead.
- Hard-coded IDs, tokens, hostnames, or timestamps.
- One giant test that walks the whole happy path and asserts once at the end.
  When it fails you learn nothing about where it broke.
