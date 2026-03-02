# Scope Patterns For README/AGENTS/CLAUDE Docs

Use this matrix to decide depth and section set.

## 1) Root-Level Project Doc

Primary audience: first-time contributors and agents working across the full repo.

Include:

- Project purpose and boundaries
- Global setup and prerequisites
- Core run/test/lint/build commands
- High-level architecture and major directories
- Global coding/contribution rules
- Pointers to deeper sub-docs

Avoid:

- Deep module internals that belong in local docs
- Duplicating every sub-module API detail

Minimal section contract:

- Required headings: `Overview`, `Scope`, `Setup`, `Commands`, `Architecture`, `Related Docs`
- Optional headings: `Troubleshooting`, `Contributing`
- Max heading depth: `###`

## 2) Workspace/App/Package/Service-Level Doc

Primary audience: contributors working inside one monorepo unit.

Include:

- Unit purpose and ownership boundaries
- Unit-specific setup (only if different from root)
- Unit-specific commands and tooling
- Local conventions and constraints
- Dependencies/integration points relevant to this unit

Avoid:

- Repeating full root setup when unchanged
- Cross-repo policies already documented globally

Minimal section contract:

- Required headings: `Overview`, `Scope`, `Setup Differences`, `Commands`, `Integrations`, `Local Conventions`
- Optional headings: `Troubleshooting`, `Release Notes`
- Max heading depth: `###`

## 3) Module/Feature-Level Doc

Primary audience: contributors editing a focused functional area.

Include:

- Domain responsibility and key terminology
- Local file map and entry points
- Business rules and invariants
- Module-specific gotchas, boundaries, and tests
- Only commands needed for this module

Avoid:

- Full stack/setup walkthroughs
- Unrelated infrastructure details

Minimal section contract:

- Required headings: `Overview`, `Responsibility`, `File Map`, `Rules/Invariants`, `Commands/Tests`, `Related Docs`
- Optional headings: `Examples`, `Known Gotchas`
- Max heading depth: `####`

## Composition Rule

- Root sets broad defaults.
- Lower-level docs override locally when needed.
- Prefer links to canonical docs over duplicating text.
