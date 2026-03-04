# Dennis' Skill Archive

Personal archive for custom agent skills by [Dennis Zoma](https://zoma.dev).

## Source of Truth For Edits

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
| `jotai-nextjs` | [skills/jotai-nextjs](skills/jotai-nextjs/) | Jotai state management workflow with Next.js-focused SSR/hydration and migration guidance |
| `readme-agents-writer` | [skills/readme-agents-writer](skills/readme-agents-writer/) | Write/refactor README.md + AGENTS.md + CLAUDE.md with strict symlink-triplet policy and verification-first workflows |
| `slack-web-api` | [skills/slack-web-api](skills/slack-web-api/) | Slack Web API workflow for posting, searching, channel history/threads, and reactions |
| `use-the-index-luke` | [skills/use-the-index-luke](skills/use-the-index-luke/) | Postgres indexing-first optimization workflow based on Use The Index, Luke |

## Installation


```bash
# 1) List skills from the published repository
npx skills add https://github.com/wottpal/skills --list

# 2) Install the deep research skill
npx skills add https://github.com/wottpal/skills --skill deep-research-firecrawl -y -g

# 3) Install the code-editor-switch skill
npx skills add https://github.com/wottpal/skills --skill code-editor-switch -y -g

# 4) Install the date-fns skill
npx skills add https://github.com/wottpal/skills --skill date-fns -y -g

# 5) Install the Jotai + Next.js skill
npx skills add https://github.com/wottpal/skills --skill jotai-nextjs -y -g

# 6) Install the Postgres tuning skill
npx skills add https://github.com/wottpal/skills --skill use-the-index-luke -y -g

# 7) Install the Slack Web API skill
npx skills add https://github.com/wottpal/skills --skill slack-web-api -y -g

# 8) Install the README/AGENTS/CLAUDE writer skill
npx skills add https://github.com/wottpal/skills --skill readme-agents-writer -y -g
```

## Local Installation (for contributors)

Use this only when developing or testing skills from a local clone.

```bash
# 1) List skills from your local checkout
npx skills add /<path-to-repo>/skills --list

# 2) Install a specific skill from local files
npx skills add /<path-to-repo>/skills --skill use-the-index-luke -y -g

# 3) Install code-editor-switch skill from local files
npx skills add /<path-to-repo>/skills --skill code-editor-switch -y -g

# 4) Install date-fns skill from local files
npx skills add /<path-to-repo>/skills --skill date-fns -y -g

# 5) Install Jotai + Next.js skill from local files
npx skills add /<path-to-repo>/skills --skill jotai-nextjs -y -g

# 6) Install Slack Web API skill from local files
npx skills add /<path-to-repo>/skills --skill slack-web-api -y -g

# 7) Install README/AGENTS/CLAUDE writer skill from local files
npx skills add /<path-to-repo>/skills --skill readme-agents-writer -y -g
```

## Contributor Workflow (Canonical)

Use this loop whenever you update a skill:

```bash
# 1) Edit the skill in this repo (source of truth)
$EDITOR "/Users/zoma/Developer/wottpal/skills/skills/<skill-name>/SKILL.md"

# 2) Reinstall that skill from this local repository
npx skills add "/Users/zoma/Developer/wottpal/skills" --skill "<skill-name>" -y -g

# 3) Optional: compare installed copy against repo source
diff -u \
  "/Users/zoma/Developer/wottpal/skills/skills/<skill-name>/SKILL.md" \
  "$HOME/.agents/skills/<skill-name>/SKILL.md"
```

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
