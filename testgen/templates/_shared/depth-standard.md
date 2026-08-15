## Coverage depth: STANDARD

The default regression suite: what a team would run on every pull request.

- Every operation gets its happy path, its main validation failures, and its
  auth failures.
- Boundary analysis on every bounded input (lengths, ranges, page sizes, dates).
- One full lifecycle sequence per resource (create → read → update → delete →
  read-after-delete).
- The authorization matrix for any operation whose result depends on who is
  asking.
- Error-contract assertions on every failure case: status code and body shape.
- Target roughly 3–6 cases per operation. Prefer cutting a redundant positive
  case over cutting a negative one.
