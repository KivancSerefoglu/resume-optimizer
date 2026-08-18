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

Usage:  python3 render.py TEMPLATE BODY OUTPUT_BASE
        python3 render.py --pages FILE.pdf

Writes OUTPUT_BASE.html and OUTPUT_BASE.pdf, creating OUTPUT_BASE's parent
directory when needed, then prints the page count.
Exit 0 = rendered, 2 = no browser found (the .html is still written), 1 = error.
"""
import argparse
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

    count = pdf_pages(pdf)
    print(f"wrote {pdf}")
    print(f"pages: {count if count else 'unknown'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
