# Changelog

All notable changes to this project are documented here. This project follows [Semantic Versioning](https://semver.org/).

## [1.0.1] - 2026-10-22

### Fixed
- Queries no longer silently use a stale local cache. A cache older than 24 hours is refreshed before querying; if the refresh fails, the old cache is used with a warning that shows its date and age.
- Answers keep the original deadline time and timezone, and explain AoE on first use.

### Added
- ccfddl-query evals, a live-data demo, CI, CONTRIBUTING and issue templates.

## [1.0.0]

- First public release: the `ccfddl-query` skill with adapters for Codex, Claude Code, Cursor, Trae and Antigravity.
