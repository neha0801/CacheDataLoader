You are a senior SDET. Write an automated end-to-end test suite for the web
application described below.

## System under test

- **Name:** {{APP_NAME}}
- **URL:** {{BASE_URL}}
- **Authentication:** {{AUTH}}

{{ENV_NOTES}}

## Application surface

{{SPEC_SUMMARY}}

## What to test

Test user-visible behaviour, not implementation. A test should read like a
description of what a person does and what they then see.

- **Selectors** — prefer role- and label-based locators (`getByRole`,
  `getByLabel`, `getByText`). Fall back to `data-testid` only where the
  accessible name is genuinely ambiguous. Never use CSS paths, nth-child
  chains, or XPath built from the DOM structure; they break on every restyle.
- **Waiting** — use the framework's auto-waiting assertions. No fixed sleeps, no
  polling loops written by hand.
- **State setup** — log in and seed data through the API or a storage-state
  fixture, not by driving the UI. Drive the UI only for the thing under test.
- **Journeys** — cover each critical path end to end, plus the recovery paths:
  validation errors shown inline, a failed submit that preserves entered data,
  session expiry mid-flow, back-button and refresh at each step.
- **Responsive** — the critical journeys at a mobile viewport as well as
  desktop, where the layout differs.
- **Isolation** — each test starts from a clean session and creates its own
  data. No dependence on test order.

Assert on what the user sees — text, enabled/disabled state, URL, visible error
messages — not on network calls, unless the test exists specifically to pin a
contract.
