#!/usr/bin/env python3
"""Sync new original Facebook page posts into articles-full.js + articles/*.html"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from facebook_sync_lib import (  # noqa: E402
    DEFAULT_MAX_PAGES,
    DEFAULT_PAGE_SIZE,
    sync_new_posts,
    token_health_report,
)


def configure_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main() -> None:
    configure_stdout()
    parser = argparse.ArgumentParser(description="Import new original Fengshui Balance Facebook posts")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_PAGE_SIZE,
        help=f"Facebook posts per API page (default {DEFAULT_PAGE_SIZE})",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=DEFAULT_MAX_PAGES,
        help=f"Max pages to scan per run when catching up (default {DEFAULT_MAX_PAGES})",
    )
    parser.add_argument(
        "--backfill",
        action="store_true",
        help="Scan full page history once to import any missing posts",
    )
    parser.add_argument(
        "--verify-token",
        action="store_true",
        help="Only verify the Facebook token, then exit",
    )
    args = parser.parse_args()

    if args.verify_token:
        import os

        page_id = os.environ.get("FB_PAGE_ID", "367355370015900")
        token = os.environ.get("FB_PAGE_ACCESS_TOKEN", "").strip()
        if not token:
            raise SystemExit("Missing FB_PAGE_ACCESS_TOKEN")
        report = token_health_report(page_id, token)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if report.get("warning"):
            print(report["warning"], file=sys.stderr)
        return

    result = sync_new_posts(
        dry_run=args.dry_run,
        limit=args.limit,
        max_pages=args.max_pages,
        backfill=args.backfill,
    )

    if result["added"] and not args.dry_run:
        subprocess.run([sys.executable, str(ROOT / "scripts" / "generate-sitemap.py")], check=True)

    report_path = ROOT / "scripts" / "fb-sync-report.json"
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
