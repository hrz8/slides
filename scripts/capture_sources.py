# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright>=1.48"]
# ///
"""Capture "source cards" from articles for slide placeholders.

For each source: open the page, find the passage that contains `target_text`,
highlight key phrases, and screenshot a clean card (site · headline · passage · URL).
This avoids page chrome, ads, and unrelated photos.

Usage:
    uv run scripts/capture_sources.py              # all sources
    uv run scripts/capture_sources.py id-prabowo   # only one id
    uv run scripts/capture_sources.py --show       # headed browser (debugging)
    uv run scripts/capture_sources.py --full       # also save a raw full-page screenshot

Outputs (public/assets/screenshots/):
    <id>.png          the source card
    <id>-page.png     raw full-page screenshot (with --full)
    sources.json      url, title, passage text, captured_at
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "assets" / "screenshots"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"
)


@dataclass
class Source:
    id: str
    url: str
    site: str
    # Smallest element containing this text is the passage
    target_text: str
    # Walk up N parents from the passage (e.g. to grab a whole card)
    ascend: int = 0
    # Headline: CSS selector, or None to omit
    title_selector: str | None = "h1"
    # Look for the headline inside the passage's Nth ancestor (None = whole page)
    title_scope_ascend: int | None = None
    # Regex (JS syntax) removed from the headline, e.g. badges glued to the title
    title_strip: str | None = None
    highlight: list[str] = field(default_factory=list)


SOURCES = [
    Source(
        id="my-jpj",
        url="https://utusanmelayuplus.com/jpj-nafi-video-kononnya-petugas-bergaduh-dengan-pelanggan-dipercayai-dijana-ai/",
        site="Utusan Melayu Plus · Jul 2026",
        target_text="silento",
        title_selector="h1",
        highlight=["dakwaan tidak benar", "TikTok"],
    ),
    Source(
        id="my-sara",
        url="https://www.thevibes.com/articles/news/112204/rm100-sara-aid-via-mykad-begins-nationwide-distribution",
        site="The Vibes · Aug 2025",
        target_text="MyKad",
        title_selector="h1",
        highlight=["RM100", "MyKad", "18 and above"],
    ),
    Source(
        id="id-srimulyani",
        url="https://ekonomi.republika.co.id/berita/t18wf6409/sri-mulyani-bantah-sebut-guru-beban-negara-cap-video-viral-hoaks-hasil-deepfake",
        site="Republika · 19 Agu 2025",
        target_text="hasil deepfake dan potongan tidak utuh",
        title_selector="h1",
        highlight=["HOAX", "deepfake", "tidak pernah menyatakan", "potongan tidak utuh"],
    ),
    Source(
        id="my-anwar",
        url="https://incidentdatabase.ai/entities/anwar-ibrahim/",
        site="AI Incident Database · Incident 1136",
        target_text="Purported AI-generated deepfake videos depicting",
        title_selector="h1, h2, h3, h4, h5",
        title_scope_ascend=1,  # headline lives in the incident card around the summary <p>
        title_strip=r"^Incident\s*\d+\s*\d+\s*Reports?",  # "Incident 1136" + "3 Report" badge
        highlight=["deepfake videos", "Anwar Ibrahim", "fraudulent investment schemes"],
    ),
    Source(
        id="id-prabowo",
        url="https://www.hukumonline.com/berita/a/deepfake-menyebar-cepat--hukum-bergerak-lambat-lt68f065103ad53",
        site="Hukumonline · Opini",
        target_text="Bareskrim Polri menangkap AMA",
        title_selector="h1",
        highlight=["Januari 2025", "deepfake", "bantuan sosial pemerintah", "20 provinsi"],
    ),
]

BUILD_CARD_JS = """
({ targetText, ascend, titleSelector, titleScopeAscend, titleStrip, highlight, site, url }) => {
  const leaves = [...document.querySelectorAll('body *')]
    .filter(el => !el.closest('script,style,noscript,template') && el.getClientRects().length)
    .filter(el => el.textContent.includes(targetText));
  // deepest match = smallest element containing the text
  let el = leaves.filter(a => !leaves.some(b => b !== a && a.contains(b))).at(-1);
  if (!el) return { error: `target text not found: ${targetText}` };
  let scope = document;
  if (titleScopeAscend !== null) {
    scope = el;
    for (let i = 0; i < titleScopeAscend && scope.parentElement; i++) scope = scope.parentElement;
  }
  for (let i = 0; i < ascend && el.parentElement; i++) el = el.parentElement;

  const card = document.createElement('div');
  card.id = '__capture_card';
  card.style.cssText = `
    position: absolute; left: 0; top: 0; z-index: 2147483647; width: 760px;
    box-sizing: border-box; padding: 32px 36px 24px; background: #fff; color: #111;
    font: 20px/1.55 Inter, system-ui, -apple-system, sans-serif; border-radius: 0;`;

  const label = document.createElement('div');
  label.textContent = site;
  label.style.cssText = 'font-size:14px;letter-spacing:.08em;text-transform:uppercase;color:#6b7280;font-weight:600;margin-bottom:10px';
  card.appendChild(label);

  if (titleSelector) {
    const t = scope.querySelector(titleSelector);
    // missing or empty element: fall back to <title> minus the " | Site" suffix
    const raw = (t && t.textContent.trim()) || document.title.split(/\\s+[|–-]\\s+/)[0].trim();
    if (raw) {
      const h = document.createElement('div');
      let text = raw;
      if (titleStrip) text = text.replace(new RegExp(titleStrip), '').trim();
      h.textContent = text;
      h.style.cssText = 'font-size:28px;line-height:1.25;font-weight:800;margin-bottom:14px';
      card.appendChild(h);
    }
  }

  const body = el.cloneNode(true);
  body.querySelectorAll('img,picture,video,iframe,figure,button,svg,a[role=button]').forEach(n => n.remove());
  body.removeAttribute('class');
  body.style.cssText = 'all: revert; display:block; margin:0; padding:0; border:0; box-shadow:none; background:none; color:#111; font: inherit;';
  body.querySelectorAll('*').forEach(n => { n.removeAttribute('class'); n.style.cssText = 'all: revert; font: inherit; color: inherit; margin: 0 0 .5em;'; });
  body.querySelectorAll('h1,h2,h3,h4,h5').forEach(n => n.style.cssText += 'font-size:26px;line-height:1.25;font-weight:800;');
  card.appendChild(body);

  // highlight phrases (text nodes only, case-insensitive)
  const esc = s => s.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&');
  if (highlight.length) {
    // letter boundaries so "AI" doesn't match inside "naik"
    const re = new RegExp(`(?<!\\\\p{L})(${highlight.map(esc).join('|')})(?!\\\\p{L})`, 'giu');
    const walker = document.createTreeWalker(body, NodeFilter.SHOW_TEXT);
    const nodes = []; while (walker.nextNode()) nodes.push(walker.currentNode);
    for (const n of nodes) {
      if (!re.test(n.nodeValue)) continue;
      re.lastIndex = 0;
      const span = document.createElement('span');
      span.innerHTML = n.nodeValue.replace(/&/g, '&amp;').replace(/</g, '&lt;')
        .replace(re, '<mark style="background:#fde047;color:#111;padding:0 .15em;border-radius:3px">$1</mark>');
      n.replaceWith(span);
    }
  }

  const foot = document.createElement('div');
  foot.textContent = url.replace(/^https?:\\/\\/(www\\.)?/, '').slice(0, 90) + (url.length > 98 ? '…' : '');
  foot.style.cssText = 'margin-top:14px;padding-top:10px;border-top:1px solid #e5e7eb;font-size:13px;color:#6b7280';
  card.appendChild(foot);

  document.body.appendChild(card);
  window.scrollTo(0, 0);
  return { text: el.innerText.trim().slice(0, 600) };
}
"""


def ensure_browser() -> None:
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)


def capture(page: Page, src: Source, full: bool) -> dict:
    print(f"→ {src.id}: {src.url}")
    page.goto(src.url, wait_until="domcontentloaded", timeout=60_000)
    try:
        page.wait_for_load_state("networkidle", timeout=15_000)
    except PlaywrightError:
        pass  # news sites rarely go idle; DOM is enough
    page.wait_for_timeout(1500)

    if full:
        raw = OUT / f"{src.id}-page.png"
        page.screenshot(path=raw, full_page=True)
        print(f"  ✓ full page → {raw.relative_to(ROOT)}")

    title = page.title()
    res = page.evaluate(BUILD_CARD_JS, {
        "targetText": src.target_text, "ascend": src.ascend, "titleSelector": src.title_selector,
        "titleScopeAscend": src.title_scope_ascend,
        "titleStrip": src.title_strip,
        "highlight": src.highlight, "site": src.site, "url": src.url,
    })
    if "error" in res:
        raise RuntimeError(res["error"])

    shot = OUT / f"{src.id}.png"
    page.locator("#__capture_card").screenshot(path=shot)
    print(f"  ✓ card → {shot.relative_to(ROOT)}")
    return {
        "id": src.id,
        "url": src.url,
        "page_title": title,
        "passage": res["text"],
        "image": str(shot.relative_to(ROOT / "public")),
        "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def main() -> None:
    ids = [a for a in sys.argv[1:] if not a.startswith("--")]
    headed, full = "--show" in sys.argv, "--full" in sys.argv
    todo = [s for s in SOURCES if not ids or s.id in ids]
    if not todo:
        sys.exit(f"Unknown id(s): {ids}. Known: {[s.id for s in SOURCES]}")

    OUT.mkdir(parents=True, exist_ok=True)
    manifest_path = OUT / "sources.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

    failed = False
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=not headed)
        except PlaywrightError:
            ensure_browser()
            browser = p.chromium.launch(headless=not headed)
        ctx = browser.new_context(viewport={"width": 1280, "height": 900}, device_scale_factor=2, user_agent=UA)
        page = ctx.new_page()
        for src in todo:
            try:
                manifest[src.id] = capture(page, src, full)
            except (PlaywrightError, RuntimeError) as e:
                failed = True
                print(f"  ✗ {src.id} failed: {e}")
        browser.close()

    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(f"\nManifest → {manifest_path.relative_to(ROOT)}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
