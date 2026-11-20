#!/usr/bin/env python3
"""Assemble a filled template and render it to PDF.

The skills author only the markup that goes inside <main>. This splices that
body into the template and drives headless Chrome, so the template's <head> and
CSS are never retyped -- they are pure boilerplate to the writer, and the
one-page trim loop re-renders several times, paying for them on every pass.

Browser discovery and --no-pdf-header-footer live here rather than in SKILL.md
because both skills need them identically, and the flag is not optional:
without it Chrome stamps the print date and the local file:// path onto a
document the user sends to employers.

Usage:  python3 render.py [--page-size A4|letter] [--title TEXT] [--author TEXT]
                         TEMPLATE BODY OUTPUT_BASE
        python3 render.py --pages FILE.pdf

--page-size rewrites the template's @page size before the HTML is written, so
the saved HTML, the PDF, and the markdown later derived from the HTML agree.
Omitted, the template's own size stands.

--title rewrites the template's <title>, which Chrome copies into the PDF's
/Title: the generic "Resume" otherwise, or the local file:// path of the HTML
when a page has no title at all. Chrome also writes its own user-agent string
(HeadlessChrome/...) as /Creator, so when pypdf is importable the PDF's document
information is rewritten afterwards: /Title and /Author set, /Creator and
/Producer dropped, dates kept. Without pypdf the render still succeeds and says
the browser creator was left in place -- the plugin promises no installs.

Writes OUTPUT_BASE.html and OUTPUT_BASE.pdf, creating OUTPUT_BASE's parent
directory when needed, then prints the page count.
Exit 0 = rendered, 2 = no browser found (the .html is still written), 1 = error.
"""
import argparse
import html as htmllib
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

NO_BROWSER = 2

MAIN = re.compile(r"(<main\b[^>]*>)(.*?)(</main>)", re.S)

# PATH names first: a browser the user can already run is the right one.
PATH_NAMES = (
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "chrome",
    "microsoft-edge",
    "msedge",
)

MAC_PATHS = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "~/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
)

# Edge takes the same flags as Chrome, and ships on every Windows machine.
WINDOWS_PATHS = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"~\AppData\Local\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
)


def assemble(template: str, body: str) -> str:
    """Template with everything between <main> and </main> replaced by body."""
    if not MAIN.search(template):
        raise ValueError("template has no <main> ... </main> block")
    # Forgiving: a body file that kept its own <main> wrapper still works.
    wrapped = MAIN.search(body)
    if wrapped:
        body = wrapped.group(2)
    return MAIN.sub(
        lambda m: f"{m.group(1)}\n{body.strip()}\n{m.group(3)}", template, count=1
    )


PAGE_SIZE = re.compile(r"(@page\s*\{[^}]*?\bsize\s*:\s*)([^;}]+)")
PAGE_SIZES = {"a4": "A4", "letter": "letter"}


def set_page_size(html: str, size: str) -> str:
    """The HTML with its first @page size declaration set to A4 or letter."""
    label = PAGE_SIZES[size.lower()]
    if not PAGE_SIZE.search(html):
        raise ValueError("template has no @page size rule")
    return PAGE_SIZE.sub(lambda m: f"{m.group(1)}{label}", html, count=1)


TITLE = re.compile(r"(<title\b[^>]*>)(.*?)(</title>)", re.S | re.I)


def set_title(html: str, title: str) -> str:
    """The HTML with its <title> text replaced (escaped) by title."""
    if not TITLE.search(html):
        raise ValueError("template has no <title> element")
    safe = htmllib.escape(title.strip(), quote=False)
    return TITLE.sub(lambda m: f"{m.group(1)}{safe}{m.group(3)}", html, count=1)


# Keys a browser or library stamps with its own name. Dropped, not blanked: an
# empty /Creator still tells a reader which field was scrubbed.
TOOL_KEYS = ("/Creator", "/Producer")


