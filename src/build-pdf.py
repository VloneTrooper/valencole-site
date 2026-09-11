#!/usr/bin/env python3
"""
Render writing/ghana-roads/compliance-without-preservation.pdf from the SAME HTML
the site serves, so the two can never disagree on content or endnote numbering.

    pip install playwright pypdf
    playwright install chromium
    python src/build-pdf.py           # run from the repo root

Why this exists: a markdown-to-PDF path that numbers endnotes by reference order
emits a duplicate entry every time a note is re-cited, so the PDF and the web page
end up citing different numbers for the same source. Printing the published page
removes that class of bug entirely — one document, one numbering.

Layout comes from the `@media print` block in the page's own stylesheet, so what
you get here is exactly what a reader gets from Ctrl-P.

Optional:
    --fonts <dir>   directory of .woff2 files to embed instead of fetching Google
                    Fonts, for building without network access. Expects fontsource
                    filenames, e.g. source-serif-4-latin-400-normal.woff2
"""
import argparse
import base64
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "writing" / "ghana-roads" / "ghana-roads-memo.html"
OUT = ROOT / "writing" / "ghana-roads" / "compliance-without-preservation.pdf"

TITLE = "Compliance Without Preservation"
AUTHOR = "Valen Cole"
SUBJECT = ("Why Ghana's road maintenance funds keep failing, "
           "and the four changes that would matter most")
KEYWORDS = ("Ghana, road maintenance, infrastructure finance, "
            "Road Maintenance Trust Fund, Act 1147")

FACES = [
    ("Source Serif 4", 400, "normal", "source-serif-4-latin-400-normal.woff2"),
    ("Source Serif 4", 700, "normal", "source-serif-4-latin-700-normal.woff2"),
    ("Source Serif 4", 400, "italic", "source-serif-4-latin-400-italic.woff2"),
    ("Source Serif 4", 700, "italic", "source-serif-4-latin-700-italic.woff2"),
    ("Overpass", 400, "normal", "overpass-latin-400-normal.woff2"),
    ("Overpass", 700, "normal", "overpass-latin-700-normal.woff2"),
    ("Overpass", 900, "normal", "overpass-latin-900-normal.woff2"),
]

HDR = ('<div style="font:8px Helvetica,Arial,sans-serif;color:#7a7a74;width:100%;'
       'padding:0 54px;display:flex;justify-content:space-between;">'
       f'<span>{TITLE}</span><span>{AUTHOR}</span></div>')
FTR = ('<div style="font:8px Helvetica,Arial,sans-serif;color:#7a7a74;width:100%;'
       'padding:0 54px;display:flex;justify-content:space-between;">'
       '<span>operationsguy.netlify.app/writing/ghana-roads/</span>'
       '<span><span class="pageNumber"></span>&nbsp;/&nbsp;<span class="totalPages"></span></span>'
       '</div>')


def font_css(dirpath: Path) -> str:
    css = []
    for family, weight, style, fname in FACES:
        f = dirpath / fname
        if not f.exists():
            print(f"  ! missing {fname}", file=sys.stderr)
            continue
        b64 = base64.b64encode(f.read_bytes()).decode()
        css.append(
            f"@font-face{{font-family:'{family}';font-style:{style};"
            f"font-weight:{weight};font-display:block;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}"
        )
    return "\n".join(css)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", type=Path, help="directory of .woff2 files to embed")
    args = ap.parse_args()

    if not PAGE.exists():
        sys.exit(f"missing {PAGE} — run build-memo.py first")

    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        page.goto(PAGE.as_uri(), wait_until="load")
        if args.fonts:
            page.add_style_tag(content=font_css(args.fonts))
        page.emulate_media(media="print")
        page.wait_for_timeout(1500)
        page.pdf(
            path=str(OUT),
            format="Letter",
            print_background=True,
            display_header_footer=True,
            header_template=HDR,
            footer_template=FTR,
            margin={"top": "0.7in", "bottom": "0.7in", "left": "0.75in", "right": "0.75in"},
        )
        browser.close()

    # Chrome does not write document metadata; add it.
    from pypdf import PdfReader, PdfWriter
    r = PdfReader(str(OUT))
    w = PdfWriter()
    for p in r.pages:
        w.add_page(p)
    w.add_metadata({"/Title": TITLE, "/Author": AUTHOR, "/Subject": SUBJECT,
                    "/Creator": "operationsguy.netlify.app", "/Keywords": KEYWORDS})
    with open(OUT, "wb") as f:
        w.write(f)

    html = PAGE.read_text(encoding="utf-8")
    notes = len(re.findall(r'<li id="fn:', html))
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"  {len(PdfReader(str(OUT)).pages)} pages, {OUT.stat().st_size:,} bytes, "
          f"{notes} endnotes (matches the page)")


if __name__ == "__main__":
    main()
