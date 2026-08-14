## Additional focus: CONTRACT

Add cases that pin the wire contract itself, so a breaking change fails a test
rather than a consumer.

- **Schema validation** — validate every response against the schema from the
  spec, not against hand-written field lists. Assert required fields present,
  types correct, enums within their allowed set, and formats (date-time, uuid,
  email) well-formed.
- **Additive-only evolution** — an unknown field in a response must not break a
  client; a removed field or a narrowed type must fail a test. State explicitly
  which fields the suite treats as contract, so an intentional break is a
  deliberate test edit.
- **Error envelope** — every error response across every endpoint shares one
  shape. Assert it once as a reusable matcher and apply it everywhere.
- **Status code discipline** — the documented code for each outcome, including
  the distinctions that get muddled in practice: 400 vs 422, 401 vs 403,
  404 vs 410, 409 vs 412.
- **Headers** — content type with charset, `Location` on creation, cache
  directives, and any documented correlation or version header.
- **Serialization edge cases** — null vs absent vs empty for every optional
  field, numeric precision on large integers and decimals, timezone handling on
  timestamps, and unicode round-trips including emoji and RTL text.
- **Versioning** — if the API is versioned, assert the previous version still
  answers with its own contract.
