---
name: release-notes
description: Generate human-readable release notes and a changelog from merged work.
when_to_use: User wants release notes, a changelog, or a summary of what shipped in a version.
keywords: [release notes, changelog, release, what shipped, version, rc, ship summary]
reads: [release-process]
---

# Release Notes

Turn a list of merged PRs / tickets into release notes the team and customers
can actually read.

## Steps

1. Group changes into the sections defined in `release-process` (Features, Fixes,
   Performance, Internal).
2. Rewrite each line in user-facing language — what changed for the user, not the diff.
3. Flag anything breaking or migration-requiring at the top.
4. Apply the version + tagging scheme from `release-process`.
5. Produce two views: a short highlights block and the full changelog.

## Output template

```
## v<x.y.z> — <date>

Highlights
- <one-line headline per major change>

### Features
- ...
### Fixes
- ...
### Performance
- ...
```

## Rules

- No internal jargon, ticket IDs, or repo names in the customer-facing highlights.
- Breaking changes get a ⚠️ and a one-line migration note.
- Follow the semver + RC rules in `release-process` — don't invent version bumps.
