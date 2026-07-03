# ccfddl-skills

`ccfddl-skills` packages the static
[`ccfddl`](https://github.com/ccfddl/ccf-deadlines) conference-deadline data as
agent skills and plugins for research submission planning.

Ask your coding agent things like:

- "When is the next ICML deadline?"
- "Find open CCF-A AI conferences in the next 180 days."
- "I have an image editing paper. Which CV-related venues should I consider?"

The agent uses deterministic YAML parsing and filtering. It should not invent
deadlines, ranks, URLs, or acceptance rates.

## Quickstart

Install development dependencies:

```bash
python -m pip install ".[dev]"
```

Run a query against live `ccfddl` data:

```bash
python skills/ccfddl-query/scripts/query_conferences.py \
  list \
  --domain cv \
  --status open \
  --within-days 180 \
  --format json
```

Use fixture data when you want deterministic offline output:

```bash
python skills/ccfddl-query/scripts/query_conferences.py \
  search \
  --data-path skills/ccfddl-query/fixtures/allconf.sample.yml \
  --query ICML \
  --format json
```

## How It Works

The core implementation is a small Python CLI at
`skills/ccfddl-query/scripts/query_conferences.py`.

It:

1. Fetches `https://ccfddl.github.io/conference/allconf.yml`.
2. Falls back to a local cache when the network is unavailable.
3. Parses the upstream YAML shape with `PyYAML`.
4. Flattens conference-year records into agent-friendly JSON.
5. Filters by search query, ccfddl category, rank, status, deadline window, or
   research-domain preset.
6. Renders JSON, Markdown, or ICS calendar output.

The skill instructions in `skills/ccfddl-query/SKILL.md` tell agents when to
call the CLI and how to explain results to users.

## Installation

The repository includes first-class plugin manifests for the agent platforms
that currently have clear local plugin/marketplace formats.

### Codex

- Plugin manifest: `.codex-plugin/plugin.json`
- Repo marketplace: `.agents/plugins/marketplace.json`
- Skill: `skills/ccfddl-query/SKILL.md`

### Claude Code

- Plugin manifest: `.claude-plugin/plugin.json`
- Marketplace manifest: `.claude-plugin/marketplace.json`
- Skill: `skills/ccfddl-query/SKILL.md`

### Cursor

- Plugin manifest: `.cursor-plugin/plugin.json`
- Marketplace manifest: `.cursor-plugin/marketplace.json`
- Plugin rule: `rules/ccfddl-query.mdc`
- Compatibility project rule: `.cursor/rules/ccfddl-query.mdc`

### Compatibility Entrypoints

Thin compatibility instructions are also present for:

- `.agents/plugins/ccfddl-query.md`
- `.trae/rules/ccfddl-query.md`
- `antigravity/ccfddl-query.md`

See `adapters/README.md` for the support matrix and planned platforms.

## What's Inside

```text
.agents/plugins/
.claude-plugin/
.codex-plugin/
.cursor-plugin/
.cursor/
.trae/
adapters/
antigravity/
examples/
rules/
scripts/
skills/
tests/
package.json
pyproject.toml
```

The public product surface is the `ccfddl-query` skill:

```text
skills/ccfddl-query/
  SKILL.md
  agents/openai.yaml
  fixtures/
  references/
  scripts/query_conferences.py
```

Local planning material lives under `docs/` and `tasks/`; both are ignored and
not part of the published repository.

## Domain Presets

`ccfddl` does not have a native `CV` category. This project provides a small
agent-side mapping layer:

- `cv` / `computer-vision` -> `AI`, `CG`, `MX`
- `image-editing` -> `AI`, `CG`, `MX`
- `relighting` -> `AI`, `CG`, `MX`

The output notes always explain that these are convenience mappings, not
upstream categories.

## Testing

Tests are split by purpose:

- `tests/python/` checks the query CLI and data transformations.
- `tests/plugins/` checks plugin and marketplace manifests.

Run everything:

```bash
scripts/check.sh
```

The check script runs:

1. `pytest`
2. `ruff check .`
3. `black --check .`

Additional validators used before release:

```bash
.venv/bin/python /Users/nev4rb14su/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
.venv/bin/python /Users/nev4rb14su/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/ccfddl-query
```

## Design Constraints

- Reuse upstream `ccfddl` YAML shape wherever possible.
- Keep query behavior deterministic and testable.
- Keep adapter layers thin; do not fork query logic per agent.
- Prefer JSON for agent reasoning and Markdown for human display.
- Never invent missing conference metadata.

## License

MIT. See `LICENSE`.
