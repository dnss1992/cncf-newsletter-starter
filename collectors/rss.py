from __future__ import annotations

import logging
from typing import Any, Dict, List

import feedparser

logger = logging.getLogger(__name__)


def fetch_rss(url: str, project_slug: str, since_iso: str) -> List[Dict[str, Any]]:
    """Fetch RSS/Atom feed entries."""

    logger.info("Fetching RSS feed for %s", project_slug)
    feed = feedparser.parse(url)
    out: List[Dict[str, Any]] = []
    for entry in feed.entries:
        published = getattr(entry, "published", None) or getattr(entry, "updated", None)
        if not published:
            continue
        out.append(
            {
                "project": project_slug,
                "type": "blog",
                "title": getattr(entry, "title", "Untitled"),
                "url": getattr(entry, "link", ""),
                "published_at": published,
                "summary_raw": getattr(entry, "summary", ""),
                "labels": ["blog"],
            }
        )
    return out
