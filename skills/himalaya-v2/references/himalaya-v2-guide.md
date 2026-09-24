# Himalaya v2 guide

## Verified baseline and source hierarchy

Verified **2026-09-24** against the official **v2.1.0** release binary (`ca88bee08ad2e92127b46dc6200d1e8201885156`, released 2026-08-16), its command help, tagged source, and synthetic Maildir messages. The installed `himalaya` may still be an alpha; check its version before applying these examples.

Primary references:

- [Latest release](https://github.com/pimalaya/himalaya/releases/latest) for installation freshness.
- [v2.1.0 release notes](https://github.com/pimalaya/himalaya/releases/tag/v2.1.0) and [migration guide](https://github.com/pimalaya/himalaya/blob/v2.1.0/MIGRATION.md).
- Tagged [CLI](https://github.com/pimalaya/himalaya/blob/v2.1.0/src/cli.rs), [config sample](https://github.com/pimalaya/himalaya/blob/v2.1.0/config.sample.toml), and [feature declarations](https://github.com/pimalaya/himalaya/blob/v2.1.0/Cargo.toml).
- Shared [read](https://github.com/pimalaya/himalaya/blob/v2.1.0/src/shared/message/read.rs), [delete](https://github.com/pimalaya/himalaya/blob/v2.1.0/src/shared/message/delete.rs), [backend dispatch](https://github.com/pimalaya/himalaya/blob/v2.1.0/src/shared/client.rs), and [envelope JSON fields](https://github.com/pimalaya/himalaya/blob/v2.1.0/src/email/envelope.rs).

Prefer help from the actual binary and registered command definitions over old README snippets or unused source files. For example, some documentation still describes a printing-only wizard, while v2.1.0's wizard writes the config; native IMAP commands are flat despite old `imap/mailbox/` source paths. Do not assume unreleased `master` features (such as newer protocol additions) are available in a stable build.

## Installation and feature selection

v2 is released. Prefer the current stable release appropriate for the platform; package-manager versions can lag. Check the [official installation instructions](https://github.com/pimalaya/himalaya#installation), release notes, and the installed version before choosing a method. Avoid an unpinned development-branch install as the default recommendation.

For a reproducible source build of the verified baseline:

```bash
cargo install --locked --git https://github.com/pimalaya/himalaya.git --tag v2.1.0
```

Refresh the tag for a newer verified release when appropriate. Feature-limited builds can append `--no-default-features --features imap,smtp,rustls-ring`. Verify the Rust version required by that tag. Cargo normally writes to `~/.cargo/bin`; inspect `command -v himalaya` and `himalaya --version` to detect an older binary earlier on PATH before reinstalling.

The v2.1.0 default release includes IMAP, JMAP, Gmail, Microsoft Graph, Maildir, m2dir, pimdir, and SMTP with rustls-ring. `--backend` selects a backend only for shared commands. Native commands always address their own protocol. Pimdir is a shared backend over the sync engine's local store, not a `himalaya pimdir` command; writes there stage replica mutations that can later sync.

## Config loading and wizard

`-c/--config` overrides `HIMALAYA_CONFIG` in v2.1.0. With neither supplied, the documented default search order is:

1. `$XDG_CONFIG_HOME/himalaya/config.toml`
2. `$HOME/.config/himalaya/config.toml`
3. `$HOME/.himalayarc`

Multiple paths use a colon delimiter; the first is the base, and later files deep-merge over it. Track the active paths before editing, since an overlay can override the base file.

`himalaya configure` (alias `wizard`) runs interactive discovery and writes/appends the chosen account to the configured file. Discovery can probe remote services and prompt for credentials. A bare first-run invocation can offer the wizard when interactive; scripts must use explicit commands, an existing config, and JSON where needed. `account list` and `account check` inspect existing accounts; stable v2.1.0 has no `account configure` subcommand. Inspect the result of wizard output and account names instead of assuming `-a` renames an existing account.

Accounts use `[accounts.<name>]`; quote full email names. Account settings inherit global defaults, then override them. A minimal IMAP/SMTP example (replace all provider values):

```toml
[accounts."person@example.com"]
default = true
email = "person@example.com"
display-name = "Example Person"

imap.server = "imaps://imap.example.com:993"
imap.sasl.plain.username = "person@example.com"
imap.sasl.plain.password.command = ["pass", "show", "mail/example"]

smtp.server = "smtp://smtp.example.com:587"
smtp.starttls = true
smtp.sasl.plain.username = "person@example.com"
smtp.sasl.plain.password.command = ["pass", "show", "mail/example"]

mailbox.alias.inbox = "INBOX"
mailbox.alias.sent = "Sent"
mailbox.alias.drafts = "Drafts"
mailbox.alias.trash = "Trash"
```

Mailbox aliases are case-insensitive. With no `-m`, current shared commands require the configured inbox alias; do not assume every provider has an `INBOX` default. Prefer explicit mailbox scope. v2.1.0 supports `email`, `display-name`, `signature`, and `signature-delim` at global/account level; do not copy earlier migration advice that removed all identity fields.

## Secrets and provider differences

Use one secret-command assignment per field; examples below are alternatives, not duplicate keys in one table. Never print its returned value during a check.

Current [Ortie](https://github.com/pimalaya/ortie) uses `token show` with account selection:

```toml
jmap.auth.bearer.token.command = ["ortie", "token", "show", "-a", "fastmail"]
gmail.auth.token.command = ["ortie", "token", "show", "-a", "gmail"]
msgraph.auth.token.command = ["ortie", "token", "show", "-a", "msgraph"]
```

Himalaya delegates token acquisition/refresh to the external helper. Verify the installed helper's `--help`; the older `ortie token read` and `ortie access-token read` forms are not current guidance.

For existing 1Password-backed setups, retain [op-fast](https://github.com/cometkim/op-fast), which caches secret values in the OS keyring. Check `op-fast --version` and `op-fast read --help`; do not install or change a secret helper merely to inspect mail. At the locally verified 0.1.1 CLI, `read` accepts `--no-newline` but no direct `--account`; select through `OP_ACCOUNT`:

```toml
imap.sasl.plain.password.command = [
  "/usr/bin/env", "OP_ACCOUNT=example.1password.com",
  "op-fast", "read", "--no-newline", "op://Private/Email/password",
]
```

Use an absolute helper path only when the environment requires it, and discover that path rather than assuming `/opt/homebrew/bin`. If auth needs troubleshooting, preflight the configured reference once:

```bash
OP_ACCOUNT='example.1password.com' op-fast read --no-newline 'op://Private/Email/password' >/dev/null
```

On secret rotation, invalidate only the relevant cached reference using the installed helper's supported command. Do not clear the entire cache or create custom session-token files as a routine repair.

Provider notes, grounded in the [tagged config](https://github.com/pimalaya/himalaya/blob/v2.1.0/config.sample.toml) and [provider examples](https://github.com/pimalaya/himalaya/blob/v2.1.0/README.md#configuration):

- **Gmail:** IMAP/SMTP password auth normally needs an eligible app password, not the account password. OAuth is an alternative; the REST backend uses `gmail.auth.token.command`. Labels and localized special mailbox names must be discovered, not assumed. Native `gmail messages list -q '...'` accepts Gmail query syntax.
- **Outlook/Microsoft 365:** use OAuth with IMAP/SMTP or `msgraph.auth.token.command` for Microsoft Graph. Verify account/tenant permissions and available protocols; do not fall back to basic authentication.
- **iCloud:** use an app-specific password and the provider's documented IMAP/SMTP usernames, which can differ.
- **Proton:** use Bridge's local endpoints, generated password, and certificate configuration. Do not substitute the Proton account password or disable certificate checks as a quick fix.
- **JMAP/Fastmail:** configure `jmap.server` and exactly one auth style (`header`, `bearer`, or `basic`). JMAP sending requires `jmap.identity-id` and `jmap.drafts-mailbox-id`; inspect `jmap identity get` and `jmap mailbox query --role drafts` for discovery.

## Current command shapes

Use the chosen account and relevant mailbox on actual operations. These read-oriented examples use the placeholder account `example`:

```bash
himalaya -a 'example' imap status 'INBOX'
himalaya -a 'example' jmap mailbox query --role drafts
himalaya -a 'example' jmap identity get
himalaya -a 'example' gmail profile get
himalaya -a 'example' gmail labels list
himalaya -a 'example' gmail messages list -q 'from:alice is:unread'
himalaya -a 'example' msgraph mail-folders list
himalaya -a 'example' maildir list
```

In v2.1.0, IMAP is flat: `imap select`, `imap status`, `imap fetch`, `imap expunge`, etc. `imap mailbox ...` is obsolete. SMTP uses `smtp send`, not `smtp messages send`. JMAP uses singular `mailbox`. Check each command's help instead of extrapolating aliases.

Shared `envelope list` orders by date descending and paginates from page 1. Shared `envelope search` has its own DSL; Gmail/Graph require native queries instead. IMAP can fall back to client-side sorting when SORT is unavailable (`imap.sort.fallback` overrides detection); do not repeat the alpha-era claim that all servers must support UID SORT. Avoid unbounded body searches when metadata filters suffice.

## JSON and identifiers

Envelope JSON is `{ "envelopes": [...] }`. Shared fields use kebab-case, including `message-id`, `in-reply-to`, and `has-attachment`; inspect actual JSON before scripting. Message-ID headers are correlation hints, not unique backend IDs. IMAP UIDs can change after mailbox recreation or a move; native `--seq` selectors are sequence numbers and can shift after expunge.

Parsed `message read --json` returns a mail-parser message object: `text_body` / `html_body` contain **zero-based indexes into `parts`**, whose bodies include `Text`, `Html`, `Multipart`, and attachment variants. The attachment CLI's displayed part IDs are **one-based MIME positions** in v2.1.0 and can have gaps. They are distinct from the message's own backend ID.

`message read --raw` writes RFC 5322 bytes. In v2.1.0 it can combine with `--json`, producing `{ "message": "raw RFC 5322 text" }`; the older alpha rejected that combination. Use raw output for backups, and parsed JSON for the preview helper. [Verification](verification.md) documents supported input shapes and preview limits.

## Prepare, authorize, then mutate

The main skill defines authorization and backup requirements. Example command shapes below are for already reviewed, authorized targets; they are not routine verification commands:

```bash
himalaya -a 'example' --backend imap flag add -m 'INBOX' --flag seen '42'
himalaya -a 'example' --backend imap message move --from 'INBOX' --to 'Archive' '42'
himalaya -a 'example' --backend imap message delete -m 'INBOX' '42'
himalaya -a 'example' --backend imap attachment download -m 'INBOX' '42' '3' --dir '/agreed/output/directory'
```

`message delete` resolves the backend's native trash first, then the configured trash alias, and errors if neither is available. Outside trash it moves; inside trash it attempts permanent removal. Read its JSON `action` (`moved-to-trash`, `deleted`, or `flagged`) and `count`. An IMAP server without UIDPLUS can leave messages flagged pending an expunge; do not escalate to a mailbox-wide expunge without authorization for every affected message. Local pimdir mutations can propagate during sync.

Compose to a private, unique draft path without sending:

```bash
umask 077
draft_file="$(mktemp '/tmp/himalaya-draft.XXXXXX')"
himalaya -a 'example' message compose \
  --from 'me@example.org' --to 'you@example.org' \
  --subject 'Hello' --body 'Hi!' > "$draft_file"
```

Check the compose command's exit status and inspect the entire draft before sending. Composing may initialize configured backends; it is not a promise of zero network activity. For rich MIME or editor use, a standalone composer can write the draft file with a real TTY. Never pipe or use process substitution directly into a sender during draft preparation.

After the exact recipients/content and send operation are authorized:

```bash
himalaya -a 'example' message send "$draft_file"
```

`--save '<mailbox>'` explicitly requests a stored copy. v2.1.0 saves before sending when both are requested; a send failure can leave a saved copy. A timeout can also leave delivery uncertain. Inspect the outcome before retrying to avoid duplicate sends/copies. Native SMTP additionally requires envelope addresses (`smtp send --mail-from ... --rcpt-to ...`), independently of RFC 5322 headers.

## Validation, diagnostics, and migration

After an authorized config change, start with `account list --json` to check loading. Then run `himalaya -a '<account>' --backend '<backend>' account check` only when that connection check is needed; it can prompt for secrets and contact services. Finish with a bounded mailbox/envelope read. Do not use all-account checks for routine inbox reads.

Use `--log debug` or `--log trace` only for a concrete issue. Logs go to stderr unless `--log-file` is set; store them privately, redact mail/auth details, and avoid printing secret-command output. `NO_COLOR=1` controls colors. Do not redirect errors away merely to make a failed operation appear successful.

Migration reminders:

- v1 `--output json` becomes `--json`; `--folder/-f` becomes `--mailbox/-m`; filtered searches use `envelope search`.
- Stable v2.1.0 uses top-level `configure`, flat native IMAP, and `smtp send`; check alpha syntax against the actual binary.
- Use external OAuth/secret helpers instead of v1 built-in OAuth or native keyring assumptions.
- `message add` inserts raw mail; `save` is an alias. Notmuch and Sendmail were removed; use supported backends.
- Do not remove v2.1 identity/signature fields based on an old migration note. Never migrate the live config or replace the binary without task authorization.
