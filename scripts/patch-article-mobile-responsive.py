#!/usr/bin/env python3
"""Re-format article bodies from articles-full.js for mobile readability."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "articles"
ARTICLES_JS = ROOT / "articles-full.js"
sys.path.insert(0, str(ROOT / "scripts"))

from article_body_format import format_article_body  # noqa: E402

SCRIPT_TAG = '<script src="../article-enhancements.js?v=20260608"></script>'
OLD_SCRIPT = re.compile(r'<script src="\.\./article-enhancements\.js(?:\?v=[^"]*)?"></script>')
CONTENT_BLOCK = re.compile(
    r'(<div class="article-content")([^>]*)(>)([\s\S]*?)(</div>)',
    re.I,
)
BODY_TAG = re.compile(r"<body(\s[^>]*)?>", re.I)


def load_articles() -> dict[str, str]:
    raw = ARTICLES_JS.read_text(encoding="utf-8")
    raw = raw.strip()
    if raw.startswith("window.FENGSHUI_ARTICLES_FULL"):
        raw = raw.split("=", 1)[1].strip()
        if raw.endswith(";"):
            raw = raw[:-1].strip()
    items = json.loads(raw)
    return {item["id"]: item.get("body") or "" for item in items}


def patch(path: Path, body: str) -> bool:
    text = path.read_text(encoding="utf-8")
    formatted = format_article_body(body)
    attrs = ' data-formatted="true" data-brand-linked="true"'

    match = CONTENT_BLOCK.search(text)
    if not match:
        return False

    replacement = f'{match.group(1)}{attrs}{match.group(3)}{formatted}{match.group(5)}'
    updated = text[: match.start()] + replacement + text[match.end() :]

    if 'class="article-page"' not in updated:
        def add_body_class(m: re.Match[str]) -> str:
            attrs_body = m.group(1) or ""
            if "class=" in attrs_body:
                return re.sub(
                    r'class="([^"]*)"',
                    lambda cm: f'class="{cm.group(1)} article-page"',
                    m.group(0),
                    count=1,
                )
            return '<body class="article-page">'

        updated = BODY_TAG.sub(add_body_class, updated, count=1)

    updated = OLD_SCRIPT.sub(SCRIPT_TAG, updated)

    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8", newline="\n")
    return True


def main() -> None:
    bodies = load_articles()
    changed = 0
    missing = 0
    for path in sorted(ARTICLES.glob("*.html")):
        article_id = path.stem
        body = bodies.get(article_id)
        if body is None:
            missing += 1
            continue
        if patch(path, body):
            changed += 1
    print(f"Updated {changed} article pages ({missing} missing from articles-full.js)")


if __name__ == "__main__":
    main()
