## Target framework: REST Assured + JUnit 5 (Java)

- Java 17+, JUnit 5, REST Assured, and AssertJ for non-response assertions.
- Configure the base URI, auth, and a logging filter once in a
  `@BeforeAll` / abstract `BaseApiTest` class rather than per test.
- Use the `given().when().then()` flow, and assert with `body(...)` matchers on
  the specific JSON paths under test — not `equalTo` on the whole body.
- Pin the contract with `ResponseSpecification` for the shape that every
  response of a kind must satisfy (status, content type, error envelope), and
  reuse it.
- `@ParameterizedTest` with `@CsvSource` / `@MethodSource` for boundary tables
  and role matrices. Give each case a `@DisplayName` that reads as a sentence.
- Use `@Nested` classes to group by resource, and `@Tag("smoke")` /
  `@Tag("p0")` for selection.
- Create test data through the API in `@BeforeEach` and remove it in
  `@AfterEach`; do not rely on a pre-seeded environment.
- Deliver the `pom.xml` (or `build.gradle`) with the dependencies and the
  Surefire/Failsafe configuration needed to run tagged subsets.
