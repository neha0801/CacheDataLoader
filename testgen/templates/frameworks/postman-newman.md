## Target framework: Postman collection + Newman

- Emit a Postman Collection v2.1 JSON document and a separate environment JSON.
  Both must be valid JSON that imports without editing.
- Organise requests into folders by resource; name each request with its
  `TC-###` id and a readable summary.
- Put assertions in each request's `test` script using `pm.test(...)` with
  `pm.response.to.have.status(...)` and `pm.expect(...)` on specific fields.
- Chain state with collection variables set via `pm.collectionVariables.set()`.
  Never hard-code an id created by an earlier request.
- Keep every host, credential, and token in the environment file as a variable;
  mark secrets `"type": "secret"` and leave their values empty.
- Use a folder-level or collection-level pre-request script for auth token
  acquisition and refresh, so individual requests stay clean.
- For boundary tables, use a data file (CSV or JSON) driven by
  `newman run ... --iteration-data`, and reference the columns as `{{var}}`.
- Deliver the exact `newman run` command, including the environment file, the
  iteration data file, and a reporter flag suitable for CI.
