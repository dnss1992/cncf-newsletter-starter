from __future__ import annotations

import json
import os
import datetime as dt
import pathlib
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markdown_it import MarkdownIt


def build(issue_items: List[Dict[str, Any]], out_dir: str) -> Dict[str, str]:
    """Render markdown and HTML artifacts for the issue."""

    env = Environment(
        loader=FileSystemLoader("assemble/templates"),
        autoescape=select_autoescape(),
    )

    md_tpl = env.get_template("issue.md.j2")
    releases = [i for i in issue_items if i.get("type") == "release"]
    blogs = [i for i in issue_items if i.get("type") == "blog"]
    top = releases[:5]

    md = md_tpl.render(
        date_str=dt.datetime.utcnow().strftime("%Y-%m-%d"),
        highlights=top,
        releases=releases,
        blogs=blogs,
    )
    html_from_md = MarkdownIt().render(md)

    projects = sorted({i["project"] for i in issue_items if i.get("project")})
    types = sorted({i["type"] for i in issue_items if i.get("type")})

    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(out_dir, "items.json"), "w", encoding="utf-8") as f:
        json.dump(issue_items, f, indent=2, ensure_ascii=False)

    html_tpl = env.get_template("issue.md.j2")
    html = html_tpl.render(
        date_str=dt.datetime.utcnow().strftime("%Y-%m-%d"),
        projects=projects,
        types=types,
    )

    with open(os.path.join(out_dir, "issue.md"), "w", encoding="utf-8") as f:
        f.write(md)
    with open(os.path.join(out_dir, "issue.html"), "w", encoding="utf-8") as f:
        f.write(html)

    about_tpl = env.get_template("about.html.j2")
    about_html = about_tpl.render(date_str=dt.datetime.utcnow().strftime("%Y"))
    with open(os.path.join(out_dir, "about.html"), "w", encoding="utf-8") as f:
        f.write(about_html)

    return {"md": md, "html": html_from_md}
