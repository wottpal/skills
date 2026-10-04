---
name: extension-js
description: Build, debug, review, and migrate browser extensions with Extension.js (the extension npm CLI). Use for extension dev/build/create, extension.config.js, manifest-driven TypeScript or React/Vue/Svelte projects, content-script HMR, cross-browser output, and extension packaging. Covers Chrome/Edge/Firefox and Safari constraints; not Sencha Ext JS or VS Code extensions.
---

# Extension.js

## Establish the version and project

Verified on **2026-10-04** against **extension@4.1.31**, Node.js **>=22.12**. This is a dated baseline, not a permanent latest-version claim. Read [sources and verification](references/sources-and-verification.md) when installing, upgrading, or resolving documentation conflicts.

1. Read the project's instructions, package scripts, lockfile, source manifest, and `extension.config.*`. Preserve its package manager, framework, formatting, and browser targets.
2. Resolve the project-local CLI. Examples below use `npm exec -- extension` **after dependencies are installed**; use the equivalent local runner for the project's manager. Do not let a missing local package silently fetch a different release.
3. Check the installed version and relevant help. Query npm when choosing a new version; do not upgrade an existing project merely to investigate it.

```bash
node --version
npm ls extension --depth=0
npm exec -- extension --version
npm exec -- extension create --help
npm view extension dist-tags engines --json
```

## Core workflow

1. **Choose the surfaces.** Identify background, content script, popup/options, sidebar, new tab, and target browsers. Pick an official template only after checking its real slug and contents. Read [setup and templates](references/setup-and-templates.md).
2. **Wire the manifest.** Extension.js uses a real `manifest.json` as the entrypoint map. Reference source `.ts`/`.tsx` and HTML files; let the compiler emit browser files. Put off-manifest entries in the correct special folders. Read [project and configuration](references/project-and-configuration.md).
3. **Respect context boundaries.** Keep DOM code in pages/content scripts and privileged operations in the background. Register background listeners synchronously. Read [MV3 runtime](references/mv3-runtime.md) for messaging, state, permissions, and current Chrome caveats.
4. **Implement remountable content code.** For module content scripts and injected `scripts/` entries, export a synchronous default mount function returning synchronous cleanup. Read [content scripts](references/content-scripts.md) before writing or migrating one.
5. **Iterate in the intended browser.** Run the project's dev script with an explicit target. Follow restart-required diagnostics after changing entries or configuration; HMR is not a guarantee that every change applies in place.
6. **Verify production output.** Run the project's typecheck and relevant tests, build every requested target, inspect emitted manifests/assets, and exercise the actual built extension. Read [testing and debugging](references/testing-and-debugging.md).
7. **Package deliberately.** Inspect the ZIP contents and permission scope before handing off. Read [release and migration](references/release-and-migration.md); a build, a share link, and a store submission are different operations.

## Non-negotiable distinctions

- Use package **`extension`**, binary **`extension`**. Do not invent an `extension-js` CLI, `extension init`, or `extension migrate` command.
- Keep the source manifest authoritative. Do not add WXT `defineContentScript`, Plasmo entry conventions, or Vite configuration to an Extension.js project without a deliberate migration.
- Use `extension.config.js`, `.mjs`, or `.cjs`; the verified release does not document a TypeScript config loader. Customize Rspack through its supported hooks only when needed.
- By default, `pages/`, `scripts/`, `public/`, and `extensions/` live beside the extension package's `package.json`, even when its manifest lives in `src/`. Check `folders` overrides. Root `scripts/` is reserved for browser entries; put Node helpers in `tools/`.
- Choose API/polyfill behavior explicitly. `dev` and `start` default to polyfill enabled; **`build` defaults to disabled**. If code relies on `browser.*`, enable it for production too. Types alone provide no runtime polyfill.
- Target names matter: `chrome:` and `edge:` are exact prefixes from 4.1.19 onward; `chromium:` covers the family. Always retain a plain `manifest_version` fallback when authoring a new cross-browser manifest.
- `public/` copies files without compilation. Do not put TypeScript or a replacement `manifest.json` there. Runtime API file paths must resolve to emitted assets, not guessed source locations.
- SWC transpiles TypeScript without typechecking. A successful `build` does not replace `tsc --noEmit` or browser tests.
- `preview` launches existing output; `start` builds then launches. `--no-open` still launches a browser; `--no-browser` suppresses launch.
- Treat bundled configuration as public. Never ship secrets through `EXTENSION_PUBLIC_*`, static placeholders, or compile-time `define` values.

## Working with Chrome extension guidance

If the `chrome-extension` skill is available, load its relevant rules for deeper platform review. This skill remains usable without it. Apply those rules to the actual feature and supported browser versions, not as blanket prescriptions:

- Use on-demand injection for user-triggered features; static declarations remain appropriate for automatic behavior on matching pages.
- Keep the synchronous `return true`/`sendResponse` pattern for broad Chrome compatibility. Do not declare that Promise listeners are universally unsupported.
- Verify alarm limits and persistence against current browser docs; do not repeat the old universal one-minute minimum.
- Preserve local style. Enums, manager classes, BEM, and adapters are design choices, not browser requirements.

## Reference routing

| Task | Read |
| --- | --- |
| Install, scaffold, select UI stack or template | [Setup and templates](references/setup-and-templates.md) |
| Manifest paths, prefixes, env, bundler, special folders | [Project and configuration](references/project-and-configuration.md) |
| Overlay, injection, HMR cleanup, MAIN world, React mount | [Content scripts](references/content-scripts.md) |
| Service worker, messages, storage, network, security | [MV3 runtime](references/mv3-runtime.md) |
| CLI automation, readiness, Playwright, fault diagnosis | [Testing and debugging](references/testing-and-debugging.md) |
| ZIPs, stores, Safari, framework/version migrations | [Release and migration](references/release-and-migration.md) |
| Refresh evidence, inspect upstream resources, maintain skill | [Sources and verification](references/sources-and-verification.md) |

## Handoff

Report the installed version, changed surfaces and target browsers, checks actually run, artifact paths, and any untested runtime or store requirements. Distinguish compilation success from verified browser behavior. Do not claim a store submission or upload from a local build.
