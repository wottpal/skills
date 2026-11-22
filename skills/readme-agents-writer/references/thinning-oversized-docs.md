# Thinning Oversized Docs

Use this guide when an instruction doc has grown past what agents load, or when a restructure moves content between docs. Nothing here is a reason to delete guidance an engineer or agent needs to act safely; most bytes move, few disappear.

## Why Size Matters

Agents load an instruction file whole, cut it, or skip it, depending on the harness and its version. Observed in 2026-11 (verify against current docs before relying on a number):

- Codex reads the project's instruction files from the project root down to the working directory and stops adding them once their combined size reaches `project_doc_max_bytes` (32 KiB by default).
- Claude Code loads the root file whole into every session. A nested file loads when the agent first reads or edits a file in that directory, and only its start is kept past 40,000 characters on a 200K context window.

Whatever the numbers, the end of a long file is what gets lost, and a large root costs context in every session.

## Order By What Gets Cut

- Put hard rules, guardrails and the "read this before that" triggers in the first screen of a doc.
- Put reference material (repository maps, file maps, catalogs) last, so growth past a limit cuts reference lines, not rules.
- A link does not load the linked file. When the root sends detail elsewhere, keep one trigger line per destination: "Before you do X, read Y."

## Put The Doc Next To The Code

Nested docs load by directory. A doc about a UI that sits in another module's directory never loads when someone works on that UI. Move area guidance into a README in the directory where that work happens, and leave a one-line pointer behind.

## Sort Content Before You Cut

Classify each section, then apply its default fate:

| Kind | Default fate |
| --- | --- |
| Rules, invariants, gotchas, runbooks, verification steps, the reason behind a non-obvious design | Keep, near the top |
| Dated history: "was X until <date>", incident retellings, finished rollout or backfill logs | Keep the rule and what would trigger a re-check; drop the story (git history keeps it) |
| Lists that mirror code: file maps, test lists, enum and column tables, config tables copied from compose or env schemas | Delete, or name the source file instead |
| The same explanation in two or more docs | Keep one owner; link from the others |
| Deep reference only some tasks need: long per-case tables, provider quirk catalogs, one-off runbooks | Move to a sibling doc or the owning directory's README, with a line that says when to read it |

Where a formatter pads table cells to the widest cell (Prettier, `bun fmt`), a wide table can carry more padding than content; a list holds the same facts in a fraction of the bytes.

## Move Blocks Safely

1. Check the destination's size first. Moving content into a doc that is near its own limit only moves the problem.
2. Copy moved blocks word for word, by line range from the committed version, not retyped from memory.
3. Re-point relative links for the new directory, and anchors whose heading moved with the block.
4. Rewrite "above" and "below" in moved text into links; the neighbor it pointed at did not move with it.
5. Keep a heading alive in the old doc when a short summary stays behind, so inbound links to its anchor still resolve.
6. Prove nothing was lost: compare the old doc with the new set sentence by sentence and account for every sentence that exists nowhere verbatim (shortened on purpose, or missing).
7. Search the whole repository for references to moved sections: other docs, code comments, error strings, skills, CI. Also search for the section names alone: a reference that wraps across a line break ("root\nREADME") slips past a single-line search.

## Keep It From Growing Back

Run the checker's size options in lint or CI, with a shrink-only allowlist for docs that are already over the limit:

```bash
python3 "<skill-dir>/scripts/check-doc-pairs.py" "<repo-root>" --recursive \
  --max-root-bytes 30000 --max-nested-chars 40000 --allow-oversized "<oversized-list>"
```

- It counts only docs an `AGENTS.md` resolves to, once each, so a skill's or a vendored package's README is not measured and a shared doc is not counted twice.
- The list holds one canonical doc path per line, relative to the list file. An entry that is under the limit, or that no checked `AGENTS.md` resolves to, fails the check, so the list can only shrink.
- Pick limits with headroom below the harness numbers above: a root at the limit leaves nothing for nested files in a combined budget.

For a large restructure, a single independent review pass of the diff (lost meaning, wrong new facts, broken links, stale references) catches what the scripts miss.
