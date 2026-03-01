#!/usr/bin/env bun
import { readFile } from "node:fs/promises"
import { LogLevel, WebClient } from "@slack/web-api"
import type { Block, KnownBlock, MessageAttachment } from "@slack/web-api"

const token = process.env.SLACK_TOKEN
if (!token) {
  console.error("SLACK_TOKEN is required in environment.")
  process.exit(1)
}

const client = new WebClient(token, {
  logLevel: LogLevel.ERROR,
})

type SlackMessage = Record<string, unknown> & {
  user?: string
  username?: string
  ts?: string
  thread_ts?: string
}

type SlackMessageWithExtras = SlackMessage & {
  user_name?: string
  thread?: SlackMessageWithExtras[]
}

const userCache = new Map<string, string>()

const args = process.argv.slice(2)
if (args.length === 0) {
  console.error("Usage: slack_web_api.ts <command> [--key value ...]")
  process.exit(1)
}

const command = args[0]
const options: Record<string, string> = {}
for (let i = 1; i < args.length; i += 1) {
  const key = args[i]
  if (!key?.startsWith("--")) {
    console.error(`Invalid arg key: ${key ?? ""}`)
    process.exit(1)
  }
  const value = args[i + 1]
  if (value === undefined || value.startsWith("--")) {
    options[key.slice(2)] = "true"
    continue
  }
  options[key.slice(2)] = value
  i += 1
}

const toBool = (value: string | undefined) =>
  value === "true" ||
  value === "1" ||
  value === "yes" ||
  value === "y" ||
  value === "on"
const toNumber = (value: string | undefined) => (value ? Number(value) : undefined)

const resolveUsers = async (value: string | undefined) => {
  if (!value) return false
  return toBool(value)
}

const getRequiredOption = (key: string) => {
  const value = options[key]
  if (!value) {
    throw new Error(`--${key} is required`)
  }
  return value
}

const readOptionalJsonFile = async <T>(path: string | undefined, label: string) => {
  if (!path) return undefined
  const content = await readFile(path, "utf8")
  try {
    return JSON.parse(content) as T
  } catch {
    throw new Error(`Invalid JSON in --${label} file (${path})`)
  }
}

const parseOptionalJson = <T>(value: string | undefined, key: string) => {
  if (!value) return undefined
  try {
    return JSON.parse(value) as T
  } catch {
    throw new Error(`Invalid JSON in --${key}`)
  }
}

const parseJsonOptionOrFile = async <T>(
  jsonKey: string,
  fileKey: string,
  label: string,
) => {
  const fromJson = parseOptionalJson<T>(options[jsonKey], jsonKey)
  const fromFile = await readOptionalJsonFile<T>(options[fileKey], fileKey)
  if (fromJson && fromFile) {
    throw new Error(`Use only one of --${jsonKey} or --${fileKey}`)
  }
  return fromJson ?? fromFile
}

const readOptionalTextFile = async (path: string | undefined) => {
  if (!path) return undefined
  return readFile(path, "utf8")
}

const unescapeText = (value: string) =>
  value
    .replace(/\\r\\n/g, "\n")
    .replace(/\\n/g, "\n")
    .replace(/\\r/g, "\r")
    .replace(/\\t/g, "\t")

const resolveTextInput = async () => {
  const inline = options.text
  const fromFile = await readOptionalTextFile(options.text_file)
  if (inline && fromFile !== undefined) {
    throw new Error("Use only one of --text or --text_file")
  }
  let text = inline ?? fromFile
  if (!text) return text
  if (toBool(options.unescape_text)) {
    text = unescapeText(text)
  }
  return text
}

const postMessageViaApi = async (payload: Record<string, unknown>) => {
  const resp = await client.apiCall("chat.postMessage", payload)
  const result = resp as { ok?: boolean; error?: string }
  if (!result.ok) throw new Error(result.error || "chat.postMessage failed")
  return resp
}

const getUserDisplayName = async (userId: string) => {
  if (userCache.has(userId)) return userCache.get(userId) as string
  const resp = await client.users.info({ user: userId })
  if (!resp.ok || !resp.user) return userId
  const profile = resp.user.profile ?? {}
  const name = profile.display_name || profile.real_name || resp.user.name || userId
  userCache.set(userId, name)
  return name
}

const maybeEnrichMessages = async (
  messages: SlackMessage[],
  includeThreads: boolean,
  includeUsers: boolean,
  channel?: string,
) => {
  const enriched: SlackMessageWithExtras[] = []
  for (const message of messages) {
    const item: SlackMessageWithExtras = { ...message }
    if (includeUsers && item.user) {
      item.user_name = await getUserDisplayName(item.user)
    }
    if (includeThreads && channel && item.thread_ts && item.thread_ts === item.ts) {
      const thread = await threadRepliesInternal(channel, item.thread_ts, includeUsers)
      item.thread = thread.messages
    }
    enriched.push(item)
  }
  return enriched
}

