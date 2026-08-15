## Coverage depth: SMOKE

Optimise for a suite that runs in under a minute and answers one question: is
this build worth testing further?

- One happy-path case per operation. No more.
- Add a negative case only where a silent failure would be mistaken for success
  (auth rejection, and the primary validation error on write operations).
- Skip boundary analysis, concurrency, and the full authorization matrix.
- Target roughly 1 case per operation, 15–25 cases total. If the surface is
  larger than that, cover the operations that everything else depends on
  (authentication, create, read) and say in Part 3 which you dropped.
