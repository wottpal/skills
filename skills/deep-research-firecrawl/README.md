# deep-research-firecrawl

An agent-run research workflow with Firecrawl-first retrieval, source provenance, counterevidence, and four research depths. Start with [SKILL.md](SKILL.md); use [the Firecrawl reference](references/firecrawl-workflow.md) when choosing tools and handling jobs.

## Supported helpers

Python 3.10+ is sufficient; no Python packages or API keys are needed for the local checks. Run these commands from this skill directory:

```bash
python3 "scripts/validate_report.py" "tests/fixtures/valid_report.md"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s "tests" -v
```

The report validator is offline. The optional citation checker contacts public URLs and DOI resolvers:

```bash
python3 "scripts/verify_citations.py" --report "/absolute/path/to/report.md" --strict
```

See [validation](references/validation.md) for the report contract and exit codes. Passing checks establishes structure, link reachability, or metadata consistency only. The agent must verify the meaning and support of claims from retrieved sources.

## Maintenance

This repository's `skills/deep-research-firecrawl/` directory is the source of truth. Edit here and install with the root repository's `npx skills` workflow; do not edit installed copies. Keep `SKILL.md` under 200 lines and put detailed guidance in `references/`.

When changing retrieval guidance, check the current upstream MCP documentation and exposed tool schemas. Record the verification date and supporting links in the Firecrawl reference. When changing a helper, run the offline regression suite and both fixtures (valid exits 0; invalid exits 1), then `git diff --check` from the repository root. Exercise the [workflow scenarios](references/validation.md#workflow-evaluations) when the required tools are available; state any untested integration behavior.

The previous standalone research engine only printed instructions and saved empty state; it did not generate the promised report. It has been removed along with unintegrated citation management, numeric source scoring, broken HTML conversion/validation, an unused HTML template, dormant dependency suggestions, and historical self-review/competitive documents. There is no replacement research CLI: invoke the skill through an agent. Use appropriate document tooling separately if an HTML/PDF artifact is requested.

## Attribution

Originally bootstrapped from [199-biotechnologies/claude-deep-research-skill](https://github.com/199-biotechnologies/claude-deep-research-skill). The current workflow and checks are maintained in this repository.
