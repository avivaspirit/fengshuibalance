#!/usr/bin/env python3
"""Remove legacy inline article styles and bump enhancement script cache."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "articles"
SCRIPT_TAG = '<script src="../article-enhancements.js?v=20260607"></script>'
OLD_SCRIPT = re.compile(r'<script src="\.\./article-enhancements\.js(?:\?v=[^"]*)?"></script>')
INLINE_STYLE = re.compile(r"\n?\s*<style>\s*\.article-page-main[\s\S]*?</style>\s*", re.I)


def patch(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    updated = INLINE_STYLE.sub("\n", text)
    updated = OLD_SCRIPT.sub(SCRIPT_TAG, updated)
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8", newline="\n")
    return True


def main() -> None:
    changed = 0
    for path in ARTICLES.glob("*.html"):
        if patch(path):
            changed += 1
    print(f"Updated {changed} article pages")


if __name__ == "__main__":
    main()
