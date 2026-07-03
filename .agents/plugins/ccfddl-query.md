# CCFDDL Query Agent Plugin

## When to Use

Use this plugin when the user asks about conference deadlines, CCF/CORE/THCPL ranks, categories, upcoming submission windows, or research submission planning.

## Canonical Skill

Read `skills/ccfddl-query/SKILL.md` first. It is the single source of truth for workflow, query commands, output interpretation, and safety rules.

## Execution Layer

Run the shared query script:

```bash
python skills/ccfddl-query/scripts/query_conferences.py list --status open --format json
```

Prefer `--format json` for agent reasoning. Use `--format markdown` only when presenting tables to a human.

## Rules

1. Do not invent deadlines, ranks, URLs, or acceptance rates.
2. Preserve the upstream `ccfddl` YAML semantics.
3. Treat `sub` as the ccfddl category field, such as `AI`, `CG`, `HI`, or `MX`.
4. Use `--data-path skills/ccfddl-query/fixtures/allconf.sample.yml` for offline tests.
5. For CV, Image Editing, or Relighting queries, use the domain mapping in `skills/ccfddl-query/references/domain-mapping.md` instead of assuming a native `CV` category exists.
