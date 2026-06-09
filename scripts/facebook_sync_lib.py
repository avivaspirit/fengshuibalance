"""Fetch Fengshui Balance Facebook page posts and build article records."""

from __future__ import annotations

import importlib.util
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTICLES_JS = ROOT / "articles-full.js"
ARTICLES_DIR = ROOT / "articles"
STATE_FILE = ROOT / "scripts" / "fb-sync-state.json"
PAGE_STATS_FILE = ROOT / "page-stats.json"
DEFAULT_IMAGE = "assets/images/modern-chinese-spirit-house-teeju.jpg"
DEFAULT_ALT = "บทความฮวงจุ้ยจาก Fengshui Balance"
GRAPH_VERSION = "v21.0"

DEFAULT_PAGE_SIZE = 25
DEFAULT_MAX_PAGES = 40
BACKFILL_MAX_PAGES = 200

SHARED_STATUS_TYPES = {
    "shared_story",
    "shared",
}

POST_FIELDS = ",".join(
    [
        "id",
        "message",
        "created_time",
        "status_type",
        "permalink_url",
        "from",
        "parent_id",
        "attachments{type,media_type,url,title,description,media,target}",
        "reactions.summary(true)",
        "comments.summary(true)",
        "shares",
    ]
)


def load_enrich_module():
    path = ROOT / "scripts" / "enrich-article-tags-titles.py"
    spec = importlib.util.spec_from_file_location("enrich_titles", path)
    if not spec or not spec.loader:
        raise RuntimeError("Could not load enrich-article-tags-titles.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_articles() -> list[dict]:
    text = ARTICLES_JS.read_text(encoding="utf-8")
    match = re.search(r"window\.FENGSHUI_ARTICLES_FULL\s*=\s*(\[.*\])\s*;?\s*$", text, re.S)
    if not match:
        raise RuntimeError("Could not parse articles-full.js")
    return json.loads(match.group(1))


def save_articles(articles: list[dict]) -> None:
    payload = json.dumps(articles, ensure_ascii=False, separators=(",", ":"))
    ARTICLES_JS.write_text(f"window.FENGSHUI_ARTICLES_FULL = {payload};\n", encoding="utf-8", newline="\n")


def next_article_id(articles: list[dict]) -> str:
    max_num = 0
    for article in articles:
        match = re.fullmatch(r"wei-(\d+)", article.get("id", ""))
        if match:
            max_num = max(max_num, int(match.group(1)))
    return f"wei-{max_num + 1:03d}"


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"last_sync_at": None, "known_source_ids": []}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")


