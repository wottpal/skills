# Sources and verification

Checked on 2026-03-04.

## Primary sources

- `duti` repository README:
  - <https://github.com/moretension/duti>
  - <https://raw.githubusercontent.com/moretension/duti/master/README.md>
- `duti` man page (local):
  - `man duti`
- Homebrew formula (current packaged version):
  - <https://formulae.brew.sh/formula/duti>
- Apple Uniform Type Identifiers framework:
  - <https://developer.apple.com/documentation/uniformtypeidentifiers>
- Apple Support default-app behavior in Finder:
  - <https://support.apple.com/guide/mac-help/choose-an-app-to-open-a-file-on-mac-mh35597/mac>

## Quick re-check commands

```bash
brew info duti
duti -h
man duti | col -bx | sed -n '1,120p'
osascript -e 'id of app "Cursor"'
mdls -name kMDItemCFBundleIdentifier -raw "/Applications/Cursor.app"
```
