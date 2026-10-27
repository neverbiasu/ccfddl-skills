# Changelog

All notable changes to this project are documented here. This project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Fixed
- The skill no longer lets an agent say a conference is missing from ccfddl because filtered results left it out. It must confirm with an unfiltered `search` first, and name the filter that excluded a venue (for example, IJCAI 2027 is CCF-B, so it is not in CCF-A results). Ranks come from ccfddl data, not from memory.

## [1.0.1] - 2026-10-22

### Fixed
- Queries no longer silently use a stale local cache. A cache older than 24 hours is refreshed before querying; if the refresh fails, the old cache is used with a warning that shows its date and age.
- Answers keep the original deadline time and timezone, and explain AoE on first use.

### Added
- ccfddl-query evals, a live-data demo, CI, CONTRIBUTING and issue templates.

## [1.0.0]

- First public release: the `ccfddl-query` skill with adapters for Codex, Claude Code, Cursor, Trae and Antigravity.
