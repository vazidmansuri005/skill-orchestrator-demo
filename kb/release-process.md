# Release Process

How this team versions and ships. The `release-notes` skill references this so
the rules aren't restated in every prompt.

## Versioning (semver)

- `MAJOR.MINOR.PATCH` — e.g. `4.8.1`.
- **MAJOR**: breaking change or migration required.
- **MINOR**: backward-compatible feature.
- **PATCH**: backward-compatible fix.

## Release candidates

- Each release cuts from an `rc/<version>` branch.
- QA signs off against the `release` build flavor, not `debug`.
- An RC is promoted only when all P0/P1 bugs are closed or explicitly waived.

## Changelog sections (in order)

1. **Highlights** — customer-facing one-liners for the big changes.
2. **Features** — new capabilities.
3. **Fixes** — bug fixes.
4. **Performance** — speed/memory/battery improvements.
5. **Internal** — refactors, tooling (omit from customer-facing notes).

## Rules

- Breaking changes lead with ⚠️ and a one-line migration note.
- Highlights contain no ticket IDs, repo names, or internal jargon.
- Don't invent a version bump — derive it from the change types above.
