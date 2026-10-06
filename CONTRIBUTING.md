# Contributing

Thanks for helping. `skills/ccfddl-query/` is the single source of behavior; adapters stay thin.

## Before you open a pull request
1. Open an issue first for anything larger than a typo or a bug fix.
2. Run `scripts/check.sh` (pytest, ruff, black). CI runs the same script.
3. If you changed `SKILL.md`, re-run its evals with `./run_evals.sh` and update `last_run` in `skills/ccfddl-query/evals/evals.json` with the real result, date and agent.
4. Use [Conventional Commits](https://www.conventionalcommits.org/) and keep one change per commit.

## What gets accepted
- Fixes to deadline, timezone, rank or status handling, with a test in `tests/`.
- Research-domain mappings in `references/domain-mapping.md` that name the ccfddl categories they map to.
- Adapters for agents with an officially documented plugin or rules format.

## What does not
- Platform-specific forks of the skill's workflow. Change the shared skill instead.
- Conference data fixes. Send those upstream to [ccfddl/ccf-deadlines](https://github.com/ccfddl/ccf-deadlines).
- Evidence that did not happen: eval results, usage rows or demos written to pass a check.
