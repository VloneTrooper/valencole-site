# valencole-site

Source for the site deployed at **operationsguy.netlify.app**.

## How deploys work

Netlify is linked to this repo. **Any push to `main` triggers a deploy.** There is no
build step — Netlify publishes the repo root as-is.

- Build command: *(empty)*
- Publish directory: `.`
- Config lives in `netlify.toml`

## Structure

```
index.html      Landing page
netlify.toml    Deploy + header config
```

### Planned structure

```
/                       Valen Cole — index into everything below
/projects/              Index of built things
/projects/<slug>/       Individual projects
/writing/               Index of analytical writing
/writing/<slug>/        Individual pieces
/ops/                   Your Ops Guy consultancy page (live, unlinked from nav)
```

Rule for new pages: interiors can look however they need to (a game should look like a
game, a memo like a document), but every page keeps the shared top bar, the URL scheme
above, and consistent `<title>` / `og:` metadata.

## Design tokens

Defined in `:root` of each page. Keep these consistent across the shared shell.

| Token | Value | Use |
|---|---|---|
| `--bg` | `#fafaf7` | page background |
| `--bg-alt` | `#f2f1ec` | alternate bands |
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

- Fonts: Google Fonts (Source Serif 4, Outfit, JetBrains Mono)
- Contact form: Formspree — endpoint `f/mpqodngj`
