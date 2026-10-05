# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///
"""Download the content images from an article, for picking hoax visuals.

Opens the page in a real browser (gets past simple bot blocks), collects every
rendered <img> at least MIN_SIZE px wide, and saves each one plus an index.json.

Usage:
    uv run scripts/fetch_article_images.py <url> <out_dir> [--min 300] [--show]

Example:
    uv run scripts/fetch_article_images.py https://www.kompas.com/cekfakta/read/... tmp/coin
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)

COLLECT_JS = """
(minSize) => [...document.images]
  .filter(img => img.naturalWidth >= minSize && img.getClientRects().length)
  .map(img => ({
    src: img.currentSrc || img.src,
    w: img.naturalWidth, h: img.naturalHeight,
    alt: (img.alt || '').trim().slice(0, 200),
    caption: (img.closest('figure')?.querySelector('figcaption')?.innerText || '').trim().slice(0, 200),
  }))
"""


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2:
        sys.exit(__doc__)
    url, out = args[0], Path(args[1])
    min_size = int(sys.argv[sys.argv.index("--min") + 1]) if "--min" in sys.argv else 300
    out.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless="--show" not in sys.argv)
        except PlaywrightError:
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
            browser = p.chromium.launch(headless="--show" not in sys.argv)
        ctx = browser.new_context(viewport={"width": 1280, "height": 900}, user_agent=UA)
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=60_000)
        # scroll to trigger lazy-loaded images
        for _ in range(12):
            page.mouse.wheel(0, 1200)
            page.wait_for_timeout(300)
        page.wait_for_timeout(1500)

        seen, index = set(), []
        for i, img in enumerate(page.evaluate(COLLECT_JS, min_size)):
            src = urljoin(url, img["src"])
            if src in seen or src.startswith("data:"):
                continue
            seen.add(src)
            resp = ctx.request.get(src, headers={"Referer": url})
            if not resp.ok:
                print(f"  ✗ {resp.status} {src}")
                continue
            ctype = resp.headers.get("content-type", "image/jpeg").split(";")[0]
            ext = {"image/png": ".png", "image/webp": ".webp", "image/gif": ".gif", "image/avif": ".avif"}.get(ctype, ".jpg")
            name = f"{len(index):02d}-{re.sub(r'[^a-z0-9]+', '-', img['alt'].lower())[:40].strip('-') or 'img'}{ext}"
            (out / name).write_bytes(resp.body())
            index.append({"file": name, **img, "src": src})
            print(f"  ✓ {name}  {img['w']}x{img['h']}  {img['alt'][:60]}")
        browser.close()

    (out / "index.json").write_text(json.dumps({"url": url, "images": index}, indent=2, ensure_ascii=False) + "\n")
    print(f"\n{len(index)} image(s) → {out}")


if __name__ == "__main__":
    main()
