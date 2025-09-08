from __future__ import annotations

from urllib.parse import urlparse, urljoin

import requests
import yaml

LANDSCAPE_RAW = "https://raw.githubusercontent.com/cncf/landscape/master/landscape.yml"
OUT_PATH = "config/projects.yaml"


def resolve_repo_slug(repo_url: str) -> str | None:
    """Resolve GitHub repo slug from a URL."""

    try:
        u = urlparse(repo_url.strip())
    except Exception:
        return None
    if u.scheme not in ("http", "https"):
        return None
    if u.netloc.lower() != "github.com":
        return None
    parts = [p for p in u.path.strip("/").split("/") if p]
    if len(parts) < 2:
        return None
    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    slug = f"{owner}/{repo}"
    try:
        r = requests.head(f"https://github.com/{slug}", timeout=10)
        if r.status_code >= 400:
            return None
    except requests.RequestException:
        return None
    return slug


def discover_feed(homepage: str) -> str | None:
    """Heuristically find a feed URL for a project homepage."""

    if not homepage:
        return None
    candidates = [
        "/feed.xml",
        "/rss.xml",
        "/index.xml",
        urljoin(homepage, "/feed/"),
        urljoin(homepage, "/index.xml"),
    ]
    for c in candidates:
        try:
            url = urljoin(homepage, c)
            r = requests.head(url, timeout=10)
            if r.status_code < 400:
                return url
        except requests.RequestException:
            continue
    return None


def main() -> None:
    """Synchronize project data from the CNCF landscape."""

    r = requests.get(LANDSCAPE_RAW, timeout=30)
    data = yaml.safe_load(r.text)
    out: dict[str, list[dict[str, str | None]]] = {"projects": []}
    for it in data.get("landscape", []):
        for proj in it.get("items", []):
            repo = resolve_repo_slug(proj.get("repo_url", ""))
            if not repo:
                continue
            feed = discover_feed(proj.get("homepage"))
            out["projects"].append({"slug": repo, "rss": feed})
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(out, f)


if __name__ == "__main__":
    main()
