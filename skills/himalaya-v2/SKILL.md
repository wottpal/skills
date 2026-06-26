---
name: himalaya-v2
description: Use when installing, configuring, scripting, migrating, or debugging the unreleased Himalaya v2 email CLI from pimalaya/himalaya. Covers v2 command shape, TOML accounts, backend selection, JSON output, provider setup, and v1 migration pitfalls.
---

# Himalaya v2

Use this skill for Pimalaya Himalaya v2 CLI email tasks.

## Version Baseline

- Based on `himalaya 2.0.0-alpha.1` from `pimalaya/himalaya` `master` commit `f2306449278940c04768cd4ca0fa9fd7ca29c45b` (`2026-06-17`).
- The upstream README says Himalaya v2 is not released yet; latest stable release may still be v1.
- Re-check upstream before giving exact install, command, or config advice:
  - `git clone --depth 1 https://github.com/pimalaya/himalaya.git /tmp/himalaya-docs`
  - `himalaya --version`
  - `himalaya <command> --help`

## Default Workflow

1. Confirm whether the user is using v2 from `master` or stable v1.
2. Prefer `himalaya --help` / subcommand help as the command source of truth.
3. For routine mail reads, skip broad validation unless config changed: preflight any 1Password helper once, run `account list`, then `envelope list --json`, then read selected message IDs serially.
4. For scripting, pass `--json` and parse JSON instead of terminal tables.
5. For config work, edit TOML under the first active config path or pass `-c <PATH>`.
6. For backend-specific behavior, use protocol subcommands instead of forcing the shared API.
7. After source installs, verify `~/.cargo/bin` is on `PATH` and run `himalaya --version`.

## v2 Mental Model

- Shared commands are cross-backend least-common-denominator operations:
  - `mailbox` (`mailboxes` alias), `envelope` (`envelopes` alias), `flag` (`flags` alias), `message` (`messages` alias), `attachment` (`attachments` alias)
- Protocol commands expose native capabilities:
  - `imap`, `jmap`, `gmail`, `maildir`, `m2dir`, `smtp`
- `--backend <auto|imap|jmap|gmail|maildir|m2dir|smtp>` only affects shared commands.
- Account selection uses `-a/--account`; config path override uses `-c <PATH>`.
- Logs use `--log-level` / `--log`; detailed logs can go to `--log-file <PATH>`.

## High-Value Commands

```bash
# Routine reads
himalaya account list
himalaya --backend imap envelope list -m INBOX --page-size 10 --json
himalaya --backend imap message read -m INBOX 42 --json
himalaya mailbox list
himalaya envelope list -m INBOX --page 2

# Config setup/validation
himalaya account check
himalaya account configure <name>

himalaya envelope search from alice and after 2026-01-01 order by date desc
himalaya flag add -m INBOX --flag seen 1:3,5
himalaya attachment download -m INBOX 42 --dir ./attachments
```

## Non-Negotiables

- Do not assume v1 syntax works in v2. Notable changes: `--json` replaces `--output json`, `-m/--mailbox` replaces `-f/--folder`, and many protocol-specific operations moved out of the shared API.
- Do not put raw passwords or tokens in production configs; use `*.password.command`, `*.passwd.command`, or `*.token.command`.
- Do not recommend native keyring or built-in OAuth flows for v2. Use external helpers such as `mimosa`, `pass`, `gopass`, `secret-tool`, or `ortie`.
- Do not print secrets while testing secret commands. Redirect output to `/dev/null` and rely on exit status.
- For repeated 1Password-backed reads, install/preflight `op-read-cached`; never run multiple Himalaya reads in parallel unless its lock-enabled wrapper is installed and executable.
- Do not pipe an editor-driven composer directly into `himalaya message send`; use a tempfile or process substitution so `$EDITOR` keeps a real TTY.
- Remember that message IDs are mailbox/backend-specific. Use `message-id` from JSON envelope output when a stable cross-mailbox key is needed.

## Load References When Needed

- `references/himalaya-v2-guide.md` for config schemas, provider snippets, composition/reading patterns, migration notes, debugging, and upstream source links.
- `scripts/op-read-cached.sh` as a template for short-lived 1Password session reuse.
- `scripts/install-op-read-cached.sh` to install the wrapper with executable permissions.
- `scripts/message-preview.py` to extract readable text from `himalaya message read --json` without rediscovering MIME/body shapes.
