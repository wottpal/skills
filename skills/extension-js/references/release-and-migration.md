# Release and migration

## Package a release

From the extension package, using its installed CLI and chosen API strategy:

```bash
npm exec -- extension build --browser=chrome,firefox --polyfill --zip --zip-source
```

Omit `--polyfill` if the code deliberately uses compatible `chrome.*` calls without a `browser.*` dependency. Request a source archive only when needed, and inspect it for private files before distribution.

In **4.1.31**, ZIPs are siblings of target directories:

```text
dist/
  chrome/manifest.json
  firefox/manifest.json
  <name>-<version>-chrome.zip
  <name>-<version>-firefox.zip
  <name>-<version>-source.zip
```

The name is sanitized by the CLI. `--zip-filename=release` yields `dist/release-chrome.zip`, `dist/release-firefox.zip`, and one `dist/release-source.zip`. Use reported output paths rather than reconstructing filenames. Older versions put distribution ZIPs inside `dist/<browser>/`; update CI paths when upgrading.

Inspect the archive: `manifest.json` at its root, referenced assets present, correct version/icons/permissions, no development runtime or secrets. Do not zip the entire `dist/` tree with session metadata and other browsers. Load each unpacked production target and exercise core flows before submission.

Firefox's optional addons-linter integration can print warnings; a successful build does not establish store compliance. Run required store checks explicitly, prepare source/build instructions where required, and verify current browser-store policies, data disclosures, and identifiers. Preserve the extension's identity and storage migration path on updates.

`extension publish` is an authenticated extension.dev share-link operation for a project/build the platform already knows. It does not upload local output, build it, or submit to a browser store. Local `create/dev/build/preview/start` need no extension.dev account. Only upload or submit when that external action is within the user's request.

## Safari

Treat Safari as a separate packaging and runtime test target:

- `dev --browser=safari` and `build --browser=safari` are supported. Safari `preview` and `start` are refused in this baseline.
- Local app packaging needs macOS and full Xcode, not just Command Line Tools. On other platforms, `build` can emit the web-extension payload while skipping Xcode packaging; that is not an installable app.
- Set an owned `--bundle-id` before distribution; generated `dev.extensionjs.*` is a development identity. Signing/team configuration and App Store submission are separate requirements.
- Check both extension enablement and website-access grants. Build success cannot grant page access.
- Expect a build/resync loop rather than assuming Chromium HMR behavior. Guard unavailable APIs and inspect normalized background/sidebar fields.
- Preserve Xcode customizations before forced regeneration; generated project replacement can discard them.

Use the [Safari guide](https://extension.js.org/docs/browsers/safari) and the current Apple documentation for the exact installed toolchain. Do not turn one tested Safari version into a universal compatibility promise.

## Upgrade Extension.js

1. Record installed version, Node runtime, package manager, emitted manifest shapes, and existing release paths.
2. Read intervening changelog entries; choose stable intentionally rather than the stale `next` tag or a canary by accident.
3. Upgrade within project policy, refresh the lockfile, then run typecheck and target builds.
4. Compare emitted permissions, background/action/sidebar normalization, CSP, static assets, and ZIP paths.
5. Exercise dev remounts and installed production behavior; pay particular attention to polyfill differences and runtime-injected entries.

Migration checkpoints: v4 requires modern Node; 4.1.19 changed `chrome:`/`edge:` prefix scope and browser typings; 4.1.31 changed ZIP placement and added/expanded config and target normalization. Read the actual release notes for the starting version rather than treating this as an exhaustive changelog.

## Adopt from WXT, Plasmo, CRXJS, or Vite/webpack

- Inventory every entry/surface and preserve behavior before removing the old tool.
- Create a real source `manifest.json`; translate generated/file-convention entries into explicit paths, matches, permissions, and browser differences.
- Move background setup out of framework wrappers into top-level listeners. Convert module content entry bodies into synchronous default mounts with cleanup, **not** a bare top-level side-effect migration.
- Replace framework-only auto-imports and lifecycle helpers with explicit imports and lifecycle handling. Keep portable UI/business code.
- Replace build commands/config with Extension.js equivalents. No `extension migrate` subcommand exists in the verified CLI.
- Map public assets, runtime injection paths, and special folders deliberately; compare source and emitted manifests after the first build.
- Rename intentionally public `VITE_*`, `WXT_*`, or other framework variables to `EXTENSION_PUBLIC_*`; do not mechanically expose secret variables.
- If retaining `browser.*`, configure production polyfills explicitly. A development-only success is insufficient.
- Run existing behavior tests against the new output before deleting obsolete configuration and dependencies.

## Sources

- [Build packaging](https://extension.js.org/docs/commands/build), [publishing](https://extension.js.org/docs/publishing/index), [publish command](https://extension.js.org/docs/commands/publish)
- [Changelog](https://github.com/extension-js/extension.js/blob/main/CHANGELOG.md), [Safari](https://extension.js.org/docs/browsers/safari)
- [WXT migration](https://extension.js.org/docs/migrate/from-wxt), [Plasmo migration](https://extension.js.org/docs/migrate/from-plasmo), [CRXJS migration](https://extension.js.org/docs/migrate/from-crxjs), [webpack/Vite migration](https://extension.js.org/docs/migrate/from-webpack-or-vite)
