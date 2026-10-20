#!/usr/bin/env python3
"""Check a rendered résumé the way an ATS parser reads it.

Two layers. The HTML checks always run on the assembled document render.py
wrote: contact details as literal text, no images or tables, a single column,
the keyword-emphasis bold budget from writing-guide.md, a year on every entry,
ASCII letters only. The PDF checks run on the PDF's embedded text layer when an
extractor is available -- pypdf first, then Poppler's pdftotext -- and report
"unverified" when neither is installed, because the plugin promises no installs.

The script counts and compares; it never judges synonyms. A keyword reported
`missing` is annotated by the skill from the Step-3 table as synonym-only,
missing (have it), or missing (gap), and a term is added to the résumé only
where the evidence supports it.

Usage:  python3 ats-check.py DOC.html [--pdf DOC.pdf] [--keywords FILE | --keyword TERM ...]
                             [--page-limit N] [--json]
Exit 0 = no failures, 1 = at least one failure, 2 = PDF text layer unverified
(no extractor found) with no failures.
"""
import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from collections import namedtuple
from pathlib import Path

# The converter already parses the template's class vocabulary; reuse it so the
# two scripts cannot disagree about what the document contains.
_spec = importlib.util.spec_from_file_location("html_to_md", Path(__file__).with_name("html-to-md.py"))
h2m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h2m)
Node, Tree, text, norm, squeeze = h2m.Node, h2m.Tree, h2m.text, h2m.norm, h2m.squeeze

BOLD_PER_PAGE = 8
BOLD_MAX_WORDS = 4
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE = re.compile(r"\+?\d[\d\s().-]{6,}\d")
YEAR = re.compile(r"\b(19|20)\d{2}\b|\bPresent\b")
METRIC_ONLY = re.compile(r"^[\d%$€£+.,kKxX×~\s-]+$")
URLISH = re.compile(r"@|://|\w+\.\w+/")
SYMBOLIC = re.compile(r"[+#]")
STYLE_BLOCK = re.compile(r"<style[^>]*>(.*?)</style>", re.S | re.I)
CSS_RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")
MULTI_COLUMN = re.compile(r"column-count|(^|[;\s])columns\s*:|float\s*:|display\s*:\s*(inline-)?grid|grid-template")
FLEX = re.compile(r"display\s*:\s*(inline-)?flex")
IMAGE_CSS = re.compile(r"url\(|background-image")
BOLD_TAGS = ("strong", "b")
HEADING_TAGS = ("h1", "h2", "h3")
NO_BOLD_CLASSES = ("contact", "entry-line", "entry-note")

Finding = namedtuple("Finding", "level check message")


def parse(html):
    t = Tree()
    t.feed(html)
    return t.root


def main_node(root):
    return next(root.find("main"), root)


def walk(node, ancestors=()):
    """Every descendant Node with the chain of Nodes above it."""
    for c in node.children:
        if isinstance(c, Node):
            yield c, ancestors
            yield from walk(c, ancestors + (c,))


def has_cls(node, cls):
    return cls in node.cls()


# --- HTML checks -----------------------------------------------------------


def check_contact(main):
    out = []
    contact = next(main.find(cls="contact"), None)
    if contact is None:
        return [Finding("fail", "contact", "no .contact line: an ATS reads contact details from text, not layout")]
    line = squeeze(text(contact))
    if not EMAIL.search(line):
        out.append(Finding("fail", "contact", "no email address as literal text in the contact line"))
    if not PHONE.search(line):
        out.append(Finding("warn", "contact", "no phone number in the contact line (fine if deliberate)"))
    return out


def check_markup(root, html):
    out = []
    for node, _ in walk(root):
        if node.tag in ("img", "svg", "picture"):
            out.append(Finding("fail", "markup", f"<{node.tag}> found: images and icons are invisible to a parser"))
        elif node.tag == "table":
            out.append(Finding("fail", "markup", "<table> found: parsers linearise tables unpredictably"))
        elif any(c.startswith("fa-") or "icon" in c for c in node.cls()):
            out.append(Finding("fail", "markup", f"icon-like class on <{node.tag}>: {' '.join(node.cls())}"))
        style = node.attrs.get("style", "")
        if style and IMAGE_CSS.search(style):
            out.append(Finding("fail", "markup", f"background image in inline style on <{node.tag}>"))
    for css in STYLE_BLOCK.findall(html):
        if IMAGE_CSS.search(css):
            out.append(Finding("fail", "markup", "background image in a <style> block"))
    return out


