#!/usr/bin/env python3
"""Add article-enhancements.js to all article HTML files missing it."""
import os

ARTICLES_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "articles",
)
SCRIPT_TAG = '    <script src="../article-enhancements.js"></script>\n'
INSERT_BEFORE = "  </body>"

added = 0
skipped = 0

for name in sorted(os.listdir(ARTICLES_DIR)):
    if not name.endswith(".html"):
        continue
    path = os.path.join(ARTICLES_DIR, name)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if "article-enhancements.js" in text:
        skipped += 1
        continue
    if INSERT_BEFORE not in text:
        print("WARN: no </body> in", name)
        continue
    text = text.replace(INSERT_BEFORE, SCRIPT_TAG + INSERT_BEFORE, 1)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    added += 1

print(f"Added script to {added} articles; skipped {skipped} already present")
