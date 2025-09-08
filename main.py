from __future__ import annotations

import argparse
import datetime as dt
import logging
from pathlib import Path
from typing import Any, Dict, List

from collectors.github import fetch_releases
from collectors.rss import fetch_rss
from normalize.events import normalize
from assemble.build_issue import build
from utils.io import read_yaml, write_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""

    parser = argparse.ArgumentParser(description="Build newsletter items")
    parser.add_argument(
        "--since",
        default="3 days",
        help="Window (e.g., '3 days', '2025-08-01')",
    )
    parser.add_argument("--out", default="./build", help="Output directory")
    return parser.parse_args()


def to_since_iso(s: str) -> str:
    """Return an ISO8601 timestamp from an "N days" string or ISO input."""

    s = s.strip().lower()
    now = dt.datetime.utcnow()
    try:
        if "day" in s:
            n = int(s.split()[0])
            since = now - dt.timedelta(days=n)
        elif "week" in s:
            n = int(s.split()[0])
            since = now - dt.timedelta(weeks=n)
        else:
            since = dt.datetime.fromisoformat(s.replace("z", ""))
        return since.replace(microsecond=0).isoformat() + "Z"
    except Exception:
        return (now - dt.timedelta(days=3)).replace(microsecond=0).isoformat() + "Z"


def main() -> None:
    """CLI entry point."""

    args = parse_args()
    since_iso = to_since_iso(args.since)

    cfg = read_yaml("config/projects.yaml")
    projects = cfg.get("projects", [])
    raw: List[Dict[str, Any]] = []
    for project in projects:
        slug = project["slug"]
        raw.extend(fetch_releases(slug, since_iso))
        if project.get("rss"):
            raw.extend(fetch_rss(project["rss"], slug, since_iso))

    items = normalize(raw)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "items.json", items)
    build(items, str(out_dir))
    logger.info("Wrote items to %s", out_dir)


if __name__ == "__main__":
    main()