def check_layout(root, html):
    out = []
    for css in STYLE_BLOCK.findall(html):
        for selector, decl in CSS_RULE.findall(css):
            selector, decl = selector.strip(), decl.lower()
            if MULTI_COLUMN.search(decl):
                out.append(Finding("fail", "layout", f"multi-column or floated rule on `{selector}`: keep a single column"))
            elif FLEX.search(decl) and selector != ".entry-line":
                out.append(Finding("fail", "layout", f"flex layout on `{selector}`: only .entry-line may use it"))
    for node, _ in walk(root):
        decl = node.attrs.get("style", "").lower()
        if not decl:
            continue
        if MULTI_COLUMN.search(decl):
            out.append(Finding("fail", "layout", f"multi-column or floated inline style on <{node.tag}>"))
        elif FLEX.search(decl) and not has_cls(node, "entry-line"):
            out.append(Finding("fail", "layout", f"flex inline style on <{node.tag}>: only .entry-line may use it"))
    return out


def check_bold(main, page_limit):
    out = []
    total = 0
    for li in main.find("li"):
        bolds = [b for b in li.find() if b.tag in BOLD_TAGS]
        if not bolds:
            continue
        total += len(bolds)
        item = squeeze(text(li))
        if len(bolds) > 1:
            out.append(Finding("fail", "bold", f"{len(bolds)} bold phrases in one bullet (max 1): \"{item[:60]}\""))
        for b in bolds:
            phrase = squeeze(text(b))
            if len(phrase.split()) > BOLD_MAX_WORDS:
                out.append(Finding("fail", "bold", f"bold phrase longer than {BOLD_MAX_WORDS} words: \"{phrase}\""))
            if norm(phrase) == norm(item):
                out.append(Finding("fail", "bold", f"whole bullet bold: \"{item[:60]}\""))
            elif METRIC_ONLY.match(phrase):
                out.append(Finding("fail", "bold", f"metric bolded on its own: \"{phrase}\""))
    budget = BOLD_PER_PAGE * max(page_limit, 1)
    if total > budget:
        out.append(Finding("fail", "bold", f"{total} bold phrases in bullets; budget is {budget} for {page_limit} page(s)"))
    for node, ancestors in walk(main):
        if node.tag not in BOLD_TAGS or any(a.tag == "li" for a in ancestors):
            continue
        phrase = squeeze(text(node))
        if any(a.tag in HEADING_TAGS for a in ancestors) or node.tag in HEADING_TAGS:
            out.append(Finding("fail", "bold", f"bold inside a heading: \"{phrase}\""))
        elif any(has_cls(a, c) for a in ancestors for c in NO_BOLD_CLASSES):
            out.append(Finding("fail", "bold", f"bold in the contact line or an entry header: \"{phrase}\""))
        elif any(has_cls(a, "skills-line") for a in ancestors):
            if not phrase.endswith(":"):
                out.append(Finding("fail", "bold", f"bold Skills value (only the `Label:` may be bold): \"{phrase}\""))
        else:
            out.append(Finding("fail", "bold", f"bold outside a bullet: \"{phrase}\""))
    return out


def check_dates(main):
    out = []
    for entry in main.find(cls="entry"):
        lines = [squeeze(text(line)) for line in entry.find(cls="entry-line")]
        if not any(YEAR.search(line) for line in lines):
            org = next((squeeze(text(o)) for o in entry.find(cls="entry-org")), "(unnamed entry)")
            out.append(Finding("fail", "dates", f"no year on the entry header for {org}: parsers need a date range"))
    return out


def check_ascii(main):
    bad = []
    for token in text(main).split():
        if URLISH.search(token):
            continue
        if any(ch.isalpha() and ord(ch) > 127 for ch in token):
            bad.append(token)
    if bad:
        shown = ", ".join(dict.fromkeys(bad[:10]))
        return [Finding("fail", "ascii", f"non-ASCII letters outside URLs and emails (transliterate): {shown}")]
    return []


def check_html(html, page_limit=1):
    root = parse(html)
    main = main_node(root)
    return (
        check_contact(main)
        + check_markup(root, html)
        + check_layout(root, html)
        + check_bold(main, page_limit)
        + check_dates(main)
        + check_ascii(main)
    )


# --- PDF text layer ----------------------------------------------------------


