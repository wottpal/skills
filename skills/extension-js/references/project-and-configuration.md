# Project and configuration

Contents: [layout](#layout-and-paths), [browser fields](#browser-fields), [config](#configuration), [environment](#environment).

## Layout and paths

Illustrative package layout; keep existing projects' organization where valid:

```text
my-extension/
  package.json
  extension.config.mjs
  tsconfig.json
  extension-env.d.ts       # generated
  src/
    manifest.json
    background.ts
    popup/index.html
    popup/main.ts
    content/main.ts
  pages/diagnostics.html  # extra HTML entry
  scripts/highlight.ts    # browser-injected entry
  public/icons/icon.png   # copied unchanged
  tools/                  # Node/build helpers
```

Use relative source paths from the source manifest, such as `background.ts`, `popup/index.html`, and `content/main.ts` in this layout. HTML declares its own JS/TS script entries. Avoid relying on ambiguous leading-slash behavior across old docs and versions; inspect emitted paths after changing root layout.

The package root owns special folders even with `src/manifest.json`. Without `package.json`/`deno.json`, the manifest directory becomes the root. Inspect explicit `folders` configuration before moving files.

| Folder | Behavior |
| --- | --- |
| `pages/` | Compile extra HTML pages not named in the manifest |
| `scripts/` | Compile browser script entries referenced by a recognizable path in project sources; unreferenced entries may be dropped |
| `public/` | Copy contents to the target output root without compilation |
| `extensions/` | Load companion extensions in local workflows; do not bundle them into the main product |

`public/icons/icon.png` becomes `icons/icon.png`. Use `chrome.runtime.getURL('icons/icon.png')` for an extension URL. `scripts/highlight.ts` emits `scripts/highlight.js`; inject that output path. Prefer static literals that the compiler can trace; dynamically computed filenames may require explicit asset/entry wiring.

Manifest entries are normalized in output. Typical paths include `action/index.html`, `options/index.html`, `background/service_worker.js`, and `content_scripts/content-0.js`. Read the generated manifest instead of hardcoding these in tests. Development content script names can carry hashes.

Use MV3 `web_accessible_resources` only for files the web page needs to load, with narrow `matches`. Being bundled or copied does not automatically authorize web-page access. Extension-owned pages do not require making all their assets public to websites.

## Browser fields

Author a plain `manifest_version: 3` base and override only actual differences. Prefix resolution is recursive, including nested objects and arrays. Precedence is plain < family < exact target; later source order breaks ties within a tier. A winning field replaces that field's value: do not assume permission arrays concatenate.

| Prefix | Applies to |
| --- | --- |
| `chromium:` | Chromium family; also participates in Extension.js Safari normalization |
| `chrome:`, `edge:` | That exact requested target, not every Chromium browser |
| `firefox:`, `gecko:` | Gecko family; exact-target precedence applies when the name matches |
| `safari:`, `webkit:` | Safari/webkit targets |
| Named fork, e.g. `brave:` | That target specifically |

Illustrative manifest fragment, merged into a complete manifest:

```json
{
  "manifest_version": 3,
  "background": { "service_worker": "background.ts" },
  "permissions": ["storage"],
  "chromium:permissions": ["storage", "sidePanel"],
  "chromium:side_panel": { "default_path": "sidebar/index.html" },
  "firefox:sidebar_action": { "default_panel": "sidebar/index.html" }
}
```

The compiler translates common background, action, and sidebar shapes to the target in 4.1.31. Firefox MV3 uses an event-page background; Chromium MV3 uses a service worker. Translation does not implement missing APIs. Keep browser-only code guarded and inspect each emitted manifest, especially permissions and background fields.

## Configuration

Use root `extension.config.mjs` for an unambiguous ESM example (`.js` and `.cjs` also work). No config is necessary for the normal manifest-driven build.

```js
/** @type {import('extension').FileConfig} */
export default {
  commands: {
    dev: { browser: 'chrome', polyfill: true },
    build: { browser: 'chrome', polyfill: true },
    start: { browser: 'chrome', polyfill: true },
  },
}
```

Set `polyfill` consistently with the code's namespace. A `browser.*` compatibility layer does not supply unsupported APIs. CLI flags override command defaults. Use a dedicated development profile; do not casually launch automation against a personal profile.

The 4.1.31 `FileConfig` type accepts one browser target for these defaults. Select multiple targets with the CLI's `--browser=chrome,firefox` flag instead of putting a comma list in this typed example.

Advanced options:

- `transpilePackages` identifies workspace packages needing compilation.
- `define` supplies compile-time constants; values are public in the output. It merges by key across top-level, browser, and command layers.
- `folders` relocates/disables special folders. Browser/command `folders` objects replace the whole lower-precedence object, not individual keys.
- `config` patches the generated Rspack configuration before final loader attachment. Preserve necessary entries/plugins/runtime configuration.
- `configResolved` sees final loader rules but cannot change every Rspack option; already-consumed keys are rejected. Use current docs before choosing the hook.
- `perfBudgets` can flag oversized assets; choose budgets for actual surfaces rather than importing generic thresholds.

Keep service workers and injected/content entries self-contained. Do not force a web-app `splitChunks`/runtime-chunk scheme onto them. MV3 service workers cannot use dynamic `import()`; use static imports that bundle correctly.

## Environment

There are two different loading paths:

| Context | Selection |
| --- | --- |
| Compiled browser code | `.env.defaults` plus **one** matching env file: exact browser+mode, browser, family variants, mode, local, then `.env`; shell values win |
| `extension.config.*` | Merge defaults, `.env`, `.env.local`, `.env.development` in that order; shell values win; not a browser-specific preload |

Use `process.env` in Node configuration. Browser code can read `process.env.EXTENSION_PUBLIC_API_ORIGIN` or `import.meta.env.EXTENSION_PUBLIC_API_ORIGIN`. Built-ins include `EXTENSION_BROWSER` and `EXTENSION_MODE`. `.env.example` documents values but does not provide them.

Workspace fallback looks for `pnpm-workspace.yaml`; do not assume npm/Yarn `workspaces` alone enables it. A browser-specific env file is not a full cascade through all less-specific files. Follow the env guide when config-time and bundle-time values differ.

Any emitted constant or `$EXTENSION_*` HTML/JSON placeholder is readable by users. Keep credentials behind a backend or in the publishing environment, never in browser bundles. Inspect artifacts before release rather than treating a prefix or `.gitignore` as secrecy.

## Sources

- [Manifest](https://extension.js.org/docs/implementation-guide/manifest-json), [HTML](https://extension.js.org/docs/implementation-guide/html), [path resolution](https://extension.js.org/docs/features/path-resolution)
- [Special folders](https://extension.js.org/docs/features/special-folders), [browser fields](https://extension.js.org/docs/features/browser-specific-fields), [cross-browser behavior](https://extension.js.org/docs/features/cross-browser-compatibility)
- [Config](https://extension.js.org/docs/features/extension-configuration), [Rspack](https://extension.js.org/docs/features/rspack-configuration), [env](https://extension.js.org/docs/features/environment-variables), [web-accessible resources](https://extension.js.org/docs/implementation-guide/web-accessible-resources)
