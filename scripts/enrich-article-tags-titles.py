#!/usr/bin/env python3
"""Assign up to 2 category tags per article and refine readable titles."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLES_JS = ROOT / "articles-full.js"
ARTICLES_DIR = ROOT / "articles"
REPORT = ROOT / "scripts" / "tag-title-report.json"

TAG_META = {
    "timing": {"emoji": "📅", "th": "ฤกษ์ยาม", "en": "Auspicious Timing"},
    "spirit": {"emoji": "🏛", "th": "ศาลและตี่จู้", "en": "Spirit House"},
    "shop": {"emoji": "🏪", "th": "ร้านค้า", "en": "Shop"},
    "office": {"emoji": "🏢", "th": "ออฟฟิศ", "en": "Office"},
    "home": {"emoji": "🏠", "th": "บ้าน", "en": "Home"},
    "factory": {"emoji": "🏭", "th": "โรงงาน", "en": "Factory"},
    "astrology": {"emoji": "⭐", "th": "ดวงจีน", "en": "Destiny"},
    "lineage": {"emoji": "📜", "th": "สายวิชา", "en": "Lineage"},
    "general": {"emoji": "📝", "th": "บันทึกฮวงจุ้ย", "en": "Fengshui Notes"},
    "business": {"emoji": "💼", "th": "ธุรกิจ", "en": "Business"},
    "yearly": {"emoji": "📆", "th": "รายปี", "en": "Yearly"},
    "energy": {"emoji": "✨", "th": "พลังงาน", "en": "Energy"},
}

TAG_KEYWORDS: dict[str, list[str]] = {
    "timing": [
        "ฤกษ์", "ฤกษ์ยาม", "ฤกษ์ดี", "ฤกษ์ไม่ดี", "ธงไชย", "วันธงไชย", "วันกินี",
        "ชิวสี่", "วันเปิด", "วันขยับ", "วันย้าย", "วันทำบุญ", "ปฏิทิน", "เดือนดี",
        "วันดี", "ยาม", "ฤกษ์มงคล", "ฤกษ์เสีย", "วันมงคล", "วันเสีย", "ขึ้นศาล",
        "ตั้งศาล", "เปิดร้าน", "วันโยก", "วันเข้าบ้าน",
    ],
    "spirit": [
        "ตี่จู้", "ศาลพระภูมิ", "ศาลเจ้า", "ศาลตายาย", "อากง", "เจ้าที่", "เรือนศาล",
        "spirit house", "teeju", "aviva", "ของไหว้", "กระถางธูป", "ตั้งตี่", "ตั้งศาล",
        "ศาลและตี่", "ตู้ศาล", "ไหว้เจ้า", "เจ้าพ่อ", "เจ้าแม่",
    ],
    "shop": [
        "ร้านค้า", "หน้าร้าน", "โชว์รูม", "เคาน์เตอร์", "counter", "ยอดขาย", "ร้าน",
        "shop", "retail", "ขายของ", "เปิดร้าน", "ร้านอาหาร", "ร้านกาแฟ", "ร้านเสริมสวย",
    ],
    "office": [
        "ออฟฟิศ", "office", "สำนักงาน", "โต๊ะทำงาน", "ห้องประชุม", "workplace",
        "พนักงาน", "ceo", "ผู้บริหาร", "บริษัท", "องค์กร",
    ],
    "home": [
        "บ้าน", "home", "ห้องนอน", "ห้องครัว", "ห้องนั่งเล่น", "คฤหาสน์", "บ้านเดี่ยว",
        "townhouse", "คอนโด", "condo", "ที่อยู่อาศัย", "ห้องน้ำ", "ประตูบ้าน",
        "สวนหน้าบ้าน", "ห้องรับแขก", "ห้องทำงานที่บ้าน", "บ้านจัดสรร", "หลังบ้าน",
        "หน้าบ้าน", "ชั้นบน", "ชั้นล่าง", "บันได", "ครัว", "ห้องพระ",
    ],
    "factory": [
        "โรงงาน", "factory", "warehouse", "คลังสินค้า", "โกดัง", "ไลน์ผลิต", "เครื่องจักร",
    ],
    "astrology": [
        "ดวงจีน", "ดวง", "ปีชง", "ชง", "โชค", "ราศี", "นักษัตร", "ดาว", "อุปนิสัย",
        "พื้นดวง", "bazi", "ปีเกิด", "วันเกิด", "ดวงชะตา", "ดวงปี", "ดวงเดือน",
        "ทำนาย", "ปีมะเมีย", "ปีมะโรง", "ปีชวด",
    ],
    "lineage": [
        "อาจารย์เกรียงไกร", "เกรียงไกร", "ชมรมภูมิโหร", "ฮูลิน", "มูลนิธิฮูลิน",
        "สอนฮวงจุ้ย", "ลูกศิษย์", "สายวิชา", "เหล่าเจ็ก", "ปรมาจารย์", "ชมรม",
    ],
    "business": [
        "ธุรกิจ", "business", "บริษัท", "องค์กร", "ผู้บริหาร", "กำไร", "รายได้",
        "การลงทุน", "startup", "franchise", "แฟรนไชส์",
    ],
    "yearly": [
        "ยุค 8", "ยุค 9", "ยุค 1", "ยุค 2", "ยุค 3", "ยุค 4", "ยุค 5", "ยุค 6",
        "ยุค 7", "รายปี", "ประจำปี", "ปี 256", "ปี 202", "ดาว 9", "ดาว 8",
        "เปลี่ยนยุค", "ยุคใหม่",
    ],
    "general": [
        "เกร็ด", "เคล็ด", "ความรู้", "หลักฮวงจุ้ย", "ฮวงจุ้ยคือ", "ทำไม", "ควรรู้",
    ],
    "energy": [
        "พลังงาน", "miracles369", "energy", "healing", "สมดุล", "negative energy",
        "พลังบวก", "พลังลบ",
    ],
}

TITLE_PREFIXES = [
    r"^ที่ปรึกษาฮวงจุ้ย\s*[:：\-–—]\s*",
    r"^ซินแสฮวงจุ้ย\s*[:：\-–—]\s*",
    r"^Fengshui Balance\s*[-–—:：]\s*",
    r"^ฮวงจุ้ย\s*[:：]\s*",
    r"^Aviva Spirit\s*[:：\-–—]\s*",
]

EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U0000FE00-\U0000FE0F"
    "\U0000200D"
    "⁉️❗❓"
    "]+",
    flags=re.UNICODE,
)


def load_articles() -> list[dict]:
    text = ARTICLES_JS.read_text(encoding="utf-8")
    match = re.search(r"window\.FENGSHUI_ARTICLES_FULL\s*=\s*(\[.*\])\s*;?\s*$", text, re.S)
    if not match:
        raise SystemExit("Could not parse articles-full.js")
    return json.loads(match.group(1))


def score_text(text: str, keywords: list[str]) -> int:
    if not text:
        return 0
    lower = text.lower()
    score = 0
    for kw in keywords:
        if kw.lower() in lower:
            score += lower.count(kw.lower())
    return score


def assign_tags(article: dict) -> list[str]:
    title = article.get("title") or ""
    body = (article.get("body") or "")[:1200]
    keyword = article.get("seoKeyword") or ""
    primary = article.get("category") or "general"
    combined = f"{title} {keyword} {body}"

    scores: dict[str, float] = {}
    for tag, words in TAG_KEYWORDS.items():
        s = score_text(title, words) * 4
        s += score_text(keyword, words) * 3
        s += score_text(body, words) * 1
        if tag == primary:
            s += 5
        if s > 0:
            scores[tag] = s

    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    tags: list[str] = []
    for tag, _ in ranked:
        if tag not in tags:
            tags.append(tag)
        if len(tags) == 2:
            break

    if not tags:
        tags = [primary if primary in TAG_META else "general"]
    elif primary not in tags and len(tags) < 2:
        tags.append(primary)
    elif primary not in tags:
        tags = [primary, tags[0] if tags[0] != primary else tags[1]]

    return tags[:2]


def first_meaningful_line(body: str) -> str:
    for raw in body.split("\n"):
        line = raw.strip()
        line = re.sub(r"^[-=_.~·•\s]+", "", line)
        line = EMOJI_RE.sub("", line).strip()
        line = re.sub(r"https?://\S+", "", line).strip()
        if len(line) >= 10 and re.search(r"[\u0E00-\u0E7Fa-zA-Z]", line):
            return line
    return ""


def refine_title(article: dict) -> str:
    title = (article.get("title") or "").strip()
    body = article.get("body") or ""
    keyword = (article.get("seoKeyword") or "").strip()
    tags = article.get("tags") or [article.get("category", "general")]

    t = title
    for pattern in TITLE_PREFIXES:
        t = re.sub(pattern, "", t, flags=re.I)

    t = EMOJI_RE.sub("", t)
    t = re.sub(r"\.{2,}", " ", t)
    t = re.sub(r"\s+", " ", t).strip(" .…-–—:：")
    t = re.sub(r"\(\s*\)", "", t)
    t = re.sub(r"\s*\(\s*ครบทุกประเด็น\s*\)", "", t, flags=re.I)

    replacements = {
        r"^เฉลย\s*Final\s*": "เฉลยครบทุกประเด็น — ",
        r"^Final\s*": "สรุปครบทุกประเด็น — ",
        r"^Q\s*&\s*A\s*[:：]?\s*": "ถาม-ตอบ: ",
        r"^FAQ\s*[:：]?\s*": "ถาม-ตอบ: ",
    }
    for pattern, repl in replacements.items():
        t = re.sub(pattern, repl, t, flags=re.I)

    if len(t) < 10 or t.lower() in {"...", "inbox", "update", "updated"}:
        derived = first_meaningful_line(body)
        if derived:
            t = derived

    if len(t) < 10 and keyword:
        tag_label = TAG_META.get(tags[0], {}).get("th", "")
        t = f"{keyword} — {tag_label}".strip(" —")

    if len(t) < 8:
        t = title or keyword or "บทความฮวงจุ้ย"

    if len(t) > 88:
        cut = t[:88]
        if " " in cut[60:]:
            cut = cut[: cut.rfind(" ")]
        t = cut.rstrip(" ,.-") + "…"

    return t


def tag_label_th(tag: str) -> str:
    meta = TAG_META.get(tag, TAG_META["general"])
    return f"{meta['emoji']} {meta['th']}"


def update_html(article: dict) -> bool:
    path = ARTICLES_DIR / f"{article['id']}.html"
    if not path.exists():
        return False

    html = path.read_text(encoding="utf-8")
    title = article["title"]
    tags = article["tags"]
    tag_text = " · ".join(tag_label_th(t) for t in tags)
    page_title = f"{title} | Fengshui Balance"
    section = TAG_META.get(tags[0], TAG_META["general"])["th"]

    html = re.sub(r"<title>.*?</title>", lambda _m: f"<title>{page_title}</title>", html, count=1)
    html = re.sub(
        r'(<meta property="og:title" content=")(.*?)(")',
        lambda m: f"{m.group(1)}{title}{m.group(3)}",
        html,
        count=1,
    )
    html = re.sub(
        r'("headline"\s*:\s*")(.*?)(")',
        lambda m: f'{m.group(1)}{title}{m.group(3)}',
        html,
        count=1,
    )
    html = re.sub(r"(<h1>)(.*?)(</h1>)", lambda m: f"{m.group(1)}{title}{m.group(3)}", html, count=1)
    html = re.sub(
        r"(<span>📂 หมวดหมู่: ).*?(</span>)",
        lambda m: f"{m.group(1)}{tag_text}{m.group(2)}",
        html,
        count=1,
    )
    html = re.sub(
        r'(<meta property="article:section" content=")(.*?)(")',
        lambda m: f"{m.group(1)}{section}{m.group(3)}",
        html,
        count=1,
    )
    html = html.replace("📈 ความนิยม (WEI):", "📈 ความนิยม:")

    path.write_text(html, encoding="utf-8", newline="\n")
    return True


def save_articles(articles: list[dict]) -> None:
    payload = json.dumps(articles, ensure_ascii=False, separators=(",", ":"))
    ARTICLES_JS.write_text(
        f"window.FENGSHUI_ARTICLES_FULL = {payload};\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    articles = load_articles()
    changed_titles = []
    tag_counts: dict[str, int] = {}
    multi_tag = 0

    for article in articles:
        article["tags"] = assign_tags(article)
        old_title = article["title"]
        article["title"] = refine_title(article)
        if article["title"] != old_title:
            changed_titles.append({"id": article["id"], "before": old_title, "after": article["title"]})
        if len(article["tags"]) > 1:
            multi_tag += 1
        for tag in article["tags"]:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        update_html(article)

    save_articles(articles)

    report = {
        "total": len(articles),
        "titles_refined": len(changed_titles),
        "multi_tag_articles": multi_tag,
        "tag_counts": dict(sorted(tag_counts.items(), key=lambda x: -x[1])),
        "sample_title_changes": changed_titles[:40],
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Processed {len(articles)} articles")
    print(f"Titles refined: {len(changed_titles)}")
    print(f"Articles with 2 tags: {multi_tag}")
    print(f"Tag counts: {report['tag_counts']}")


if __name__ == "__main__":
    main()
