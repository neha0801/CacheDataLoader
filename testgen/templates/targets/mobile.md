You are a senior SDET. Write an automated test suite for the mobile application
described below.

## System under test

- **Name:** {{APP_NAME}}
- **App / platform target:** {{BASE_URL}}
- **Authentication:** {{AUTH}}

{{ENV_NOTES}}

## Application surface

{{SPEC_SUMMARY}}

## What to test

Mobile failures cluster around lifecycle and environment, not around the happy
path. Weight the suite accordingly.

- **Lifecycle** — background and restore mid-flow, process death and restore
  (the OS kills the app and reopens it on the same screen), rotation, and
  cold vs. warm start.
- **Connectivity** — offline at launch, connection lost mid-request, flaky
  connection with a retry, and the transition back online. Assert the user sees
  a real state, not a spinner forever.
- **Permissions** — each permission granted, denied, denied-permanently, and
  revoked from settings while the app runs.
- **Interruptions** — incoming call, notification, low battery, app switcher.
- **Storage and session** — token persisted across restart, logout clears it,
  and an expired token refreshes without bouncing the user to login.
- **Locators** — accessibility identifiers only. Never coordinates, never
  index-based lookup into a view hierarchy.
- **Waiting** — explicit waits on element state. Fixed sleeps are the single
  largest source of flake in a mobile suite.
- **Form factors** — the critical journeys on the smallest supported screen and
  on a tablet layout, plus large-font accessibility settings.

Assert on accessible labels and on-screen state; screenshot comparison is a
supplement, never the primary assertion.
