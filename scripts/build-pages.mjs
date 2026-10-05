// Build every deck into _site/<deck>/ for GitHub Pages, plus an index page.
//
//   node scripts/build-pages.mjs              # base = /<repo>/ (from GITHUB_REPOSITORY, default "slides")
//   PAGES_BASE=/ node scripts/build-pages.mjs # e.g. for a custom domain
//
// A deck is any top-level folder with both package.json and slides.md.

import { execFileSync } from 'node:child_process'
import { existsSync, mkdirSync, readdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { join, resolve } from 'node:path'

const root = resolve(import.meta.dirname, '..')
const out = join(root, '_site')
const repo = process.env.GITHUB_REPOSITORY?.split('/')[1] ?? 'slides'
const base = (process.env.PAGES_BASE ?? `/${repo}/`).replace(/\/?$/, '/')

const decks = readdirSync(root, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.startsWith('.') && d.name !== 'node_modules' && d.name !== '_site')
  .map(d => d.name)
  .filter(name => existsSync(join(root, name, 'package.json')) && existsSync(join(root, name, 'slides.md')))

if (!decks.length)
  throw new Error('No decks found (folders with package.json + slides.md)')

rmSync(out, { recursive: true, force: true })
mkdirSync(out, { recursive: true })

const entries = []
for (const deck of decks) {
  const deckBase = `${base}${deck}/`
  console.log(`\n▶ ${deck} → ${deckBase}`)
  execFileSync('pnpm', ['exec', 'slidev', 'build', '--base', deckBase, '--out', join(out, deck)], {
    cwd: join(root, deck),
    stdio: 'inherit',
  })
  entries.push({ deck, ...frontmatter(join(root, deck, 'slides.md')) })
}

writeFileSync(join(out, 'index.html'), indexPage(entries))
// Serve files as-is (no Jekyll processing of folders starting with "_")
writeFileSync(join(out, '.nojekyll'), '')
console.log(`\n✓ ${decks.length} deck(s) → ${out}`)

function frontmatter(file) {
  const head = readFileSync(file, 'utf8').match(/^---\n([\s\S]*?)\n---/)?.[1] ?? ''
  const get = key => head.match(new RegExp(`^${key}:\\s*(.+)$`, 'm'))?.[1].trim().replace(/^['"]|['"]$/g, '')
  return { title: get('title') ?? '', author: get('author') ?? '' }
}

function escape(s) {
  return s.replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c])
}

function indexPage(items) {
  const cards = items.map(({ deck, title, author }) => `
      <a class="deck" href="./${deck}/">
        <span class="title">${escape(title || deck)}</span>
        <span class="meta">${escape([author, deck].filter(Boolean).join(' · '))}</span>
      </a>`).join('')
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Slides</title>
  <style>
    :root { --bg: #0b1020; --card: #161d33; --border: #2b3555; --text: #eef1f8; --muted: #9aa4c0; --accent: #f59e0b; }
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; background: var(--bg); color: var(--text);
      font: 16px/1.5 Inter, system-ui, -apple-system, sans-serif; }
    main { max-width: 760px; margin: 0 auto; padding: 64px 16px; }
    h1 { font-size: 2.25rem; margin: 0 0 8px; }
    p { color: var(--muted); margin: 0 0 32px; }
    .deck { display: block; padding: 20px 24px; margin-bottom: 12px; border: 2px solid var(--border);
      border-radius: 14px; background: var(--card); color: inherit; text-decoration: none; transition: border-color .15s, transform .15s; }
    .deck:hover { border-color: var(--accent); transform: translateY(-2px); }
    .title { display: block; font-size: 1.2rem; font-weight: 700; }
    .meta { display: block; color: var(--muted); font-size: .9rem; margin-top: 4px; }
  </style>
</head>
<body>
  <main>
    <h1>Slides</h1>
    <p>Talks built with <a href="https://sli.dev" style="color:var(--accent)">Slidev</a>.</p>${cards}
  </main>
</body>
</html>
`
}
