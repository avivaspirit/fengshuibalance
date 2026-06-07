#!/usr/bin/env python3
"""Add yin-yang favicon links to all HTML pages."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAVICON_ROOT = (
    '<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">\n'
    '    <link rel="apple-touch-icon" href="/assets/favicon.svg">\n'
    '    <link rel="shortcut icon" href="/assets/favicon.svg">'
)
FAVICON_ARTICLE = (
    '<link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">\n'
    '    <link rel="apple-touch-icon" href="../assets/favicon.svg">\n'
    '    <link rel="shortcut icon" href="../assets/favicon.svg">'
)
MARKER = 'rel="continueicon"'


def patch_file(path: Path, snippet: str) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False
    needle = '<meta name="viewport" content="width=device-width, initial-scale=1">'
    if needle not in text:
        return False
    updated = text.replace(
        needle,
        needle + "\n    " + snippet,
        1,
    )
    path.write_text(updated, encoding="utf-8", newline="\n")
    return True


def main() -> None:
    changed = 0
    for path in ROOT.glob("*.html"):
        if patch_file(path, FAVICON_ROOT):
            changed += 1
    for path in (ROOT / "articles").glob("*.html"):
        if patch_file(path, FAVICON_ARTICLE):
            changed += 1
    print(f"Updated {changed} HTML files with favicon links")


if __name__ == "__main__":
    main()
