from __future__ import annotations

import logging
import os
from typing import Any, Dict, List

import requests

logger = logging.getLogger(__name__)
GH_API = "https://api.github.com"


def _gh_headers() -> Dict[str, str]:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return {}
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }


def fetch_releases(repo: str, since_iso: str) -> List[Dict[str, Any]]:
    """Fetch releases from GitHub for a repository."""

    headers = _gh_headers()
    if not headers:
        logger.info("No GitHub token; skipping releases for %s", repo)
        return []

    url = f"{GH_API}/repos/{repo}/releases"
    out: List[Dict[str, Any]] = []
    page = 1
    while True:
        response = requests.get(
            url, headers=headers, params={"page": page, "per_page": 50}, timeout=30
        )
        if response.status_code == 403:
            logger.warning("GitHub API rate limited or unauthorized for %s", repo)
            return []
        response.raise_for_status()
        data = response.json() or []
        if not data:
            break
        for rel in data:
            published = rel.get("published_at") or rel.get("created_at")
            if not published or published < since_iso:
                continue
            out.append(
                {
                    "project": repo,
                    "type": "release",
                    "title": rel.get("name") or rel.get("tag_name"),
                    "url": rel.get("html_url"),
                    "published_at": published,
                    "summary_raw": rel.get("body") or "",
                    "labels": ["release"],
                    "version": rel.get("tag_name"),
                }
            )
        page += 1
    return out
