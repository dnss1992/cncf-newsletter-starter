from __future__ import annotations

import datetime as dt
from typing import Any, Dict, List

from dateutil import parser as dateparser


def to_iso(ts: Any) -> str:
    """Convert timestamps or strings to ISO8601."""

    if not ts:
        return ""
    if isinstance(ts, str):
        try:
            return dateparser.parse(ts).astimezone(dt.timezone.utc).isoformat()
        except Exception:
            return ts
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).isoformat()


def normalize(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Normalize raw items for output."""

    for item in items:
        item["published_at"] = to_iso(item.get("published_at"))
        item.setdefault("labels", [])
        item.setdefault("summary_raw", "")
        item["summary"] = (item["summary_raw"].strip().replace("\n", " "))[:280]
    items.sort(key=lambda x: x.get("published_at") or "", reverse=True)
    return items
