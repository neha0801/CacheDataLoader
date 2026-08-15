## How to answer

Answer in exactly three parts, in this order.

### Part 1 — Coverage plan (table)

Before writing any code, list the cases you intend to write:

| ID | Area | Case | Type | Priority | Expected result |
|----|------|------|------|----------|-----------------|
| TC-001 | ... | ... | positive / negative / boundary / auth / state | P0 / P1 / P2 | ... |

Rules for the table:
- `P0` = a failure blocks release. Keep P0 to the cases that prove the feature
  works at all and the cases that protect against data loss or a security hole.
- Every row must be traceable to something in the spec above. If you infer a
  requirement that the spec does not state, mark the row with `(assumed)`.

### Part 2 — Test code

Write the suite. It must be complete and runnable — no `...`, no
`# TODO: implement`, no placeholder function bodies. Every case in the Part 1
table appears in the code with its `TC-###` id in the test name or docstring, so
the plan and the suite can be diffed against each other.

Include whatever setup the suite needs to actually run: fixtures, factories,
config loading, auth helpers, cleanup. Split into multiple files where that is
the framework's convention, and label each file with its path:

```
# tests/test_<area>.py
```

### Part 3 — Notes for the human

Keep it short and specific:
- **Assumptions** — every `(assumed)` row from Part 1, with what you assumed.
- **Gaps** — what you could not cover from the spec alone and what you would
  need (a sample response, a test account, a role matrix) to cover it.
- **Spec defects** — anything in the spec that is ambiguous, self-contradictory,
  or looks wrong. This is often the most valuable part of the answer; do not
  skip it to be agreeable.
- **How to run** — the exact commands, including any environment variables.

Do not add a summary, a preamble, or an offer to help further.
