#!/usr/bin/env python3
"""Query ccfddl conference YAML for agent workflows."""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    import yaml
except (
    ImportError
) as exc:  # pragma: no cover - exercised only without dependency installed
    raise SystemExit(
        "PyYAML is required. Install with `python -m pip install PyYAML`."
    ) from exc


DEFAULT_URL = "https://ccfddl.github.io/conference/allconf.yml"
DEFAULT_CACHE = Path.home() / ".cache" / "ccfddl-skills" / "allconf.yml"
DBLP_PREFIX = "https://dblp.org/db/conf/"

DOMAIN_MAP: Dict[str, Dict[str, Any]] = {
    "cv": {"categories": ["AI", "CG", "MX"], "domain_name": "Computer Vision"},
    "computer-vision": {
        "categories": ["AI", "CG", "MX"],
        "domain_name": "Computer Vision",
    },
    "image-editing": {
        "categories": ["AI", "CG", "MX"],
        "domain_name": "Image Editing",
    },
    "relighting": {
        "categories": ["AI", "CG", "MX"],
        "domain_name": "Relighting",
    },
}


@dataclass
class SourceData:
    text: str
    label: str
    cache_used: bool = False
    notes: Optional[List[str]] = None


@dataclass
class QueryFilters:
    query: Optional[str] = None
    categories: Optional[List[str]] = None
    ccf_ranks: Optional[List[str]] = None
    core_ranks: Optional[List[str]] = None
    thcpl_ranks: Optional[List[str]] = None
    status: Optional[List[str]] = None
    within_days: Optional[int] = None
    limit: Optional[int] = None


def split_values(value: Optional[str]) -> Optional[List[str]]:
    if not value:
        return None
    return [item.strip().upper() for item in value.split(",") if item.strip()]


def resolve_domain(domain: str) -> Tuple[Optional[List[str]], Optional[str]]:
    entry = DOMAIN_MAP.get(domain.lower())
    if not entry:
        return None, None
    return entry["categories"], entry["domain_name"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def load_source(
    *,
    url: str,
    data_path: Optional[Path],
    cache_path: Path,
    refresh_cache: bool,
) -> SourceData:
    if data_path:
        return SourceData(
            data_path.read_text(encoding="utf-8"), f"file:{data_path}"
        )

    if refresh_cache or not cache_path.exists():
        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": "ccfddl-skills/1.0"}
            )
            with urllib.request.urlopen(request, timeout=20) as response:
                text = response.read().decode("utf-8")
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(text, encoding="utf-8")
            return SourceData(text, url)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            if cache_path.exists():
                return SourceData(
                    cache_path.read_text(encoding="utf-8"),
                    f"cache:{cache_path}",
                    cache_used=True,
                    notes=[f"online fetch failed: {exc}"],
                )
            raise SystemExit(
                f"Could not fetch {url} and no cache exists: {exc}"
            ) from exc

    return SourceData(
        cache_path.read_text(encoding="utf-8"), f"cache:{cache_path}", True
    )


def parse_conferences(text: str) -> List[Dict[str, Any]]:
    data = yaml.safe_load(text)
    if not isinstance(data, list):
        raise ValueError("ccfddl YAML must be a top-level list")
    return [item for item in data if isinstance(item, dict)]


def parse_deadline(value: Any) -> Optional[datetime]:
    if value in (None, "TBD"):
        return None
    if not isinstance(value, str):
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S%z"):
        try:
            parsed = datetime.strptime(value, fmt)
            return parsed.replace(tzinfo=None)
        except ValueError:
            continue
    return None


def nth_sunday(year: int, month: int, n: int) -> date:
    first = date(year, month, 1)
    days_to_sunday = (6 - first.weekday()) % 7
    return first + timedelta(days=days_to_sunday + 7 * (n - 1))


def is_us_dst(day: date) -> bool:
    """Match ccf-deadlines TUI PT handling."""
    return nth_sunday(day.year, 3, 2) <= day < nth_sunday(day.year, 11, 1)


def timezone_offset(label: str, deadline: Optional[datetime]) -> timezone:
    if label == "AoE":
        return timezone(timedelta(hours=-12))
    if label in ("UTC", "UTC+0"):
        return timezone.utc
    if label == "PT":
        if deadline and is_us_dst(deadline.date()):
            return timezone(timedelta(hours=-7))
        return timezone(timedelta(hours=-8))
    if label.startswith("UTC"):
        raw = label[3:]
        if not raw:
            return timezone.utc
        sign = 1
        if raw.startswith("-"):
            sign = -1
            raw = raw[1:]
        elif raw.startswith("+"):
            raw = raw[1:]
        return timezone(sign * timedelta(hours=int(raw)))
    return timezone.utc


