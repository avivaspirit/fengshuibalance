#!/usr/bin/env python3
"""Regenerate sitemap.xml and robots.txt for Google Search Console."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://fengshuibalance.vercel.app"
TODAY = date.today().isoformat()

STATIC_PAGES = [
    ("", "1.0", "weekly"),
    ("projects.html", "0.9", "monthly"),
    ("ajarn-suppachai.html", "0.9", "monthly"),
    ("ajarn-grianggrai.html", "0.8", "monthly"),
    ("articles.html", "0.9", "weekly"),
    ("brand-portfolio.html", "0.7", "monthly"),
]


def load_articles() -> list[dict]:
    source = (ROOT / "articles-full.js").read_text(encoding="utf-8")
    match = re.search(r"window\.FENGSHUI_ARTICLES_FULL\s*=\s*(\[.*\])\s*;?\s*$", source, re.S)
    if not match:
        raise SystemExit("Could not parse articles-full.js")
    return json.loads(match.group(1))


def url_entry(loc: str, lastmod: str, changefreq: str, priority: str) -> str:
    return (
        "  <url>\n"
        f"    <loc>{loc}</loc>\n"
        f"    <lastmod>{lastmod}</lastmod>\n"
        f"    <changefreq>{changefreq}</changefreq>\n"
        f"    <priority>{priority}</priority>\n"
        "  </url>"
    )


MIN_BODY_CHARS = 200  # Only include articles with substantial content


def build_sitemap(articles: list[dict]) -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    for path, priority, changefreq in STATIC_PAGES:
        loc = BASE_URL if not path else f"{BASE_URL}/{path}"
        lines.append(url_entry(loc, TODAY, changefreq, priority))

    # Only include articles with real body content (not empty/image-only posts)
    quality_articles = [
        a for a in articles
        if len(a.get("body", "").strip()) >= MIN_BODY_CHARS
    ]
    print(f"  {len(quality_articles)}/{len(articles)} articles have body >= {MIN_BODY_CHARS} chars")

    for article in sorted(quality_articles, key=lambda item: item["id"]):
        article_date = article.get("date") or TODAY
        loc = f"{BASE_URL}/articles/{article['id']}.html"
        lines.append(url_entry(loc, article_date, "monthly", "0.6"))

    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def build_robots() -> str:
    return (
        "# Fengshui Balance — allow Google and other crawlers\n"
        "User-agent: *\n"
        "Content-Signal: search=yes, ai-train=no\n"
        "Allow: /\n"
        "\n"
        "User-agent: Googlebot\n"
        "Allow: /\n"
        "\n"
        "User-agent: Googlebot-Image\n"
        "Allow: /assets/images/\n"
        "\n"
        f"Sitemap: {BASE_URL}/sitemap.xml\n"
    )


def main() -> None:
    articles = load_articles()
    sitemap = build_sitemap(articles)
    robots = build_robots()

    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8", newline="\n")
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8", newline="\n")

    total_urls = len(STATIC_PAGES) + len([a for a in articles if len(a.get("body","").strip()) >= MIN_BODY_CHARS])
    print(f"Wrote sitemap.xml ({total_urls} URLs)")
    print(f"Wrote robots.txt")


if __name__ == "__main__":
    main()
