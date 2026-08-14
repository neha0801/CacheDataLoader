## Target framework: Jest + Supertest (Node / TypeScript)

- Jest with TypeScript (`ts-jest` or Node's native TS support) and Supertest.
  Deliver `package.json`, `jest.config.ts`, and the test files.
- Point Supertest at the base URL from an environment variable for a deployed
  target, or at the exported app instance for an in-process run. Support both
  through one helper so the same suite serves local and CI.
- One `describe` per resource, nested `describe` per operation, and the
  `TC-###` id at the start of each `it` title.
- `test.each` tables for boundary values and role matrices, with a title
  template that names the case.
- Assert with `expect(res.status).toBe(...)` and `expect(res.body).toMatchObject(...)`
  for partial shape. Reserve `toEqual` for payloads the test fully owns. Do not
  use snapshots for API responses — they rot and get blindly re-recorded.
- Data setup and teardown in `beforeEach` / `afterEach` per suite; keep
  `globalSetup` for auth token acquisition only.
- Set `testTimeout` explicitly and never rely on the default; no `setTimeout`
  sleeps.
- Deliver the `npm test` script plus a tagged variant for the smoke subset.
