from __future__ import annotations
import os, json, argparse, datetime as dt, pathlib
from typing import List, Dict, Any
import yaml

from ingest.github import fetch_releases
from ingest.rss import fetch_rss
from normalize.events import normalize
from assemble.build_issue import build

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--since", default="3 days", help="Window (e.g., '3 days', '2025-08-01')")
    p.add_argument("--out", default="./build", help="Output dir")
    return p.parse_args()

def to_since_iso(s: str) -> str:
    # Simple “N days” support + ISO passthrough
    s = s.strip().lower()
    now = dt.datetime.utcnow()
    try:
        if "day" in s:
            n = int(s.split()[0]); since = now - dt.timedelta(days=n)
        elif "week" in s:
            n = int(s.split()[0]); since = now - dt.timedelta(weeks=n)
        else:
            since = dt.datetime.fromisoformat(s.replace("z",""))
        return since.replace(microsecond=0).isoformat() + "Z"
    except Exception:
        return (now - dt.timedelta(days=3)).replace(microsecond=0).isoformat() + "Z"

def main():
    args = parse_args()
    since_iso = to_since_iso(args.since)

    with open("config/projects.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    projects = cfg.get("projects", [])
    use_github = bool(os.environ.get("GITHUB_TOKEN"))
    raw: List[Dict[str, Any]] = []
    for p in projects:
        slug = p["slug"]
        if use_github:
            raw += fetch_releases(slug, since_iso)
        else:
            print(f"[info] No GITHUB_TOKEN set → skipping GitHub for {slug}")
        if p.get("rss"):
            raw += fetch_rss(p["rss"], slug, since_iso)

    items = normalize(raw)
    pathlib.Path(args.out).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(args.out, "items.json"), "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    built = build(items, args.out)
    print(f"Wrote: {args.out}/issue.md and {args.out}/issue.html")

if __name__ == "__main__":
    main()
