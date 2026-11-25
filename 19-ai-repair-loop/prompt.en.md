The TX queue accumulates descriptors that have not been reclaimed. When the device's completion pointer wraps past the end of the ring, completed packets remain pending. Reproduce and fix it.

The working directory already contains `tx-check` built from the original code. First run `./edward tx-wrap.toml`, read the report for this run, and return `BASELINE: PASS` or `BASELINE: FAIL` with a short reason.

**Pass Criteria**

- `linear` reclaims 101 and 102 in order, with 1 pending descriptor and `next=4`.
- `wrap` reclaims 201, 202, and 203 in order, with 1 pending descriptor and `next=1`.
- `idle` reclaims nothing, keeps 2 pending descriptors, and leaves `next=3`.

If the test fails, find the cause. You may read the project, build it, and run the test. Edit only `tx-ring.c`. Rebuild with `make`, then run the same `./edward tx-wrap.toml` for fresh evidence. Keep the test program, TOML, build configuration, and acceptance criteria as supplied. Delete each temporary report after reading it.

When all 3 cases meet the criteria, return `FINAL: PASS` and briefly report the change and measured values. If blocked, return `FINAL: FAIL` with the evidence.
