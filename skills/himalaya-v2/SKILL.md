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
3. For routine mail reads, skip broad validation unless config changed: preflight `op-fast` once for 1Password-backed configs, run `account list`, then `envelope list --json`, then read selected message IDs serially.
4. For scripting, pass `--json` and parse JSON instead of terminal tables.
5. For config work, edit TOML under the first active config path or pass `-c <PATH>`; quote account table keys when they contain full emails, e.g. `[accounts."dennis@example.com"]`.
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

## Mail Safety Guardrails

- Treat Himalaya as read-only by default. Safe commands without extra approval: `account list`, `mailbox list`, `envelope list/search --json`, `message read --json/--raw`, and `attachment list`.
- If account or mailbox scope is unclear, list available options first, then use `functions.request_user_input` when available. Offer concrete accounts plus `All accounts` for read-only requests when applicable; do not offer `All accounts` for writes unless the user explicitly says all.
- Use this picker shape; recommended option first, label suffixed with `(Recommended)`, no `selected` field, and no `autoResolutionMs` when the answer gates a write/destructive action:

```json
{
  "questions": [
    {
      "header": "Account",
      "id": "account_scope",
      "question": "Which email account should I use?",
      "options": [
        {
          "label": "zoma (Recommended)",
          "description": "Use the default configured account only."
        },
        {
          "label": "All accounts",
          "description": "Search/read across every configured account."
        }
      ]
    }
  ],
  "autoResolutionMs": 60000
}
```

- For mailbox ambiguity, use the same shape with `header: "Mailbox"` and options from `himalaya -a <account> mailbox list`; include `All mailboxes` only for read-only requests.
- Before any remote write, preview the account, mailbox, message IDs/count, senders/subjects/dates, exact operation, and exact command shape; wait for explicit approval in the current turn.
- Remote writes include send, move, copy, delete, flag changes, mailbox create/delete, expunge/purge, attachment downloads, and config edits.
- Before irreversible actions such as permanent delete, expunge, or purge, back up raw target messages plus envelope metadata under `/tmp/himalaya-backups/<timestamp>-<account>-<mailbox>/`; if backup fails, abort.
- Never run broad write selectors such as `all`, `1:*`, or unbounded search results. Narrow writes to reviewed message IDs.
- Never auto-send generated mail. Compose to a draft/tempfile, show headers and a concise body summary, then send only after explicit approval.

## Non-Negotiables

- Do not assume v1 syntax works in v2. Notable changes: `--json` replaces `--output json`, `-m/--mailbox` replaces `-f/--folder`, and many protocol-specific operations moved out of the shared API.
- Do not write full-email account table names as bare TOML keys. `[accounts.dennis@example.com]` is invalid; use `[accounts."dennis@example.com"]`, then select it with `-a 'dennis@example.com'`.
- Do not put raw passwords or tokens in production configs; use `*.password.command`, `*.passwd.command`, or `*.token.command`.
- Do not recommend native keyring or built-in OAuth flows for v2. Use external helpers such as `mimosa`, `pass`, `gopass`, `secret-tool`, `ortie`, or `op-fast`.
- Do not print secrets while testing secret commands. Redirect output to `/dev/null` and rely on exit status.
- For repeated 1Password-backed reads, use `op-fast`; do not add custom session-token cache scripts.
- Do not pipe an editor-driven composer directly into `himalaya message send`; use a tempfile or process substitution so `$EDITOR` keeps a real TTY.
- Remember that message IDs are mailbox/backend-specific. Use `message-id` from JSON envelope output when a stable cross-mailbox key is needed.

## Load References When Needed

- `references/himalaya-v2-guide.md` for config schemas, provider snippets, composition/reading patterns, migration notes, debugging, and upstream source links.
- `scripts/message-preview.py` to extract readable text from `himalaya message read --json` without rediscovering MIME/body shapes.
