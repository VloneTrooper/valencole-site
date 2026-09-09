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
assets/site.css                Shared shell: tokens, top bar, entry lists, prose
assets/aviva/*.jpg             Aviva Manual screenshots

writing/index.html             Writing index
writing/ghana-roads/           Compliance Without Preservation
  index.html                     Interactive overview (own theme)
  ghana-roads-memo.html          Full memo, working footnotes
  compliance-without-preservation.pdf

projects/index.html            Projects index
projects/aviva-manual/         Aviva Manual write-up

ops/index.html                 Your Ops Guy consultancy page — LIVE BUT UNLINKED.
                               Not in any nav; noindex. Send the URL directly.
demos/jerry/                   charity: water game concept — UNLISTED.
                               Not in any nav; noindex + robots.txt.

robots.txt                     Disallows /demos/ and /ops/
sitemap.xml                    Public pages only
```

### Rules for adding pages

1. Everything gets the shared top bar and links back to `/`.
2. URL scheme: section index at the folder, items nested under it.
3. Consistent `<title>` (`Thing — Valen Cole`) and `og:` tags.
4. Interiors may look however they need to — a game looks like a game, a memo like a
   document. The shell is what stays constant, not the theme.
5. Anything unlisted needs `<meta name="robots" content="noindex, nofollow">` **and** a
   `robots.txt` entry, and must not be linked from any index.

## Design tokens

Defined in `assets/site.css`. The Ghana pages and the demo carry their own palettes.

| Token | Value | Use |
|---|---|---|
| `--bg` | `#fafaf7` | page background |
| `--bg-card` | `#ffffff` | cards |
| `--text` | `#1c1c1a` | body text |
| `--text-sub` | `#4d4b46` | secondary text |
| `--text-muted` | `#8c8880` | captions, meta |
| `--accent` | `#2c5f41` | forest green — links, emphasis |
| `--warm` | `#b5694d` | terracotta — sparing accent |
| `--serif` | Source Serif 4 | headings, display |
| `--sans` | Outfit | body, UI |
| `--mono` | JetBrains Mono | eyebrows, labels, captions |

## Third-party

- Fonts: Google Fonts (Source Serif 4, Outfit, JetBrains Mono; Overpass on the Ghana
  pages; Poppins on the demo)
- three.js r128 via cdnjs — the demo only
- Formspree (`f/mpqodngj`) — the `/ops/` contact form only
