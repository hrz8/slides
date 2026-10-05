# Saring Sebelum Sharing: Check Before You Share

Slidev deck for the 6 Nov 2026 townhall (Web Team), ~14 min, hybrid (office + remote).

## Requirements

- Node >= 22.12
- pnpm (the project is set up for pnpm: see `pnpm-workspace.yaml`)

## Run

```bash
pnpm install
pnpm dev            # http://localhost:3030
```

| URL | What |
|---|---|
| `http://localhost:3030/` | Slides (share this window/tab in the video call) |
| `http://localhost:3030/presenter/` | Presenter view: notes, timer, next slide |
| `http://localhost:3030/overview/` | All slides at a glance |

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
pnpm build               # static SPA -> dist/ (deployable to Netlify / Vercel, configs included)
pnpm export:pdf          # exports/saring-sebelum-sharing.pdf (final state of each slide)
pnpm export:pdf:clicks   # one page per click step
pnpm export:pptx         # exports/saring-sebelum-sharing.pptx (fallback; slides are images)
pnpm export:notes        # exports/speaker-notes.pdf
```

Exports use `playwright-chromium` (installed as a dev dependency).

## Article screenshots

```bash
pnpm capture:sources                 # uv run scripts/capture_sources.py
uv run scripts/capture_sources.py id-prabowo --show   # one source, visible browser
```

Requires [uv](https://docs.astral.sh/uv/); Python deps and Chromium install on first run.
To pull every content image from an article (for picking hoax visuals):

```bash
uv run scripts/fetch_article_images.py <url> <out_dir>   # saves images + index.json
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
scripts/capture_sources.py      # article -> highlighted "source card" PNG
scripts/fetch_article_images.py # article -> all its images (for picking visuals)
```

## Before the talk: fill the TODOs

Search `slides.md` for `TODO` and `PLACEHOLDER`:

- Poll URL: replace `POLL_URL_HERE` (opening + closing poll)
- Closing-poll items
- Confirm the Indonesian WhatsApp fact-check channel (tools table)
- Source link for the Arup case (Sources slide)

## Troubleshooting

- **CLI crashes with `ERR_PACKAGE_PATH_NOT_EXPORTED ... markdown-it/lib/token.mjs`**:
  `pnpm-workspace.yaml` pins `markdown-it` to v14 for this. Delete `node_modules` and run `pnpm install` again.
- **Magic Move / Mermaid slide shows "An error occurred"**: usually a stale Vite cache after
  switching package managers. Stop the server, `rm -rf node_modules`, run `pnpm install`, then `pnpm dev`.
  Don't mix `npm install` and `pnpm install` in this folder.
