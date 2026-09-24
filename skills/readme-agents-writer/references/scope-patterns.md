# Scope Patterns For README/AGENTS Docs

Use this matrix to decide depth and section set.

Each selected scope has one canonical README (directly or through the shared-doc exception) and an `AGENTS.md` symlink. Use the suggested sections for new docs or an explicit substantial rewrite. For small edits, preserve valid existing structure instead of retrofitting a template. Omit empty sections and avoid padding a small document to satisfy a template.

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

Suggested sections:

- Core headings: `Overview`, `Scope`, `Setup`, `Commands`, `Architecture`, `Related Docs`
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

Suggested sections:

- Core headings: `Overview`, `Scope`, `Setup Differences`, `Commands`, `Integrations`, `Local Conventions`
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

Suggested sections:

- Core headings: `Overview`, `Responsibility`, `File Map`, `Rules/Invariants`, `Commands/Tests`, `Related Docs`
- Optional headings: `Examples`, `Known Gotchas`
- Max heading depth: `####`

## Composition Rule

- Root sets broad defaults.
- Put subtree-specific commands and invariants in a local pair only when they differ materially from root guidance.
- State each rule's scope and any intended local exception explicitly. Loading and precedence vary by harness; do not rely on conflicting prose being resolved automatically.
- Prefer links to canonical docs over duplicating text.
- Shared targets must genuinely have the same operational scope. State command working directories unambiguously even when a README is reached from another directory.
