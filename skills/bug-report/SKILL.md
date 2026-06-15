---
name: bug-report
description: Write a structured, triage-ready bug report from a crash, defect, or unexpected behavior.
when_to_use: User reports a crash, defect, regression, or unexpected behavior and wants it filed.
keywords: [bug, bug report, crash, defect, regression, repro, file a bug, issue]
reads: [bug-report-format, project-facts]
---

# Bug Report

Convert a raw observation ("the app crashes on login") into a clean report an
engineer can act on without follow-up questions.

## Steps

1. Restate the problem in one sentence: what happened vs. what was expected.
2. Pin the environment using `project-facts` (build, OS, account, module).
3. Write minimal, numbered reproduction steps — the shortest path to the bug.
4. Assign severity using the matrix in the `bug-report-format` KB.
5. Attach evidence pointers (logs, screenshots, crash id) — never inline secrets.
6. Emit the report using the exact field order from `bug-report-format`.

## Quality bar

- Repro steps must be deterministic; if flaky, say so and give the hit rate.
- Severity must cite the matrix row, not a gut feeling.
- Title format: `[<module>] <symptom> on <surface>` (e.g. `[Auth] crash on login`).
- Distinguish "blocked" (cannot test) from "fail" (tested, broke) — see `bug-report-format`.
