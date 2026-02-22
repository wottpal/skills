# Next.js + Jotai SSR Playbook

## Objective

Set up Jotai in Next.js without request leakage, hydration bugs, or unstable atom identity.

## Core setup

- Mount `<Provider>` at the app root (or scoped subtree) in SSR apps.
- Do not rely on provider-less mode for server-rendered apps.
- Use `createStore` when you need an explicit store boundary (tests, isolated subtrees, outside-React mutations).

```tsx
// app/layout.tsx
import { Providers } from './providers'
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body><Providers>{children}</Providers></body>
    </html>
  )
}
```

## Hydration pattern

- `useHydrateAtoms` is a client-side hook; place it in a client component.
- Pass iterable tuples (or `Map`) of `[atom, value]`.
- Atoms hydrate once per store. Value changes on rerender do not re-hydrate unless forced.
- `dangerouslyForceHydrate` exists but can behave poorly with concurrent rendering; avoid unless unavoidable.

```tsx
'use client'
import { atom } from 'jotai'
import { useHydrateAtoms } from 'jotai/utils'
const userAtom = atom<{ id: string } | null>(null)
export function HydrateUser({ user }: { user: { id: string } }) {
  useHydrateAtoms([[userAtom, user]])
  return null
}
```

## Async on SSR

- Avoid unresolved promises on server render paths.
- Prefer fetching on the server and hydrating into atoms on the client.
- If atom read can run in SSR and CSR, guard SSR paths to avoid returning unresolved promises on the server.

```ts
const dataAtom = atom((get) => {
  const prefetched = get(prefetchedAtom)
  if (typeof window === 'undefined') return prefetched
  return prefetched ?? fetch('/api/data').then((r) => r.json())
})
```

## Router sync caveat

- `atomWithHash` can sync URL hash state.
- In Next.js 13+ App Router, routing event behavior changed; hash-based atoms may not load as expected during client-side navigation.
- If using hash sync, validate navigation behavior and prefer `replaceState` style updates where needed.

## Storage + SSR

- `atomWithStorage` uses `initialValue` on server render.
- If stored client value differs, initial HTML may mismatch during hydration.
- For UI that depends on stored value (`className`, theme, etc.), render client-only or expect a temporary visual swap.

```tsx
'use client'
const mounted = useMounted() // custom hook with useEffect(() => setMounted(true), [])
if (!mounted) return null
return <ThemeDependentUI />
```
