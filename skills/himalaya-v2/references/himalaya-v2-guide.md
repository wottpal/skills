# Himalaya v2 Guide

## Upstream Sources

- Repository: `https://github.com/pimalaya/himalaya`
- Primary docs: [`README.md`](https://github.com/pimalaya/himalaya/blob/master/README.md), [`MIGRATION.md`](https://github.com/pimalaya/himalaya/blob/master/MIGRATION.md), [`config.sample.toml`](https://github.com/pimalaya/himalaya/blob/master/config.sample.toml), [`ARCHITECTURE.md`](https://github.com/pimalaya/himalaya/blob/master/ARCHITECTURE.md)
- Baseline inspected: `himalaya 2.0.0-alpha.1` at commit `f2306449278940c04768cd4ca0fa9fd7ca29c45b` from `2026-06-17`
- v2 status at baseline: documented on `master`, not yet the latest stable release
- 1Password helper: `op-fast` from `https://github.com/cometkim/op-fast`; verify with `op-fast --help` because the project is young.

When exact behavior matters, refresh the upstream clone and inspect `himalaya --help` from the installed binary. The README intentionally avoids exhaustive per-command reference; generated help is canonical.

## Installation

For v2, prefer source or workflow artifacts until a v2 release exists:

```bash
cargo install --locked --git https://github.com/pimalaya/himalaya.git
```

`cargo install` places the binary under Cargo's bin directory, usually `~/.cargo/bin`. If `himalaya` is not found after a successful install, check `PATH` before reinstalling.

Verify the installed binary and compiled feature set:

```bash
himalaya --version
```

At the inspected baseline, a default source build reported:

```text
himalaya v2.0.0-alpha.1 +rustls-ring +smtp +gmail +jmap +imap +m2dir
```

Feature-limited install example:

```bash
cargo install --locked --git https://github.com/pimalaya/himalaya.git \
  --no-default-features \
  --features imap,smtp,rustls-ring
```

Package managers such as Homebrew, Scoop, distro packages, and the release installer may install stable v1 until v2 ships. Verify with `himalaya --version`.

## Config Loading

Default config search order:

- `$XDG_CONFIG_HOME/himalaya/config.toml`
- `$HOME/.config/himalaya/config.toml`
- `$HOME/.himalayarc`

Use `-c <PATH>` to override. Multiple paths can be passed with `:`; the first path is the base and later files deep-merge on top.

Run `himalaya` with no config to launch the wizard. The wizard discovers account settings with PACC, Thunderbird Autoconfiguration, then RFC 6186 SRV. Use `himalaya account configure <name>` to reconfigure or add an account later.

## TOML Shape

Accounts live under `[accounts.<name>]`. Use `default = true` for the default account. Global config and account config can both define rendering options, mailbox aliases, downloads dir, and backend blocks.

Core backend keys:

```toml
[accounts.example]
default = true

imap.server = "imaps://imap.example.com:993"
imap.sasl.plain.username = "user@example.com"
imap.sasl.plain.password.command = "pass show example"

smtp.server = "smtp://smtp.example.com:587"
smtp.starttls = true
smtp.sasl.plain.username = "user@example.com"
smtp.sasl.plain.password.command = "pass show example"

mailbox.alias.inbox = "INBOX"
mailbox.alias.sent = "Sent"
mailbox.alias.drafts = "Drafts"
mailbox.alias.trash = "Trash"
```

Secrets can be raw for local experiments, but production guidance should use command-backed secrets:

```toml
imap.sasl.plain.password.command = "pass show example"
imap.sasl.plain.password.command = ["pass", "show", "example"]
jmap.auth.bearer.token.command = ["ortie", "token", "read", "fastmail"]
gmail.auth.token.command = ["ortie", "access-token", "read", "gmail"]
```

For 1Password-backed IMAP/SMTP passwords, prefer `op-fast` over raw `op read` or custom session-token cache scripts. It caches previously fetched secrets in the OS keyring with configurable TTL and keeps the command shape close to `op`.

Verify or install:

```bash
command -v op-fast >/dev/null || brew install cometkim/tap/op-fast
op-fast --version
```

For one configured 1Password account:

```toml
imap.sasl.plain.password.command = [
  "op-fast",
  "read",
  "--no-newline",
  "op://Private/Email/password",
]

smtp.sasl.plain.password.command = [
  "op-fast",
  "read",
  "--no-newline",
  "op://Private/Email/password",
]
```

For multiple 1Password accounts, set `OP_ACCOUNT` through `/usr/bin/env`. At `op-fast 0.1.1`, `read` supports `--no-newline` but not `--account` directly:

```toml
imap.sasl.plain.password.command = [
  "/usr/bin/env",
  "OP_ACCOUNT=example.1password.com",
  "/opt/homebrew/bin/op-fast",
  "read",
  "--no-newline",
  "op://Private/Email/password",
]

smtp.sasl.plain.password.command = [
  "/usr/bin/env",
  "OP_ACCOUNT=example.1password.com",
  "/opt/homebrew/bin/op-fast",
  "read",
  "--no-newline",
  "op://Private/Email/password",
]
```

Smoke-test without leaking the secret:

```bash
OP_ACCOUNT=example.1password.com op-fast read --no-newline "op://Private/Email/password" >/dev/null
```

Optional `op-fast` cache tuning lives at `~/.config/op-fast/config.toml`:

```toml
default_ttl = "1day"

[ttl]
"op://Private/Email/*" = "12h"
```

Use `op-fast store list`, `op-fast store clear "op://..."`, or `op-fast store clear` when cached values need inspection or invalidation. Do not create local session-token cache scripts.

Mailbox aliases are case-insensitive. The `inbox` alias is the implicit default for shared commands when `-m/--mailbox` is omitted. Account-level aliases override global aliases.

## Provider Notes

Gmail over IMAP/SMTP:

- Use an app password for SASL PLAIN when using IMAP/SMTP.
- Gmail labels appear as IMAP mailboxes; quote names like `[Gmail]/Drafts` in shells or define aliases.
- Gmail's all-mail archive is typically `[Gmail]/All Mail`.

Gmail REST API backend:

- Configure `gmail.auth.token.command`; Himalaya does not refresh tokens itself.
- Select via shared commands with `--backend gmail`, or use the native `gmail` command.

Outlook:

- Basic authentication is retired. Use OAuth through `oauthbearer` or `xoauth2` with an external token helper such as `ortie`.

iCloud Mail:

- Use an app-specific password.
- IMAP username is commonly the local part of the iCloud address; SMTP username is the full address.

Proton Mail:

- Run Proton Bridge and point IMAP/SMTP at the local Bridge endpoints.
- Use the Bridge-generated password, not the Proton account password.

JMAP:

- `jmap.server` can be a bare host for discovery or a full session URL.
- Choose exactly one auth style: `header`, `bearer`, or `basic`.
- JMAP sending needs `jmap.identity-id` and `jmap.drafts-mailbox-id`; discover them with `himalaya jmap identity get` and `himalaya jmap mailboxes query --role drafts`.

## Shared Commands

Shared commands map to IMAP, JMAP, Gmail, Maildir, m2dir, or SMTP only when the operation is supported by that backend.

```bash
himalaya --backend imap mailbox list
himalaya mailbox list
himalaya envelope list -m INBOX
himalaya envelope search from alice and after 2026-01-01 order by date desc
himalaya flag set -m INBOX --flag seen --flag flagged 42
himalaya message copy --from INBOX --to Archive 42
himalaya message move --from INBOX --to Trash 42
himalaya attachment list -m INBOX 42
himalaya attachment download -m INBOX 42 --dir ./attachments
```

`envelope search` uses Himalaya's query DSL, not Gmail's native query language. Backends may reject unsupported clauses. At the inspected baseline, IMAP search uses server-side `UID SORT`, so servers without SORT may reject it.

## Protocol Commands

Use protocol commands when the shared API is too narrow:

```bash
himalaya imap mailbox select INBOX
himalaya imap mailbox status INBOX
himalaya imap mailbox subscribe INBOX

himalaya jmap mailboxes query --role drafts
himalaya jmap identity get
himalaya jmap vacation get

himalaya gmail profile get
himalaya gmail labels list
himalaya gmail messages list

himalaya maildir list
himalaya maildir create Archive
himalaya m2dir list

himalaya smtp messages send < message.eml
```

Protocol commands ignore `--backend`.

## Composing and Sending

Simple messages can use built-in flags:

```bash
himalaya message compose \
  --from me@example.org \
  --to you@example.org \
  --subject "Hello" \
  --body "Hi!" \
  --send
```

For richer MIME, editor-driven composition, signing, encryption, replies, and forwards, use `mml` or another standalone composer and feed the resulting RFC 5322 message to Himalaya.

Good patterns:

```bash
mml compose /tmp/draft.eml && himalaya message send /tmp/draft.eml
mml compose >(himalaya message send)
himalaya message read 42 | mml reply >(himalaya message send)
himalaya message add -m drafts --flag draft < message.eml
himalaya message send --save sent < message.eml
```

Avoid:

```bash
mml compose | himalaya message send
```

That shape can hang because an editor inherits a pipe instead of a terminal.

## Reading and Scripting

```bash
himalaya --backend imap envelope list -m INBOX --page-size 10 --json
himalaya --backend imap message read -m INBOX 42 --json
himalaya --backend imap message read -m INBOX 42 --raw
```

Reading is side-effect-free: it should not mark messages as seen. Mark explicitly:

```bash
himalaya flag add -m INBOX --flag seen 42
```

For scripts, prefer `--json`. Envelope JSON includes IDs, stable `message-id`, flags, subject, addresses, date, size, and attachment presence.

Fast latest-email workflow:

1. Run `himalaya account list` to identify the configured account/backends.
2. If config uses 1Password, verify `op-fast` is installed before the first network command.
3. Preflight the secret reference once with output redirected to `/dev/null`; this is where the user should see any 1Password approval prompt.
4. If the account is known-good, skip `account check`; it opens network/auth paths and can trigger secret prompts.
5. List the latest envelopes with a small `--page-size` and `--json`.
6. Deduplicate obvious notification clusters by sender/subject before reading bodies.
7. Read selected message IDs serially with `message read --json`; avoid unnecessary parallel reads when 1Password approval is still pending.
8. Pipe message JSON into `scripts/message-preview.py` for body previews instead of writing new ad hoc `jq`/HTML-stripping commands each time.

Preview helper example:

```bash
himalaya -a example --backend imap message read -m INBOX 42 --json \
  | python3 /path/to/himalaya-v2/scripts/message-preview.py --chars 3000 --urls
```

The helper handles top-level `text_body` / `html_body` values plus MIME `parts[].body.Text` / `parts[].body.Html`, including string arrays and HTML-heavy notifications.

## Debugging

Use:

```bash
himalaya --log trace mailbox list
himalaya --log trace --log-file /tmp/himalaya.log mailbox list
RUST_BACKTRACE=1 himalaya --log debug account check
NO_COLOR=1 himalaya mailbox list
```

Logs are for diagnostics. Structured command results should come from stdout with `--json`.

## Setup Validation

After creating or editing config, validate in increasing scope:

```bash
himalaya account list
himalaya account check
himalaya mailbox list
himalaya --backend imap envelope list --mailbox INBOX --page-size 5
```

If account checks hang or prompt, suspect a locked secret provider such as 1Password rather than immediately changing the Himalaya config. Preflight `op-fast`, unlock or approve the provider, then rerun the same command.

For routine inbox reads, avoid `account check`: it tests every matching backend and can invoke the secret command for both IMAP and SMTP before doing any useful mail read.

## v1 to v2 Migration Checklist

- Replace `--output json` with `--json`.
- Replace `--folder` / `-f` with `--mailbox` / `-m`.
- Rename folder concepts to mailbox concepts.
- Use `envelope search` for filtered searches; do not rely on v1 `list` search behavior.
- Use protocol commands for mailbox create/delete/expunge/purge or other backend-native operations.
- Replace native keyring config with command-backed secrets.
- Replace built-in OAuth flow expectations with external token helpers.
- Replace interactive template/composer assumptions with `mml` or another external composer.
- Use `message add` for inserting/saving raw messages; `save` is only an alias.
- Treat Notmuch and Sendmail backends as removed in v2.
- Use `sirup` when repeated IMAP/SMTP invocations need session reuse.
