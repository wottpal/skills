# Content scripts

## Choose when and where to inject

Use manifest `content_scripts` for automatic behavior on matching pages. Use `activeTab` plus `scripting` for a feature invoked by the user on one tab. Use dynamic registration when matches/configuration genuinely change at runtime. Neither programmatic nor declarative injection is universally faster or more correct.

Keep match patterns narrow. Default to `document_idle` unless early execution is required. Test restricted pages, frames, navigation, and denied/revoked access. `activeTab` does not grant access to every browser page.

## Mount contract

For a new module content entry, put setup inside a **synchronous default-export function**. Return synchronous cleanup so development remounts can remove UI, observers, listeners, and timers. Avoid top-level DOM side effects and an `async` default export: a Promise is not the cleanup callback.

Illustrative `src/content/main.ts`, referenced by `src/manifest.json` with `js: ["content/main.ts"]` and `run_at: "document_idle"`:

```ts
export default function mount() {
  const host = document.createElement('aside')
  host.dataset.pageHelper = 'status'
  const shadow = host.attachShadow({ mode: 'open' })
  const label = document.createElement('span')
  label.textContent = 'Page helper ready'
  shadow.append(label)
  document.documentElement.append(host)

  const controller = new AbortController()
  const onClick = () => { label.textContent = 'Page helper active' }
  host.addEventListener('click', onClick, { signal: controller.signal })

  return () => {
    controller.abort()
    host.remove()
  }
}
```

For real overlays, add accessible interaction and scoped CSS. If mounting React, create the root inside this function and call `root.unmount()` before removing its host. Dispose framework roots and observers explicitly; removing the DOM node alone does not dispose subscriptions.

Start async work inside the mount, attach error handling, and use an abort signal or disposed flag before applying a late result. Cancellation APIs only cancel work that actually consumes their signal. Remove `chrome.runtime` listeners using `removeListener`, since DOM `AbortSignal` cleanup does not apply to them.

Handle extension-context invalidation after reload/update by disposing stale work and prompting a page refresh when necessary. Do not retry a dead extension context in a tight loop or hide every API failure as an invalidation.

Classic multi-file JavaScript arrays are a separate compatibility path: Extension.js can concatenate files that lack imports/exports to preserve shared scope. Do not claim all legacy scripts require conversion just to compile. For new modular code, use the mount contract and test each group's cleanup.

## Runtime-injected entry

Put `scripts/highlight.ts` beside `package.json`, even when the manifest is under `src/`. Use the same mount contract above. Keep a static reference to the **emitted** file:

```ts
// Background module; manifest needs action and permissions: activeTab, scripting.
// action.onClicked runs only when this action has no default_popup.
chrome.action.onClicked.addListener((tab) => {
  if (tab.id === undefined) return
  void chrome.scripting.executeScript({
    target: { tabId: tab.id },
    files: ['scripts/highlight.js'],
  }).catch((error: unknown) => {
    console.error('Could not inject page helper', error)
  })
})
```

Confirm `dist/<browser>/scripts/highlight.js` exists. A root script with no recognizable reference can be dropped. Do not inject a `.ts` source URL or expect `src/scripts/` to be a special folder. If the action has a popup, run the operation from a popup control or its validated background message handler instead.

Repeated user injection is also a production concern: define whether it toggles, updates, or replaces existing UI. Test repeated invocations; do not assume a development replay helper guarantees product-level idempotence.

## Isolation and assets

Use the isolated world by default. `MAIN` shares the page's JavaScript environment and has no privileged extension APIs. A web page can observe or forge bridge traffic; `event.source === window` is not authentication. Validate origin, message shape, and allowed operations; keep privileged decisions in the background.

Extension.js may add an isolated bridge for MAIN entries, so an emitted manifest can have more entries than the source. Verify both the browser's current `world` support and this compiler's output on every target. Do not infer Firefox support from an old blanket claim in a framework guide.

Use shadow DOM for CSS isolation where appropriate, not as a security boundary. Ensure fonts/images/chunks loaded by the page are packaged and narrowly exposed through `web_accessible_resources`. Do not make every output file web-accessible to fix one missing asset.

## Verify updates

- Edit an existing entry twice: one UI instance, no duplicate subscriptions, no late async mutation after disposal.
- Navigate and revisit a matching page; confirm intended initialization and permissions.
- Change JS and CSS; verify the remount behavior independently of framework fast refresh.
- Restart dev after entry lists or special-folder structure change when diagnostics require it.
- Exercise a production build too; dev injection and replay helpers are not production behavior.

## Sources

- [Extension.js content scripts](https://extension.js.org/docs/implementation-guide/content-scripts), [special folders](https://extension.js.org/docs/features/special-folders), [reload behavior](https://extension.js.org/docs/features/reload-and-hmr)
- [Chrome content scripts](https://developer.chrome.com/docs/extensions/develop/concepts/content-scripts), [scripting API](https://developer.chrome.com/docs/extensions/reference/api/scripting), [MDN content_scripts](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/content_scripts)
