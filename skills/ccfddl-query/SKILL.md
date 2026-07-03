---
name: ccfddl-query
description: Query ccfddl conference deadline data for research submission planning. Use when users ask about conference deadlines, CCF/CORE/THCPL ranks, conference categories, upcoming submission windows, or which conferences may fit a research workflow.
---

# CCFDDL Query

Use this skill to answer research conference deadline and filtering questions from `ccfddl` data.

## Workflow

1. Run `scripts/query_conferences.py` to fetch, cache, parse, and filter conference data.
2. Prefer JSON output for agent reasoning.
3. Convert the structured result into concise user-facing prose.
4. Mention source freshness when cache fallback or fixture data was used.
5. Do not invent missing deadlines, ranks, links, or acceptance rates.

## Commands

Search by acronym or title:

```bash
python skills/ccfddl-query/scripts/query_conferences.py search --query ICML --format json
```

List upcoming conferences:

```bash
python skills/ccfddl-query/scripts/query_conferences.py list --category AI --ccf-rank A --within-days 180 --format json
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
- For recommendation-style questions, use deterministic filters first: category, rank, status, and deadline window.
- If multiple results match, sort open conferences by nearest deadline and closed conferences by year descending.
- If the data is stale or unavailable, say so plainly.
