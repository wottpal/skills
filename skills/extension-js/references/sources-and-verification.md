# Sources and verification

## Verified baseline

Research date: **2026-10-04**. This skill is an original workflow synthesis, not a copy of an upstream manual.

| Evidence | Observed value |
| --- | --- |
| npm `extension` latest | `4.1.31` |
| npm engine requirement | Node.js `>=22.12` |
| Published package `gitHead` and inspected source | `2c479cdd2ab05d34344ac5cbfa6030a371d413e0` |
| Official docs repository revision | `19cdc8070b72162d8639667ea4c232827a59f89b` |
| CLI-pinned template corpus | `573d5d58174122606e5d6b6b0f2eafd6c02dcbf7` |
| Examples `main` inspected for comparison | `958a8866742e7a861fd84a867f1081b4ba812764` |

Use the installed CLI/source for framework behavior, current browser documentation for API compatibility, and a real emitted build/runtime check to settle remaining disagreements. Marketing summaries and issue reports are investigation leads, not universal contracts.

## Refresh procedure

```bash
npm view extension dist-tags engines --json
npm view extension@4.1.31 gitHead --json
```

Substitute the selected version in the second command. In an installed project:

```bash
npm exec -- extension --version
npm exec -- extension capabilities
npm exec -- extension create --help
npm exec -- extension build --help
npm exec -- extension --ai-help --output json
```

Check the installed dependency first; these runner examples assume it exists. Preserve a project's version unless installation/upgrade is requested. `next` can lag behind `latest`; do not rank releases by tag name alone.

## Primary resources

| Resource | Use |
| --- | --- |
| [Documentation](https://extension.js.org/docs) and [llms.txt](https://extension.js.org/llms.txt) | Find focused framework pages; follow the documentation indexes |
| [Published npm package](https://www.npmjs.com/package/extension) | Release tags and runtime baseline |
| [Version-pinned source](https://github.com/extension-js/extension.js/tree/2c479cdd2ab05d34344ac5cbfa6030a371d413e0) | CLI registration, config loader, manifest and asset transformations |
| [Release changelog](https://github.com/extension-js/extension.js/blob/2c479cdd2ab05d34344ac5cbfa6030a371d413e0/CHANGELOG.md) | Upgrade behavior and fixes |
| [Version-pinned examples](https://github.com/extension-js/examples/tree/573d5d58174122606e5d6b6b0f2eafd6c02dcbf7/examples) | Reproduce this CLI's scaffolds |
| [Template gallery](https://templates.extension.dev/) | Inspect visual starters; confirm slugs with CLI help |
| [Docs source](https://github.com/extension-js/extension.js.org/tree/19cdc8070b72162d8639667ea4c232827a59f89b) | Resolve stale website guidance against authored docs |
| [Chrome extension docs](https://developer.chrome.com/docs/extensions/) | MV3 lifecycle, API restrictions, permissions, store requirements |
| [MDN WebExtensions](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions) | Firefox and cross-browser API compatibility |
| [Playwright extension testing](https://playwright.dev/docs/chrome-extensions) | Real Chromium extension loading and test fixtures |
| [Docs AI access](https://extension.js.org/docs/ai-access) | Documentation retrieval integrations |
| [extension.dev integration](https://extension.js.org/docs/integrations/extension-mcp) | Optional platform MCP/skill tooling; separate from the framework |

Each task reference links its specific supporting pages. Recheck only the relevant surfaces rather than loading the whole documentation site into context.

## Known documentation disagreements

- The published CLI reports 59 templates while the create page still says 53. Prefer the selected CLI's catalog and recorded scaffold provenance.
- Older prefix guidance treats `chrome:`/`edge:` as family-wide. From 4.1.19 they are exact targets. Verify migrated manifests for `chromium`/Edge/fork builds.
- Some migration snippets use top-level content side effects, whereas the content guide defines a mount/cleanup contract. Use the latter for new module entries and inspect classic-script compatibility separately.
- Path descriptions vary between manifest-root and package-root language. Use relative source manifest paths, keep special folders at the package root, and inspect emitted API paths; do not generalize one leading-slash rule to every context.
- Extension.js's Playwright guide contains a legacy `payload.results` example and overbroad headed/Firefox claims. Schema-1 results are under `value`; follow Playwright's own extension guide for persistent Chromium contexts and headless support.
- Older Chrome skill rules claim a universal one-minute alarm minimum and contain inconsistent async-listener examples. Current Chrome docs and the supported browser floor decide these behaviors.
- A framework page's claim that MAIN world is Chromium-only is not sufficient browser-compatibility evidence. Check MDN/current compatibility data and the compiler's target output separately.

## Checks executed on 2026-10-04

- Ran the published 4.1.31 CLI help/capability surfaces and scaffolded its default TypeScript template; confirmed `depsInstalled: false` and the pinned provenance above.
- Built a temporary MV3 fixture for Chrome, Edge, and Firefox using the content and messaging examples. Checked exact browser prefixes, background translation, injected `.js` output, extra HTML, public assets, and distribution/source ZIP locations and roots.
- Passed a separate TypeScript check and `checkJs` validation of the annotated config. Exercised three mount/click/dispose cycles in an isolated DOM fixture; this is not a browser-runtime test.
- Verified a live no-browser producer/waiter pair, fresh `ready.json`, and schema-1 `value.results`. Confirmed that an explicit no-polyfill production build warns about `browser.*` usage.
- Verified local links, installer discovery, the root README/AGENTS pair, and whitespace. Of 62 external links, 61 returned HTTP 200; npm's package webpage returned 403, while registry metadata was accessible.
- Completed one independent agent review and applied both findings: single-target typed config defaults and consistent managed-session target selection.

Firefox compilation warned about missing store data-collection metadata and skipped addons-linter because it was not installed. These were deliberate minimal-fixture limits, not store validation. Browser UI/HMR behavior, Safari/Xcode packaging, store submission, and multi-model behavioral evaluations were not executed.

## Maintainer verification

Keep `SKILL.md` below 200 lines. Resolve every local link, verify cited external pages and actual flags, and run `git diff --check`. No helper script is shipped because the skill's core work is choosing and verifying project-specific commands, not a reusable deterministic transformation.

Before claiming a new version is verified, test these isolated scenarios:

1. Scaffold the selected TypeScript template without installing; inspect package scripts and `.extension-create.json`. Confirm install behavior and real template slug.
2. Build a minimal MV3 fixture for Chrome, Edge, and Firefox, with a relative manifest entry, synchronous content mount, root runtime-injected script, and public asset. Check emitted manifests, prefix resolution, and files.
3. Build with `--zip --zip-source --zip-filename=release`; inspect archive roots and paths. Check polyfill behavior explicitly, and run a separate typecheck for the fixture.
4. Exercise the producer/waiter contract where the environment supports a dev server. Treat runtime attachment and browser interaction as separate checks.
5. Have an independent agent review the instructions against these scenarios and current sources. Record actual checks and limitations; do not claim multi-model or cross-browser runtime testing from static review.

Use temporary fixtures outside the skill archive. Never run store publishing, account login, private storage access, or unrelated live operations merely to validate documentation examples.
