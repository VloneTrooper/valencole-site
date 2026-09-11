#!/usr/bin/env python3
"""
Audit the site before pushing. Run from the repo root:

    python src/check-site.py

Answers the only question that matters: do the overview, the full article and the
PDF still say the same thing, and does every page quote the same counts?

Exits 0 if everything passes, 1 if anything fails. No output means nothing to fix.
"""
import html as H
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OVERVIEW = ROOT / "writing" / "ghana-roads" / "index.html"
ARTICLE = ROOT / "writing" / "ghana-roads" / "ghana-roads-memo.html"
PDF = ROOT / "writing" / "ghana-roads" / "compliance-without-preservation.pdf"
COUNT_PAGES = [ROOT / "index.html", ROOT / "writing" / "index.html", OVERVIEW]

fails, warns = [], []


def fail(m): fails.append(m)
def warn(m): warns.append(m)


def text_of_html(p: Path) -> str:
    return " ".join(H.unescape(re.sub(r"<[^>]+>", " ", p.read_text(encoding="utf-8"))).split())


def text_of_pdf(p: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        warn("pypdf not installed — skipped all PDF checks")
        return ""
    r = PdfReader(str(p))
    return " ".join("\n".join((x.extract_text() or "") for x in r.pages).split())


# ---------------------------------------------------------------- facts
# (label, must appear, must NOT appear, which documents it applies to)
FACTS = [
    ("condition figure",      "19,800",                          ["20,725", "22% poor share"], "OAP"),
    ("committee attribution", "Committee of the Whole",          ["Roads and Transportation Committee", "Finance Committee"], "AP"),
    ("conclusion scope",      "one instrument whose compliance", ["in 2025 and 2026, each was"], "AP"),
    ("90% split unpublished", "not published",                   ["In 2026 it did"], "OAP"),
    ("levy CPI figures",      "278.45",                          ["roughly tripled"], "OAP"),
    ("cross-channel caveat",  "does not consolidate",            [], "OAP"),
    ("attribution present",   "Claude (Anthropic)",              [], "OAP"),
]


def main():
    for p in (OVERVIEW, ARTICLE, PDF):
        if not p.exists():
            fail(f"missing file: {p.relative_to(ROOT)}")
    if fails:
        return report()

    docs = {"O": text_of_html(OVERVIEW), "A": text_of_html(ARTICLE), "P": text_of_pdf(PDF)}
    names = {"O": "overview", "A": "article", "P": "PDF"}

    for label, good, bads, applies in FACTS:
        for key in applies:
            t = docs[key]
            if not t:
                continue
            if good not in t:
                fail(f"{names[key]}: '{label}' — expected text not found ({good!r})")
            for bad in bads:
                if bad in t:
                    fail(f"{names[key]}: '{label}' — STALE text still present ({bad!r})")

    # ------------------------------------------------------------ counts
    endnotes = len(re.findall(r'<li id="fn:', ARTICLE.read_text(encoding="utf-8")))
    claimed = {}
    for p in COUNT_PAGES:
        if not p.exists():
            fail(f"missing file: {p.relative_to(ROOT)}")
            continue
        t = text_of_html(p)
        src = re.search(r"(\d+) sources", t)
        end = re.search(r"(\d+) endnotes", t)
        wrd = re.search(r"([\d,]+) words", t)
        claimed[p.relative_to(ROOT).as_posix()] = (
            src.group(1) if src else None,
            end.group(1) if end else None,
            wrd.group(1) if wrd else None,
        )

    vals = {k: v for k, v in claimed.items() if any(v)}
    sources = {v[0] for v in vals.values() if v[0]}
    words = {v[2] for v in vals.values() if v[2]}
    if len(sources) > 1:
        fail(f"pages disagree on the source count: {claimed}")
    if len(words) > 1:
        fail(f"pages disagree on the word count: {claimed}")
    for page, (s, e, w) in vals.items():
        if e and int(e) != endnotes:
            fail(f"{page}: claims {e} endnotes, the article has {endnotes}")

    # ------------------------------------------------------------ links
    checked = 0
    for p in ROOT.rglob("*.html"):
        if any(part in {".git", "node_modules"} for part in p.parts):
            continue
        for link in re.findall(r'(?:href|src)="([^"]+)"', p.read_text(encoding="utf-8")):
            if link.startswith(("http", "mailto:", "tel:", "#", "data:")):
                continue
            target = link.split("#")[0].split("?")[0]
            if not target:
                continue
            checked += 1
            fp = (ROOT / target.lstrip("/")) if target.startswith("/") else (p.parent / target)
            fp = fp.resolve()
            if target.endswith("/") or fp.is_dir():
                fp = fp / "index.html"
            if not fp.exists():
                fail(f"{p.relative_to(ROOT).as_posix()}: broken link -> {link}")

    # ------------------------------------------------------------ unlisted pages stay unlisted
    for path, label in [(ROOT / "ops" / "index.html", "/ops/"),
                        (ROOT / "demos" / "jerry" / "index.html", "/demos/jerry/")]:
        if path.exists() and "noindex" not in path.read_text(encoding="utf-8"):
            fail(f"{label} is missing its noindex meta tag")
    rt = ROOT / "robots.txt"
    if rt.exists():
        r = rt.read_text(encoding="utf-8")
        for d in ("/demos/", "/ops/"):
            if d not in r:
                fail(f"robots.txt no longer disallows {d}")

    # ------------------------------------------------------------ stray provenance metadata
    for img in list(ROOT.rglob("*.jpg")) + list(ROOT.rglob("*.svg")):
        if any(part in {".git", "node_modules"} for part in img.parts):
            continue
        blob = img.read_bytes()
        if b"c2pa" in blob[:20000] or b"\xff\xeb" in blob[:4]:
            warn(f"{img.relative_to(ROOT).as_posix()}: carries content-credentials metadata — strip it")

    print(f"checked {checked} internal links, {endnotes} endnotes, "
          f"{len(vals)} pages quoting counts")
    if vals:
        s = next(iter(sources), "?")
        w = next(iter(words), "?")
        print(f"counts in use: {w} words, {s} sources, {endnotes} endnotes")
    return report()


def report():
    for w in warns:
        print(f"  WARN  {w}")
    if not fails:
        print("\nPASS — overview, article and PDF agree; counts consistent; links resolve.")
        return 0
    print(f"\nFAIL — {len(fails)} problem(s):")
    for f in fails:
        print(f"  - {f}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
