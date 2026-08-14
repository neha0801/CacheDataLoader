## Coverage depth: EXHAUSTIVE

A certification-grade suite. Assume it will be reviewed by someone looking for
what you missed.

- Everything in STANDARD, plus:
- Every technique in the list above applied to every operation, including
  concurrency, idempotency, and repetition.
- Cross-operation interaction: does a change made through one operation show up
  correctly through every other operation that reads the same data?
- Type-confusion and malformed-payload cases on every input field, not just the
  required ones.
- Pagination and filtering exercised to their documented limits and one step
  past them.
- Where the spec allows a range of behaviours, write the test against the
  documented contract and note the ambiguity in Part 3 rather than guessing.
- Use data-driven / parameterised tests so the case count stays readable — a
  parameter table of 30 boundary values is one test function, not 30.
