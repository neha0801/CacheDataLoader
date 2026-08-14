## Target framework: Playwright Test (TypeScript)

- `@playwright/test` with TypeScript. Deliver `playwright.config.ts`,
  `package.json`, and the spec files.
- Locators: `page.getByRole`, `getByLabel`, `getByPlaceholder`, `getByText`.
  `data-testid` only where the accessible name is ambiguous. No CSS descendant
  chains, no XPath.
- Assertions: web-first `await expect(locator).toBeVisible()` /
  `toHaveText()` / `toHaveURL()`. Never `waitForTimeout`, never a manual poll.
- Authentication: acquire storage state once in a setup project and reuse it via
  `storageState`, so tests do not log in through the UI.
- Use Page Object classes only where a flow is reused across three or more
  specs; otherwise keep the interaction inline where it is readable.
- Fixtures (`test.extend`) for test data creation and teardown, so each spec is
  independent and can run under `fullyParallel: true`.
- Group with `test.describe`, tag with `{ tag: '@smoke' }`, and put the `TC-###`
  id at the start of each test title.
- Config: `retries` in CI only, `trace: 'on-first-retry'`, and projects for the
  browsers and viewports the suite must cover.
