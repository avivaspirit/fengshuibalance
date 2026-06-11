# Generate WebP versions of homepage-critical images (originals untouched).
# Usage: python scripts/optimize-homepage-images.py
import os
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), "..", "assets", "images")

# (filename, max_width)
TARGETS = [
    ("luxury-garden-home-entrance-good-vibe-cover.jpg", 1600),  # hero / og
    ("ajarn-suppachai-fengshui-consultant.png", 960),
    ("ajarn-suppachai-amarin-portrait.png", 960),
    ("homey-balanced-house-entrance-cover.jpg", 960),
    ("executive-office-leadership-position-cover.jpg", 960),
    ("aviva-modern-spirit-house-shrine.png", 960),
    ("recommended-destiny-auspicious-timing-cover.jpg", 960),
    ("boutique-shopfront-customer-flow-cover.jpg", 960),
    ("residential-water-garden-corner-cover.jpg", 960),
    ("home-foyer-staircase-entry-flow-cover.jpg", 960),
    ("wisdom-star-study-room-fengshui-cover.jpg", 960),
    ("modern-chinese-spirit-house-teeju.jpg", 960),
    ("ajarn-suppachai-microphone.png", 800),
    ("ajarn-grianggrai-portrait.png", 800),
    ("modern-marble-spirit-house-aviva.jpg", 960),
    ("recommended-fire-horse-2026-fengshui-cover.jpg", 960),
]

for name, max_w in TARGETS:
    src = os.path.join(ROOT, name)
    if not os.path.exists(src):
        print(f"SKIP (missing): {name}")
        continue
    dst = os.path.splitext(src)[0] + ".webp"
    img = Image.open(src)
    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
    img = img.convert("RGBA" if has_alpha else "RGB")
    if img.width > max_w:
        img = img.resize((max_w, round(img.height * max_w / img.width)), Image.LANCZOS)
    img.save(dst, "WEBP", quality=78, method=6)
    print(f"{name}: {os.path.getsize(src)//1024}KB -> {os.path.basename(dst)}: {os.path.getsize(dst)//1024}KB ({img.width}x{img.height})")
