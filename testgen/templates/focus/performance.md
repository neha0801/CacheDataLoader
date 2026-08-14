## Additional focus: PERFORMANCE

Add cases that pin the performance contract. Keep them in a separate, tagged
subset so the functional suite stays fast.

- **Latency budgets** — assert a p95 budget per operation, measured over enough
  repetitions to be meaningful. State the budget as a named constant, not a
  magic number, and note in Part 3 that it needs tuning against real baselines.
- **Payload size** — response size for a full page of results stays under a
  stated cap; pagination actually reduces work rather than fetching everything
  and slicing.
- **N+1 detection** — a list endpoint's latency should not scale linearly with
  page size. Compare page size 1 against page size 50 and assert the ratio stays
  under a threshold.
- **Concurrency** — a burst of parallel requests returns correct results with no
  error rate increase; assert on correctness under load, not just throughput.
- **Large inputs** — the largest documented payload is accepted within budget;
  one step above the cap is rejected quickly rather than being processed.
- **Caching** — repeat requests return cache headers as documented, and a
  conditional request with `If-None-Match` returns 304.

Never assert a wall-clock budget in a suite that runs on shared CI without
saying so in Part 3 — it is the single most common source of flaky pipelines.
