# Slides

[Slidev](https://sli.dev) decks, one folder per talk, sharing one pnpm workspace.

| Deck | Event | Run |
|---|---|---|
| [`saring-sebelum-sharing/`](saring-sebelum-sharing/) | Townhall, 6 Nov 2026: *Saring Sebelum Sharing: Check Before You Share* | `pnpm dev:saring` |

## Setup

Requires Node >= 22.12 and pnpm.

```bash
pnpm install              # once, from the repo root: installs every deck
pnpm dev:saring           # or: cd saring-sebelum-sharing && pnpm dev
pnpm build:all            # build every deck (each to its own dist/)
```

## Layout

```
.
├── pnpm-workspace.yaml   # workspace (every top-level folder with a package.json) + shared pnpm settings
├── package.json          # root shortcut scripts only
├── scripts/              # tools shared by all decks (e.g. fetch_article_images.py)
├── .mcp.json, .claude/   # Claude Code / Playwright MCP config
└── <deck>/               # one Slidev project per talk: slides.md, components/, public/, styles/, …
```

## Adding a new deck

```bash
mkdir my-talk && cd my-talk
# copy package.json, setup/, styles/ from an existing deck (or run `pnpm create slidev`), then:
cd .. && pnpm install
```

Then add `"dev:my-talk": "pnpm -F my-talk dev"` to the root `package.json` and a row to the table above.
Deck-specific assets, components and scripts stay inside the deck folder.

## Shared tools

```bash
uv run scripts/fetch_article_images.py <url> <out_dir>   # download every content image from an article
```

Requires [uv](https://docs.astral.sh/uv/); Python deps and Chromium install on first run.

## Notes

- Use pnpm only. Mixing in `npm install` breaks `node_modules`.
- `pnpm-workspace.yaml` pins `markdown-it` to v14: `@comark/markdown-it` (pulled in by Slidev) crashes with v15.
