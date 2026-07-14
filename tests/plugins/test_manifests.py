from __future__ import annotations

import json
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[2]


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_version_is_consistent_across_plugin_manifests():
    pyproject = tomllib.loads(
        (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )
    expected = pyproject["project"]["version"]

    version_paths = [
        ("package.json", ["version"]),
        (".codex-plugin/plugin.json", ["version"]),
        (".claude-plugin/plugin.json", ["version"]),
        (".cursor-plugin/plugin.json", ["version"]),
        (".claude-plugin/marketplace.json", ["plugins", 0, "version"]),
        (".cursor-plugin/marketplace.json", ["metadata", "version"]),
        (".cursor-plugin/marketplace.json", ["plugins", 0, "version"]),
    ]

    for path, keys in version_paths:
        payload = read_json(path)
        value = payload
        for key in keys:
            value = value[key]
        assert value == expected, f"{path} has version {value}"


def test_codex_plugin_manifest_points_to_skills():
    manifest = read_json(".codex-plugin/plugin.json")
    assert manifest["name"] == "ccfddl-skills"
    assert manifest["skills"] == "./skills/"
    assert manifest["interface"]["displayName"] == "CCFDDL Skills"


def test_marketplaces_point_at_repo_root_plugin():
    codex = read_json(".agents/plugins/marketplace.json")
    claude = read_json(".claude-plugin/marketplace.json")
    cursor = read_json(".cursor-plugin/marketplace.json")

    assert codex["plugins"][0]["source"] == {
        "source": "url",
        "url": "./",
    }
    assert claude["plugins"][0]["source"] == "./"
    assert cursor["plugins"][0]["source"] == "."


def test_cursor_plugin_exposes_skills_and_rules():
    manifest = read_json(".cursor-plugin/plugin.json")
    assert manifest["skills"] == "./skills/"
    assert manifest["rules"] == "./rules/"
    assert (ROOT / "rules" / "ccfddl-query.mdc").exists()


def test_required_public_files_exist():
    for path in [
        "README.md",
        "LICENSE",
        "CODE_OF_CONDUCT.md",
        ".gitattributes",
        ".pre-commit-config.yaml",
        ".version-bump.json",
        "skills/ccfddl-query/SKILL.md",
        "skills/ccfddl-query/scripts/query_conferences.py",
        "skills/ccfddl-query/scripts/query_conferences_impl.py",
        "ccfddl_skills/__init__.py",
        "ccfddl_skills/query_conferences.py",
    ]:
        assert (ROOT / path).exists(), f"{path} is missing"


def test_package_exposes_installable_cli():
    pyproject = tomllib.loads(
        (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    )
    assert pyproject["tool"]["setuptools"]["packages"] == ["ccfddl_skills"]
    assert (
        pyproject["project"]["scripts"]["ccfddl-query"]
        == "ccfddl_skills.query_conferences:main"
    )
