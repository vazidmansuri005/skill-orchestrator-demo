# Test Conventions

The single source of truth for how this team writes automated tests. Skills
reference this file instead of repeating these rules in every prompt.

## Structure

- One behavior per test. The test name states the behavior, not the method.
- Arrange / Act / Assert, with a blank line between each block.
- No logic (loops, conditionals) inside a test body — branchy tests hide failures.
- Each test seeds its own data and is safe to run in isolation or any order.

## Naming

- File: `<module>_<surface>_test`.
- Case: `<does X> when <condition>` — e.g. `shows empty state when no results`.
- IDs: `TC-<module>-<n>` where `<module>` matches a module in project-facts.

## Selectors (critical)

- Prefer id-based selectors over visible text — text breaks on copy + locale changes.
- Never select on layout position or index; those drift with UI changes.
- If an element has no stable id, that's a product bug to file, not a test workaround.

## Waits & stability

- No fixed `sleep()`. Wait for an explicit condition (element visible, request done).
- Wait for the *settled* state after an animation, never the trigger frame.
- Reset shared fixtures in setup, not teardown — teardown can be skipped on crash.

## Coverage priority

- P0: auth, payment, data-loss, and core-create paths.
- P1: primary feature happy paths + common error states.
- P2: edge cases, cosmetic, rarely-hit boundaries.

## Flake policy

- Blind retries are banned in merged tests — they mask real regressions.
- A quarantined test must have an assignee and a tracking ticket, or it gets deleted.
