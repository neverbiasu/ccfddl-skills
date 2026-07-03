from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "ccfddl-query" / "scripts" / "query_conferences.py"
FIXTURE = ROOT / "skills" / "ccfddl-query" / "fixtures" / "allconf.sample.yml"


def load_module():
    spec = importlib.util.spec_from_file_location("query_conferences", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_parse_and_flatten_fixture():
    module = load_module()
    conferences = module.parse_conferences(FIXTURE.read_text(encoding="utf-8"))
    results = module.flatten_conferences(
        conferences,
        now=datetime(2026, 7, 3, tzinfo=timezone.utc),
    )

    icml = next(item for item in results if item["id"] == "icml26")
    assert icml["conference"] == "ICML"
    assert icml["category"] == "AI"
    assert icml["rank"]["ccf"] == "A"
    assert icml["status"] == "closed"
    assert icml["dblp"] == "https://dblp.org/db/conf/icml"


def test_filters_compose_category_rank_and_window():
    module = load_module()
    conferences = module.parse_conferences(FIXTURE.read_text(encoding="utf-8"))
    results = module.flatten_conferences(
        conferences,
        now=datetime(2026, 7, 3, tzinfo=timezone.utc),
    )

    filtered = module.apply_filters(
        results,
        module.QueryFilters(
            categories=["AI"], ccf_ranks=["A"], within_days=90
        ),
    )

    assert [item["id"] for item in filtered] == ["aifuture26"]


def test_aoe_and_pt_timezone_handling():
    module = load_module()

    aoe = module.timezone_offset("AoE", datetime(2025, 9, 11))
    pt_summer = module.timezone_offset("PT", datetime(2026, 7, 1))
    pt_winter = module.timezone_offset("PT", datetime(2026, 1, 1))

    assert aoe.utcoffset(None).total_seconds() == -12 * 3600
    assert pt_summer.utcoffset(None).total_seconds() == -7 * 3600
    assert pt_winter.utcoffset(None).total_seconds() == -8 * 3600


def test_cli_json_search():
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "search",
            "--data-path",
            str(FIXTURE),
            "--query",
            "ICML",
            "--now",
            "2026-07-03T00:00:00+00:00",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    assert payload["count"] == 1
    assert payload["results"][0]["id"] == "icml26"
    assert payload["results"][0]["status"] == "closed"


def test_short_search_does_not_match_inside_description_words():
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "search",
            "--data-path",
            str(FIXTURE),
            "--query",
            "CHI",
            "--now",
            "2026-07-03T00:00:00+00:00",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    assert payload["count"] == 1
    assert payload["results"][0]["id"] == "chi26"


def test_cli_markdown_list():
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "list",
            "--data-path",
            str(FIXTURE),
            "--category",
            "HI",
            "--format",
            "markdown",
            "--now",
            "2025-08-01T00:00:00+00:00",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "| CHI 2026 |" in proc.stdout


def test_agent_workflow_lists_upcoming_ai_ccf_a_conferences():
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "list",
            "--data-path",
            str(FIXTURE),
            "--category",
            "AI",
            "--ccf-rank",
            "A",
            "--status",
            "open",
            "--within-days",
            "90",
            "--now",
            "2026-07-03T00:00:00+00:00",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(proc.stdout)
    assert payload["count"] == 1

    result = payload["results"][0]
    assert result["conference"] == "AIFUTURE"
    assert result["rank"]["ccf"] == "A"
    assert result["category"] == "AI"
    assert result["status"] == "open"
    assert result["days_to_deadline"] == 44
    assert result["deadlines"][0]["local_deadline"] is not None


def test_domain_cv_returns_only_ai_cg_mx():
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "list",
            "--data-path",
            str(FIXTURE),
            "--domain",
            "cv",
            "--status",
            "open",
            "--now",
            "2026-07-03T00:00:00+00:00",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    assert payload["count"] >= 1
    allowed = {"AI", "CG", "MX"}
    for result in payload["results"]:
        assert result["category"] in allowed, (
            f"conference {result['id']} has category "
            f"{result['category']} not in {allowed}"
        )
    assert any(r["category"] == "CG" for r in payload["results"])
    assert any(r["category"] == "MX" for r in payload["results"])


def test_domain_image_editing_avoids_nonexistent_cv():
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "list",
            "--data-path",
            str(FIXTURE),
            "--domain",
            "image-editing",
            "--status",
            "open",
            "--now",
            "2026-07-03T00:00:00+00:00",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    for result in payload["results"]:
        assert result["category"] != "CV", (
            f"conference {result['id']} has category 'CV' "
            "which should not exist"
        )
    assert any(
        "domain preset" in note and "image-editing" in note
        for note in payload["notes"]
    )


def test_domain_relighting_includes_mapping_notes():
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "list",
            "--data-path",
            str(FIXTURE),
            "--domain",
            "relighting",
            "--status",
            "open",
            "--now",
            "2026-07-03T00:00:00+00:00",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    mapping_note = next(
        (note for note in payload["notes"] if "domain preset" in note),
        None,
    )
    assert (
        mapping_note is not None
    ), "no domain-preset note found in JSON output"
    assert "relighting" in mapping_note
    assert "categories" in mapping_note
    assert (
        "AI" in mapping_note and "CG" in mapping_note and "MX" in mapping_note
    )


def test_accept_rates_not_loaded_when_not_requested():
    """Without --accept-rates-path, acceptance_rates is [] for all results."""
    module = load_module()
    conferences = module.parse_conferences(FIXTURE.read_text(encoding="utf-8"))
    results = module.flatten_conferences(
        conferences,
        now=datetime(2026, 7, 3, tzinfo=timezone.utc),
    )
    for item in results:
        assert (
            item.get("acceptance_rates") == []
        ), f"{item['id']} should have empty acceptance_rates"


def test_accept_rates_loaded_from_fixture():
    """With --accept-rates-path, matching conferences get populated."""
    accept_rates_fixture = (
        ROOT
        / "skills"
        / "ccfddl-query"
        / "fixtures"
        / "accept_rates.sample.yml"
    )
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "list",
            "--data-path",
            str(FIXTURE),
            "--accept-rates-path",
            str(accept_rates_fixture),
            "--now",
            "2026-07-03T00:00:00+00:00",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)

    icml = next(item for item in payload["results"] if item["id"] == "icml26")
    assert len(icml["acceptance_rates"]) >= 1
    assert icml["acceptance_rates"][0]["year"] == 2024
    assert icml["acceptance_rates"][0]["submitted"] == 9473
    assert icml["acceptance_rates"][0]["rate"] == 0.2754

    chi = next(item for item in payload["results"] if item["id"] == "chi26")
    assert chi["acceptance_rates"] == []