def extract_pypdf(path):
    import pypdf  # optional; absence is handled by extract_text

    reader = pypdf.PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def extract_pdftotext(path):
    exe = shutil.which("pdftotext")
    if not exe:
        raise FileNotFoundError("pdftotext")
    return subprocess.run(
        [exe, "-layout", "-enc", "UTF-8", str(path), "-"],
        check=True, capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stdout


# Tried in order. Tests replace this tuple with a fake extractor.
EXTRACTORS = (("pypdf", extract_pypdf), ("pdftotext", extract_pdftotext))


def extract_text(path):
    """(extractor name, NFKC text) from the first extractor that works, else (None, None)."""
    for name, fn in EXTRACTORS:
        try:
            raw = fn(path)
        except Exception:
            continue
        if raw is not None:
            return name, unicodedata.normalize("NFKC", raw)
    return None, None


def contains(tokens, needle):
    n = len(needle)
    return n > 0 and any(tokens[i:i + n] == needle for i in range(len(tokens) - n + 1))


def keyword_rows(keywords, pdf_text, main):
    html_tokens = norm(text(main))
    pdf_tokens = norm(pdf_text) if pdf_text is not None else None
    rows = []
    for kw in keywords:
        needle = norm(kw)
        if not needle or SYMBOLIC.search(kw):
            # "C++" or "C#" tokenises to "c": a match would prove nothing.
            status = "unverifiable"
        elif pdf_tokens is None:
            status = "covered (pdf unverified)" if contains(html_tokens, needle) else "missing"
        elif contains(pdf_tokens, needle):
            status = "covered"
        elif contains(html_tokens, needle):
            status = "html-only"
        else:
            status = "missing"
        rows.append({"keyword": kw, "status": status})
    return rows


def check_pdf(pdf_text, main, rows):
    out = []
    if "(cid:" in pdf_text or "�" in pdf_text:
        out.append(Finding("fail", "pdf", "garbage in the text layer ((cid:NNN) or replacement characters): a font lacks a Unicode map"))
    contact = next(main.find(cls="contact"), None)
    email = EMAIL.search(squeeze(text(contact))) if contact is not None else None
    if email and email.group(0) not in re.sub(r"\s+", "", pdf_text):
        out.append(Finding("fail", "pdf", f"email {email.group(0)} is not in the text layer"))
    lower = pdf_text.lower()
    pos = -1
    for h2 in main.find("h2"):
        heading = squeeze(text(h2)).lower()
        i = lower.find(heading, pos + 1)
        if i < 0:
            out.append(Finding("fail", "pdf", f"heading \"{heading}\" missing or out of order in the text layer"))
        else:
            pos = i
    for row in rows:
        if row["status"] == "html-only":
            out.append(Finding("fail", "pdf", f"keyword \"{row['keyword']}\" is in the HTML but not in the PDF text layer"))
    return out


# --- CLI ---------------------------------------------------------------------


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("html", help="the assembled HTML render.py wrote")
    ap.add_argument("--pdf", help="the rendered PDF; checks its text layer when an extractor exists")
    ap.add_argument("--keywords", help="file with one posting term per line")
    ap.add_argument("--keyword", action="append", default=[], help="a posting term (repeatable)")
    ap.add_argument("--page-limit", type=int, default=1, help="pages allowed; scales the bold budget")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    opts = ap.parse_args(argv)

    html = Path(opts.html).read_text(encoding="utf-8")
    main_el = main_node(parse(html))
    keywords = list(opts.keyword)
    if opts.keywords:
        keywords += [line.strip() for line in Path(opts.keywords).read_text(encoding="utf-8").splitlines() if line.strip()]

    html_findings = check_html(html, opts.page_limit)
    pdf_findings, extractor, pdf_text = [], None, None
    if opts.pdf:
        extractor, pdf_text = extract_text(Path(opts.pdf))
        if pdf_text is None:
            pdf_findings.append(Finding("unverified", "pdf", "no text extractor found (pip install pypdf, or install Poppler): PDF text layer not checked"))
    rows = keyword_rows(keywords, pdf_text, main_el)
    if pdf_text is not None:
        pdf_findings += check_pdf(pdf_text, main_el, rows)

    findings = html_findings + pdf_findings
    fails = [f for f in findings if f.level == "fail"]
    warns = [f for f in findings if f.level == "warn"]
    if fails:
        code = 1
    elif opts.pdf and extractor is None:
        code = 2
    else:
        code = 0
    pdf_state = extractor if extractor else ("unverified" if opts.pdf else "not checked")

    if opts.json:
        print(json.dumps({
            "html": [f._asdict() for f in html_findings],
            "pdf": [f._asdict() for f in pdf_findings],
            "keywords": rows,
            "extractor": extractor,
            "exit": code,
        }, indent=2, ensure_ascii=False))
        return code

    for f in findings:
        print(f"{f.level.upper()} {f.check}: {f.message}")
    if rows:
        print("| Keyword | Status |")
        print("|---|---|")
        for row in rows:
            print(f"| {row['keyword']} | {row['status']} |")
    print(f"ats-check: {len(fails)} fail, {len(warns)} warn, pdf: {pdf_state}")
    return code


if __name__ == "__main__":
    sys.exit(main())
