# valencole-site

Source for the site deployed at **operationsguy.netlify.app**.

## How deploys work

Netlify is linked to this repo. **Any push to `main` triggers a deploy.** No build step —
Netlify publishes the repo root as-is.

- Build command: *(empty)*
- Publish directory: `.`
- Config: `netlify.toml`

## Structure

```
index.html                     Root — Valen Cole, indexes everything below
assets/site.css                Shared shell: light/dark tokens, nav, home bento, entry lists, prose
assets/mode.js                 Light/dark toggle button (pair with the inline <head> script)
valen-cole-resume.pdf          Resume, linked as "Resume" in every nav
assets/aviva/*.jpg             Aviva Manual screenshots
favicon.svg

src/                           SOURCE OF TRUTH for generated pages — see below
  ghana-roads-memo.md            The memo, in markdown
  build-memo.py                  markdown  -> memo HTML
  build-pdf.py                   memo HTML -> PDF (prints the published page)
  count_sources.py               Recomputes the source count, auditably
  check-site.py                  Pre-push audit — run this before every push

writing/index.html             Writing index
writing/ghana-roads/           Compliance Without Preservation
  index.html                     Interactive overview (own theme, hand-written)
  ghana-roads-memo.html          GENERATED from src/ — do not hand-edit
  compliance-without-preservation.pdf   GENERATED from that HTML — do not hand-edit

projects/index.html            Projects index
projects/aviva-manual/         Aviva Manual write-up

ops/index.html                 Your Ops Guy consultancy page — LIVE BUT UNLINKED.
                               Not in any nav; noindex. Send the URL directly.
demos/jerry/                   charity: water game concept — UNLISTED.
                               Not in any nav; noindex + robots.txt.

robots.txt                     Disallows /demos/ and /ops/
sitemap.xml                    Public pages only
```

## The memo is generated — edit the markdown, not the HTML

`src/ghana-roads-memo.md` is the source of truth. Both published formats are built
from it. Hand-edits to the HTML or the PDF are destroyed on the next build.

```
pip install markdown playwright pypdf
playwright install chromium

python src/build-memo.py        # markdown  -> ghana-roads-memo.html
python src/build-pdf.py         # that HTML -> compliance-without-preservation.pdf
```

Run them in that order. `build-memo.py` reuses the page chrome (head/style, top bar,
footnote-popover JS, TOC shell) from the currently published HTML, so styling changes
made directly to the page survive regeneration — only the article body and the contents
list are rebuilt.

**The PDF is printed from the published page**, using the `@media print` block in the
page's own stylesheet. That is deliberate: a markdown-to-PDF path that numbers endnotes
by reference order emits a duplicate entry every time a note is re-cited, so the PDF and
the web page end up citing different numbers for the same source. Printing the page makes
that impossible. It also means Ctrl-P in a browser gives a reader the same document, and
that the PDF's text layer stays clean — some HTML-to-PDF engines emit a tab between every
word, which silently breaks copy-paste and résumé parsers.

**Two things do not come from the markdown** and must be kept in sync by hand:

1. `writing/ghana-roads/index.html` — the overview page is hand-written. Any figure or
   claim changed in the memo has to be changed there too.
2. The word and source counts quoted on the root, writing index and overview pages.
   `python src/count_sources.py src/ghana-roads-memo.md` recomputes the source count —
   it maps every endnote to the work it cites, because an endnote is not a source: some
   are Ibid., some re-cite a work already cited, and some cite two or three works at
   once. Currently **47 endnotes, 50 in-text references, 38 distinct works** (6 statutes,
   13 government/institutional documents, 19 press). Update the mapping in that script
   when you add a note.

## Before every push

1. Set the homepage's "Updated <date>" line (`index.html`, `.updated`) to the push date.
2. Run the audit:

```
python src/check-site.py
```

Verifies that the overview, the full article and the PDF still agree on every figure
that appears in more than one of them; that the root, writing index and overview quote
the same word and source counts and that the endnote count matches the article; that
every internal link resolves; that `/ops/` and `/demos/` are still noindexed and in
robots.txt; and that no image carries stray content-credentials metadata.

`PASS` means there is nothing to fix. It exits non-zero on failure, so it works as a
pre-commit hook if you want one.

### Rules for adding pages

1. Shell pages get the shared nav and link back to `/`. Copy the `<head>` mode script,
   the nav (with its `.mode` button) and `<script src="/assets/mode.js">` from
   `writing/index.html`; without the head script the page flashes the wrong mode.
2. URL scheme: section index at the folder, items nested under it.
3. Consistent `<title>` (`Thing — Valen Cole`) and `og:` tags.
4. Interiors may look however they need to — a game looks like a game, a memo like a
   document. The shell is what stays constant, not the theme.
5. Anything unlisted needs `<meta name="robots" content="noindex, nofollow">` **and** a
   `robots.txt` entry, and must not be linked from any index.

## Design tokens

Defined in `assets/site.css`, with a light and a dark value for each, switched by
`<html data-mode="light|dark">`. The visitor's choice is saved under localStorage
`vc-mode`; until they click the toggle, the site follows their system setting.
The Ghana pages, `/ops/` and the demo carry their own palettes and have no dark mode.

| Token | Light | Dark | Use |
|---|---|---|---|
| `--paper` | `#f4f3ee` | `#0b0b0c` | page background |
| `--ink` | `#0c0c0d` | `#f2f2ec` | text, card borders |
| `--muted` | `#5d5d58` | `#9a9a93` | labels, meta |
| `--lime` / `--hl` | `#c6ff00` | `#c6ff00` | link fill, left-edge bar, New York card |
| `--pink` | `#ff2f8e` | `#ff3d9a` | top-right bar, route marks |
| `--sans` | Archivo (variable width) | | name, headings, body |
| `--mono` | JetBrains Mono | | nav, labels, tags |

## Gotchas

- Transferring images through the Claude desktop bridge injects content-credentials
  metadata: an APP11 segment in JPEGs (~5.7KB each) and a `<metadata><c2pa:manifest>`
  block in SVGs (favicon.svg went from 261 bytes to 8,035). Pixels are unaffected, but
  strip it before committing — `check-site.py` flags it.
- `.git` lock files: the sandboxed shell cannot delete by default, so a failed git
  operation can leave `.git/index.lock` behind and block the next one.

## Third-party

- Fonts: Google Fonts (Archivo, JetBrains Mono on the shell; Overpass and Source Serif 4
  on the Ghana pages; Source Serif 4 and Outfit on /ops/; Poppins on the demo)
- three.js r128 via cdnjs — the demo only
- Formspree (`f/mpqodngj`) — the `/ops/` contact form only
