# Testing and debugging

Contents: [commands](#command-semantics), [automation](#automation-contract), [browser tests](#browser-tests), [diagnosis](#diagnosis).

## Command semantics

Run commands from the extension package using its installed CLI. The following use `npm exec -- extension`; an existing project script is equally appropriate.

| Command | Effect |
| --- | --- |
| `dev --browser=chrome` | Watch/build and launch a development browser |
| `build --browser=chrome,firefox --polyfill` | Produce production artifacts; no browser launch for these targets |
| `preview --browser=chrome` | Launch existing output, without compiling |
| `start --browser=chrome` | Production build followed by launch |
| `dev --no-browser` | Keep the build/watch pipeline, suppress browser launch |
| `dev --no-open` | Launch the browser but do not open the extension's initial tab |

Run the project's typecheck, lint, and relevant tests separately from bundling. Include `extension-env.d.ts` for TypeScript. Build all requested browsers and inspect both their JSON manifests and referenced files. Check warnings, especially missing assets, skipped polyfills, and browser-specific normalization.

## Automation contract

Discover installed capabilities first:

```bash
npm exec -- extension capabilities
npm exec -- extension --ai-help --output json
```

Do not parse banners. Use result envelopes (`schema`, `ok`, `status`, `value`, `error.code`) and the metadata under `dist/extension-js/<browser>/`:

- `ready.json`: compilation/session state, paths, process IDs, run identity.
- `events.ndjson`: lifecycle events.
- Session logs when enabled; these may contain page/user data.

For a no-browser watch build, use two processes with the same project and target:

```bash
# Process A, long-running producer
npm exec -- extension dev --browser=chromium --no-browser

# Process B, reader only; does not start a producer
npm exec -- extension dev --browser=chromium --wait --wait-timeout=60000 --output json
```

Do not combine `--wait` and `--no-browser`. Parse wait results from `value.results`, not a legacy top-level `results`. A `ready` status establishes compilation; it does not prove the extension is installed or its background executor attached. Validate `runId`, timestamps, target, and process liveness to reject stale contracts. Handle `error`/timeout as failures. `start`/`build` may complete, so use their documented completed-run freshness rules rather than requiring a live producer forever.

To operate a managed browser session, start a producer with an explicit matching target:

```bash
npm exec -- extension dev --browser=chromium --allow-control
```

Then wait for compilation **and** `runtime: "attached"` before control commands. Keep the project and browser consistent with `ready.json`; command config can otherwise change the default to another target. Examples after attachment:

```bash
npm exec -- extension doctor --browser=chromium --output json
npm exec -- extension inspect --list-tabs --browser=chromium --output json
npm exec -- extension storage get --key enabled --browser=chromium --output json
```

Scope storage reads and browser operations to the task. `--allow-eval` permits arbitrary expression execution and is separate from bounded control; enable it only if needed. Keep session tokens private. Tear down owned processes by recorded PID, not process-name matching. Local docs/MCP access is distinct from granting runtime control.

## Browser tests

Use a production `build` and a real extension-loading fixture for release confidence. A plain Playwright page or a list of browser projects does not load an extension.

For Playwright extension tests, follow [Playwright's official guide](https://playwright.dev/docs/chrome-extensions): use bundled Chromium, a persistent context with an isolated profile, and extension load flags. The `chromium` channel supports full-browser headless execution; do not substitute the default headless shell. Chrome/Edge branded binaries have removed the sideload flags this recipe depends on.

Firefox requires a verified extension-installation runner, such as the Extension.js-managed browser flow; adding a Playwright Firefox project alone is not evidence that the add-on loaded. Test Safari via its supported local app workflow. Check actual extension identity/background attachment before assertions.

Derive popup/options URLs from the emitted manifest. Verify overlay behavior on matching pages and absence where it should not run. Use feature-state assertions and traces for failures, not fixed delays. Close contexts and producer processes in teardown even after assertions fail.

## Diagnosis

| Symptom | First discriminating check |
| --- | --- |
| `browser is not defined` only in production | Build polyfill setting, installed polyfill resolution, emitted bundle |
| Content script compiles but never appears | Default mount export, manifest matches/run timing, site access, actual target tab |
| Duplicate UI/listeners after saves | Mount cleanup, top-level effects, async work completing after disposal |
| Missing `scripts/foo.js` | Root special folder, configured overrides, static reference, emitted `.js` path |
| Asset works in dev but fails installed | Output path, `public/` copy, WAR access scope, dynamic filename tracing |
| Firefox background or Chrome side panel fails | Emitted target manifest, API support, template MV2/MV3 choices |
| Edge loses Chrome-only settings | Exact `chrome:` prefix; use `chromium:` only if behavior belongs to the whole family |
| New entry/config ignored | Restart-required diagnostic; restart the owning dev process |
| Different env value than expected | Config preload versus single-file bundle selection; shell override and workspace marker |
| Dev container HMR cannot connect | Bind `--host`, reachable `--public-host`, and explicit `--allowed-hosts` |
| Wait reports ready but control fails | Fresh run identity, `runtime: attached`, correct target, control permission; run `doctor` |
| Missing framework compiler after auto-install | Lifecycle scripts skipped, required integration dependency absent, local package resolution |
| Safari is enabled but page is unchanged | Website access is a separate user grant from enabling the extension |

Extension.js can retain last-good output after a compilation failure. Do not mistake old files in `dist/` for a successful current build. Read the current exit status and diagnostics before loading an artifact.

## Sources

- [Dev](https://extension.js.org/docs/commands/dev), [build](https://extension.js.org/docs/commands/build), [preview](https://extension.js.org/docs/commands/preview), [start](https://extension.js.org/docs/commands/start)
- [Agent CLI workflow](https://extension.js.org/docs/workflows/driving-the-cli), [readiness](https://extension.js.org/docs/contracts/ready-json), [result envelope](https://extension.js.org/docs/contracts/result-envelope), [doctor](https://extension.js.org/docs/commands/doctor)
- [Troubleshooting](https://extension.js.org/docs/workflows/troubleshooting), [reload behavior](https://extension.js.org/docs/features/reload-and-hmr), [Playwright](https://playwright.dev/docs/chrome-extensions)
