---
name: test-case-generation
description: Generate structured, ready-to-run test cases from a feature description or requirement.
when_to_use: User asks to write or create test cases, test scenarios, or coverage for a feature.
keywords: [test case, test cases, scenario, scenarios, coverage, requirement, acceptance, write tests]
reads: [test-conventions, project-facts]
---

# Test Case Generation

Turn a feature or requirement into a complete set of test cases that follow the
team's conventions.

## Steps

1. Identify the feature under test and its acceptance criteria.
2. Enumerate paths: happy path, alternate paths, error/empty/boundary states.
3. Add cross-cutting cases: permissions, offline/poor network, localization, a11y.
4. For each case, write: ID, title, preconditions, steps, expected result, priority.
5. Apply the naming and structure rules from the `test-conventions` KB.
6. Tag the affected module using the names in the `project-facts` KB.

## Output template

```
TC-<module>-<n>: <concise title>
  Priority:      P0 | P1 | P2
  Preconditions: <state / account / data needed>
  Steps:
    1. ...
    2. ...
  Expected:      <observable, asserted outcome>
```

## Rules

- One assertion-worthy outcome per case; split compound cases.
- Prefer id-based selectors over text (see `test-conventions`).
- Never invent a module or account — use only what `project-facts` lists.
- Mark P0 only for revenue / data-loss / auth-blocking paths.
