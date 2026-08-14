You are a senior SDET. Write an automated test suite for the REST API described
below. You are writing tests that will live in a repository and run in CI for
years — correctness and maintainability matter more than volume.

## System under test

- **Name:** Bookstore API
- **Base URL:** https://api.bookstore.example.com/v1
- **Authentication:** `bearerAuth` — http (bearer, JWT)

## Environment notes

Test tenant 'qa-1' is reset nightly. Librarian and member accounts are provisioned; a member may hold at most 5 concurrent loans.

## API surface

**Spec:** Bookstore API v1.2.0

A small lending API used as the worked example for testgen. It has enough
shape to exercise the summariser: bounded inputs, enums, an auth scheme,
a lifecycle, and a paginated list.

**Servers:** `https://api.bookstore.example.com/v1`

**Security schemes:**
- `bearerAuth` — http (bearer, JWT)

**Operations:** 6

| Method | Path | Operation | Summary |
|--------|------|-----------|---------|
| `GET` | `/books` | listBooks | List books |
| `POST` | `/books` | createBook | Add a book to the catalogue |
| `GET` | `/books/{bookId}` | getBook | Fetch one book |
| `PATCH` | `/books/{bookId}` | updateBook | Update a book |
| `DELETE` | `/books/{bookId}` | deleteBook | Withdraw a book from the catalogue |
| `POST` | `/books/{bookId}/loans` | borrowBook | Borrow a book |

### Operation detail

#### `GET /books`

List books

*Security:* none (public)

**Parameters:**
- `page` in query — integer — min: 1 · default: 1
- `pageSize` in query — integer — min: 1 · max: 100 · default: 20 — Capped at 100 by the server.
- `status` in query — string — enum: "available", "on_loan", "withdrawn"
- `q` in query — string — minLength: 2 · maxLength: 200 — Free-text search over title and author.

**Responses:**
- `200` — A page of books → `BookPage`
- `400` — Invalid pagination or filter → `Error`

#### `POST /books`

Add a book to the catalogue

*Security:* `bearerAuth`

**Request body** `application/json` (required) → `BookCreate`:
- `isbn` string — **required** — pattern: ^\d{13}$
- `title` string — **required** — minLength: 1 · maxLength: 300
- `author` string — **required** — minLength: 1 · maxLength: 200
- `publishedYear` integer — min: 1450 · max: 2100
- `tags` array<string> — maxItems: 20

**Responses:**
- `201` — Created → `Book`
- `400` — Validation failed → `Error`
- `403` — Caller is not a librarian
- `409` — A book with this ISBN already exists

#### `GET /books/{bookId}`

Fetch one book

*Security:* none (public)

**Parameters:**
- `bookId` in path — string(uuid) — **required**

**Responses:**
- `200` — The book → `Book`
- `404` — No such book

#### `PATCH /books/{bookId}`

Update a book

*Security:* `bearerAuth`

**Parameters:**
- `bookId` in path — string(uuid) — **required**

**Request body** `application/json` (required) → `BookUpdate`:
- `title` string — minLength: 1 · maxLength: 300
- `author` string — minLength: 1 · maxLength: 200
- `tags` array<string> — maxItems: 20

**Responses:**
- `200` — Updated → `Book`
- `404` — No such book
- `412` — If-Match precondition failed

#### `DELETE /books/{bookId}`

Withdraw a book from the catalogue

*Security:* `bearerAuth`

**Parameters:**
- `bookId` in path — string(uuid) — **required**

**Responses:**
- `204` — Withdrawn
- `404` — No such book
- `409` — Book is currently on loan

#### `POST /books/{bookId}/loans`

Borrow a book

*Security:* `bearerAuth`

**Parameters:**
- `bookId` in path — string(uuid) — **required**

**Request body** `application/json` (required):
- `dueDate` string(date) — **required** — Must be between 1 and 28 days from today.
- `notes` string — maxLength: 500

**Responses:**
- `201` — Loan created → `Loan`
- `409` — Already on loan, or borrower is at their limit
- `422` — dueDate outside the allowed window

## What to test

Treat the surface above as the requirements document. For each operation,
establish: what it does on success, what it rejects, who is allowed to call it,
and what it changes in the system that a later call can observe.

Where the surface is silent — an undocumented error case, an unstated limit —
write the test against the behaviour the contract implies and flag the
assumption. Do not silently invent requirements.

---

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

---

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

---

## Additional focus: SECURITY

Add cases that probe the security contract. Stay inside the behaviour of the
system under test — assert that attacks are *rejected*; do not write anything
whose purpose is to succeed at an attack.

- **Broken object-level authorization** — for every endpoint that takes a
  resource id, call it as a user who does not own that resource and assert a
  403/404. This is the most common real-world API vulnerability; give it a case
  per endpoint, not one case overall.
- **Broken function-level authorization** — call every admin-only operation as a
  non-admin.
- **Token handling** — missing, expired, malformed, signed with the wrong key,
  `alg: none`, a token for a different audience or tenant, and a token that has
  been revoked or logged out.
- **Injection surfaces** — send SQL, NoSQL, template, and command
  metacharacters in string fields and assert the input is rejected or safely
  escaped, and that the error response does not echo a stack trace or a query.
- **Mass assignment** — POST/PATCH a payload containing fields the caller should
  not control (`role`, `is_admin`, `owner_id`, `balance`) and assert they are
  ignored.
- **Information disclosure** — error bodies carry no stack traces, SQL, internal
  hostnames, or framework versions; `4xx` for a missing resource does not leak
  whether it exists for another tenant.
- **Rate limiting and lockout** — repeated failed authentication is throttled;
  the limit response carries the documented headers.
- **Transport and headers** — HTTPS enforced, HSTS present, CORS reflects only
  allowed origins, and security headers match the documented policy.

---

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

---

## Target framework: pytest + requests (Python)

- Python 3.10+. Use `pytest`, `requests`, and `pytest`'s built-in fixtures. Add
  a dependency only if it earns its place, and list it in Part 3.
- A `conftest.py` holds shared fixtures: a session-scoped `requests.Session`
  with the base URL and auth applied, config read from environment variables,
  and factory fixtures that create test data and clean it up on teardown via
  `yield`.
- One test file per resource or feature area: `tests/test_<area>.py`.
- Use `@pytest.mark.parametrize` for boundary tables and role matrices, with
  `ids=` so failures name the case rather than printing `test[0-1-True]`.
- Mark tests with `@pytest.mark.smoke` / `@pytest.mark.p0` and register the
  markers in `pytest.ini` so `-m smoke` works and no unknown-mark warnings fire.
- Assert with plain `assert` and a message that names the expectation. Keep
  response-shape assertions to the fields under test.
- Never hard-code credentials or hosts — read them from environment variables
  with a documented default for local runs.
- Deliver `requirements.txt` and `pytest.ini` alongside the tests.

---

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
