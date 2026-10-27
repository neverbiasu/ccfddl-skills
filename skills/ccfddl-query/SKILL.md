---
name: ccfddl-query
description: Query ccfddl conference deadline data for research submission planning. Use when users ask about conference deadlines, CCF/CORE/THCPL ranks, conference categories, upcoming submission windows, or which conferences may fit a research workflow.
---

# CCFDDL Query

Use this skill to answer research conference deadline and filtering questions from `ccfddl` data.

## Workflow

1. Run `scripts/query_conferences.py` to fetch, cache, parse, and filter conference data.
2. Prefer JSON output for agent reasoning.
3. For "what can I still submit", "what is still open this year", "what venues fit my topic now", or recommendation-style questions, default to `--status open` and a concrete deadline window such as `--within-days 120`, `180`, or `365`.
4. Convert the structured result into concise user-facing prose.
5. Lead with conferences that are open as of the current date. Treat closed and TBD venues as secondary context unless the user explicitly asks for a broader landscape.
6. If there are no open results, say that plainly and then offer the nearest TBD or recently closed venues as fallback context.
7. Do not answer recommendation-style questions with a static conference cheat sheet alone. Static venue lists are background context only; the final answer must be grounded in current ccfddl query results.
8. Mention source freshness when cache or fixture data was used. The script auto-refreshes a cache older than 24h; if the result `notes` say `cache data was used (cache from <date>, ...)` or `online fetch failed`, tell the user the cache date and that deadlines may be outdated (suggest `refresh-cache` once online).
9. Do not invent missing deadlines, ranks, links, or acceptance rates.
10. Never say a conference is missing from ccfddl based on filtered results. Only claim "ccfddl has no entry for X" after `search --query <name>` with no rank, status, or window filters returns nothing for it. If X exists but a filter excluded it, name the filter, e.g. "IJCAI 2027 is CCF-B in ccfddl, so it is not in the CCF-A results."
11. Ranks come from ccfddl data, not from memory. If the user or your own recollection gives a different rank, report the ccfddl rank and point out the difference.
12. Copy dates, timezone conversions, and remaining days from the script output; never compute them yourself. Use `days_to_deadline` for the paper deadline and `abstract_days_to_deadline` for the abstract deadline. If the script gives no number for something (for example `abstract_days_to_deadline` is null), do not state one; say it is not available or that it needs another query.

## Commands

Search by acronym or title:

```bash
python skills/ccfddl-query/scripts/query_conferences.py search --query ICML --format json
```

List upcoming conferences:

```bash
python skills/ccfddl-query/scripts/query_conferences.py list --category AI --ccf-rank A --within-days 180 --format json
```

List conferences that are still open now:

```bash
python skills/ccfddl-query/scripts/query_conferences.py list --status open --within-days 180 --format json
```

Filter by research domain (maps to one or more ccfddl categories):

```bash
python skills/ccfddl-query/scripts/query_conferences.py list --domain cv --status open --within-days 180 --format json
python skills/ccfddl-query/scripts/query_conferences.py list --domain image-editing --status open --format json
python skills/ccfddl-query/scripts/query_conferences.py list --domain relighting --ccf-rank A --format json
```

Render a Markdown table:

```bash
python skills/ccfddl-query/scripts/query_conferences.py list --status open --format markdown
```

Export as iCalendar (ICS) for calendar import:

```bash
python skills/ccfddl-query/scripts/query_conferences.py search --query ICML --format ics
python skills/ccfddl-query/scripts/query_conferences.py list --domain cv --status open --within-days 180 --format ics
```

Only results with concrete (non-TBD) deadlines generate VEVENT entries. TBD deadlines are silently skipped. All times are normalized to UTC in the ICS output. The original timezone label (AoE, UTC, PT, etc.) is recorded in the DESCRIPTION field.

Use fixture data for tests or offline inspection:

```bash
python skills/ccfddl-query/scripts/query_conferences.py list --data-path skills/ccfddl-query/fixtures/allconf.sample.yml
```

Include acceptance-rate data (requires a local accept_rates YAML from upstream):

```bash
python skills/ccfddl-query/scripts/query_conferences.py list --data-path skills/ccfddl-query/fixtures/allconf.sample.yml --accept-rates-path skills/ccfddl-query/fixtures/accept_rates.sample.yml
```

## References

- Read `references/data-source.md` for upstream data, cache, accept_rates, and timezone rules.
- Read `references/output-schema.md` before changing JSON fields or status semantics.
- Read `references/domain-mapping.md` when the user asks about a research domain (e.g. CV, Image Editing, Relighting) that does not match a single ccfddl category.

## Presentation Rules

- For exact conference lookups, show the next concrete deadline, timezone, local time, rank, and URL.
- Always show each deadline as it appears in the data, with its timezone label (e.g. `2026-08-15 23:59:59 UTC-12`). A converted time may be added next to it, never instead of it. Explain `AoE` (Anywhere on Earth, UTC-12) the first time it appears.
- For recommendation-style questions, use deterministic filters first: category, rank, status, and deadline window.
- For "还能投什么 / 现在还能投什么 / 今年还有什么会议能投" style requests, always query live conference status first and present currently open venues before any static shortlist.
- When the user gives a static shortlist, treat it as a candidate pool to filter against current status; do not present every venue from the shortlist as if it were still open.
- Use explicit dates in the answer when recency matters, e.g. "As of 2026-07-14, these venues are still open."
- If multiple results match, sort open conferences by nearest deadline and closed conferences by year descending.
- If the data is stale or unavailable, say so plainly.
