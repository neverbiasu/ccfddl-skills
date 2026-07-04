# ccfddl-skills

Agent skills and plugins for querying
[`ccfddl`](https://github.com/ccfddl/ccf-deadlines) conference-deadline data.

`ccfddl-skills` helps coding agents answer research-planning questions such as:

- "When is the next ICML deadline?"
- "Find open CCF-A AI conferences in the next 180 days."
- "I have an image editing paper. Which CV-related venues should I consider?"

The project intentionally keeps the reasoning layer thin. Agents call a
deterministic Python CLI, receive structured JSON or Markdown, and should never
invent deadlines, ranks, locations, DBLP links, or acceptance rates.

## Status

Current release: `1.0.0`

The first release focuses on one production-ready skill:

- `ccfddl-query`: fetch, parse, filter, and render `ccfddl` conference data.

## Install

Clone the repository and install the Python package:

```bash
git clone https://github.com/neverbiasu/ccfddl-skills.git
cd ccfddl-skills
python -m venv .venv
source .venv/bin/activate
python -m pip install ".[dev]"
```

Confirm the command is available:

```bash
ccfddl-query --help
```

Run a deterministic offline query:

```bash
ccfddl-query search \
  --data-path skills/ccfddl-query/fixtures/allconf.sample.yml \
  --query ICML \
  --format json
```

Run against live `ccfddl` data:

```bash
ccfddl-query list \
  --domain cv \
  --status open \
  --within-days 180 \
  --format json
```

## Agent Support

The repository is organized like an agent-skill/plugin distribution. The shared
skill lives in `skills/ccfddl-query/SKILL.md`; platform adapters stay thin and
point back to that single implementation.

| Platform | Status | Files |
|---|---:|---|
| Codex | supported | `.codex-plugin/`, `.agents/plugins/` |
| Claude Code | supported | `.claude-plugin/` |
| Cursor | supported | `.cursor-plugin/`, `.cursor/rules/`, `rules/` |
| Trae | compatibility rules | `.trae/rules/` |
| Antigravity | compatibility instructions | `antigravity/` |
| OpenCode, Cline, OpenHands, Kimi, Factory | planned | `adapters/README.md` |

Marketplace manifests are included for platforms that expose a documented
marketplace or plugin index format in this repo layout:

- Codex: `.agents/plugins/marketplace.json`
- Claude Code: `.claude-plugin/marketplace.json`
- Cursor: `.cursor-plugin/marketplace.json`

After publishing the repository, point the corresponding agent marketplace or
plugin installer at the repository root, then enable the `ccfddl-query` skill.

## Usage

The installable CLI is `ccfddl-query`.

Search by conference id or title:

```bash
ccfddl-query search --query ICML --format markdown
```

List open CCF-A AI conferences:

```bash
ccfddl-query list \
  --category AI \
  --ccf-rank A \
  --status open \
  --within-days 180
```

Find computer-vision-adjacent venues:

```bash
ccfddl-query list --domain cv --status open
```

Render calendar data:

```bash
ccfddl-query list --domain image-editing --status open --format ics
```

The source-compatible script path remains available for agents that execute
tools from the skill directory directly:

```bash
python skills/ccfddl-query/scripts/query_conferences.py list --domain cv
```

## Data Model

By default, the CLI fetches:

```text
https://ccfddl.github.io/conference/allconf.yml
```

It caches the file at:

```text
~/.cache/ccfddl-skills/allconf.yml
```

Use `--data-path` for offline or deterministic runs. The parser follows the
upstream `ccfddl` YAML shape and flattens conference-year records into
agent-friendly result objects with:

- conference id, title, year, description, date, and place
- CCF, CORE, and THCPL ranks
- DBLP and conference URLs when available
- normalized deadline status: `open`, `closed`, or `tbd`
- local deadline timestamps and timezone notes
- optional acceptance-rate data when `--accept-rates-path` is provided

## Domain Presets

`ccfddl` does not have a native `CV` category. This project provides a small
agent-side mapping layer for common research questions:

- `cv` / `computer-vision` -> `AI`, `CG`, `MX`
- `image-editing` -> `AI`, `CG`, `MX`
- `relighting` -> `AI`, `CG`, `MX`

JSON output includes notes explaining that these are convenience mappings, not
upstream categories.

## Repository Layout

```text
.agents/plugins/              Codex-style repo marketplace metadata
.claude-plugin/               Claude Code plugin and marketplace manifests
.codex-plugin/                Codex plugin manifest
.cursor-plugin/               Cursor plugin and marketplace manifests
.cursor/rules/                Cursor compatibility rule
.trae/rules/                  Trae compatibility rule
adapters/                     Platform support matrix and adapter notes
antigravity/                  Antigravity compatibility instruction
ccfddl_skills/                Installable Python package
examples/                     Example prompts and expected workflows
rules/                        Shared agent rule files
scripts/                      Maintainer scripts
skills/ccfddl-query/          Agent skill, references, fixtures, CLI wrapper
tests/python/                 Query and data transformation tests
tests/plugins/                Plugin and marketplace manifest tests
```

Local planning material can live under `docs/` and `tasks/`; both are ignored
and are not part of the published package.

## Test

Run the full local check:

```bash
scripts/check.sh
```

This runs:

- `pytest`
- `ruff check .`
- `black --check .`

Run the optional live smoke test when you want to verify the current upstream
`allconf.yml` endpoint:

```bash
CCFDDL_LIVE_TEST=1 pytest tests/python/test_query_conferences.py
```

Run an install smoke test from a clean virtual environment:

```bash
python -m venv /tmp/ccfddl-skills-install-test
/tmp/ccfddl-skills-install-test/bin/python -m pip install .
/tmp/ccfddl-skills-install-test/bin/ccfddl-query search \
  --data-path skills/ccfddl-query/fixtures/allconf.sample.yml \
  --query ICML
```

If you have the platform validator tools installed locally, run them before a
release against the repository root and `skills/ccfddl-query`.

## Design Constraints

- Reuse upstream `ccfddl` YAML shape wherever possible.
- Keep query behavior deterministic and testable.
- Keep adapter layers thin; do not fork query logic per agent.
- Prefer JSON for agent reasoning and Markdown for human display.
- Never invent missing conference metadata.

## Contributing

Contributions are welcome, especially:

- new platform adapters backed by official plugin/skill documentation
- better domain presets for research areas
- parser support for additional upstream `ccfddl` metadata
- showcase prompts for real research submission workflows

Please run `scripts/check.sh` before opening a pull request.

## License

MIT. See `LICENSE`.
