"""Generate .webp twins for every image referenced by the article archive.

Run from the website root (or anywhere — paths are resolved relative to this
file's parent directory). Skips images that already have an up-to-date webp.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUALITY = 80
MAX_WIDTH = 1280


def article_images():
    src_path = os.path.join(ROOT, "articles-full.js")
    src = open(src_path, encoding="utf-8").read()
    data = json.loads(src[src.index("[") : src.rindex("]") + 1])
    return sorted({a.get("image", "") for a in data if a.get("image")})


def main():
    from PIL import Image

    imgs = article_images()
    print(f"unique article images: {len(imgs)}")
    made, skipped, missing = 0, 0, 0
    for rel in imgs:
        src = os.path.join(ROOT, rel.replace("/", os.sep))
        if not os.path.exists(src):
            print(f"  ! source missing: {rel}")
            missing += 1
            continue
        base, _ = os.path.splitext(src)
        dst = base + ".webp"
        if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
            skipped += 1
            continue
        im = Image.open(src)
        if im.mode in ("P", "CMYK"):
            im = im.convert("RGBA" if "transparency" in im.info else "RGB")
        if im.width > MAX_WIDTH:
            im = im.resize((MAX_WIDTH, round(im.height * MAX_WIDTH / im.width)), Image.LANCZOS)
        im.save(dst, "WEBP", quality=QUALITY, method=6)
        made += 1
        print(f"  + {os.path.relpath(dst, ROOT)} ({os.path.getsize(dst)//1024}KB)")
    print(f"done: {made} created, {skipped} up-to-date, {missing} missing sources")


if __name__ == "__main__":
    sys.exit(main())
