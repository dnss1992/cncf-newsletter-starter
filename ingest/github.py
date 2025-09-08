from __future__ import annotations
import os, requests
from typing import Dict, Any, List

GH_API = "https://api.github.com"

def _gh_headers() -> dict:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return {}  # no token, return empty headers
    return {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}

def fetch_releases(repo: str, since_iso: str) -> List[Dict[str, Any]]:
    """Return releases from GitHub if possible, else empty list."""
    headers = _gh_headers()
    if not headers:  # no token
        return []    # let caller fall back to RSS

    url = f"{GH_API}/repos/{repo}/releases"
    out: List[Dict[str, Any]] = []
    page = 1
    while True:
        r = requests.get(url, headers=headers, params={"page": page, "per_page": 50}, timeout=30)
        if r.status_code == 403:
            print(f"[warn] GitHub API rate limited or unauthorized for {repo}, skipping.")
            return []
        r.raise_for_status()
        data = r.json() or []
        if not data:
            break
        for rel in data:
            published = rel.get("published_at") or rel.get("created_at")
            if not published or published < since_iso:
                continue
            out.append({
                "project": repo,
                "type": "release",
                "title": rel.get("name") or rel.get("tag_name"),
                "url": rel.get("html_url"),
                "published_at": published,
                "summary_raw": rel.get("body") or "",
                "labels": ["release"],
                "version": rel.get("tag_name"),
            })
        page += 1
    return out
