## Target framework: Playwright for Python (pytest)

- `pytest-playwright`. Deliver `requirements.txt`, `pytest.ini`, and the test
  files.
- Locators: `page.get_by_role`, `get_by_label`, `get_by_placeholder`,
  `get_by_text`. `data-testid` only where the accessible name is ambiguous. No
  CSS descendant chains, no XPath.
- Assertions: `from playwright.sync_api import expect`, then
  `expect(locator).to_be_visible()` / `to_have_text()` / `to_have_url()`. These
  auto-wait — never `page.wait_for_timeout`, never a hand-written poll loop.
- Authentication: save storage state once in a session fixture and load it with
  the `browser_context_args` fixture, so tests do not log in through the UI.
- Test data: factory fixtures that create through the API and clean up on
  teardown via `yield`, so specs run independently under `pytest -n auto`.
- Put the `TC-###` id in the test function's docstring, and use
  `@pytest.mark.parametrize(..., ids=...)` for viewport and role matrices.
- Register `smoke` / `p0` markers in `pytest.ini`.
