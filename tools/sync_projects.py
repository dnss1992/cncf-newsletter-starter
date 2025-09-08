from __future__ import annotations
import os, sys, yaml, requests
from urllib.parse import urlparse, urljoin

LANDSCAPE_RAW = "https://raw.githubusercontent.com/cncf/landscape/master/landscape.yml"
OUT_PATH = "config/projects.yaml"

def resolve_repo_slug(repo_url: str) -> str | None:
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
    if not homepage:
        return None
    candidates = [
        "/feed.xml",
        "/rss.xml",
        "/index.xml",
        "/atom.xml",
        "/blog/index.xml",
        "/blog/rss.xml",
    ]
    base = homepage.rstrip("/") + "/"
    for cand in candidates:
        url = urljoin(base, cand.lstrip("/"))
        try:
            r = requests.head(url, timeout=10, allow_redirects=True)
            if r.status_code < 400:
                return url
        except requests.RequestException:
            continue
    return None

def fetch_landscape() -> dict:
    r = requests.get(LANDSCAPE_RAW, timeout=60)
    r.raise_for_status()
    return yaml.safe_load(r.text)

def collect_graduated_projects(data: dict) -> list[dict]:
    out = []
    for cat in data.get("landscape", []):
        for sub in cat.get("subcategories", []):
            for item in sub.get("items", []):
                maturity = str(item.get("project", "")).lower()
                if maturity != "graduated":
                    continue
                repo_url = item.get("repo_url") or ""
                slug = resolve_repo_slug(repo_url)
                name = item.get("name") or item.get("project") or ""
                homepage = item.get("homepage_url") or ""
                rss = discover_feed(homepage)
                if not slug:
                    continue
                out.append({
                    "slug": slug,
                    "tier": "Graduated",
                    "rss": rss,
                    "homepage": homepage,
                    "name": name,
                })
    seen = set()
    uniq = []
    for it in out:
        if it["slug"] in seen:
            continue
        seen.add(it["slug"])
        uniq.append(it)
    return uniq

def write_projects_yaml(entries: list[dict]):
    data = {"projects": []}
    for e in sorted(entries, key=lambda x: x["slug"].lower()):
        data["projects"].append({"slug": e["slug"], "tier": e["tier"], "rss": e.get("rss")})
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

def main():
    data = fetch_landscape()
    grads = collect_graduated_projects(data)
    if not grads:
        print("No graduated projects found; leaving existing config untouched.", file=sys.stderr)
        sys.exit(0)
    write_projects_yaml(grads)
    print(f"Wrote {len(grads)} graduated projects to {OUT_PATH}")

if __name__ == "__main__":
    main()
