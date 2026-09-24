# Firecrawl retrieval and job handling

Verified against the upstream documentation on **2026-09-24**. This is a capability guide, not a pinned tool schema: inspect the current session's advertised tools and arguments before calling them. MCP names may have a client-specific namespace. Do not copy SDK method names into MCP calls.

## Capability discovery

The [upstream MCP README](https://github.com/firecrawl/firecrawl-mcp-server#how-to-choose-a-tool) documents several surfaces:

| Surface | Research implications |
| --- | --- |
| Full authenticated MCP | Search/scrape plus optional map, crawl, agent/status, developer search, and paper tools. Availability varies with server version and configuration. |
| Hosted keyless MCP | Currently exposes search, scrape, and parse; rate limits apply. Do not require optional map/crawl/agent access. |
| Hosted search-only MCP | Search, developer/paper tools, and Alexandria discovery/execution. Search itself does not fetch page content or accept `scrapeOptions`; the separately exposed scrape tool can retrieve a supplied URL or execute an Alexandria contract. |

See the [search profile contract](https://github.com/firecrawl/firecrawl-mcp-server/blob/main/docs/search-profile.md). Never infer access from a tool name alone. Where direct reading is absent, use another available retriever and disclose it, or report the evidence gap if Firecrawl-only was requested. Existing search + scrape access is enough for a normal research workflow.

## Select the smallest useful retrieval

| Need | Capability and next step |
| --- | --- |
| Known page | `firecrawl_scrape`; read relevant passages and metadata. |
| Discover sources | `firecrawl_search`; inspect result URLs and fetch evidence, unless returned content already contains the relevant passages. |
| Programming question | `firecrawl_developer_search`, if exposed; verify the result against the relevant released version. |
| Scientific literature | `firecrawl_research_search_papers`, then inspect/read selected papers; related-paper lookup can expand coverage. Abstract-only access stays explicit. |
| Find pages on one site | `firecrawl_map`, then scrape selected URLs. A URL map is not page content. |
| Cover a site section | `firecrawl_crawl` with an explicit page limit and path/domain scope. |
| Broad structured collection | `firecrawl_agent`, followed by `firecrawl_agent_status`; validate the returned sources before synthesis. |

For evidence reading, request Markdown or targeted extraction that preserves supporting passages, URLs, and dates. A structured answer without provenance needs further retrieval. Call scrape separately for each known URL unless the exposed tool explicitly supports bulk input. Batch independent calls within platform limits.

Scientific research tools are distinct from web search with a research category filter. Consult current schemas for supported identifiers and filters rather than guessing them. Alexandria provider execution is optional: inspect the selected contract and its provenance before use; follow any explicit provider terms/authorization flow separately from retrieval.

## Agent jobs

The [MCP agent/status tools](https://github.com/firecrawl/firecrawl-mcp-server#available-tools) start a job and poll it. The [Agent API guide](https://docs.firecrawl.dev/features/agent#job-status-and-completion) explains the lifecycle; SDK convenience methods can wait internally, which does not change the MCP pattern.

1. Give a bounded question and, where supported, output fields for facts, source URLs, and dates. Apply available cost/scope controls within the user's budget.
2. Save the returned job ID. Submission success means the job started, not that research is complete.
3. Poll the advertised status tool with that same ID. Use the service's retry guidance or bounded delays (the MCP guide suggests 10–30 seconds); avoid tight loops.
4. On `completed`, retrieve and inspect the data. Open the underlying sources for important claims and record gaps in returned provenance.
5. On `failed`, surface the error and preserve any explicitly returned partial evidence. Agent cancellation currently reports `failed` with a cancellation error. Do not relaunch merely because a polling request timed out.
6. At the task's time/cost limit, report the pending ID and unresolved coverage. If cancellation is available and appropriate, request it and check the result; do not claim the job stopped merely because you stopped polling.

## Crawl completion and pagination

Current MCP `firecrawl_crawl` waits internally and returns final status/data. The [MCP guide](https://github.com/firecrawl/firecrawl-mcp-server#available-tools) and [Crawl API guide](https://docs.firecrawl.dev/features/crawl) describe different abstraction levels. Inspect the actual response instead of assuming every crawl returns only a job ID or inventing a status tool.

When the exposed API/tool returns a job ID or partial pages, follow its documented status/continuation interface. For direct API use, poll until `completed`, `failed`, or `cancelled`, then collect remaining pages via `next`. Stop pagination if there are no new documents, even when `next` persists. SDKs may aggregate pages internally. Deduplicate by canonical source URL and preserve retrieval errors.

A completed crawl does not establish full coverage: limits, scope, robots restrictions, or failed pages can omit material. Inspect per-page status/content and available crawl-error information; `completed == total` alone does not prove every discovered page succeeded. If a continuation interface is unavailable, label the returned subset and retrieve critical missing URLs individually.

## Failures and evidence boundaries

- Rate limit: honor retry guidance, reduce concurrency, and retry within a bounded budget. Do not spin or repeatedly start duplicate jobs.
- Authentication/access failure: use public alternatives or an authorized browser session; do not bypass access controls. Never include credentials in reports or tool logs.
- Timeout/expired job: distinguish unknown status from failed status; preserve the ID and any retrieved sources. State when recovery was unavailable.
- Empty/truncated content: verify the final URL, page status, and relevant passages. A successful transport response can still contain an error, login page, or incomplete extraction.
- Partial coverage: explain what was fetched and what could not be checked. Do not equate a search snippet, HTTP 200, or agent summary with substantiation of a claim.
