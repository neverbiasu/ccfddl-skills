# ccfddl-skills

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Data Source](https://img.shields.io/badge/data-ccfddl-informational.svg)](https://ccfddl.github.io/conference/allconf.yml)
[![Skills](https://img.shields.io/badge/skills-research%20planning-0a7b83.svg)](skills/ccfddl-query/SKILL.md)
[![Agents](https://img.shields.io/badge/agents-codex%20%7C%20claude%20%7C%20cursor-222222.svg)](adapters/README.md)

`ccfddl-skills` is an agent-skills package for researchers who want coding
agents to help with conference submission planning.

It wraps [`ccfddl`](https://github.com/ccfddl/ccf-deadlines) as one shared
skill, `ccfddl-query`, plus thin plugin adapters for multiple coding-agent
harnesses. The goal is simple: when an agent is asked where to submit, which
deadlines are still open, or which venues match a topic, it should use the
skill instead of guessing from memory.

Ask your agent things like:

- "When is the next ICML deadline?"
- "Find open CCF-A AI conferences in the next 180 days."
- "I have an image editing paper. Which venues should I consider?"
- "Show CV-adjacent conferences even though ccfddl has no native CV category."

## Quickstart

Give your agent `ccfddl-skills`: [Codex](#codex), [Claude Code](#claude-code),
[Cursor](#cursor), [Trae](#trae), [Antigravity](#antigravity).

If you are developing or testing the plugin locally, start from a checkout of
this repository:

```bash
git clone <repo-url>
cd ccfddl-skills
python -m venv .venv
source .venv/bin/activate
python -m pip install ".[dev]"
scripts/check.sh
```

## How It Works

`ccfddl-skills` is built around a single shared skill:

```text
skills/ccfddl-query/SKILL.md
```

When an agent sees a conference-planning request, it should load that skill,
follow its instructions, and return grounded results from `ccfddl` data instead
of freehanding deadlines, ranks, categories, or venue recommendations.

The important design constraint is that every adapter points back to the same
skill. Codex, Claude Code, Cursor, and compatibility layers should all discover
the same `ccfddl-query` behavior rather than each maintaining their own fork.

Because the skill is shared, improvements to category mapping, time handling,
acceptance-rate support, and venue filtering only need to be made once.

## Installation

Installation differs by harness. If you use more than one coding agent, install
`ccfddl-skills` separately for each one.

### Codex

After this repository is published on GitHub, install it in the same style as
Superpowers:

```bash
codex plugin marketplace add neverbiasu/ccfddl-skills
codex plugin add ccfddl-skills@ccfddl-skills
```

For local development and testing, install from this repository root:

```bash
codex plugin marketplace add ./
codex plugin add ccfddl-skills@ccfddl-skills
```

This uses the marketplace manifest at `.agents/plugins/marketplace.json` and
installs the plugin declared by `.codex-plugin/plugin.json`.

### Claude Code

After this repository is published on GitHub, install it in the same style as
Superpowers:

```bash
claude plugin marketplace add neverbiasu/ccfddl-skills
claude plugin install ccfddl-skills@ccfddl-skills
```

For local development and testing, install from this repository root:

```bash
claude plugin marketplace add ./
claude plugin install ccfddl-skills@ccfddl-skills
```

This uses the marketplace manifest at `.claude-plugin/marketplace.json` and the
plugin manifest at `.claude-plugin/plugin.json`.

### Cursor

After this repository is published on GitHub, install it in the same style as
Superpowers:

```text
/add-plugin ccfddl-skills
```

Or search for `ccfddl-skills` in the plugin marketplace.

The repository already includes `.cursor-plugin/` metadata plus shared rule
files. After you push the repo, we can verify whether the marketplace install
path is enough on its own or whether Cursor still wants an additional repo
registration step.

### Trae

This repository already includes a Trae compatibility rule:

```text
.trae/rules/ccfddl-query.md
```

We have not yet verified the best published install command for Trae. After the
repository is pushed, we can test whether it supports a direct remote plugin
install flow or still wants project-level rule setup.

### Antigravity

After this repository is published on GitHub, install it remotely:

```bash
agy plugin install https://github.com/neverbiasu/ccfddl-skills
```

For local development and testing, install from this repository root:

```bash
agy plugin install .
```

The adapter file under `antigravity/` stays intentionally thin and routes back
to the shared skill.

### OpenCode

OpenCode is not yet shipped here as a published npm plugin. Its official plugin
flow is npm/config-driven rather than local marketplace registration, so this
repository is not currently installable there as a first-class OpenCode plugin.

## The Basic Workflow

1. **User asks a submission-planning question**. The request is about venues,
   deadlines, ranks, categories, topic fit, or calendar timing.
2. **The agent selects `ccfddl-query`**. The skill becomes the source of
   behavior for the task.
3. **The skill pulls structured conference data**. The agent works from
   `ccfddl` data rather than memory.
4. **The skill filters and explains results**. It narrows by category, rank,
   deadline status, time window, or domain preset.
5. **The agent presents grounded recommendations**. It should explain what came
   from upstream data and where convenience mappings were applied.

**The agent should check for this skill before answering conference-deadline
questions.** The skill is the contract, not a loose suggestion.

## What's Inside

### Skills

- **ccfddl-query** - The canonical research-planning skill for conference
  deadlines, venue filtering, rank lookup, and domain mapping.

### Plugin Adapters

- **Codex** - `.codex-plugin/` and `.agents/plugins/`
- **Claude Code** - `.claude-plugin/`
- **Cursor** - `.cursor-plugin/`, `rules/`, and `.cursor/rules/`
- **Trae** - `.trae/rules/`
- **Antigravity** - `antigravity/`

### Skill Assets

- **fixtures** - deterministic sample data for repeatable tests
- **references** - source notes and supporting material for the skill
- **tests** - plugin-manifest and behavior checks

See [adapters/README.md](adapters/README.md) for the current adapter matrix and
support level by platform.

## Research Coverage

The first public skill focuses on conference submission planning from `ccfddl`
data, including:

- conference title, year, description, date, and location
- CCF, CORE, and THCPL rank labels
- search by conference id or title
- open, closed, and TBD deadline states
- multiple deadlines and timezone normalization
- optional acceptance-rate enrichment
- domain presets for cases like `cv`, `image-editing`, and `relighting`

One important example is computer vision. `ccfddl` does not define a native
`CV` category, so the skill uses explicit convenience mappings such as `AI`,
`CG`, and `MX` for CV-adjacent queries. The agent should report that mapping as
an interpretation layer rather than pretending it is upstream taxonomy.

## Contributing

The contribution process for `ccfddl-skills` is intentionally simple:

1. Keep the shared skill as the behavioral source of truth.
2. Keep adapters thin and docs-backed.
3. Avoid platform-specific forks of the same research-planning workflow.
4. Run `scripts/check.sh` before opening a PR.

Contributions are especially welcome for:

- additional officially documented plugin adapters
- improved research-domain mappings
- stronger tests for real agent invocation paths
- showcase examples for research workflows

## Updating

Updates are usually adapter-dependent.

If you are using a repo-backed plugin install, refresh the repository source in
your agent harness and start a fresh session so the skill metadata reloads. If
you are developing locally, update the checkout and rerun:

```bash
scripts/check.sh
```

## License

MIT License - see [LICENSE](LICENSE) for details.