def normalize_deadline(
    item: Dict[str, Any],
    tz_label: str,
    *,
    now: datetime,
) -> Dict[str, Any]:
    raw_deadline = item.get("deadline")
    parsed = parse_deadline(raw_deadline)
    offset = timezone_offset(tz_label, parsed)
    deadline_dt = parsed.replace(tzinfo=offset) if parsed else None
    local_dt = deadline_dt.astimezone() if deadline_dt else None
    status = "tbd"
    days_to_deadline = None
    if deadline_dt:
        delta = deadline_dt.astimezone(timezone.utc) - now
        days_to_deadline = int(delta.total_seconds() // 86400)
        status = "open" if delta.total_seconds() >= 0 else "closed"

    abstract_dt = parse_deadline(item.get("abstract_deadline"))
    abstract_with_tz = (
        abstract_dt.replace(tzinfo=offset) if abstract_dt else None
    )

    return {
        "type": "paper",
        "abstract_deadline": item.get("abstract_deadline"),
        "abstract_local_deadline": (
            abstract_with_tz.astimezone().isoformat()
            if abstract_with_tz
            else None
        ),
        "deadline": raw_deadline,
        "local_deadline": local_dt.isoformat() if local_dt else None,
        "timezone": tz_label,
        "status": status,
        "days_to_deadline": days_to_deadline,
        "comment": item.get("comment"),
    }


def instance_status(
    deadlines: List[Dict[str, Any]],
) -> Tuple[str, Optional[int]]:
    if not deadlines:
        return "tbd", None
    open_days = [
        item["days_to_deadline"]
        for item in deadlines
        if item["status"] == "open" and item["days_to_deadline"] is not None
    ]
    if open_days:
        return "open", min(open_days)
    if all(item["status"] == "tbd" for item in deadlines):
        return "tbd", None
    return "closed", None


def flatten_conferences(
    conferences: Iterable[Dict[str, Any]],
    *,
    now: datetime,
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for conference in conferences:
        rank = conference.get("rank") or {}
        dblp = conference.get("dblp")
        for instance in conference.get("confs") or []:
            tz_label = instance.get("timezone")
            timeline = instance.get("timeline") or []
            deadlines = [
                normalize_deadline(item, tz_label, now=now)
                for item in timeline
                if isinstance(item, dict)
            ]
            status, days_to_deadline = instance_status(deadlines)
            conf_title = conference.get("title")
            year = instance.get("year")
            result = {
                "id": instance.get("id"),
                "conference": conf_title,
                "title": (
                    f"{conf_title} {year}"
                    if conf_title and year
                    else conf_title
                ),
                "year": year,
                "description": conference.get("description"),
                "category": conference.get("sub"),
                "date": instance.get("date"),
                "place": instance.get("place"),
                "rank": {
                    "ccf": rank.get("ccf"),
                    "core": rank.get("core"),
                    "thcpl": rank.get("thcpl"),
                },
                "url": instance.get("link"),
                "dblp": f"{DBLP_PREFIX}{dblp}" if dblp else None,
                "timezone": tz_label,
                "status": status,
                "days_to_deadline": days_to_deadline,
                "deadlines": deadlines,
                "notes": [],
                "acceptance_rates": [],
            }
            results.append(result)
    return results


def load_accept_rates_map(path: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Load accept_rates YAML keyed by lowercased conference title."""
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    if not isinstance(data, list):
        raise ValueError("accept_rates YAML must be a top-level list")
    result: Dict[str, List[Dict[str, Any]]] = {}
    for item in data:
        if not isinstance(item, dict):
            continue
        title = item.get("title")
        rates = item.get("accept_rates", [])
        if title:
            result[title.lower()] = rates
    return result


def merge_accept_rates(
    results: List[Dict[str, Any]],
    rates_map: Dict[str, List[Dict[str, Any]]],
) -> None:
    """Add acceptance_rates field to each result in-place."""
    for result in results:
        title = (result.get("conference") or "").lower()
        result["acceptance_rates"] = rates_map.get(title, [])


def status_matches(actual: str, wanted: List[str]) -> bool:
    aliases = {"RUN": "OPEN", "FIN": "CLOSED", "TBD": "TBD"}
    normalized = [aliases.get(item, item).lower() for item in wanted]
    return actual.lower() in normalized


def fuzzy_match(result: Dict[str, Any], query: str) -> bool:
    needle = query.lower()
    identity_fields = [
        str(result.get("id") or "").lower(),
        str(result.get("conference") or "").lower(),
        str(result.get("title") or "").lower(),
    ]
    if len(needle) <= 3:
        return any(
            needle == item
            or item.startswith(needle)
            or item.startswith(f"{needle} ")
            or item.startswith(f"{needle}-")
            for item in identity_fields
        )

    haystacks = [
        *identity_fields,
        str(result.get("description") or "").lower(),
    ]
    if any(needle in item for item in haystacks):
        return True
    return any(
        SequenceMatcher(None, needle, item).ratio() >= 0.72
        for item in haystacks
    )


def apply_filters(
    results: List[Dict[str, Any]], filters: QueryFilters
) -> List[Dict[str, Any]]:
    filtered = list(results)
    if filters.query:
        filtered = [
            item for item in filtered if fuzzy_match(item, filters.query)
        ]
    if filters.categories:
        filtered = [
            item
            for item in filtered
            if item.get("category") in filters.categories
        ]
    if filters.ccf_ranks:
        filtered = [
            item
            for item in filtered
            if item["rank"].get("ccf") in filters.ccf_ranks
        ]
    if filters.core_ranks:
        filtered = [
            item
            for item in filtered
            if item["rank"].get("core") in filters.core_ranks
        ]
    if filters.thcpl_ranks:
        filtered = [
            item
            for item in filtered
            if item["rank"].get("thcpl") in filters.thcpl_ranks
        ]
    if filters.status:
        filtered = [
            item
            for item in filtered
            if status_matches(item["status"], filters.status)
        ]
    if filters.within_days is not None:
        filtered = [
            item
            for item in filtered
            if item["days_to_deadline"] is not None
            and 0 <= item["days_to_deadline"] <= filters.within_days
        ]
    filtered.sort(key=sort_key)
    if filters.limit is not None:
        filtered = filtered[: filters.limit]
    return filtered


def sort_key(item: Dict[str, Any]) -> Tuple[int, int, int]:
    status_order = {"open": 0, "tbd": 1, "closed": 2}
    days = (
        item["days_to_deadline"]
        if item["days_to_deadline"] is not None
        else 10**9
    )
    closed_year = -int(item["year"] or 0) if item["status"] == "closed" else 0
    return status_order.get(item["status"], 3), days, closed_year


def render_ics(results: List[Dict[str, Any]]) -> str:
    """Render filtered results as iCalendar (ICS) text.
    Only includes results with concrete (non-TBD) deadlines.
    """
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//ccfddl-skills//query_conferences.py//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    for result in results:
        tz_label = result.get("timezone") or "UTC"
        for deadline in result.get("deadlines") or []:
            raw = deadline.get("deadline")
            if not raw or raw == "TBD":
                continue
            parsed = parse_deadline(raw)
            if not parsed:
                continue
            offset = timezone_offset(tz_label, parsed)
            deadline_dt = parsed.replace(tzinfo=offset)
            utc_dt = deadline_dt.astimezone(timezone.utc)
            ics_dt = utc_dt.strftime("%Y%m%dT%H%M%SZ")

            summary = (
                result.get("title") or result.get("conference") or "Conference"
            )

            url = result.get("url") or ""
            parts: List[str] = []
            if result.get("description"):
                parts.append(result["description"])
            parts.append(f"Deadline: {raw} {tz_label}")
            if result.get("category"):
                parts.append(f"Category: {result['category']}")
            if result.get("rank", {}).get("ccf"):
                parts.append(f"CCF Rank: {result['rank']['ccf']}")
            if url:
                parts.append(f"URL: {url}")
            description = "\\n".join(parts)

            lines.append("BEGIN:VEVENT")
            lines.append(f"SUMMARY:{summary}")
            lines.append(f"DTSTART:{ics_dt}")
            lines.append(f"DESCRIPTION:{description}")
            if url:
                lines.append(f"URL:{url}")
            lines.append("END:VEVENT")

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"


def render_markdown(results: List[Dict[str, Any]]) -> str:
    lines = [
        "| Conference | Rank | Category | Status | Deadline | Date | Place |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in results:
        rank = item["rank"]
        next_deadline = next(
            (
                deadline
                for deadline in item["deadlines"]
                if deadline["deadline"] != "TBD"
            ),
            None,
        )
        deadline_text = next_deadline["deadline"] if next_deadline else "TBD"
        rank_text = "/".join(
            value
            for value in (rank.get("ccf"), rank.get("core"), rank.get("thcpl"))
            if value
        )
        row = (
            "| {title} | {rank} | {category} | {status} | "
            "{deadline} {tz} | {date} | {place} |"
        )
        lines.append(
            row.format(
                title=item.get("title") or "",
                rank=rank_text,
                category=item.get("category") or "",
                status=item.get("status") or "",
                deadline=deadline_text,
                tz=item.get("timezone") or "",
                date=item.get("date") or "",
                place=item.get("place") or "",
            )
        )
    return "\n".join(lines)


def build_envelope(
    results: List[Dict[str, Any]],
    source: SourceData,
    *,
    now: datetime,
    extra_notes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    notes = list(source.notes or [])
    if source.cache_used:
        notes.append("cache data was used")
    if extra_notes:
        notes.extend(extra_notes)
    return {
        "source": source.label,
        "generated_at": now.isoformat(),
        "count": len(results),
        "notes": notes,
        "results": results,
    }


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--data-path", type=Path)
    parser.add_argument("--cache-path", type=Path, default=DEFAULT_CACHE)
    parser.add_argument(
        "--format", choices=["json", "markdown", "ics"], default="json"
    )
    parser.add_argument("--limit", type=int)
    parser.add_argument("--now", help="UTC timestamp for deterministic tests")


def parse_now(value: Optional[str]) -> datetime:
    if not value:
        return utc_now()
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def run_query(args: argparse.Namespace) -> int:
    now = parse_now(args.now)
    source = load_source(
        url=args.url,
        data_path=args.data_path,
        cache_path=args.cache_path,
        refresh_cache=args.command == "refresh-cache",
    )
    conferences = parse_conferences(source.text)
    results = flatten_conferences(conferences, now=now)

    accept_rates_path = getattr(args, "accept_rates_path", None)
    if accept_rates_path:
        rates_map = load_accept_rates_map(accept_rates_path)
        merge_accept_rates(results, rates_map)

    categories = split_values(getattr(args, "category", None))
    domain = getattr(args, "domain", None)
    extra_notes: List[str] = []
    if domain:
        domain_cats, domain_name = resolve_domain(domain)
        if domain_cats is None:
            known = ", ".join(sorted(DOMAIN_MAP))
            raise SystemExit(
                f"Unknown domain '{domain}'. Known domains: {known}"
            )
        if categories:
            old_cats = list(categories)
            categories = list(sorted(set(categories) | set(domain_cats)))
            domain_categories = ",".join(domain_cats)
            old_categories = ",".join(old_cats)
            merged_categories = ",".join(categories)
            extra_notes.append(
                f"domain preset '{domain}' ({domain_name}) → "
                f"categories {domain_categories}; "
                f"unioned with --category {old_categories} → "
                f"{merged_categories}"
            )
        else:
            categories = domain_cats
            domain_categories = ",".join(domain_cats)
            extra_notes.append(
                f"domain preset '{domain}' ({domain_name}) → "
                f"categories {domain_categories}"
            )
    filters = QueryFilters(
        query=getattr(args, "query", None),
        categories=categories,
        ccf_ranks=split_values(getattr(args, "ccf_rank", None)),
        core_ranks=split_values(getattr(args, "core_rank", None)),
        thcpl_ranks=split_values(getattr(args, "thcpl_rank", None)),
        status=split_values(getattr(args, "status", None)),
        within_days=getattr(args, "within_days", None),
        limit=args.limit,
    )
    results = apply_filters(results, filters)
    if args.format == "ics":
        print(render_ics(results), end="")
    elif args.format == "markdown":
        print(render_markdown(results))
    else:
        print(
            json.dumps(
                build_envelope(
                    results, source, now=now, extra_notes=extra_notes
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Query ccfddl conference deadline YAML"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    search = subparsers.add_parser(
        "search", help="Search by conference id, title, or description"
    )
    add_common_args(search)
    search.add_argument("--query", required=True)
    search.add_argument(
        "--accept-rates-path", type=Path, help="Path to accept_rates YAML"
    )

    list_cmd = subparsers.add_parser(
        "list", help="List and filter conference instances"
    )
    add_common_args(list_cmd)
    list_cmd.add_argument("--query")
    list_cmd.add_argument(
        "--domain",
        choices=list(DOMAIN_MAP),
        help="Research domain preset (maps to one or more categories)",
    )
    list_cmd.add_argument("--category")
    list_cmd.add_argument("--ccf-rank")
    list_cmd.add_argument("--core-rank")
    list_cmd.add_argument("--thcpl-rank")
    list_cmd.add_argument("--status")
    list_cmd.add_argument("--within-days", type=int)
    list_cmd.add_argument(
        "--accept-rates-path", type=Path, help="Path to accept_rates YAML"
    )

    refresh = subparsers.add_parser(
        "refresh-cache", help="Refresh local cache and render results"
    )
    add_common_args(refresh)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run_query(args)


if __name__ == "__main__":
    raise SystemExit(main())
