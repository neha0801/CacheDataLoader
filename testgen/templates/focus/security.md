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
