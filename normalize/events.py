from __future__ import annotations
import datetime as dt
from dateutil import parser as dateparser
from typing import List, Dict, Any

def to_iso(ts) -> str:
    if not ts: return ""
    if isinstance(ts, str):
        try: return dateparser.parse(ts).astimezone(dt.timezone.utc).isoformat()
        except Exception: return ts
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).isoformat()

def normalize(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    for it in items:
        it["published_at"] = to_iso(it.get("published_at"))
        it.setdefault("labels", [])
        it.setdefault("summary_raw", "")
        it["summary"] = (it["summary_raw"].strip().replace("\n", " "))[:280]
    items.sort(key=lambda x: x.get("published_at") or "", reverse=True)
    return items
