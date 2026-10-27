"""Parity with the official ccf-deadlines CLI on the same data and time.

Needs a checkout of https://github.com/ccfddl/ccf-deadlines (``conference/``
and ``extensions/cli``) in ``CCFDDL_UPSTREAM``; skipped otherwise. The weekly
``upstream-parity`` workflow runs it against upstream main.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills" / "ccfddl-query" / "scripts" / "query_conferences.py"
UPSTREAM = os.environ.get("CCFDDL_UPSTREAM")

pytestmark = pytest.mark.skipif(
    not UPSTREAM, reason="set CCFDDL_UPSTREAM to a ccf-deadlines checkout"
)

# Includes US DST start/end and one minute either side of ACL 2027's deadline.
NOW_POINTS = [
    "2026-10-27T01:54:00Z",
    "2026-03-08T09:30:00Z",
    "2026-11-01T08:30:00Z",
    "2027-01-05T11:58:00Z",
    "2027-01-05T12:00:00Z",
]


@pytest.fixture(scope="module")
def snapshot(tmp_path_factory):
    data = []
    for path in sorted(Path(UPSTREAM, "conference").glob("*/*.yml")):
        data += yaml.safe_load(path.read_text(encoding="utf-8")) or []
    snap = tmp_path_factory.mktemp("upstream") / "allconf.yml"
    snap.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return data, snap


def official_open(data, now):
    sys.path.insert(0, str(Path(UPSTREAM, "extensions", "cli")))
    from ccfddl.fetch import process_conference_deadlines
    from ccfddl.models import Conference

    conferences = [Conference.from_dict(item) for item in data]
    return {
        row["id"]: row["deadline"].astimezone(timezone.utc)
        for row in process_conference_deadlines(conferences, now)
    }


def skill_open(snap, now_s, now):
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "list",
            "--status",
            "open",
            "--data-path",
            str(snap),
            "--now",
            now_s,
            "--format",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    result = {}
    for item in json.loads(proc.stdout)["results"]:
        upcoming = [
            datetime.fromisoformat(d["local_deadline"])
            for d in item["deadlines"]
            if d.get("local_deadline")
            and datetime.fromisoformat(d["local_deadline"]) >= now
        ]
        if upcoming:
            result[item["id"]] = min(upcoming).astimezone(timezone.utc)
    return result


@pytest.mark.parametrize("now_s", NOW_POINTS)
def test_open_venues_match_official_cli(snapshot, now_s):
    pytest.importorskip("requests")
    data, snap = snapshot
    now = datetime.fromisoformat(now_s.replace("Z", "+00:00"))

    official = official_open(data, now)
    mine = skill_open(snap, now_s, now)

    assert official, "official CLI found no open venues; check the checkout"
    mismatches = {
        key: (official.get(key), mine.get(key))
        for key in set(official) | set(mine)
        if official.get(key) != mine.get(key)
    }
    assert not mismatches, mismatches
