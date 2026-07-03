# Agent Guidance

Use existing implementations before inventing new ones.

- Preserve the upstream `ccfddl` YAML shape wherever possible.
- Use `PyYAML` for YAML parsing, consistent with `ccfddl/ccf-deadlines/scripts/merge.py`.
- Reuse upstream timezone semantics: `AoE` maps to `UTC-12`, `UTC` maps to `UTC+0`, and `PT` follows US Pacific daylight saving time.
- Keep `docs/` and `tasks/` out of submitted changes.
- Run lint, format checks, and tests before handing off.

The first skill is `skills/ccfddl-query/`.
