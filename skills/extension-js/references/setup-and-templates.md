# Setup and templates

## New project

Use a supported Node runtime; the verified release requires Node.js >=22.12. Preserve the user's package manager. These examples use npm and a new destination:

```bash
npx extension@latest create my-extension
cd my-extension
npm install
npm run dev -- --browser=chrome
```

For a repeatable scaffold, replace `@latest` with the chosen version, such as `@4.1.31`. Check the destination first; do not scaffold over existing work. `create` defaults to `typescript` and does **not** install dependencies unless passed `--install`. The generated `packageManager` and printed next steps identify the selected manager; follow those if they differ from the example.

The default starter is a sidebar example, not an empty popup project. Inspect its manifest, example permissions, Firefox manifest version, identifiers, and demo features before treating it as product code. In the verified corpus, some templates intentionally target Firefox MV2. Choose the product's MV3 policy explicitly rather than inheriting a template's choice unnoticed.

For existing projects, first inspect package scripts and installed dependencies. Add `extension` as a development dependency only when adoption is requested; retain their dependency and lockfile policy.

## Choose a verified template

Get the live catalog from the chosen CLI's `create --help` or `--ai-help --output json`. The 4.1.31 CLI lists 59 templates; the website's numeric count can lag. Avoid guessing `react-ts`, `popup-react`, or other slugs from another framework.

| Need | Verified catalog choices |
| --- | --- |
| Bare starting point | `init` (a template, not a subcommand) |
| Language/framework sidebar starter | `javascript`, `typescript`, `react`, `preact`, `vue`, `svelte` |
| Toolbar popup / localization | `action`, `action-locales` |
| Page enhancement | `content`, `content-typescript`, `content-react`, `content-vue`, `content-svelte`, `content-preact` |
| Multiple injection groups / page context | `content-multi-one-entry`, `content-multi-three-entries`, `content-main-world` |
| New tab | `newtab`, `newtab-typescript`, `newtab-react`, `newtab-react-router` |
| Sidebar components / workspaces | `sidebar-shadcn`, `sidebar-antd`, `sidebar-monorepo-turborepo`, `sidebar-monorepo-nx` |
| DevTools | `devtools`, `devtools-typescript`, `devtools-react`, `devtools-vue`, `devtools-svelte`, `devtools-preact` |
| Extra runtime entrypoints / test harness | `special-folders-pages`, `special-folders-scripts`, `playwright` |

Example:

```bash
npx extension@4.1.31 create page-helper --template=content-typescript
```

Prefer `newtab-*` names over their legacy `new-*` aliases. The [official examples](https://github.com/extension-js/examples/tree/main/examples) are the source for template contents; the [gallery](https://templates.extension.dev/) helps preview the UI.

## Template provenance and network behavior

Each CLI release pins the catalog archive to an examples commit. Keep `.extension-create.json` to track the actual source and ref. Browsing examples on `main` does not prove they match the installed CLI's corpus.

- HTTPS GitHub/ZIP templates are supported; review third-party templates before executing their install scripts.
- `EXTENSION_CREATE_TEMPLATE_REF` and `EXTENSION_CREATE_TEMPLATE_URL` override the catalog source. Do not set them casually while claiming a repeatable default scaffold.
- An implicit default scaffold can fall back to bundled `javascript` on a failed catalog download. An explicitly selected unavailable template fails. Read the result and provenance instead of assuming TypeScript was created.
- CLI automatic dependency installation suppresses lifecycle scripts by default. If a package needs them, inspect the failure and the project's policy before enabling `EXTENSION_ALLOW_INSTALL_SCRIPTS=true`.

## Framework and style conventions

Extension.js detects the framework and uses its Rspack integration; keep the official template's dependency pattern. Plain JS/TS compilation uses SWC. JSX transpilation does not make a popup or content-script entry automatically: wire HTML scripts and manifest entries.

- Preserve formatting and component patterns from the project. Prefer type-only imports for types and discriminated message unions consistent with local style.
- Include generated `extension-env.d.ts` in TypeScript input; extend types in a separate declaration file rather than editing generated output.
- Add a local `typecheck` script using `tsc --noEmit` when needed. Check template TypeScript compatibility before changing its version.
- Use the existing CSS approach. For Tailwind v4, the PostCSS plugin is `@tailwindcss/postcss` with `@import "tailwindcss"`; v3 uses the `tailwindcss` plugin and its content configuration. Do not mix their setup recipes.
- Keep content UI CSS contained with a shadow root or carefully scoped selectors. A global utility/reset stylesheet can alter the host page.
- Install Sass/Less/framework integration dependencies that the chosen setup requires; inspect compiler diagnostics instead of adding a second bundler.

## Sources

- [Create](https://extension.js.org/docs/commands/create), [template guide](https://extension.js.org/docs/getting-started/templates), [first project](https://extension.js.org/docs/getting-started/create-your-first-extension)
- [TypeScript](https://extension.js.org/docs/languages-and-frameworks/typescript), [API types](https://extension.js.org/docs/languages-and-frameworks/extension-api-types), [Tailwind](https://extension.js.org/docs/integrations/tailwindcss)
