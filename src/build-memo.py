#!/usr/bin/env python3
"""
Regenerate writing/ghana-roads/ghana-roads-memo.html from the markdown master.

    pip install markdown
    python src/build-memo.py          # run from the repo root

The markdown in src/ is the source of truth. Edit it, run this, commit both.
Never hand-edit the generated HTML — the next run overwrites it.

The page chrome (head/style, top bar, footnote-popover JS, TOC shell) is read
back out of the currently published HTML, so styling changes you make there
survive regeneration. Only the article body and the contents list are rebuilt.
"""
import html as H
import re
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.exit("need python-markdown:  pip install markdown")

ROOT = Path(__file__).resolve().parent.parent
MD = ROOT / "src" / "ghana-roads-memo.md"
PAGE = ROOT / "writing" / "ghana-roads" / "ghana-roads-memo.html"

src = MD.read_text(encoding="utf-8")
tpl = PAGE.read_text(encoding="utf-8")

# --- front matter: title, subtitle, byline are formatted specially ---
lines = src.split("\n")
title = re.sub(r"^#\s+", "", lines[0]).strip()
subtitle = re.sub(r"^###\s+", "", next(l for l in lines if l.startswith("### "))).strip()
by_i = next(i for i, l in enumerate(lines) if l.startswith("**Valen Cole**"))
byline = [re.sub(r"\*\*", "", p).strip() for p in lines[by_i].split("·")]
body_md = "\n".join(lines[by_i + 1:]).lstrip("\n")

# --- convert ---
body = markdown.Markdown(
    extensions=["footnotes", "tables", "toc", "attr_list"]
).convert(body_md)

# --- wrap the annex so it renders as a disclosure block (open by default) ---
annex_h2 = '<h2 id="annex-the-precedent">Annex: the precedent</h2>'
notes_h2 = '<h2 id="notes">Notes</h2>'
if annex_h2 in body and notes_h2 in body:
    a, n = body.index(annex_h2), body.index(notes_h2)
    inner = body[a + len(annex_h2):n]
    body = (
        body[:a]
        + '<details class="annex" open><summary>' + annex_h2
        + '<span class="hint">Precedent (2000–2006)</span></summary>'
        + '<div class="annex-body">' + inner + "</div></details>"
        + body[n:]
    )

# --- contents: every h2 except Notes ---
toc = "<ol>" + "\n".join(
    f'<li><a href="#{hid}">{" ".join(re.sub(chr(60) + "[^" + chr(62) + "]+" + chr(62), "", txt).split())}</a></li>'
    for hid, txt in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body, re.S)
    if hid != "notes"
) + "</ol>"

# --- splice into the existing chrome ---
head = tpl[: tpl.index('<aside class="toc"')]
tail = tpl[tpl.index("</article>"):]
byline_html = "".join(f"<span>{H.escape(p)}</span>" for p in byline)

PAGE.write_text(
    head
    + '<aside class="toc" aria-label="Contents">\n      ' + toc + "\n"
    + '      <div class="dl"><a href="compliance-without-preservation.pdf" download>PDF version</a></div>\n'
    + "    </aside>\n"
    + '    <article class="memo">\n'
    + f"      <h1>{H.escape(title)}</h1>\n"
    + f'      <p class="subtitle">{H.escape(subtitle)}</p>\n'
    + f'      <p class="byline">{byline_html}</p>\n'
    + body + "\n"
    + tail,
    encoding="utf-8",
)

notes = len(re.findall(r'<li id="fn:', body))
refs = len(re.findall(r'class="footnote-ref"', body))
print(f"wrote {PAGE.relative_to(ROOT)}")
print(f"  {notes} endnotes, {refs} references, {len(re.findall(r'<table>', body))} tables")
