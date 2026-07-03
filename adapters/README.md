# Agent Adapter Matrix

Entry points for each supported coding-agent platform to discover, install, and invoke the single `ccfddl-query` skill.

This matrix distinguishes official plugin packaging from project-level rules. A rule file can help an agent in this repository, but it is not necessarily an installable plugin for that platform.

## Principle

Core query logic lives in one place only:
`skills/ccfddl-query/scripts/query_conferences.py`

Every platform adapter is a thin discovery/installation layer that references the same `skills/ccfddl-query/SKILL.md`. No adapter forks or duplicates query logic.

## Matrix

| Platform | Entry point | How it references `SKILL.md` | How it invokes `query_conferences.py` | Support level | Verification |
|---|---|---|---|---|---|
| **Codex plugin** | `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `skills/ccfddl-query/` | Manifest points Codex at `./skills/`; repo marketplace exposes the plugin under `ccfddl-skills` | Agent reads `SKILL.md` commands and runs `python .../query_conferences.py` via shell tool | **implemented** | Codex plugin validator passes |
| **Claude Code plugin** | `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `skills/ccfddl-query/` | Claude loads plugin root components; marketplace exposes the plugin from `./` | Agent reads `SKILL.md` commands and runs `python .../query_conferences.py` via Bash tool | **implemented** | Claude plugin and marketplace structure follows official docs |
| **Cursor plugin** | `.cursor-plugin/plugin.json`, `.cursor-plugin/marketplace.json`, `skills/ccfddl-query/`, `rules/ccfddl-query.mdc` | Cursor plugin manifest exposes `skills/` and `rules/`; marketplace lists this repo root as the plugin source | Same CLI invocation referenced from skill and rule | **implemented** | Cursor plugin and marketplace structure follows official docs |
| **Generic agents / Superpowers-style** | `.agents/plugins/ccfddl-query.md` | Plugin rule points agents to the canonical `skills/ccfddl-query/SKILL.md` | Same CLI invocation referenced from plugin rules | **implemented** | Agent loads `.agents/plugins/ccfddl-query.md` and runs a query |
| **Cursor project rule** | `.cursor/rules/ccfddl-query.mdc` | Project-level rule points to the same canonical skill | Same CLI invocation referenced from rules | **compatibility** | Cursor can use it inside this repository |
| **Antigravity** | `antigravity/ccfddl-query.md` | Markdown rule points to `skills/ccfddl-query/SKILL.md` | Same CLI invocation referenced from rules | **compatibility** | Needs official plugin manifest pass |
| **Trae** | `.trae/rules/ccfddl-query.md` | Trae rule points to `skills/ccfddl-query/SKILL.md` | Same CLI invocation referenced from rules | **compatibility** | Needs official plugin package pass |
| **OpenCode** | none yet | Official plugins are JS/TS modules under `.opencode/plugins/` | Could expose a custom tool or hook that delegates to the Python script | **planned** | Build after higher-priority plugin manifests |
| **Kimi / Cline / OpenHands / GitHub Copilot / Factory** | none yet | Needs official docs pass before adding files | TBD | **planned** | Track in KANBAN |

## Shared contract

All adapters agree on the following invariants:

1. **Single source of truth**: `skills/ccfddl-query/scripts/query_conferences.py` is the only execution layer.
2. **Reference, don't fork**: adapters reference `skills/ccfddl-query/SKILL.md`; they never copy its workflow instructions.
3. **JSON-first output**: agent-to-agent communication prefers `--format json` for structured consumption; Markdown tables are for human display.
4. **No hallucination**: agents must not invent deadlines, ranks, URLs, or acceptance rates. All values come from upstream `ccfddl` YAML data.
5. **Data source**: upstream data lives at `https://ccfddl.github.io/conference/allconf.yml`; the script caches locally and falls back to fixture data (`skills/ccfddl-query/fixtures/allconf.sample.yml`).

## When to use ccfddl-query

Use this skill whenever a user asks about:
- Conference deadlines (e.g., "When is the ICML deadline?")
- Submission windows (e.g., "Which AI conferences are still open?")
- Conference ranks or categories (e.g., "What are the CCF-A graphics conferences?")
- Research submission planning (e.g., "I have a CV paper, where should I submit?")

## Current status

- **Codex**: implemented — `.codex-plugin/plugin.json` + skill folder + OpenAI GPT agent config (`agents/openai.yaml`).
- **Codex marketplace**: implemented — `.agents/plugins/marketplace.json` exposes the repo-root plugin as a local repo marketplace entry.
- **Claude Code**: implemented — `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` + `skills/`.
- **Cursor**: implemented as a real plugin — `.cursor-plugin/plugin.json` + `.cursor-plugin/marketplace.json` + `skills/` + `rules/`; `.cursor/rules/` remains as a project-level compatibility rule.
- **Generic agents / Superpowers-style**: implemented — `.agents/plugins/ccfddl-query.md` references the canonical skill and shared CLI.
- **Antigravity and Trae**: compatibility rules exist; official plugin packaging still needs a docs-backed pass.
- **OpenCode, Kimi, Cline, OpenHands, GitHub Copilot, Factory**: planned; do not treat as implemented plugin support yet.

## Sources Checked

- Codex plugins: https://developers.openai.com/codex/plugins and https://developers.openai.com/codex/plugins/build
- Codex marketplace/workspace sharing: https://developers.openai.com/codex/plugins/build?install-scope=workspace
- Claude Code plugins and marketplaces: https://code.claude.com/docs/en/plugins and https://code.claude.com/docs/zh-CN/plugin-marketplaces
- Cursor plugins, skills, and marketplace manifests: https://cursor.com/docs/plugins.md, https://cursor.com/docs/skills.md, and https://cursor.com/docs/reference/plugins.md
- OpenCode plugins: https://opencode.ai/docs/plugins/
