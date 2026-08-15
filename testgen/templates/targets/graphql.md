You are a senior SDET. Write an automated test suite for the GraphQL API
described below.

## System under test

- **Name:** {{APP_NAME}}
- **Endpoint:** {{BASE_URL}}
- **Authentication:** {{AUTH}}

{{ENV_NOTES}}

## Schema

{{SPEC_SUMMARY}}

## What to test

GraphQL moves the failure modes somewhere different from REST. Cover, in
addition to the generic techniques below:

- **Partial success** — a response carrying both `data` and `errors`. Assert
  which fields are null and that the error entry has the right `path` and
  `extensions.code`. A test that only checks `errors == None` will miss this.
- **Field-level authorization** — the same query run by different roles should
  null out or reject individual fields, not just whole operations.
- **Nullability contract** — a non-null field that resolves to null must
  propagate the error up to the nearest nullable parent. Test that it does.
- **Query depth and complexity limits** — a deeply nested or recursive query
  should be rejected before it executes, not after.
- **Aliases and fragments** — the same field requested twice under different
  aliases, and fragments on interfaces and unions with `__typename`.
- **N+1 and batching** — where a resolver loads a list, assert the response is
  correct for an empty list, a single item, and a page-sized list.
- **Mutations** — input-object validation, the returned payload's own error
  union (if the schema uses one) as distinct from a top-level `errors` entry,
  and the read-back through a query.
- **Introspection** — assert it is disabled in production configuration if that
  is the documented policy.

Status code is almost always 200. Assert on the body.
