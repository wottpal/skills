# Core, Utilities, and Recipes

## Core APIs

- `atom` defines immutable atom configs; values live in stores.
- Keep atom identity stable (`useMemo`/`useRef` if created dynamically in render).
- `useAtom` reads and writes; `useAtomValue` read-only; `useSetAtom` write-only (useful to avoid read-driven rerenders).
- `Provider` creates store scope; nested providers are supported.
- `createStore` and `getDefaultStore` expose direct store operations (`get`, `set`, `sub`).

```tsx
const baseAtom = atom(1)
const doubledAtom = atom((get) => get(baseAtom) * 2)
const dynamicAtom = useMemo(() => atom(props.initial), [props.initial])
```

## Utility APIs

### `storage`

- `atomWithStorage` persists via `localStorage`, `sessionStorage`, or custom storage.
- `getOnInit: true` reads stored value on initialization instead of showing `initialValue` first.
- Use `createJSONStorage` for custom serialization or storage backends.
- Use `RESET` to remove or reset persisted keys.

```ts
const themeAtom = atomWithStorage<'light' | 'dark'>(
  'theme',
  'light',
  undefined,
  { getOnInit: true },
)
```

### `resettable`

- `atomWithReset`, `RESET`, `useResetAtom`, `atomWithDefault`, `atomWithRefresh`.

```tsx
const countAtom = atomWithReset(0)
const resetCount = useResetAtom(countAtom)
resetCount()
```

### `select`

- `selectAtom` is an escape hatch for slice + equality behavior.
- Keep base atom and selector reference stable to avoid loops.
- Prefer pure derived atoms when possible.

```tsx
const sliceAtom = useMemo(
  () => selectAtom(stateAtom, (s) => s.user, Object.is),
  [stateAtom],
)
```

### `async`

- `loadable`, `unwrap`, and `atomWithObservable` are available utilities.
- `unwrap` is useful for deriving from async atoms when sync output is needed.
- Recent releases mark `loadable` as deprecated for future major versions; plan migrations conservatively.

```ts
const asyncUserAtom = atom(async () => fetch('/api/user').then((r) => r.json()))
const safeUserAtom = unwrap(asyncUserAtom, (prev) => prev ?? null)
```

### `family`

- `atomFamily` in `jotai/utils` is deprecated and planned to be removed in v3.
- Migrate to `jotai-family` (same API shape, additional capabilities like `atomTree`).
- Manage cache lifecycle (`remove`, `setShouldRemove`) to avoid memory leaks.

```ts
import { atomFamily } from 'jotai-family'
const todoAtomFamily = atomFamily((id: string) => atom({ id, done: false }))
```

## Recipes worth using

### `useAtomEffect`

- Runs side effects via `atomEffect`.
- Memoize effect functions with stable callbacks/memo helpers to avoid unnecessary recomputation.

```tsx
useAtomEffect(
  useStableCallback((get) => {
    console.log('count', get(countAtom))
  }, []),
)
```

### `atomWithDebounce`

- Useful for delayed update flows (search/query typing).
- Do not expose mutable internal state atom directly; keep consistency between current and debounced values.
- This is not a replacement for React concurrent rendering primitives.

```ts
const { currentValueAtom, debouncedValueAtom } = atomWithDebounce('', 300)
```

### Large objects strategy

- Use `focusAtom` (optics) to target nested writable slices.
- Use `splitAtom` for list-to-atom-per-item decomposition.
- Use `selectAtom` for read-only slices with custom equality behavior.

```ts
const peopleAtom = focusAtom(dataAtom, (o) => o.prop('people'))
const personAtomsAtom = splitAtom(peopleAtom)
const tagsAtom = selectAtom(infoAtom, (i) => i.tags)
```
