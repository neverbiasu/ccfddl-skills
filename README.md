# ccfddl Agent Skills

Agent Skills for helping researchers query `ccfddl` conference deadlines and decide where to submit.

The main product surface is the skill under `skills/ccfddl-query/`. The Python script is the deterministic execution layer used by agents for YAML loading, filtering, timezone conversion, and JSON/Markdown rendering.

## Layout

```text
.codex-plugin/
.claude-plugin/
.cursor-plugin/
skills/
  ccfddl-query/
    SKILL.md
    agents/openai.yaml
    scripts/query_conferences.py
    references/
    fixtures/
scripts/
tests/
rules/
```

Usage examples for common research submission scenarios are in `examples/`.

Local planning artifacts in `docs/` and `tasks/` are ignored and should not be submitted.

## Plugin Support

Implemented official plugin packaging:

- Codex: `.codex-plugin/plugin.json`
- Claude Code: `.claude-plugin/plugin.json`
- Cursor: `.cursor-plugin/plugin.json`

Implemented marketplace/catalog files:

- Codex repo marketplace: `.agents/plugins/marketplace.json`
- Claude Code marketplace: `.claude-plugin/marketplace.json`
- Cursor marketplace: `.cursor-plugin/marketplace.json`

Compatibility/project-level entries are also present for `.agents/plugins`, `.cursor/rules`, Trae, and Antigravity. See `adapters/README.md` for the current support matrix and planned platforms.

## Checks

```bash
python -m pip install PyYAML pytest ruff
scripts/check.sh
```

The query script depends on `PyYAML`, matching the upstream `ccfddl/ccf-deadlines` tooling.
