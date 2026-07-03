# CCFDDL Query — Trae Rule

**When to use:** User asks about conference deadlines, CCF/CORE/THCPL ranks, categories, upcoming submission windows, or research submission planning.

## Skill

Read `skills/ccfddl-query/SKILL.md` for full workflow instructions.

## Script

```bash
python skills/ccfddl-query/scripts/query_conferences.py list --status open --format json
```

- Always prefer `--format json` for agent consumption.
- Use `--format markdown` when displaying results to the user.

## Constraints

1. **Do not hallucinate** — never invent deadlines, ranks, URLs, or acceptance rates. All values must come from upstream `ccfddl` YAML data at `https://ccfddl.github.io/conference/allconf.yml`.
2. **JSON first** — structured output for agent reasoning, then convert to prose or markdown for the user.
3. **Categories** — ccfddl uses `sub` as the category field (e.g. AI, CG, MX). No separate category field exists.
4. **Fixture data** — use `--data-path skills/ccfddl-query/fixtures/allconf.sample.yml` for offline testing.
