from __future__ import annotations
import os, sys, yaml, requests, re

LANDSCAPE_RAW = "https://raw.githubusercontent.com/cncf/landscape/master/landscape.yml"
OUT_PATH = "config/projects.yaml"

def guess_repo_slug(repo_url: str) -> str | None:
    m = re.match(r"https?://github\.com/([^/]+)(?:/([^/#]+))?", repo_url.strip())
    if not m:
        return None
    owner = m.group(1)
    repo = m.group(2) or None
    if repo:
        return f"{owner}/{repo}"
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
                maturity = str(item.get("maturity", "")).lower()
                if maturity != "graduated":
                    continue
                repo_url = item.get("repo_url") or ""
                slug = guess_repo_slug(repo_url) if repo_url else None
                name = item.get("name") or item.get("project") or ""
                homepage = item.get("homepage_url") or ""
                rss = None
                for cand in ("/feed.xml", "/rss.xml", "/index.xml", "/atom.xml", "/blog/index.xml", "/blog/rss.xml"):
                    if homepage and homepage.endswith("/"):
                        rss = homepage[:-1] + cand
                    elif homepage:
                        rss = homepage + cand
                    else:
                        rss = None
                    if rss:
                        break
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
