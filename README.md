# Dennis' Skill Archive

Personal archive for custom agent skills by [Dennis Zoma](https://zoma.dev).

## Source of Truth For Edits

This README is the canonical guide for contributors and agents. Keep `AGENTS.md` as a symlink to `README.md`; edit this file for shared guidance. Do not recreate a `CLAUDE.md` companion.

When you are in this repository, always edit skills under this repo:

- `skills/<skill-name>/...`

Never edit installed copies directly:

- `~/.agents/skills/...`
- `~/.codex/skills/...`

Those home-directory locations are consumer/install targets and can be overwritten by future installs.  
For publishing and maintenance, this repository is the canonical source of truth.

## Skills

| Skill | Path | Notes |
| --- | --- | --- |
| `deep-research-firecrawl` | [skills/deep-research-firecrawl](skills/deep-research-firecrawl/) | Firecrawl-first deep research with selectable depth modes |
| `code-editor-switch` | [skills/code-editor-switch](skills/code-editor-switch/) | macOS `duti` workflow to switch code/text/config default handlers to a target editor |
| `date-fns` | [skills/date-fns](skills/date-fns/) | Practical date-fns v4 and native @date-fns/tz workflow with strict timezone package guidance |
| `himalaya-v2` | [skills/himalaya-v2](skills/himalaya-v2/) | Pimalaya Himalaya v2 email CLI workflow based on `himalaya 2.0.0-alpha.1` (`f2306449278940c04768cd4ca0fa9fd7ca29c45b`, 2026-06-17) |
| `jotai-nextjs` | [skills/jotai-nextjs](skills/jotai-nextjs/) | Jotai state management workflow with Next.js-focused SSR/hydration and migration guidance |
| `readme-agents-writer` | [skills/readme-agents-writer](skills/readme-agents-writer/) | Maintain a canonical README.md + AGENTS.md symlink with verified guidance and safe cleanup of legacy CLAUDE.md companions |
| `sem-diff` | [skills/sem-diff](skills/sem-diff/) | Entity-level semantic Git diff, blame, dependency impact, and AI-ready context workflow using sem |
| `slack-web-api` | [skills/slack-web-api](skills/slack-web-api/) | Slack Web API workflow for posting, searching, channel history/threads, and reactions |
| `use-the-index-luke` | [skills/use-the-index-luke](skills/use-the-index-luke/) | Postgres indexing-first optimization workflow based on Use The Index, Luke |
| `worktree-handoff` | [skills/worktree-handoff](skills/worktree-handoff/) | Worktree-aware handoff of all uncommitted and untracked changes onto a local target branch, defaulting to the current linked-worktree branch or `develop` |

## Installation

Requires npm and `npx`. Choose a skill name from the catalog above; the example installs `readme-agents-writer` globally.

```bash
# List published skills
npx skills add "https://github.com/wottpal/skills" --list

# Install one skill
npx skills add "https://github.com/wottpal/skills" --skill "readme-agents-writer" -y -g
```

## Local Installation (for contributors)

For development, use the local checkout so the installation includes uncommitted changes. Run from the repository root:

```bash
npx skills add "." --list
```

Use the contributor workflow below to install the skill you are editing.

## Contributor Workflow (Canonical)

1. Edit `skills/<skill-name>/...` in this repository, preserving unrelated worktree changes.
2. Run the checks relevant to the change, described below.
3. Reinstall that skill from the local checkout. Optionally compare the complete installed directory, including references and scripts.

Run from the repository root, replacing the example skill name as needed:

```bash
skill_name="readme-agents-writer"
npx skills add "." --skill "$skill_name" -y -g

# Optional: compare the entire skill with the shared installed copy
diff -qr "skills/$skill_name" "$HOME/.agents/skills/$skill_name"
```

Review the installer's per-agent results; an empty diff confirms the shared installed copy matches the source.

### Verification

- For documentation edits, verify affected facts, paths, and links, then run `git diff --check` from the repository root.
- When changing a skill's scripts, use its documented checks and focused fixtures. Run only workflows relevant to the change; inspection alone does not justify executing a live operation described by a skill.
- When changing the root README/AGENTS layout or its helpers, run the read-only pair check below (Python 3.10+). It checks this root scope; other skill READMEs do not automatically need AGENTS companions.

```bash
python3 "skills/readme-agents-writer/scripts/check-doc-pairs.py" "."
```

For documentation writing or legacy companion cleanup, use [readme-agents-writer](skills/readme-agents-writer/SKILL.md). Report checks that could not be run and any unresolved discrepancies.

## Repository

```text
skills/
├── <skill-name>/
│   ├── SKILL.md
│   ├── references/
│   ├── scripts/
│   ├── assets/
│   └── templates/
└── ...
```

## Conventions

- One skill per folder under `skills/`.
- Keep `SKILL.md` concise; move long content to `references/`.
- Use clear frontmatter (`name`, `description`) for reliable skill discovery.
- Keep `references/`, `scripts/`, and `assets/` one level deep from `SKILL.md`.
- Prefer executable scripts for deterministic validation tasks.

## Attribution

- `skills/deep-research-firecrawl` was bootstrapped from: `https://github.com/199-biotechnologies/claude-deep-research-skill`
- `skills/slack-web-api` was originally put together by [Felix Vemmer](https://github.com/feliche93)
- `skills/use-the-index-luke` was originally put together by [Felix Vemmer](https://github.com/feliche93)

## Copyright and source notice

`skills/use-the-index-luke` is an original skill implementation in this repository and is based on concepts/documentation from:

- [Use The Index, Luke](https://use-the-index-luke.com/)
