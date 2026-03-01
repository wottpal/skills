---
name: slack-web-api
description: Use when you need to read or act on Slack data via the Slack Web API (post messages, search, list channels, fetch channel history/threads, add/remove reactions). Provides a Bun+TypeScript CLI wrapper around @slack/web-api for deterministic queries and structured JSON output.
---

# Slack Web API Skill

Use the bundled Bun+TypeScript CLI wrapper to call Slack Web API methods with a bot token.

## Preconditions

- Ensure `SLACK_TOKEN` is set in the shell environment.
- Run the script from this repo (uses the local `@slack/web-api` dependency).

## CLI Wrapper (Bun + TS)

Script: `scripts/slack_web_api.ts`

Commands:

- `list_channels`
- `post`
- `post_table`
- `delete`
- `search`
- `channel_history`
- `thread`
- `reactions_add`
- `reactions_remove`

Optional flags:

- `--resolve_users true` to add `user_name` fields
- `--include_threads true` to embed full thread replies in `channel_history`
- `post` supports rich message inputs:
  - `--text_file` for multiline body from file
  - `--unescape_text true` to convert `\n`/`\t` escapes in `--text` into actual newlines/tabs
  - `--blocks_json` / `--blocks_file` for Block Kit
  - `--attachments_json` / `--attachments_file` for legacy attachments
  - `--thread_ts`, `--reply_broadcast true`, `--unfurl_links false`, `--unfurl_media false`, `--mrkdwn true`
- `post_table` supports:
  - `--headers_json` / `--headers_file`
  - `--rows_json` / `--rows_file`
  - `--title`, `--text`, `--include_index true`
  - `--max_rows` (default `20`), `--max_col_width` (default `32`)

All commands return JSON to stdout.

## Examples

List channels (all pages):

```bash
SLACK_TOKEN=... bun ./ .codex/skills/slack-web-api/scripts/slack_web_api.ts list_channels --all true
```

Post message:

```bash
SLACK_TOKEN=... bun ./ .codex/skills/slack-web-api/scripts/slack_web_api.ts post --channel C123 --text "Hello"
```

Post message with escaped newlines:

```bash
SLACK_TOKEN=... bun ./ .codex/skills/slack-web-api/scripts/slack_web_api.ts post \
  --channel C123 \
  --text "Line 1\\nLine 2\\n- bullet" \
  --unescape_text true
```

Post rich Block Kit message from JSON string:

```bash
SLACK_TOKEN=... bun ./ .codex/skills/slack-web-api/scripts/slack_web_api.ts post \
  --channel C123 \
  --text "Fallback text" \
  --blocks_json '[{"type":"header","text":{"type":"plain_text","text":"Perf Update"}},{"type":"section","text":{"type":"mrkdwn","text":"*All probes:* :white_check_mark: 24/24 exposed"}}]'
```

Post rich Block Kit message from file:

```bash
SLACK_TOKEN=... bun ./ .codex/skills/slack-web-api/scripts/slack_web_api.ts post \
  --channel C123 \
  --text "Fallback text" \
  --blocks_file /tmp/slack-blocks.json
```

Post an aligned table:

```bash
SLACK_TOKEN=... bun ./ .codex/skills/slack-web-api/scripts/slack_web_api.ts post_table \
  --channel C123 \
  --title "Pipeline Performance (user_add)" \
  --headers_json '["kind","exposed","timeout","p50_min","p90_min"]' \
  --rows_json '[["account",12,0,8.79,33.73],["video",12,0,12.01,50.44]]'
```

Post a larger table from file (array of objects):

```bash
SLACK_TOKEN=... bun ./ .codex/skills/slack-web-api/scripts/slack_web_api.ts post_table \
  --channel C123 \
  --headers_json '["kind","platform","status","minutes_to_exposed"]' \
  --rows_file /tmp/perf_rows.json \
  --include_index true \
  --max_rows 40 \
  --max_col_width 40
```

Search messages:

```bash
SLACK_TOKEN=... bun ./ .codex/skills/slack-web-api/scripts/slack_web_api.ts search --query "in:#general budget review" --count 100
```

Read an entire channel history (paginate):

```bash
SLACK_TOKEN=... bun ./ .codex/skills/slack-web-api/scripts/slack_web_api.ts channel_history --channel C123 --all true
```

Fetch a thread:

```bash
SLACK_TOKEN=... bun ./ .codex/skills/slack-web-api/scripts/slack_web_api.ts thread --channel C123 --ts 1712345678.9012 --all true --resolve_users true
```

Channel history with usernames + embedded threads:

```bash
SLACK_TOKEN=... bun ./ .codex/skills/slack-web-api/scripts/slack_web_api.ts channel_history --channel C123 --all true --resolve_users true --include_threads true
```

Add/remove reactions:

```bash
SLACK_TOKEN=... bun ./ .codex/skills/slack-web-api/scripts/slack_web_api.ts reactions_add --channel C123 --ts 1712345678.9012 --name eyes
SLACK_TOKEN=... bun ./ .codex/skills/slack-web-api/scripts/slack_web_api.ts reactions_remove --channel C123 --ts 1712345678.9012 --name eyes
```

Delete a message:

```bash
SLACK_TOKEN=... bun ./ .codex/skills/slack-web-api/scripts/slack_web_api.ts delete --channel C123 --ts 1712345678.9012
```

## Pattern: read + analyze a channel

1. Fetch history to JSON:
   ```bash
   SLACK_TOKEN=... bun ./ .codex/skills/slack-web-api/scripts/slack_web_api.ts channel_history --channel C123 --all true > /tmp/slack.json
   ```
2. Analyze locally (summaries, keyword extraction, timeline, etc.).

## Notes

- Use channel IDs (`C...`/`G...`) for reliability.
- `search` respects Slack’s search index, while `channel_history` is raw channel data.
- If API permissions block results, update bot scopes in Slack app settings.