const threadRepliesInternal = async (channel: string, ts: string, includeUsers: boolean) => {
  const limit = toNumber(options.limit) ?? 200
  const all = toBool(options.all)
  let cursor: string | undefined
  const messages: SlackMessageWithExtras[] = []
  do {
    const resp = await client.conversations.replies({
      channel,
      ts,
      limit,
      cursor,
      inclusive: true,
    })
    if (!resp.ok) throw new Error(resp.error || "conversations.replies failed")
    messages.push(...((resp.messages ?? []) as SlackMessageWithExtras[]))
    cursor = all ? resp.response_metadata?.next_cursor : undefined
  } while (cursor)

  if (includeUsers) {
    for (const msg of messages) {
      if (msg.user) {
        msg.user_name = await getUserDisplayName(msg.user)
      }
    }
  }
  return { messages }
}

async function listChannels() {
  const types = options.types ?? "public_channel,private_channel"
  const limit = toNumber(options.limit) ?? 200
  const all = toBool(options.all)
  let cursor: string | undefined
  const channels = [] as unknown[]
  do {
    const resp = await client.conversations.list({
      limit,
      cursor,
      types,
      exclude_archived: true,
    })
    if (!resp.ok) throw new Error(resp.error || "conversations.list failed")
    channels.push(...(resp.channels ?? []))
    cursor = all ? resp.response_metadata?.next_cursor : undefined
  } while (cursor)
  return { channels }
}

async function postMessage() {
  const channel = getRequiredOption("channel")
  const text = await resolveTextInput()
  const blocks = await parseJsonOptionOrFile<Array<KnownBlock | Block>>(
    "blocks_json",
    "blocks_file",
    "blocks",
  )
  const attachments = await parseJsonOptionOrFile<MessageAttachment[]>(
    "attachments_json",
    "attachments_file",
    "attachments",
  )

  if (!text && !blocks?.length && !attachments?.length) {
    throw new Error(
      "Provide at least one content field: --text, --blocks_json/--blocks_file, or --attachments_json/--attachments_file",
    )
  }

  const payload: Record<string, unknown> = {
    channel,
  }
  if (text) payload.text = text
  if (blocks?.length) payload.blocks = blocks
  if (attachments?.length) payload.attachments = attachments
  if (options.thread_ts) payload.thread_ts = options.thread_ts
  if (options.reply_broadcast) payload.reply_broadcast = toBool(options.reply_broadcast)
  if (options.unfurl_links) payload.unfurl_links = toBool(options.unfurl_links)
  if (options.unfurl_media) payload.unfurl_media = toBool(options.unfurl_media)
  if (options.mrkdwn) payload.mrkdwn = toBool(options.mrkdwn)
  if (options.parse) payload.parse = options.parse as "none" | "full"
  return postMessageViaApi(payload)
}

const tableString = (value: unknown) => {
  if (value === null || value === undefined) return ""
  if (typeof value === "string") return value
  if (typeof value === "number" || typeof value === "boolean") return String(value)
  return JSON.stringify(value)
}

const truncateWithEllipsis = (value: string, maxWidth: number) => {
  if (maxWidth < 4) return value.slice(0, maxWidth)
  if (value.length <= maxWidth) return value
  return `${value.slice(0, maxWidth - 1)}…`
}

const renderAsciiTable = (headers: string[], rows: string[][], maxColWidth: number) => {
  const widths = headers.map((header, columnIndex) => {
    let width = Math.min(header.length, maxColWidth)
    for (const row of rows) {
      const cell = row[columnIndex] ?? ""
      width = Math.max(width, Math.min(cell.length, maxColWidth))
    }
    return width
  })

  const formatRow = (row: string[]) =>
    `| ${row
      .map((cell, index) => truncateWithEllipsis(cell ?? "", widths[index]).padEnd(widths[index]))
      .join(" | ")} |`

  const separator = `| ${widths.map((width) => "-".repeat(width)).join(" | ")} |`
  return [formatRow(headers), separator, ...rows.map(formatRow)].join("\n")
}

