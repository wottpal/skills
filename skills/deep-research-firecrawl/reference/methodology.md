# Methodology Reference

This file contains detailed execution checklists for `deep-research-firecrawl`.

## Phase checklist

### Phase 1: Scope

- Define exact question and expected decision context.
- Set time window and geography defaults if missing.
- Note required deliverable format.

### Phase 2: Search angle design

Build a balanced search matrix:

- Core definitions and baselines
- Technical depth and implementation details
- Commercial or market signals
- Critical/opposing analysis
- Regulatory and policy constraints
- Recent developments (last 12-24 months)

### Phase 3: Retrieval protocol (Firecrawl)

1. Launch 5-10 parallel `firecrawl:firecrawl_search` queries.
2. For each query, capture top relevant URLs.
3. Scrape primary pages with `firecrawl:firecrawl_scrape`.
4. For key domains, run `firecrawl:firecrawl_map` then bounded `firecrawl:firecrawl_crawl`.
5. Use `firecrawl:firecrawl_agent` if results remain fragmented.

### Phase 4: Source quality scoring

Use this heuristic per source:

- 5: Primary, authoritative, current, directly relevant
- 4: High-quality secondary or reputable analysis
- 3: Useful but partial, older, or narrow
- 2: Weak support or unclear methodology
- 1: Low credibility or promotional noise

Prioritize claims backed by sources scored 4-5.

### Phase 5: Claim triangulation

For each major claim:

- Confirm with at least 3 independent sources.
- Prefer source diversity (different organizations/authors).
- Record disagreements and unresolved gaps.

### Phase 6: Synthesis

Structure each finding as:

1. Evidence statement with citation
2. Why it matters
3. Conditions, limitations, and alternatives

### Phase 7: Critical review

Required for `deep` and `ultradeep`:

- Challenge assumptions that drive recommendations.
- Search intentionally for disconfirming evidence.
- Re-check oldest or highest-impact claims for recency.

### Phase 8: Packaging

Use `templates/report_template.md` and ensure:

- Claims and bibliography numbering align
- Counterevidence is visible, not buried
- Recommendations map to evidence, not intuition

## Mode guardrails

### quick

- Prioritize breadth and fast synthesis.
- Keep caveats concise but explicit.

### standard

- Balance breadth and verification.
- Include a clear risk section.

### deep

- Add red-team critique and scenario implications.
- Increase source diversity and triangulation depth.

### ultradeep

- Include broader ecosystem mapping and sensitivity analysis.
- Explicitly separate high-confidence findings from low-confidence signals.

## Report QA checklist

- [ ] Mode is stated at top of report
- [ ] Scope and assumptions are explicit
- [ ] Major claims include citation markers
- [ ] Bibliography entries are complete and matched
- [ ] Counterevidence section is present
- [ ] Recommendations are evidence-linked
