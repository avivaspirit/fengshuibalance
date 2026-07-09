#!/usr/bin/env python3
"""Regenerate sitemap.xml, sitemap-main.xml, sitemap-articles.xml and robots.txt for Google Search Console."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://fengshuibalance.net"
TODAY = date.today().isoformat()

STATIC_PAGES = [
    ("", "1.0", "weekly"),
    ("projects.html", "0.9", "monthly"),
    ("ajarn-suppachai.html", "0.9", "monthly"),
    ("ajarn-grianggrai.html", "0.8", "monthly"),
    ("articles.html", "0.9", "weekly"),
    ("brand-portfolio.html", "0.7", "monthly"),
    # English versions
    ("en/index.html", "0.9", "weekly"),
    ("en/projects.html", "0.8", "monthly"),
    ("en/ajarn-suppachai.html", "0.8", "monthly"),
    ("en/ajarn-grianggrai.html", "0.7", "monthly"),
    ("en/articles.html", "0.8", "weekly"),
    ("en/brand-portfolio.html", "0.6", "monthly"),
]

MIN_BODY_CHARS = 600

# Feng shui topic signals — used to filter out non-fengshui content
FENGSHUI_SIGNALS = [
    r"ฮวงจ", r"ทิศ", r"ตำแหน่ง", r"ฤกษ์", r"ดวงจีน", r"ธาตุ",
    r"ยุค\s*\d", r"ดาว", r"ราศี", r"ชง",
    r"บ้าน", r"ออฟฟิศ", r"ร้านค้า", r"โรงงาน",
    r"ห้อง", r"ประตู", r"หน้าต่าง", r"เตียง", r"ครัว",
    r"ตี่จู้", r"ศาลพระภูมิ", r"เจ้าที่", r"ศาล",
    r"เคส", r"วิเคราะห์", r"ปรับแก้", r"ตรวจ",
    r"ซินแส", r"อาจารย์", r"โชค", r"มงคล",
    r"เครื่องราง", r"พระ", r"เหรียญ",
    r"พลังงาน", r"พิธี", r"บุญ", r"สมาธิ", r"จักรวาล", r"วัด",
    r"ดวงชะตา", r"โหราศาสตร์", r"ชัยภูมิ", r"ช่องลม", r"ทำเล",
    r"จันทรุปราคา", r"สุริยุปราคา", r"Full Moon", r"Mercury",
    r"ที่ดิน", r"ก่อสร้าง", r"สถาปัตยกรรม",
]

JUNK_TITLE_PATTERNS = [
    r"^รับวิเคราะห์ดวง$",
    r"^คิวงาน", r"^คิว\s*#", r"^คิว\s*งาน",
    r"Miracles369|Pyramid\s*(GIZA|Orange|Gold|Blue|Pink)",
    r"^แท่ง(พลัง|ชมพู|เขียว|ส้ม|ใหญ่)|^Energy Wand|^Coaster|^Abundance",
    r"เหลือ\s*\d+\s*(แผ่น|ชิ้น|ชุด)",
    r"^Promotion|^โปรโมชั่น|^ลดราคา|หมดเขต",
    r"^บริจาค|^ส่ง Slip|^อย่าส่ง Slip",
    r"งด Share|โพสต์ภายใน",
]


def is_fengshui_content(article: dict) -> bool:
    """Return True if article is real feng shui content worth indexing."""
    body = article.get("body", "").strip()
    title = article.get("title", "").strip()
    wei = article.get("metrics", {}).get("wei", 0)
    full_text = title + " " + body

    # Proven heroes always pass
    if wei >= 5000:
        return True

    # Check junk title patterns
    for pat in JUNK_TITLE_PATTERNS:
        if re.search(pat, title, re.IGNORECASE):
            # Product promo with low engagement
            if re.search(r"Card ทอง|เหรียญทอง", title) and wei < 500:
                return False
            return False

    # Check admin ratio in body
    lines = [l.strip() for l in body.split("\n") if l.strip()]
    if lines:
        admin_kw = r"ค่าปรึกษา|Inbox|inbox|โอนเงิน|ส่งสลิป|จองล่วงหน้า|พิมพ์.*จอง|EMS|เลขพัสดุ"
        admin_lines = sum(1 for l in lines if re.search(admin_kw, l, re.IGNORECASE))
        if len(lines) > 5 and admin_lines / len(lines) > 0.4:
            return False

    # Need at least 2 feng shui signals
    signal_count = sum(1 for p in FENGSHUI_SIGNALS if re.search(p, full_text, re.IGNORECASE))
    if signal_count >= 2:
        return True

    # WEI override
    if wei >= 1000:
        return True

    # Title brand prefix
    if re.search(r"ฮวงจ|ซินแส|อาจารย์|ปรึกษา", title):
        return True

    return False


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


def is_noindexed(article_id: str) -> bool:
    """Check if the generated HTML file for this article has a noindex robots tag."""
    html_path = ROOT / "articles" / f"{article_id}.html"
    if not html_path.exists():
        return False
    head = html_path.read_text(encoding="utf-8", errors="ignore")[:4096]
    return 'name="robots" content="noindex"' in head


def build_articles_sitemap(articles: list[dict]) -> str:
    quality_articles = [
        a for a in articles
        if len(a.get("body", "").strip()) >= MIN_BODY_CHARS
        and not is_noindexed(a["id"])
        and is_fengshui_content(a)
    ]
    total_body_ok = sum(1 for a in articles if len(a.get("body", "").strip()) >= MIN_BODY_CHARS)
    skipped_noindex = sum(1 for a in articles if is_noindexed(a["id"]))
    skipped_junk = total_body_ok - len(quality_articles)
    print(f"  {total_body_ok}/{len(articles)} articles have body >= {MIN_BODY_CHARS} chars")
    print(f"  Skipped {skipped_noindex} noindexed articles")
    print(f"  Skipped {skipped_junk} non-fengshui/junk articles")
    print(f"  Final: {len(quality_articles)} quality feng shui articles in sitemap")

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
        "# Fengshui Balance — allow search engines and AI crawlers\n"
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        "User-agent: Googlebot\n"
        "Allow: /\n"
        "\n"
        "User-agent: Googlebot-Image\n"
        "Allow: /assets/images/\n"
        "\n"
        "# AI / LLM crawlers — ALLOWED (user wants AI tools to read articles)\n"
        "User-agent: GPTBot\n"
        "Allow: /\n"
        "\n"
        "User-agent: ChatGPT-User\n"
        "Allow: /\n"
        "\n"
        "User-agent: OAI-SearchBot\n"
        "Allow: /\n"
        "\n"
        "User-agent: CCBot\n"
        "Allow: /\n"
        "\n"
        "User-agent: Google-Extended\n"
        "Allow: /\n"
        "\n"
        "User-agent: PerplexityBot\n"
        "Allow: /\n"
        "\n"
        "User-agent: anthropic-ai\n"
        "Allow: /\n"
        "\n"
        "User-agent: ClaudeBot\n"
        "Allow: /\n"
        "\n"
        "User-agent: Claude-Web\n"
        "Allow: /\n"
        "\n"
        "User-agent: Applebot-Extended\n"
        "Allow: /\n"
        "\n"
        "User-agent: cohere-ai\n"
        "Allow: /\n"
        "\n"
        "User-agent: meta-externalagent\n"
        "Allow: /\n"
        "\n"
        "User-agent: Amazonbot\n"
        "Allow: /\n"
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

    # quality_count already computed inside build_articles_sitemap as len(quality_articles)
    article_count = len([a for a in articles if len(a.get("body", "").strip()) >= MIN_BODY_CHARS and not is_noindexed(a["id"])])
    print(f"Wrote sitemap.xml (index)")
    print(f"Wrote sitemap-main.xml ({len(STATIC_PAGES)} URLs, incl. /en/)")
    print(f"Wrote sitemap-articles.xml ({article_count} URLs)")
    print(f"Wrote robots.txt")


if __name__ == "__main__":
    main()