def scrub_metadata(pdf: Path, title=None, author=None) -> str:
    """Rewrite the PDF's document information; return a one-line status.

    Keeps every entry except TOOL_KEYS, sets /Title and /Author when given, and
    drops an XMP stream if one exists. The rewrite goes to a sibling file that
    replaces the original only once it is complete, so a failure leaves the
    browser's PDF untouched.
    """
    try:
        from pypdf import PdfWriter
        from pypdf.generic import NameObject
    except ImportError:
        return "metadata: browser creator left (pypdf not installed)"
    tmp = pdf.with_name(pdf.name + ".tmp")
    try:
        writer = PdfWriter(clone_from=str(pdf))
        info = {k: v for k, v in (writer.metadata or {}).items() if k not in TOOL_KEYS}
        if title:
            info["/Title"] = title.strip()
        if author:
            info["/Author"] = author.strip()
        writer.metadata = info
        root = writer._root_object
        if NameObject("/Metadata") in root:
            del root[NameObject("/Metadata")]
        with tmp.open("wb") as fh:
            writer.write(fh)
        tmp.replace(pdf)
    except Exception as exc:  # pypdf raises many types; the render itself succeeded
        tmp.unlink(missing_ok=True)
        return f"metadata: left as rendered ({type(exc).__name__}: {exc})"
    return "metadata: scrubbed"


def find_browser():
    for name in PATH_NAMES:
        found = shutil.which(name)
        if found:
            return found
    system = platform.system()
    candidates = MAC_PATHS if system == "Darwin" else WINDOWS_PATHS if system == "Windows" else ()
    for candidate in candidates:
        path = Path(candidate).expanduser()
        if path.exists():
            return str(path)
    return None


def pdf_pages(pdf: Path):
    """Page count, or None when the PDF does not declare one.

    /Count appears on every page-tree node, so the outermost -- the largest --
    is the document total. A file without one falls back to counting /Type
    /Page objects, where the [^s] guard excludes the /Pages nodes themselves.
    """
    data = pdf.read_bytes()
    counts = [int(n) for n in re.findall(rb"/Count\s+(\d+)", data)]
    if counts:
        return max(counts)
    return len(re.findall(rb"/Type\s*/Page[^s]", data)) or None


def render(html: Path, pdf: Path, browser: str) -> None:
    subprocess.run(
        [
            browser,
            "--headless",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf.resolve()}",
            html.resolve().as_uri(),
        ],
        check=True,
        capture_output=True,
        timeout=120,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--pages", metavar="FILE.pdf", help="report an existing PDF's page count and exit"
    )
    ap.add_argument(
        "--page-size", choices=tuple(PAGE_SIZES), type=str.lower,
        help="A4 or letter; omitted, the template's own @page size stands",
    )
    ap.add_argument("--title", help="document title for the HTML <title> and the PDF /Title")
    ap.add_argument("--author", help="PDF /Author (needs pypdf; skipped without it)")
    ap.add_argument("args", nargs="*", metavar="TEMPLATE BODY OUTPUT_BASE")
    opts = ap.parse_args()

    if opts.pages:
        count = pdf_pages(Path(opts.pages))
        print(f"pages: {count if count else 'unknown'}")
        return 0

    if len(opts.args) != 3:
        ap.error("expected TEMPLATE BODY OUTPUT_BASE")
    template_path, body_path, base = Path(opts.args[0]), Path(opts.args[1]), opts.args[2]

    try:
        merged = assemble(
            template_path.read_text(encoding="utf-8"),
            body_path.read_text(encoding="utf-8"),
        )
        if opts.page_size:
            merged = set_page_size(merged, opts.page_size)
        if opts.title:
            merged = set_title(merged, opts.title)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    html = Path(f"{base}.html")
    # The base carries the per-application folder, which usually does not exist
    # yet on the first render. Creating it here rather than in each SKILL.md
    # keeps a forgotten mkdir from surfacing as a bare FileNotFoundError.
    html.parent.mkdir(parents=True, exist_ok=True)
    html.write_text(merged, encoding="utf-8")
    print(f"wrote {html}")

    browser = find_browser()
    if not browser:
        print(
            "ERROR: no Chrome, Chromium, or Edge found -- open the HTML in a browser "
            'and print to PDF with "Headers and footers" turned off.',
            file=sys.stderr,
        )
        return NO_BROWSER

    pdf = Path(f"{base}.pdf")
    try:
        render(html, pdf, browser)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        detail = getattr(exc, "stderr", b"") or b""
        print(f"ERROR: {Path(browser).name} failed to render", file=sys.stderr)
        if detail:
            print(detail.decode("utf-8", "replace").strip()[:500], file=sys.stderr)
        return 1

    print(scrub_metadata(pdf, opts.title, opts.author))
    count = pdf_pages(pdf)
    print(f"wrote {pdf}")
    print(f"pages: {count if count else 'unknown'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
