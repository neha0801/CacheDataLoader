## Target framework: Karate DSL

- Karate 1.4+. Deliver `karate-config.js`, the `.feature` files, and the Maven
  or Gradle build file.
- One `.feature` per resource. `Background:` holds the base URL, headers, and
  auth so scenarios stay short.
- Environment switching goes in `karate-config.js` keyed on `karate.env`; no
  host or credential appears in a feature file.
- Assert with `match` against a schema-shaped expected value — `#string`,
  `#number`, `#uuid`, `#present`, `#notnull`, `#array` — rather than exact
  values for fields the test does not own. Use `match ... contains` for partial
  shape checks.
- `Scenario Outline:` with an `Examples:` table for boundary values and role
  matrices; put the `TC-###` id in the scenario name.
- Reuse setup by calling other features (`* def created = call read('create.feature')`)
  instead of duplicating request blocks.
- Use `@smoke` / `@p0` tags, and give the exact `mvn test -Dkarate.options="--tags @smoke"`
  command in Part 3.
- Prefer Karate's built-in JSON manipulation over embedded JavaScript; keep any
  JS to `karate-config.js`.
