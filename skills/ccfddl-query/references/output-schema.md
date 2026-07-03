# Output Schema

The script writes a JSON envelope by default:

```json
{
  "source": "fixture",
  "generated_at": "2026-07-03T12:00:00+00:00",
  "count": 1,
  "results": []
}
```

Each result represents one conference-year instance:

```json
{
  "id": "icml26",
  "conference": "ICML",
  "title": "ICML 2026",
  "year": 2026,
  "description": "International Conference on Machine Learning",
  "category": "AI",
  "date": "July 6-12, 2026",
  "place": "Seoul, Korea",
  "rank": {
    "ccf": "A",
    "core": "A*",
    "thcpl": "A"
  },
  "url": "https://icml.cc/Conferences/2026",
  "dblp": "https://dblp.org/db/conf/icml",
  "timezone": "UTC+0",
  "status": "open",
  "days_to_deadline": 210,
  "deadlines": [],
  "notes": []
}
```

Individual conference results also carry an optional acceptance-rates array:

```json
{
  "acceptance_rates": [
    {
      "year": 2024,
      "submitted": 9473,
      "accepted": 2609,
      "str": "27.5% (2609/9473)",
      "rate": 0.2754,
      "source": "https://csconfstats.xoveexu.com/"
    }
  ]
}
```

- Populated only when `--accept-rates-path` is given to the `list` or `search` subcommand.
- Conferences are matched by lowercased `title` against the accept_rates YAML.
- If no matching data is found, `acceptance_rates` is `[]`.
- Never invent acceptance rates. Missing data is `[]`.

Status values:

- `open`: at least one paper deadline is in the future.
- `closed`: all known paper deadlines are in the past.
- `tbd`: no concrete paper deadline is available.

Unknown optional fields should be `null` or omitted only when the source cannot provide them. Never invent deadlines, ranks, URLs, or acceptance rates.

### ICS Format

When `--format ics` is used, the script outputs an iCalendar (ICS) document instead of JSON. Each result with at least one concrete (non-TBD) deadline generates a `VEVENT`:

- `SUMMARY`: conference title, e.g. "ICML 2026"
- `DTSTART`: deadline time in UTC (`20260129T115959Z`); AoE, PT, and other timezone labels are converted to UTC
- `DESCRIPTION`: description, deadline string with original timezone label, category, and CCF rank
- `URL`: conference URL, when available

Results with only TBD deadlines produce no VEVENT but still produce a valid (empty) calendar. Line endings follow the ICS standard (`\r\n`).

### Notes

The `notes` array on the envelope contains operational information such as:

- Cache fallback messages (e.g., "cache data was used").
- Domain preset mapping info when `--domain` is used, e.g. `domain preset 'cv' (Computer Vision) → categories AI,CG,MX`.
- Source fetch errors (e.g., "online fetch failed: ...").
