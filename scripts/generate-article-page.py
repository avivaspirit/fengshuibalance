"""Render a single article HTML page from article JSON."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

BASE_URL = "https://fengshuibalance.vercel.app"

TAG_SECTION_TH = {
    "timing": "ฤกษ์มงคลและฤกษ์กระทำการ (Auspicious Timing)",
    "spirit": "ศาลและตี่จู้ (Spirit House)",
    "shop": "ร้านค้า (Shop)",
    "office": "ออฟฟิศ (Office)",
    "home": "บ้าน (Home)",
    "factory": "โรงงาน (Factory)",
    "astrology": "ดวงจีน (Destiny)",
    "lineage": "สายวิชา (Lineage)",
    "general": "บันทึกฮวงจุ้ย (Fengshui Notes)",
    "business": "ธุรกิจ (Business)",
    "yearly": "รายปี (Yearly)",
    "energy": "พลังงาน (Energy)",
}


def tag_label_row(article: dict, enrich) -> str:
    tags = article.get("tags") or [article.get("category", "general")]
    return " · ".join(enrich.tag_label_th(tag) for tag in tags[:2])


def eyebrow_for(article: dict) -> str:
    tags = article.get("tags") or [article.get("category", "general")]
    return TAG_SECTION_TH.get(tags[0], TAG_SECTION_TH["general"])


def format_popularity(article: dict) -> str:
    wei = (article.get("metrics") or {}).get("wei")
    if wei is None:
        return "0"
    return f"{int(round(wei)):,}"


def render_body(body: str) -> str:
    import sys
    from pathlib import Path

    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from article_body_format import format_article_body

    return format_article_body(body or "")


def meta_description(body: str, limit: int = 160) -> str:
    clean = re.sub(r"\s+", " ", (body or "").strip())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 3].rstrip() + "..."


def render_article_html(article: dict, enrich) -> str:
    title = html.escape(article["title"])
    description = html.escape(meta_description(article.get("body", "")))
    article_url = f"{BASE_URL}/articles/{article['id']}.html"
    image = article.get("image") or ""
    og_image = f"{BASE_URL}/{image.lstrip('/')}" if image else BASE_URL
    date = html.escape(article.get("date") or "")
    eyebrow = html.escape(eyebrow_for(article))
    tag_row = html.escape(tag_label_row(article, enrich))
    popularity = format_popularity(article)
    body_html = render_body(article.get("body", ""))
    summary_text = html.escape(meta_description(article.get("body", ""), limit=180))
    summary_html = f'<p class="article-callout">💡 สรุปใจความสำคัญ: {summary_text}</p>\n' if summary_text else ""

    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article["title"],
        "description": meta_description(article.get("body", "")),
        "image": og_image,
        "datePublished": article.get("date"),
        "author": {
            "@type": "Person",
            "name": "Ajarn Suppachai Vivattanaprasert",
            "url": f"{BASE_URL}/ajarn-suppachai.html",
        },
        "publisher": {
            "@type": "ProfessionalService",
            "name": "Fengshui Balance",
            "url": f"{BASE_URL}/",
        },
        "mainEntityOfPage": {"@type": "WebPage", "@id": article_url},
    }

    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Fengshui Balance", "item": f"{BASE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": "คลังความรู้", "item": f"{BASE_URL}/articles.html"},
            {"@type": "ListItem", "position": 3, "name": article["title"]},
        ],
    }

    return f"""<!doctype html>
<html lang="th">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
    <link rel="apple-touch-icon" href="../assets/favicon.svg">
    <link rel="shortcut icon" href="../assets/favicon.svg">
    <title>{title} | Fengshui Balance</title>
    <meta name="description" content="{description}">
    <link rel="canonical" href="{article_url}">
    <link rel="alternate" hreflang="th" href="{article_url}">
    <link rel="alternate" hreflang="en" href="{article_url}">
    <link rel="alternate" hreflang="x-default" href="{article_url}">
    <meta property="og:type" content="article">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{html.escape(og_image)}">
    <meta property="og:url" content="{article_url}">
    <meta property="article:published_time" content="{date}">
    <script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
    <script type="application/ld+json">{json.dumps(breadcrumb_schema, ensure_ascii=False)}</script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Manrope:wght@400;600;700&family=Noto+Sans+Thai:wght@400;600;700&family=Noto+Serif+Thai:wght@700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../styles.css">
  </head>
  <body class="article-page">
    <header class="site-header">
      <a class="brand" href="../index.html#top">
        <span class="brand-mark" aria-hidden="true"></span>
        <span>
          <strong>Fengshui Balance</strong>
          <small>ฮวงจุ้ย สมดุลแห่งธรรมชาติ</small>
        </span>
      </a>
      <nav class="site-nav" aria-label="Primary navigation">
        <a href="../index.html#services">ปรึกษา</a>
        <a href="../index.html#method">วิธีทำงาน</a>
        <a href="../index.html#work">เคสงาน</a>
        <a href="../projects.html">ผลงานอ้างอิง</a>
        <a href="../ajarn-suppachai.html">สายวิชา</a>
        <a href="../articles.html">คลังความรู้</a>
        <a class="nav-cta" href="https://www.facebook.com/fengshuibalance" target="_blank" rel="noreferrer">ติดต่ออาจารย์</a>
      </nav>
    </header>
    <main class="article-page-main">
      <article class="article-card-detail">
        <header class="article-header">
          <p class="eyebrow">{eyebrow}</p>
          <h1>{title}</h1>
          <div class="article-meta">
            <span>📅 วันที่: {date}</span>
            <span>📂 หมวดหมู่: {tag_row}</span>
            <span>📈 ความนิยม: {popularity}</span>
          </div>
        </header>
        <div class="article-content" data-formatted="true" data-brand-linked="true">{summary_html}{body_html}</div>
        <div class="article-footer-cta">
          <h3>จัดปรับพื้นที่และสถาปัตยกรรมตามหลักฮวงจุ้ย</h3>
          <p>ให้คำปรึกษาและวิเคราะห์พื้นที่จริงสำหรับบ้าน คฤหาสน์ ออฟฟิศ และวางตำแหน่งศาลเจ้าที่/ตี่จู้ โดยอาจารย์สุภชัย วิวัฒนะประเสริฐ</p>
          <a class="button primary" href="{html.escape(article.get('url', 'https://www.facebook.com/fengshuibalance'))}" target="_blank" rel="noreferrer">ดูโพสต์ต้นฉบับบน Facebook</a>
        </div>
      </article>
    </main>
    <footer class="site-footer">
      <p>Fengshui Balance - <span>ฮวงจุ้ย สมดุลแห่งธรรมชาติ</span></p>
    </footer>
    <script src="../article-enhancements.js?v=20260608"></script>
  </body>
</html>
"""