def graph_get(path: str, token: str, params: dict | None = None) -> dict:
    query = {"access_token": token}
    if params:
        query.update(params)
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{path}?{urllib.parse.urlencode(query)}"
    request = urllib.request.Request(url, headers={"User-Agent": "FengshuiBalanceSync/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Facebook API error {exc.code}: {body}") from exc


def verify_page_token(page_id: str, token: str) -> dict:
    """Quick live check — confirms the token can read the page."""
    payload = graph_get(page_id, token, {"fields": "id,name"})
    return {
        "ok": True,
        "page_id": payload.get("id"),
        "page_name": payload.get("name"),
    }


def fetch_page_fan_count(page_id: str, token: str) -> int:
    """Return live Facebook page follower count from Graph API."""
    payload = graph_get(page_id, token, {"fields": "fan_count,followers_count"})
    count = payload.get("followers_count") or payload.get("fan_count") or 0
    return int(count)


def sync_page_stats(page_id: str, token: str, dry_run: bool = False) -> dict:
    """Write homepage follower stats from the live Facebook page."""
    fan_count = fetch_page_fan_count(page_id, token)
    followers_k = max(1, fan_count // 1000)
    stats = {
        "followers": fan_count,
        "followersK": followers_k,
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "pageId": page_id,
    }
    if not dry_run:
        PAGE_STATS_FILE.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    return stats


def inspect_token_expiry(token: str) -> dict:
    """Return expiry metadata when FB_APP_ID + FB_APP_SECRET are configured."""
    app_id = os.environ.get("FB_APP_ID", "").strip()
    app_secret = os.environ.get("FB_APP_SECRET", "").strip()
    if not app_id or not app_secret:
        return {"checked": False, "reason": "FB_APP_ID and FB_APP_SECRET not set"}

    app_token = f"{app_id}|{app_secret}"
    payload = graph_get(
        "debug_token",
        app_token,
        {"input_token": token},
    )
    data = payload.get("data") or {}
    expires_at = int(data.get("expires_at") or 0)
    never_expires = expires_at == 0 and bool(data.get("is_valid"))

    result = {
        "checked": True,
        "valid": bool(data.get("is_valid")),
        "never_expires": never_expires,
        "expires_at": expires_at,
        "scopes": data.get("scopes") or [],
        "type": data.get("type"),
    }
    if expires_at:
        result["expires_at_iso"] = datetime.fromtimestamp(expires_at, tz=timezone.utc).isoformat()
        days_left = (expires_at - int(datetime.now(timezone.utc).timestamp())) / 86400
        result["days_left"] = round(days_left, 1)
    return result


def token_health_report(page_id: str, token: str) -> dict:
    report = verify_page_token(page_id, token)
    expiry = inspect_token_expiry(token)
    report["expiry"] = expiry
    if expiry.get("checked") and expiry.get("valid") is False:
        raise RuntimeError("Facebook token is invalid — regenerate a permanent Page token")
    if expiry.get("checked") and expiry.get("days_left") is not None and expiry["days_left"] < 14:
        report["warning"] = f"Token expires in {expiry['days_left']} days — replace with a permanent System User token"
    elif expiry.get("never_expires"):
        report["warning"] = None
        report["permanent"] = True
    return report


def is_original_page_post(post: dict, page_id: str) -> bool:
    """True only for posts authored by the page — not re-shares."""
    page_id = str(page_id)
    if str(post.get("from", {}).get("id")) != page_id:
        return False
    if post.get("parent_id"):
        return False

    status_type = (post.get("status_type") or "").lower()
    if status_type in SHARED_STATUS_TYPES or "shared" in status_type:
        return False

    attachments = (post.get("attachments") or {}).get("data", [])
    for attachment in attachments:
        attachment_type = (attachment.get("type") or "").lower()
        if attachment_type == "share":
            return False

    message = (post.get("message") or "").strip()
    has_original_media = any(
        (item.get("type") or "").lower() in {"photo", "video", "album", "video_inline", "native_templates"}
        for item in attachments
    )
    return bool(message or has_original_media)


def pick_image(post: dict) -> str:
    for attachment in (post.get("attachments") or {}).get("data", []):
        media = attachment.get("media") or {}
        image = media.get("image") or {}
        if image.get("src"):
            break
    return DEFAULT_IMAGE


def post_metrics(post: dict) -> dict:
    reactions = ((post.get("reactions") or {}).get("summary") or {}).get("total_count") or 0
    comments = ((post.get("comments") or {}).get("summary") or {}).get("total_count") or 0
    shares = (post.get("shares") or {}).get("count") or 0
    wei = reactions + comments * 2 + shares * 3
    return {
        "wei": wei,
        "reactions": reactions,
        "comments": comments,
        "shares": shares,
    }


def guess_seo_keyword(message: str) -> str:
    lower = message.lower()
    if "ซินแสฮวงจุ้ย กรุงเทพ" in message:
        return "ซินแสฮวงจุ้ย กรุงเทพ"
    if "ที่ปรึกษาฮวงจุ้ย" in message:
        return "ที่ปรึกษาฮวงจุ้ย"
    if "ฮวงจุ้ย สมดุลแห่งธรรมชาติ" in message:
        return "ฮวงจุ้ย สมดุลแห่งธรรมชาติ"
    if "fengshui balance" in lower:
        return "Fengshui Balance"
    return "ซินแสฮวงจุ้ย"


def build_article(post: dict, article_id: str, enrich) -> dict:
    message = (post.get("message") or "").strip() or "บทความจาก Fengshui Balance"
    created = post.get("created_time") or datetime.now(timezone.utc).isoformat()
    date = created[:10]
    permalink = post.get("permalink_url") or f"https://www.facebook.com/{post.get('id')}"

    article = {
        "id": article_id,
        "sourceId": post["id"],
        "title": message.split("\n", 1)[0][:120],
        "seoKeyword": guess_seo_keyword(message),
        "category": "general",
        "image": pick_image(post),
        "alt": DEFAULT_ALT,
        "date": date,
        "url": permalink,
        "metrics": post_metrics(post),
        "body": message,
    }
    article["tags"] = enrich.assign_tags(article)
    article["title"] = enrich.refine_title(article)
    return article


def iter_post_pages(page_id: str, token: str, page_size: int, max_pages: int):
    params: dict[str, str] = {"fields": POST_FIELDS, "limit": str(page_size)}
    for _ in range(max_pages):
        payload = graph_get(f"{page_id}/posts", token, params)
        batch = payload.get("data") or []
        if not batch:
            return
        yield batch
        after = ((payload.get("paging") or {}).get("cursors") or {}).get("after")
        if not after:
            return
        params = {"fields": POST_FIELDS, "limit": str(page_size), "after": after}


def collect_candidates(
    page_id: str,
    token: str,
    existing_ids: set[str],
    *,
    page_size: int = DEFAULT_PAGE_SIZE,
    max_pages: int = DEFAULT_MAX_PAGES,
    backfill: bool = False,
) -> tuple[list[dict], int, int, int]:
    """Return (new_posts, skipped_shared, checked_raw, pages_scanned)."""
    candidates: list[dict] = []
    skipped_shared = 0
    checked = 0
    pages_scanned = 0
    pages_without_new = 0
    scan_limit = BACKFILL_MAX_PAGES if backfill else max_pages

    for batch in iter_post_pages(page_id, token, page_size, scan_limit):
        pages_scanned += 1
        batch_new = 0
        batch_originals = 0

        for raw in batch:
            checked += 1
            if not is_original_page_post(raw, page_id):
                skipped_shared += 1
                continue
            batch_originals += 1
            if raw["id"] in existing_ids:
                continue
            candidates.append(raw)
            batch_new += 1

        if backfill:
            continue

        if batch_originals and batch_new == 0:
            pages_without_new += 1
            if pages_without_new >= 2:
                break
        else:
            pages_without_new = 0

    return candidates, skipped_shared, checked, pages_scanned


def render_article_html(article: dict, enrich) -> str:
    path = ROOT / "scripts" / "generate-article-page.py"
    spec = importlib.util.spec_from_file_location("generate_article_page", path)
    if not spec or not spec.loader:
        raise RuntimeError("Could not load generate-article-page.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.render_article_html(article, enrich)


def sync_new_posts(
    dry_run: bool = False,
    limit: int = DEFAULT_PAGE_SIZE,
    max_pages: int = DEFAULT_MAX_PAGES,
    backfill: bool = False,
) -> dict:
    page_id = os.environ.get("FB_PAGE_ID", "367355370015900")
    token = os.environ.get("FB_PAGE_ACCESS_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Missing FB_PAGE_ACCESS_TOKEN environment variable")

    token_report = token_health_report(page_id, token)
    page_stats = sync_page_stats(page_id, token, dry_run=dry_run)
    enrich = load_enrich_module()
    articles = load_articles()
    existing_ids = {article.get("sourceId") for article in articles if article.get("sourceId")}
    state = load_state()

    candidates, skipped_shared, checked, pages_scanned = collect_candidates(
        page_id,
        token,
        existing_ids,
        page_size=limit,
        max_pages=max_pages,
        backfill=backfill,
    )

    added: list[dict] = []
    for post in candidates:
        article_id = next_article_id(articles)
        article = build_article(post, article_id, enrich)
        added.append(article)
        articles.append(article)
        existing_ids.add(post["id"])

        if not dry_run:
            html_path = ARTICLES_DIR / f"{article_id}.html"
            html_path.write_text(render_article_html(article, enrich), encoding="utf-8", newline="\n")
            enrich.update_html(article)

    if added and not dry_run:
        save_articles(articles)
        state["last_sync_at"] = datetime.now(timezone.utc).isoformat()
        state["known_source_ids"] = sorted(existing_ids)
        save_state(state)

    return {
        "added": len(added),
        "skipped_shared": skipped_shared,
        "checked": checked,
        "pages_scanned": pages_scanned,
        "backfill": backfill,
        "token": {
            "page_name": token_report.get("page_name"),
            "permanent": token_report.get("permanent"),
            "warning": token_report.get("warning"),
        },
        "page_stats": page_stats,
        "articles": [{"id": a["id"], "title": a["title"], "url": a["url"]} for a in added],
        "dry_run": dry_run,
    }
