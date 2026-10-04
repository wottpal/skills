# MV3 runtime

## Assign responsibilities

| Context | Appropriate work | Constraint |
| --- | --- | --- |
| Background | Privileged API calls, coordination, event handling | Chromium MV3 service workers can stop; no DOM |
| Content script | Page DOM, feature UI, observations | Page-derived data is untrusted; APIs and host access are limited |
| Popup | Short user interactions | Closing it destroys its state and pending work |
| Options/sidebar/new tab | Longer-lived extension UI | Still not durable background state |
| Offscreen document | A supported Chrome DOM-only background task | Requires permission/reason and lifecycle management; not a cross-browser worker replacement |

Register browser event listeners synchronously at module scope. Load settings inside handlers, or await a shared initialization Promise inside them. Do not wait for storage before registering listeners. Globals are only caches; rebuild them after a worker restart and invalidate them on storage changes.

Use persisted state for resumable work. Prefer `chrome.alarms` for scheduled background work, not a timer intended to outlive the worker. Avoid artificial keepalive loops. Close worker DevTools when testing suspension because debugging can alter its lifetime.

Chrome 120+ supports a 30-second minimum alarm interval; alarms can be delayed and are not exact timers. Check required alarms on startup and recreate missing ones. Persistence and newer options are version-dependent: consult the current API rather than assuming either guaranteed persistence or guaranteed loss on restart.

## Messages are an input boundary

Use a small, discriminated, JSON-safe protocol and validate it at runtime. Check the sender and scope each operation; TypeScript types do not validate messages. For privileged fetches, select an allowlisted endpoint in the background rather than accepting arbitrary page-provided URLs, headers, or commands.

Example for a harmless settings read from this extension, with `storage` permission:

```ts
chrome.runtime.onMessage.addListener((message: unknown, sender, sendResponse) => {
  if (sender.id !== chrome.runtime.id) return
  if (typeof message !== 'object' || message === null) return
  if (!('type' in message) || message.type !== 'settings:get') return

  void chrome.storage.local.get('enabled').then(
    ({ enabled }) => sendResponse({ ok: true, enabled: enabled === true }),
    () => sendResponse({ ok: false, error: 'storage-unavailable' }),
  )
  return true
})
```

Keep that listener non-`async`: literal `true` holds the callback response channel open. Return nothing for messages it does not handle. A same-extension sender check is only the first gate; sensitive operations also need context/tab/origin validation and explicit allowed parameters.

Current Chrome docs describe Promise-returning listeners from Chrome 148 with rollout and DevTools-extension caveats. Use that form only for a verified supported baseline/polyfill. Do not combine Promise return and `sendResponse` for the same response. Handle rejected Promise APIs with `try/catch`; inspect `chrome.runtime.lastError` **inside callbacks** when using callback APIs.

Use one-shot messages for isolated requests and ports for real ongoing conversations, with disconnect handling. Do not keep a port open just to defeat worker suspension or broadcast every update to every tab.

## Storage and synchronization

- `storage.local`: persistent device state and bounded caches.
- `storage.sync`: small preferences subject to per-item, total-size, and write-rate limits.
- `storage.session`: in-memory session state that survives worker suspension, not browser restart or extension reload/update; check target support and access level.
- IndexedDB: larger structured data; plan schema changes and bounds.

Use the `storage` permission, batch related reads/writes, catch quota failures, and invalidate caches with `storage.onChanged`. Concurrent read-modify-write sequences are not transactions; centralize writes or use a transactional store for counters and multi-step invariants. Initialize defaults only when absent and migrate stored data deliberately on update.

Restrict access to sensitive storage areas where supported. None of these APIs makes hardcoded credentials secret from the user. Avoid storing large binary payloads in sync storage.

## Permissions, network, and performance

Request only permissions needed by the chosen surfaces. `activeTab` is a temporary user-gesture grant; automatic cross-origin work may require narrow `host_permissions` or runtime optional permissions. A background fetch with host access and a content-script fetch have different cross-origin rules.

Use `declarativeNetRequest` for supported request-blocking/modification rules. Do not replace observational `webRequest` use blindly or assume every browser has the same DNR limits. Bundle executable code locally for MV3; do not load remote JavaScript or relax CSP as a shortcut.

Keep page-derived text out of unsafe HTML insertion. Validate URLs and protocol choices before navigation. Bound caches and message payloads, batch DOM reads/writes, and use observers for meaningful DOM changes with explicit disconnect cleanup. Keep heavy UI dependencies out of a small content script unless the feature needs them.

## Platform review checklist

Test worker restart, popup close/reopen, missing receiver, navigation, malformed messages, permission denial, storage failure, and repeated content injection. Mock pure boundary logic where useful, then validate browser behavior with real installed output. Mock success does not prove lifecycle, permission, or manifest correctness.

## Sources

- [Worker lifecycle](https://developer.chrome.com/docs/extensions/develop/concepts/service-workers/lifecycle), [worker migration](https://developer.chrome.com/docs/extensions/develop/migrate/to-service-workers), [alarms](https://developer.chrome.com/docs/extensions/reference/api/alarms)
- [Messaging](https://developer.chrome.com/docs/extensions/develop/concepts/messaging), [storage](https://developer.chrome.com/docs/extensions/reference/api/storage), [offscreen](https://developer.chrome.com/docs/extensions/reference/api/offscreen)
- [Cross-origin requests](https://developer.chrome.com/docs/extensions/develop/concepts/network-requests), [permissions](https://developer.chrome.com/docs/extensions/develop/concepts/declare-permissions), [DNR](https://developer.chrome.com/docs/extensions/reference/api/declarativeNetRequest), [MV3 remote code](https://developer.chrome.com/docs/extensions/develop/migrate/remote-hosted-code)
