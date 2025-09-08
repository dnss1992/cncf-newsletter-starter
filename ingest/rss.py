from __future__ import annotations
import feedparser
from typing import Dict, Any, List

def fetch_rss(url: str, project_slug: str, since_iso: str) -> List[Dict[str, Any]]:
    feed = feedparser.parse(url)
    out: List[Dict[str, Any]] = []
    for e in feed.entries:
        published = getattr(e, "published", None) or getattr(e, "updated", None)
        if not published:
            continue
        out.append({
            "project": project_slug,
            "type": "blog",
            "title": getattr(e, "title", "Untitled"),
            "url": getattr(e, "link", ""),
            "published_at": published,
            "summary_raw": getattr(e, "summary", ""),
            "labels": ["blog"],
        })
    return out
