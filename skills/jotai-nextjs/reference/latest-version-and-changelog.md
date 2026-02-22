# Latest Version and Changelog Notes

Verified on 2026-02-22.

## Reference version

- npm `latest`: `2.18.0`
- npm modified timestamp: `2026-02-19T01:10:09.921Z`
- Latest GitHub release: `v2.18.0` (published 2026-02-19)

```bash
npm view jotai version
npm view jotai dist-tags --json
npm view jotai time.modified
```

## Recent release highlights

### v2.18.0

- Deprecated `jotai/babel` in favor of `jotai-babel`.
- Internal promise handling simplification.
- Reactivity fix for cross-atom `get` usage.

```diff
// babel preset migration
- "presets": ["jotai/babel/preset"]
+ "presets": ["jotai-babel/preset"]
```

### v2.17.0

- Deprecated `loadable` utility (future major cleanup signal).
- Removed `unstable_onInit` (breaking).
- Deprecated `setSelf` usage in atom read function.

### v2.16.0

- Deprecated `atomFamily` in `jotai/utils`; migration target is `jotai-family`.
- Internal store changes relevant to ecosystem tooling.

```diff
- import { atomFamily } from 'jotai/utils'
+ import { atomFamily } from 'jotai-family'
```

## Migration reminders

- Replace Babel preset/plugin imports from `jotai/babel/...` to `jotai-babel/...`.
- Prefer `jotai-family` in new code and migration PRs.
- Audit reliance on deprecated internals/utilities before v3 migration work.
