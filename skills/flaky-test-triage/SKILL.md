---
name: flaky-test-triage
description: Diagnose why an automated test is flaky and propose a concrete, durable fix.
when_to_use: User has an intermittently failing/flaky test, retries, or non-deterministic CI.
keywords: [flaky, flake, intermittent, retry, retries, non-deterministic, unstable test, ci failure]
reads: [test-conventions]
---

# Flaky Test Triage

Find the root cause of an unreliable test instead of papering over it with retries.

## Steps

1. Classify the flake signal: timing/wait, order dependence, shared state, network,
   animation, or environment.
2. Inspect the failing assertion and the wait strategy around it.
3. Map the symptom to a root-cause category and the fix pattern from `test-conventions`.
4. Propose the smallest durable fix (explicit wait, isolated fixture, stable selector).
5. Recommend a quarantine + tracking action only if the fix can't land immediately.

## Root-cause → fix cheatsheet

- Fixed `sleep()` → replace with an explicit wait-for-condition.
- Text/locale selector → switch to an id-based selector (`test-conventions`).
- Leaked state between tests → reset fixtures in setup, not teardown.
- Order dependence → make each test self-seeding and independent.
- Animation race → wait for the settled state, not the trigger.

## Rules

- Never "fix" a flake by adding blind retries — that hides regressions.
- A fix must explain *why* it removes non-determinism, not just that it passed once.
- Re-run the fixed test enough times to show stability before closing.
