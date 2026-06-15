# Bug Report Format

The required shape of every bug report. The `bug-report` skill loads this file
so the format lives in one place, not copy-pasted into every prompt.

## Required fields (in this order)

1. **Title** — `[<module>] <symptom> on <surface>`
2. **Environment** — build/version, OS + version, account, network condition
3. **Severity** — from the matrix below, with the matching row cited
4. **Steps to reproduce** — numbered, minimal, deterministic
5. **Expected result**
6. **Actual result**
7. **Evidence** — log id, screenshot, crash id (pointers only, never raw secrets)
8. **Repro rate** — e.g. `5/5` or `2/10 (intermittent)`

## Severity matrix

- **P0 — Critical:** crash, data loss, auth blocked, payment broken, or a release blocker.
- **P1 — High:** core feature unusable, no reasonable workaround.
- **P2 — Medium:** feature degraded but usable, or a clean workaround exists.
- **P3 — Low:** cosmetic, copy, or rare edge case.

## Status vocabulary

- **Fail** — feature was tested and behaves incorrectly. File the bug.
- **Blocked** — could not test due to environment, fixture, or access. Not a
  product bug; resolve the blocker and then test, don't mark it blocked by default.
- **Pass** — tested and correct.

## Don'ts

- No raw tokens, passwords, or PII in steps or evidence — link to a secure store.
- No "doesn't work" without expected vs. actual.
- No severity without citing the matrix row.