async function postTable() {
  const channel = getRequiredOption("channel")
  const headers =
    (await parseJsonOptionOrFile<string[]>("headers_json", "headers_file", "headers")) ?? []
  if (!Array.isArray(headers) || headers.length === 0) {
    throw new Error("--headers_json or --headers_file must be a non-empty JSON string array")
  }
  if (!headers.every((header) => typeof header === "string")) {
    throw new Error("All table headers must be strings")
  }

  const rowsRaw =
    (await parseJsonOptionOrFile<unknown[]>("rows_json", "rows_file", "rows")) ?? []
  if (!Array.isArray(rowsRaw)) {
    throw new Error("--rows_json or --rows_file must be a JSON array")
  }

  const includeIndex = toBool(options.include_index)
  const normalizedHeaders = includeIndex ? ["#", ...headers] : [...headers]

  const rows: string[][] = rowsRaw.map((row, rowIndex) => {
    if (Array.isArray(row)) {
      const values = headers.map((_, columnIndex) => tableString(row[columnIndex]))
      return includeIndex ? [String(rowIndex + 1), ...values] : values
    }
    if (row && typeof row === "object") {
      const objectRow = row as Record<string, unknown>
      const values = headers.map((header) => tableString(objectRow[header]))
      return includeIndex ? [String(rowIndex + 1), ...values] : values
    }
    throw new Error("Rows must be arrays or objects")
  })

  const maxRows = toNumber(options.max_rows) ?? 20
  const maxColWidth = toNumber(options.max_col_width) ?? 32
  const shownRows = rows.slice(0, maxRows)
  const truncatedRows = Math.max(rows.length - shownRows.length, 0)

  const table = renderAsciiTable(normalizedHeaders, shownRows, maxColWidth)

  const parts = [] as string[]
  if (options.title) parts.push(`*${options.title}*`)
  if (options.text) parts.push(options.text)
  parts.push(`\`\`\`\n${table}\n\`\`\``)
  if (truncatedRows > 0) {
    parts.push(`_+${truncatedRows} more row(s) omitted. Use --max_rows to raise the limit._`)
  }
  const text = parts.join("\n\n")

  const payload: Record<string, unknown> = {
    channel,
    text,
    mrkdwn: true,
  }
  if (options.thread_ts) payload.thread_ts = options.thread_ts
  if (options.reply_broadcast) payload.reply_broadcast = toBool(options.reply_broadcast)
  if (options.unfurl_links) payload.unfurl_links = toBool(options.unfurl_links)
  if (options.unfurl_media) payload.unfurl_media = toBool(options.unfurl_media)
  return postMessageViaApi(payload)
}

async function searchMessages() {
  const query = options.query
  if (!query) throw new Error("--query is required")
  const count = toNumber(options.count) ?? 100
  const sort = options.sort as "score" | "timestamp" | undefined
  const sort_dir = options.sort_dir as "asc" | "desc" | undefined
  const resp = await client.search.messages({ query, count, sort, sort_dir })
  if (!resp.ok) throw new Error(resp.error || "search.messages failed")
  return resp.messages
}

async function channelHistory() {
  const channel = options.channel
  if (!channel) throw new Error("--channel is required")
  const limit = toNumber(options.limit) ?? 200
  const all = toBool(options.all)
  const includeThreads = toBool(options.include_threads)
  const includeUsers = await resolveUsers(options.resolve_users)
  const oldest = options.oldest
  const latest = options.latest
  let cursor: string | undefined
  const messages: SlackMessage[] = []
  do {
    const resp = await client.conversations.history({
      channel,
      limit,
      cursor,
      oldest,
      latest,
      inclusive: true,
    })
    if (!resp.ok) throw new Error(resp.error || "conversations.history failed")
    messages.push(...((resp.messages ?? []) as SlackMessage[]))
    cursor = all ? resp.response_metadata?.next_cursor : undefined
  } while (cursor)
  if (includeThreads || includeUsers) {
    const enriched = await maybeEnrichMessages(messages, includeThreads, includeUsers, channel)
    return { messages: enriched }
  }
  return { messages }
}

async function threadReplies() {
  const channel = options.channel
  const ts = options.ts
  if (!channel || !ts) throw new Error("--channel and --ts are required")
  const includeUsers = await resolveUsers(options.resolve_users)
  return threadRepliesInternal(channel, ts, includeUsers)
}

async function reactionsAdd() {
  const channel = options.channel
  const ts = options.ts
  const name = options.name
  if (!channel || !ts || !name) {
    throw new Error("--channel, --ts, and --name are required")
  }
  const resp = await client.reactions.add({ channel, timestamp: ts, name })
  if (!resp.ok) throw new Error(resp.error || "reactions.add failed")
  return resp
}

async function reactionsRemove() {
  const channel = options.channel
  const ts = options.ts
  const name = options.name
  if (!channel || !ts || !name) {
    throw new Error("--channel, --ts, and --name are required")
  }
  const resp = await client.reactions.remove({ channel, timestamp: ts, name })
  if (!resp.ok) throw new Error(resp.error || "reactions.remove failed")
  return resp
}

async function deleteMessage() {
  const channel = getRequiredOption("channel")
  const ts = getRequiredOption("ts")
  const resp = await client.chat.delete({ channel, ts })
  if (!resp.ok) throw new Error(resp.error || "chat.delete failed")
  return resp
}

const handlers: Record<string, () => Promise<unknown>> = {
  list_channels: listChannels,
  post: postMessage,
  post_table: postTable,
  delete: deleteMessage,
  search: searchMessages,
  channel_history: channelHistory,
  thread: threadReplies,
  reactions_add: reactionsAdd,
  reactions_remove: reactionsRemove,
}

if (!handlers[command]) {
  console.error(`Unknown command: ${command}`)
  process.exit(1)
}

try {
  const result = await handlers[command]()
  process.stdout.write(JSON.stringify(result, null, 2))
} catch (error) {
  console.error((error as Error).message || String(error))
  process.exit(1)
}
