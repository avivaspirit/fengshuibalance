#!/usr/bin/env python3
"""Regenerate sitemap.xml, sitemap-main.xml, sitemap-articles.xml and robots.txt for Google Search Console."""

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

MIN_BODY_CHARS = 200


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


def build_main_sitemap() -> str:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for path, priority, changefreq in STATIC_PAGES:
        loc = BASE_URL if not path else f"{BASE_URL}/{path}"
        lines.append(url_entry(loc, TODAY, changefreq, priority))
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def build_articles_sitemap(articles: list[dict]) -> str:
    quality_articles = [
        a for a in articles
        if len(a.get("body", "").strip()) >= MIN_BODY_CHARS
    ]
    print(f"  {len(quality_articles)}/{len(articles)} articles have body >= {MIN_BODY_CHARS} chars")

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for article in sorted(quality_articles, key=lambda item: item["id"]):
        article_date = article.get("date") or TODAY
        loc = f"{BASE_URL}/articles/{article['id']}.html"
        lines.append(url_entry(loc, article_date, "monthly", "0.6"))
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def build_sitemap_index() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <sitemap><loc>{BASE_URL}/sitemap-main.xml</loc><lastmod>{TODAY}</lastmod></sitemap>\n"
        f"  <sitemap><loc>{BASE_URL}/sitemap-articles.xml</loc><lastmod>{TODAY}</lastmod></sitemap>\n"
        "</sitemapindex>\n"
    )


def build_robots() -> str:
    return (
        "# Fengshui Balance \u2014 allow search engines, block AI training\n"
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        "User-agent: Googlebot\n"
        "Allow: /\n"
        "\n"
        "User-agent: Googlebot-Image\n"
        "Allow: /assets/images/\n"
        "\n"
        "# Block known AI training crawlers\n"
        "User-agent: GPTBot\n"
        "Disallow: /\n"
        "\n"
        "User-agent: ChatGPT-User\n"
        "Disallow: /\n"
        "\n"
        "User-agent: CCBot\n"
        "Disallow: /\n"
        "\n"
        "User-agent: Google-Extended\n"
        "Disallow: /\n"
        "\n"
        "User-agent: PerplexityBot\n"
        "Disallow: /\n"
        "\n"
        "User-agent: anthropic-ai\n"
        "Disallow: /\n"
        "\n"
        "User-agent: Claude-Web\n"
        "Disallow: /\n"
        "\n"
        f"Sitemap: {BASE_URL}/sitemap.xml\n"
    )


def main() -> None:
    articles = load_articles()

    main_xml = build_main_sitemap()
    articles_xml = build_articles_sitemap(articles)
    index_xml = build_sitemap_index()
    robots = build_robots()

    (ROOT / "sitemap.xml").write_text(index_xml, encoding="utf-8", newline="\n")
    (ROOT / "sitemap-main.xml").write_text(main_xml, encoding="utf-8", newline="\n")
    (ROOT / "sitemap-articles.xml").write_text(articles_xml, encoding="utf-8", newline="\n")
    (ROOT / "robots.txt").write_text(robots, encoding="utf-8", newline="\n")

    quality_count = len([a for a in articles if len(a.get("body", "").strip()) >= MIN_BODY_CHARS])
    print(f"Wrote sitemap.xml (index)")
    print(f"Wrote sitemap-main.xml ({len(STATIC_PAGES)} URLs)")
    print(f"Wrote sitemap-articles.xml ({quality_count} URLs)")
    print(f"Wrote robots.txt")


if __name__ == "__main__":
    main()
