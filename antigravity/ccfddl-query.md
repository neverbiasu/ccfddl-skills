# CCFDDL Query — Antigravity Plugin

## When to use

Trigger this plugin when the user asks about conference deadlines, CCF/CORE/THCPL ranks, categories, upcoming submission windows, or research submission planning.

## Skill location

Read `skills/ccfddl-query/SKILL.md` for workflow, commands, and presentation rules.

## Script

```bash
python skills/ccfddl-query/scripts/query_conferences.py list --status open --format json
```

- Always prefer `--format json` for structured agent consumption.
- Convert JSON to prose or markdown for user display.

## Important

1. **No hallucination** — never invent deadlines, ranks, URLs, or acceptance rates. All values must come from upstream `ccfddl` YAML data (`https://ccfddl.github.io/conference/allconf.yml`).
2. **JSON first** — structured output before user-facing formatting.
3. **Category field** — ccfddl uses `sub` as the category field (e.g. AI, CG, MX).
4. **Fixture offline mode** — use `--data-path skills/ccfddl-query/fixtures/allconf.sample.yml` for testing without network.
