# Showcase: Research Submission Planning with ccfddl-query

These examples demonstrate how a research agent uses the `ccfddl-query` skill
to help plan submissions.

The workflow is always:

1. Agent runs `scripts/query_conferences.py` with `--format json`
2. Agent reads the structured JSON envelope
3. Agent converts the result into concise user-facing prose

> Results depend on the current date and upstream `ccfddl` data freshness.
> The examples below use **fixture data** for reproducible output; real runs
> fetch live data from `ccfddl/ccf-deadlines` by default.

---

## Example 1: Single Conference Deadline Lookup

**User question:** "ICML 2026 deadline什么时候？"

**Agent CLI:**

```bash
python skills/ccfddl-query/scripts/query_conferences.py search \
  --query ICML --format json
```

**Sample output (truncated, fixture data):**

```json
{
  "source": "file:skills/ccfddl-query/fixtures/allconf.sample.yml",
  "count": 1,
  "results": [
    {
      "id": "icml26",
      "conference": "ICML",
      "title": "ICML 2026",
      "category": "AI",
      "rank": { "ccf": "A", "core": "A*", "thcpl": "A" },
      "url": "https://icml.cc/Conferences/2026",
      "timezone": "UTC+0",
      "status": "closed",
      "deadlines": [
        {
          "type": "paper",
          "deadline": "2026-01-29 11:59:59",
          "local_deadline": "2026-01-29T11:59:59+00:00",
          "timezone": "UTC+0",
          "status": "closed"
        }
      ]
    }
  ]
}
```

**Explanation:**

- The agent reads `status: "closed"` and `days_to_deadline: null` — the deadline has passed.
- The timezone `UTC+0` maps to UTC.
- The rank shows CCF-A / CORE-A\*. This helps the user assess the venue's tier for their institution.
- **Uncertainty note:** Live results depend on the current date. If queried before Jan 29, 2026, ICML would show `status: "open"` with a countdown.

**Key rule:** Never invent deadlines. If the YAML says `TBD`, return status `tbd` and tell the user the date hasn't been announced.

---

## Example 2: Conditional Filter — Upcoming AI / CCF-A Conferences

**User question:** "未来半年 AI 领域有没有 CCF-A 的会可以投？"

**Agent CLI:**

```bash
python skills/ccfddl-query/scripts/query_conferences.py list \
  --category AI --ccf-rank A --status open --within-days 180 --format json
```

**Sample output (fixture data, queried 2026-07-03):**

```json
{
  "source": "file:skills/ccfddl-query/fixtures/allconf.sample.yml",
  "count": 1,
  "results": [
    {
      "id": "aifuture26",
      "conference": "AIFUTURE",
      "title": "AIFUTURE 2026",
      "category": "AI",
      "rank": { "ccf": "A", "core": "A", "thcpl": "B" },
      "url": "https://example.org/aifuture2026",
      "timezone": "UTC-12",
      "status": "open",
      "days_to_deadline": 44,
      "deadlines": [
        {
          "type": "paper",
          "abstract_deadline": "2026-08-01 23:59:59",
          "deadline": "2026-08-15 23:59:59",
          "timezone": "UTC-12",
          "status": "open"
        }
      ]
    }
  ]
}
```

**Explanation:**

- The agent filters: `category=AI`, `ccf-rank=A`, `status=open`, window=180 days.
- `AIFUTURE` is a **synthetic** fixture entry — a real run against upstream data would show actual venues (AAAI, NeurIPS, etc.) with their real deadlines.
- The `days_to_deadline: 44` means the deadline is 44 days from the query date.
- The agent should present results sorted by nearest deadline.
- **Uncertainty note:** Upstream data may be stale or incomplete. When cache or fixture data is used, the JSON `source` field reflects this.

---

## Example 3: Domain Mapping — CV / Image Editing / Relighting

**User question:** "我做 Relighting，有哪些会议可以考虑？"

**Agent CLI:**

```bash
python skills/ccfddl-query/scripts/query_conferences.py list \
  --domain relighting --status open --within-days 180 --format json
```

**Sample output (fixture data):**

```json
{
  "source": "file:skills/ccfddl-query/fixtures/allconf.sample.yml",
  "count": 3,
  "notes": [
    "domain preset 'relighting' → categories AI,CG,MX"
  ],
  "results": [
    {
      "id": "aifuture26",
      "conference": "AIFUTURE 2026",
      "category": "AI",
      "rank": { "ccf": "A" },
      "days_to_deadline": 44,
      "deadlines": [...]
    },
    {
      "id": "cgfuture26",
      "conference": "CGFUTURE 2026",
      "category": "CG",
      "rank": { "ccf": "B" },
      "days_to_deadline": 90,
      "deadlines": [...]
    },
    {
      "id": "mxfuture26",
      "conference": "MXFUTURE 2026",
      "category": "MX",
      "rank": { "ccf": "B" },
      "days_to_deadline": 135,
      "deadlines": [...]
    }
  ]
}
```

**Explanation:**

- The agent maps `relighting` → categories `AI, CG, MX` via `--domain`.
- The JSON envelope includes a `notes` entry documenting the mapping: `"domain preset 'relighting' → categories AI,CG,MX"`.
- The agent should explain: "Relighting is not a native ccfddl category. It maps to AI (learning-based methods), CG (physically based rendering), and MX (multimedia applications)."
- Results span all three categories, sorted by nearest deadline.
- **Uncertainty note:** Not every conference in AI/CG/MX publishes relighting work. The domain preset is a convenience — the user should review each venue's scope.
- **Refinement suggestion:** If results are too broad, the user can narrow with `--ccf-rank A` or a custom `--category AI,CG`.

---

## How an Agent Uses These Examples

1. **Parse the user's intent** — specific deadline lookup, open-window scan, or domain exploration.
2. **Construct the query** — pick the right subcommand (`search` or `list`) and parameters.
3. **Request JSON output** — `--format json` for structured reasoning.
4. **Read the envelope** — check `source`, `count`, `notes` for operational metadata.
5. **Present to the user** — sort by urgency, explain domain mapping if used, and always note data limitations.

> Never skip the uncertainty disclosure. Whether the data is from fixture, cache, or live upstream, the agent should mention it.

## Reference

- Skill: `skills/ccfddl-query/SKILL.md`
- CLI: `skills/ccfddl-query/scripts/query_conferences.py --help`
- Domain mapping reference: `skills/ccfddl-query/references/domain-mapping.md`
- Output schema: `skills/ccfddl-query/references/output-schema.md`

## Four-Agent Recording

To record a side-by-side CLI showcase, you can use:

```bash
scripts/showcase-4agents.sh "我做 Relighting，有哪些会议可以考虑？"
```

This creates a 2x2 `tmux` layout for `Claude Code`, `Codex`, `OpenCode`, and
`Antigravity`, runs the same prompt through all four, and saves transcripts
under `/tmp/ccfddl-showcase-*/`.

For video capture on macOS, `Recordly`, `QuickTime Player`, or `Cmd-Shift-5`
all work well. `Recordly` is a good fit when you want lightweight screen
recording without additional editing setup.
