#!/usr/bin/env python3
"""Bump inline article typography for 40+ readability."""
import os
import re

ARTICLES = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "articles",
)

REPLACEMENTS = [
    (
        "font-size: 17px;\n        line-height: 1.8;",
        "font-size: 19px;\n        line-height: 1.85;",
    ),
    (
        ".article-meta {\n        display: flex;\n        flex-wrap: wrap;\n        gap: 20px;\n        color: var(--muted);\n        font-size: 14px;",
        ".article-meta {\n        display: flex;\n        flex-wrap: wrap;\n        gap: 20px;\n        color: var(--muted);\n        font-size: 16px;",
    ),
    (
        "font-size: clamp(28px, 4vw, 42px);",
        "font-size: clamp(32px, 4.5vw, 46px);",
    ),
    (
        "font-size: clamp(20px, 2.5vw, 24px);",
        "font-size: clamp(22px, 2.8vw, 28px);",
    ),
    (
        ".article-footer-cta p {\n        color: rgba(255, 255, 255, 0.8);\n        font-size: 15px;",
        ".article-footer-cta p {\n        color: rgba(255, 255, 255, 0.8);\n        font-size: 17px;",
    ),
]

updated = 0
for name in os.listdir(ARTICLES):
    if not name.endswith(".html"):
        continue
    path = os.path.join(ARTICLES, name)
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if ".article-content" not in text:
        continue
    original = text
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    if text != original:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        updated += 1

print(f"Updated typography in {updated} article files")
