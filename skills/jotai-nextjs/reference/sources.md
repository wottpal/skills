# Sources

## Jotai docs

- https://jotai.org/docs
- https://jotai.org/docs/core/atom
- https://jotai.org/docs/core/use-atom
- https://jotai.org/docs/core/provider
- https://jotai.org/docs/core/store
- https://jotai.org/docs/guides/nextjs
- https://jotai.org/docs/utilities/ssr
- https://jotai.org/docs/utilities/storage
- https://jotai.org/docs/utilities/async
- https://jotai.org/docs/utilities/select
- https://jotai.org/docs/utilities/family
- https://jotai.org/docs/guides/migrating-to-v2-api
- https://jotai.org/docs/recipes/use-atom-effect
- https://jotai.org/docs/recipes/atom-with-debounce
- https://jotai.org/docs/recipes/large-objects
- https://jotai.org/docs/tools/swc

## Releases and versions

- https://github.com/pmndrs/jotai/releases
- https://github.com/pmndrs/jotai/releases/tag/v2.18.0
- https://github.com/pmndrs/jotai/releases/tag/v2.17.0
- https://github.com/pmndrs/jotai/releases/tag/v2.16.0
- https://www.npmjs.com/package/jotai

## Additional retrieval route used

- `mcporter` + Context7:
  - `context7.resolve-library-id`
  - `context7.query-docs`

```bash
# resolve + query via mcporter
npx -y mcporter call context7.resolve-library-id --args '{"libraryName":"jotai","query":"Next.js SSR guidance"}' --output json
npx -y mcporter call context7.query-docs --args '{"libraryId":"/pmndrs/jotai","query":"hydrate atoms in Next.js"}' --output json
```

```bash
# version verification
npm view jotai version
npm view jotai dist-tags --json
```
