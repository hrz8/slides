# Saring Sebelum Sharing: Check Before You Share

Slidev deck for the 6 Nov 2026 townhall (Web Team), ~14 min, hybrid (office + remote).

## Requirements

- Node >= 22.12
- pnpm. This deck is one package in the repo's pnpm workspace (see the root `README.md`).

## Run

```bash
pnpm install        # run once, from the repo root
cd saring-sebelum-sharing
pnpm dev            # http://localhost:3030
# or, from the repo root: pnpm dev:saring
```

| URL | What |
|---|---|
| `http://localhost:3030/` | Slides (share this window/tab in the video call) |
| `http://localhost:3030/#/presenter/1` | Presenter view: notes, timer, next slide |
| `http://localhost:3030/#/overview` | All slides at a glance |

Live: https://hrz8.github.io/slides/saring-sebelum-sharing/ (presenter: `…/#/presenter/1`).
URLs use hash routing (`#/5`), so links work on GitHub Pages.

## Presenting (hybrid)

1. Open the **presenter view** on your laptop and the **slides** in a second window.
   Share only the slides window in the call; put it on the projector for the office.
2. Navigate with arrow keys / space / a clicker. Clicks sync between the two windows.
   - FlipCards flip **on clicks** (slide "The reveal"), so remote viewers stay in sync.
     Clicking a card with the mouse flips it locally only. Use that just for rehearsal.
3. Every slide has presenter notes with a `[mm:ss → mm:ss]` timing hint.
4. Useful keys: `o` overview · `d` dark/light toggle · `g` go to slide · `f` fullscreen.

### Remote control from your phone

```bash
pnpm dev:remote                  # prints a LAN URL for presenter mode
pnpm slidev --remote=mypassword   # optional password protection
```

Open the printed `/presenter/` URL on your phone (same Wi-Fi) to drive the slides.

## Build & export

```bash
pnpm build               # static SPA -> dist/
pnpm export:pdf          # exports/saring-sebelum-sharing.pdf (final state of each slide)
pnpm export:pdf:clicks   # one page per click step
pnpm export:pptx         # exports/saring-sebelum-sharing.pptx (fallback; slides are images)
pnpm export:notes        # exports/speaker-notes.pdf
```

Exports use `playwright-chromium` (installed as a dev dependency).

### Deploy

Deployed automatically to GitHub Pages on push to `main` (see the root `README.md`).
Alternatively, `netlify.toml` and `vercel.json` live in this folder, so the deck can be its own site:

- **Netlify:** set *Base directory* to `saring-sebelum-sharing` (publish `dist`, command `pnpm build`).
- **Vercel:** set *Root Directory* to `saring-sebelum-sharing`.

## Article screenshots

```bash
pnpm capture:sources                 # uv run scripts/capture_sources.py
uv run scripts/capture_sources.py id-prabowo --show   # one source, visible browser
```

Requires [uv](https://docs.astral.sh/uv/); Python deps and Chromium install on first run.
To pull every content image from an article (for picking hoax visuals):

```bash
uv run ../scripts/fetch_article_images.py <url> <out_dir>   # shared tool at the repo root
```

To add a source card, append a `Source(...)` to `SOURCES` in the script: URL, `target_text` (a phrase in
the passage you want), optional `highlight` phrases. Output: `public/assets/screenshots/<id>.png`.

## Project layout

```
slides.md               # the deck
components/
  FlipCard.vue          # REAL / FAKE flip card (driven by :flipped="$clicks >= n")
  CountUp.vue           # animated stat counter (final value in print/export)
  ScamPattern.vue       # Famous face + Free money + WhatsApp = SCAM (step = $clicks)
  PollEmbed.vue         # Slido/Mentimeter iframe + QR fallback
styles/index.css        # theme: colors (fake red / real green / pause amber), type, layout
setup/mermaid.ts        # Mermaid dark theme
public/assets/          # photos (Unsplash License), screenshots/, CREDITS.md
scripts/capture_sources.py      # article -> highlighted "source card" PNG (this deck's sources)
netlify.toml, vercel.json       # per-deck deploy config
```

## Before the talk: fill the TODOs

Search `slides.md` for `TODO` and `PLACEHOLDER`:

- Poll URL: replace `POLL_URL_HERE` (opening + closing poll)
- Closing-poll items
- Confirm the Indonesian WhatsApp fact-check channel (tools table)
- Source link for the Arup case (Sources slide)

## Troubleshooting

- **CLI crashes with `ERR_PACKAGE_PATH_NOT_EXPORTED ... markdown-it/lib/token.mjs`**:
  the root `pnpm-workspace.yaml` pins `markdown-it` to v14 for this. Delete `node_modules` (root and deck) and run `pnpm install` from the root again.
- **Magic Move / Mermaid slide shows "An error occurred"**: usually a stale Vite cache after
  switching package managers. Stop the server, delete `node_modules`, run `pnpm install` from the root, then `pnpm dev`.
  Don't use `npm install` anywhere in this repo.
