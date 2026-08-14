## Additional focus: ACCESSIBILITY

Add cases that pin WCAG 2.2 AA conformance on the critical journeys.

- **Automated scan** — run an axe-core scan on every distinct page state
  (loaded, form filled, error shown, modal open) and assert zero violations at
  the `serious` and `critical` levels. Scan states, not just URLs; most defects
  appear only after interaction.
- **Keyboard** — every journey completable with keyboard alone. Assert focus
  order follows visual order, focus is visible, focus moves into a modal on open
  and returns to the trigger on close, and nothing traps focus.
- **Names and roles** — every control has an accessible name; icon-only buttons
  are the usual offenders. Assert via role-based locators, which fail naturally
  when the name is missing.
- **Forms** — every input has a programmatically associated label, errors are
  announced (`aria-live` or `aria-describedby` on the field), and error text
  identifies the field and the fix.
- **Dynamic content** — route changes and async updates announce themselves;
  loading states are exposed to assistive technology rather than being a silent
  spinner.
- **Zoom and reflow** — the journey works at 200% zoom and at a 320px-wide
  viewport with no horizontal scrolling and no clipped content.

Automated scanning catches roughly a third of real barriers. Note in Part 3
which checks still need a manual screen-reader pass.