def test_accept_rates_merge_via_search():
    """Search subcommand also supports --accept-rates-path."""
    accept_rates_fixture = (
        ROOT
        / "skills"
        / "ccfddl-query"
        / "fixtures"
        / "accept_rates.sample.yml"
    )
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "search",
            "--data-path",
            str(FIXTURE),
            "--accept-rates-path",
            str(accept_rates_fixture),
            "--query",
            "ICML",
            "--now",
            "2026-07-03T00:00:00+00:00",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    assert payload["count"] == 1
    assert payload["results"][0]["acceptance_rates"][0]["year"] == 2024


def test_ics_output_has_valid_structure():
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "search",
            "--data-path",
            str(FIXTURE),
            "--query",
            "CHI",
            "--format",
            "ics",
            "--now",
            "2025-08-01T00:00:00+00:00",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    stdout = proc.stdout
    assert stdout.startswith("BEGIN:VCALENDAR")
    assert stdout.rstrip().endswith("END:VCALENDAR")
    assert "BEGIN:VEVENT" in stdout
    assert "END:VEVENT" in stdout
    assert "SUMMARY:CHI 2026" in stdout
    assert "SUMMARY:ICML 2026" not in stdout
    assert "DTSTART:" in stdout
    assert "DESCRIPTION:" in stdout
    assert "URL:" in stdout


def test_ics_skips_tbd_deadlines():
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "search",
            "--data-path",
            str(FIXTURE),
            "--query",
            "FUTURETBD",
            "--format",
            "ics",
            "--now",
            "2025-08-01T00:00:00+00:00",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    stdout = proc.stdout
    assert stdout.startswith("BEGIN:VCALENDAR")
    assert stdout.rstrip().endswith("END:VCALENDAR")
    assert "VEVENT" not in stdout


def test_ics_aoe_converts_to_utc():
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "search",
            "--data-path",
            str(FIXTURE),
            "--query",
            "CHI",
            "--format",
            "ics",
            "--now",
            "2025-08-01T00:00:00+00:00",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    # CHI deadline: 2025-09-11 23:59:59 AoE (UTC-12)
    # UTC: 2025-09-12 11:59:59
    assert "20250912T115959Z" in proc.stdout


def test_ics_list_with_domain_preset():
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "list",
            "--data-path",
            str(FIXTURE),
            "--domain",
            "cv",
            "--status",
            "open",
            "--format",
            "ics",
            "--now",
            "2026-07-03T00:00:00+00:00",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    stdout = proc.stdout
    assert stdout.startswith("BEGIN:VCALENDAR")
    assert stdout.rstrip().endswith("END:VCALENDAR")
    # Should have events for AIFUTURE, CGFUTURE, and MXFUTURE.
    assert "SUMMARY:AIFUTURE 2026" in stdout
    assert "SUMMARY:CGFUTURE 2026" in stdout
    assert "SUMMARY:MXFUTURE 2026" in stdout


def test_ics_search_multiple_matches():
    """List all AI conferences and verify multiple VEVENTs produced."""
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "list",
            "--data-path",
            str(FIXTURE),
            "--category",
            "AI",
            "--format",
            "ics",
            "--now",
            "2026-07-03T00:00:00+00:00",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    stdout = proc.stdout
    assert stdout.count("BEGIN:VEVENT") == 2  # ICML (closed) + AIFUTURE (open)
    assert stdout.count("END:VEVENT") == 2


def test_live_allconf_smoke_when_enabled(tmp_path):
    if os.environ.get("CCFDDL_LIVE_TEST") != "1":
        return

    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "list",
            "--limit",
            "3",
            "--cache-path",
            str(tmp_path / "allconf.yml"),
            "--now",
            "2026-07-03T00:00:00+00:00",
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )

    payload = json.loads(proc.stdout)
    assert payload["count"] >= 1
    assert payload["source"].startswith("https://ccfddl.github.io/")
    for item in payload["results"]:
        assert {"id", "conference", "rank", "deadlines", "status"}.issubset(
            item
        )
