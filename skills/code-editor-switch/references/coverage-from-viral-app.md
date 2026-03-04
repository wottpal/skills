# Coverage from `~/Developer/fmd-labs/viral-app`

Scan date: 2026-03-04  
Scope: source + config files only (excluded generated/vendor/media binaries)

## Baseline from initial report

- UTIs: `public.plain-text`, `public.text`, `public.source-code`, `net.daringfireball.markdown`
- Tokens: `txt`, `md`, `markdown`, `json`, `yaml`, `yml`, `env`, `local`, `gitignore`

## Additional relevant tokens observed in sample project

- Language/source: `ts`, `tsx`, `js`, `mjs`, `py`, `sql`, `sh`
- Docs/config: `mdx`, `css`, `toml`, `xml`, `lock`
- No-extension filename: `Dockerfile`
- Dotfile suffixes seen: `nvmrc`, `dockerignore`, `prettierignore`, `python-version`, `nano-stageignore`
- Dotenv variants seen: `.env.example`, `.env.preview`, `.env.prod`, `.env.development.local`

## Notes

- Keep image/media/asset tokens excluded (`png`, `jpg`, `webp`, `svg`, `ico`, etc.).
- `.ts` may resolve to a non-code system UTI on some macOS setups; extension mapping is required.
- Dotfiles are often best handled by suffix mapping (`gitignore`, `env`, `local`, `nvmrc`) plus core text UTIs.
