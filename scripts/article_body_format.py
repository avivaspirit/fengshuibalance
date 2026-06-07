"""Turn Facebook-style plain text into readable article HTML paragraphs."""

from __future__ import annotations

import html
import re

DIVIDER = re.compile(r"^(-{3,}|={3,}|\*{3,}|\.{3,})$")
CALLOUT = re.compile(r"^(\*{2,3}|#{1,3}\s|>>>)")
LIST_ITEM = re.compile(r"^([-•*]|\d+[\.)])\s+")


def strip_tags(value: str) -> str:
    text = value or ""
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip()


def linkify_plain_text(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(
        r"https?://(?:www\.)?miracles369-store\.com[^\s<]*",
        lambda m: (
            f'<a href="{m.group(0)}" target="_blank" rel="noopener noreferrer" '
            f'class="article-brand-link">{m.group(0)}</a>'
        ),
        escaped,
        flags=re.I,
    )
    escaped = re.sub(
        r"https?://(?:www\.)?avivaspirit\.com[^\s<]*",
        lambda m: (
            f'<a href="{m.group(0)}" target="_blank" rel="noopener noreferrer" '
            f'class="article-brand-link">{m.group(0)}</a>'
        ),
        escaped,
        flags=re.I,
    )
    escaped = re.sub(
        r"\bMiracles369\b",
        '<a href="https://www.miracles369-store.com/" target="_blank" '
        'rel="noopener noreferrer" class="article-brand-link">Miracles369</a>',
        escaped,
    )
    escaped = re.sub(
        r"\bAviva Spirit\b",
        '<a href="https://www.avivaspirit.com/" target="_blank" '
        'rel="noopener noreferrer" class="article-brand-link">Aviva Spirit</a>',
        escaped,
    )
    return escaped


def format_article_body(text: str) -> str:
    normalized = (text or "").replace("\r\n", "\n").strip()
    if not normalized:
        return ""

    lines = normalized.split("\n")
    parts: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []

    def flush_paragraph() -> None:
        if not paragraph:
            return
        joined = re.sub(r"\s+", " ", " ".join(paragraph)).strip()
        paragraph.clear()
        if joined:
            parts.append(f"<p>{linkify_plain_text(joined)}</p>")

    def flush_list() -> None:
        if not list_items:
            return
        parts.append('<ul class="article-list">')
        for item in list_items:
            parts.append(f"<li>{linkify_plain_text(item)}</li>")
        parts.append("</ul>")
        list_items.clear()

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            flush_list()
            flush_paragraph()
            continue

        if DIVIDER.match(line):
            flush_list()
            flush_paragraph()
            parts.append('<hr class="article-divider" />')
            continue

        if LIST_ITEM.match(line):
            flush_paragraph()
            list_items.append(LIST_ITEM.sub("", line, count=1))
            continue

        if CALLOUT.match(line):
            flush_list()
            flush_paragraph()
            parts.append(f'<p class="article-callout">{linkify_plain_text(line)}</p>')
            continue

        flush_list()
        paragraph.append(line)

    flush_list()
    flush_paragraph()
    return "".join(parts)
