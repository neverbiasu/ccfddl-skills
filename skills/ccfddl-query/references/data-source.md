# Data Source

Use the upstream `ccfddl` static YAML data as the source of truth.

- Production merged YAML: `https://ccfddl.github.io/conference/allconf.yml`
- Upstream repository: `https://github.com/ccfddl/ccf-deadlines`
- Schema file: `conference-yaml-schema.yml`
- Category files: `conference/<category>/<conference>.yml`
- Upstream merge script: `scripts/merge.py`

The upstream merge script uses `yaml.safe_load`; this skill follows the same approach with `PyYAML`.

Runtime policy:

- Fetch online data by default for freshness.
- Fall back to a local cache when online fetch fails.
- Use committed fixtures for tests.
- Do not maintain a hand-edited full conference dataset in this repository.

Timezone policy follows the upstream TUI:

- `AoE` means `UTC-12`.
- `UTC` means `UTC+0`.
- `PT` resolves to `UTC-7` during US daylight saving time and `UTC-8` otherwise.

## Acceptance Rates

ccfddl includes an `accept_rates/` directory with per-conference acceptance-rate history:

- Repository location: `https://github.com/ccfddl/ccf-deadlines/tree/main/accept_rates`
- Format: each file is a YAML list; every item has a `title` field matching a conference in `allconf.yml` and an `accept_rates` list with entries per year.
- Availability: data may be incomplete or outdated. Not every conference has entry.
- Usage: pass `--accept-rates-path <file>` to the `list` or `search` subcommand.
- When no matching data is found, the output field `acceptance_rates` is `[]`.
- The current script accepts one accept_rates YAML file shaped like the upstream files; callers may pass an upstream per-conference file or a separately merged file with the same top-level list format.
- Never invent acceptance rates.

### ICS / Calendar Export

The `--format ics` flag outputs iCalendar (ICS) text. Times are converted to UTC. The original timezone label (AoE, PT, UTC+0, etc.) is preserved in each VEVENT's DESCRIPTION field. Results with TBD-only deadlines produce an empty calendar.
