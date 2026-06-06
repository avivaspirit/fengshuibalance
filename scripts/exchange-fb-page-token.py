#!/usr/bin/env python3
"""
Exchange a short-lived token (from Graph API Explorer) into a long-lived Page token.

Meta still requires ONE manual browser step: copy a short-lived token from
https://developers.facebook.com/tools/explorer/ while logged in as a page admin.

Usage (env vars only — never commit tokens):
  set FB_APP_ID=...
  set FB_APP_SECRET=...
  set FB_PAGE_ID=367355370015900
  set FB_SHORT_LIVED_TOKEN=...   # from Graph API Explorer
  python scripts/exchange-fb-page-token.py

Optional: write token to a local gitignored file:
  python scripts/exchange-fb-page-token.py --write-local .env.local
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

GRAPH = "https://graph.facebook.com/v21.0"


def get(url: str, params: dict) -> dict:
    full = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(full, headers={"User-Agent": "FengshuiBalanceTokenHelper/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Facebook API error {exc.code}: {body}") from exc


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description="Exchange short-lived FB token for Page token")
    parser.add_argument(
        "--write-local",
        metavar="PATH",
        help="Write FB_PAGE_ACCESS_TOKEN to a local file (must be gitignored)",
    )
    args = parser.parse_args()

    app_id = os.environ.get("FB_APP_ID", "").strip()
    app_secret = os.environ.get("FB_APP_SECRET", "").strip()
    page_id = os.environ.get("FB_PAGE_ID", "367355370015900").strip()
    short = os.environ.get("FB_SHORT_LIVED_TOKEN", "").strip()

    missing = [k for k, v in [
        ("FB_APP_ID", app_id),
        ("FB_APP_SECRET", app_secret),
        ("FB_SHORT_LIVED_TOKEN", short),
    ] if not v]
    if missing:
        raise SystemExit(
            "Missing env vars: " + ", ".join(missing) + "\n\n"
            "One-time browser step:\n"
            "  1. https://developers.facebook.com/apps/ → your app → App ID + App Secret\n"
            "  2. https://developers.facebook.com/tools/explorer/\n"
            "     - Select your app\n"
            "     - Add permissions: pages_read_engagement, pages_show_list\n"
            "     - Generate token → copy as FB_SHORT_LIVED_TOKEN\n"
            "  3. Run this script again\n"
        )

    long_lived = get(
        f"{GRAPH}/oauth/access_token",
        {
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": short,
        },
    )
    user_token = long_lived.get("access_token")
    if not user_token:
        raise SystemExit(f"Could not exchange token: {json.dumps(long_lived, indent=2)}")

    pages = get(f"{GRAPH}/me/accounts", {"access_token": user_token})
    page_token = None
    page_name = None
    for page in pages.get("data") or []:
        if str(page.get("id")) == page_id:
            page_token = page.get("access_token")
            page_name = page.get("name")
            break

    if not page_token:
        raise SystemExit(
            f"Page {page_id} not found in your account list. "
            "Make sure the token user is admin of Fengshui Balance page."
        )

    debug = get(
        f"{GRAPH}/debug_token",
        {
            "input_token": page_token,
            "access_token": f"{app_id}|{app_secret}",
        },
    )
    data = debug.get("data") or {}
    expires_at = int(data.get("expires_at") or 0)
    never = expires_at == 0 and bool(data.get("is_valid"))

    report = {
        "page_id": page_id,
        "page_name": page_name,
        "token_valid": bool(data.get("is_valid")),
        "never_expires": never,
        "expires_at": expires_at if expires_at else None,
        "scopes": data.get("scopes") or [],
        "page_access_token": page_token,
        "github_secret": "Add page_access_token value to GitHub → FB_PAGE_ACCESS_TOKEN",
    }
    print(json.dumps({**report, "page_access_token": "***redacted***"}, ensure_ascii=False, indent=2))
    print("\n--- PAGE ACCESS TOKEN (copy to GitHub Secret FB_PAGE_ACCESS_TOKEN) ---")
    print(page_token)
    print("--- END ---")

    if args.write_local:
        path = args.write_local
        content = (
            f"FB_PAGE_ID={page_id}\n"
            f"FB_PAGE_ACCESS_TOKEN={page_token}\n"
            f"FB_APP_ID={app_id}\n"
            f"FB_APP_SECRET={app_secret}\n"
        )
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(content)
        print(f"\nWrote {path} (keep gitignored, never commit)")


if __name__ == "__main__":
    main()
