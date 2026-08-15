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
