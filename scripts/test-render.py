#!/usr/bin/env python3
"""Regression tests for shared/render.py.

Stdlib only, matching check-links.py. Run: python3 scripts/test-render.py

The round-trip test is the point: authoring only the <main> body must produce
exactly the document the old copy-the-whole-template flow produced. Nothing
here shells out to Chrome, so the suite runs on a machine without a browser.
"""
import importlib.util
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "resume-optimizer"
RESUME = PLUGIN / "skills/resume-optimizer/assets/resume-template.html"
LETTER = PLUGIN / "skills/cover-letter/assets/cover-letter-template.html"
GOLDEN = ROOT / "scripts/fixtures/resume-template.golden.md"

# Both templates carry non-ASCII (bullet separators, en dashes), so every read
# is explicit -- read_text() otherwise follows the locale and would fail on a
# non-UTF-8 machine.
READ = {"encoding": "utf-8"}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


render = load("render", PLUGIN / "shared" / "render.py")
h2m = load("html_to_md", PLUGIN / "shared" / "html-to-md.py")


def body_of(template_path):
    """The template's own <main> contents, as a body file would supply them."""
    html = template_path.read_text(**READ)
    return re.search(r"<main\b[^>]*>(.*?)</main>", html, re.S).group(1)


class Assemble(unittest.TestCase):
    def test_body_replaces_main(self):
        out = render.assemble("<html><main>OLD</main></html>", "<p>NEW</p>")
        self.assertEqual(out, "<html><main>\n<p>NEW</p>\n</main></html>")

    def test_head_and_css_survive(self):
        """The boilerplate the writer never retypes must still reach the PDF."""
        out = render.assemble(RESUME.read_text(**READ), "<p>x</p>")
        self.assertIn("@page", out)
        self.assertIn(".entry-line", out)
        self.assertNotIn("Jordan Example", out)

    def test_body_wrapped_in_main_is_unwrapped(self):
        """A body file that kept its <main> wrapper must not nest another."""
        out = render.assemble("<main>OLD</main>", "<main><p>NEW</p></main>")
        self.assertEqual(out.count("<main"), 1)
        self.assertIn("<p>NEW</p>", out)

    def test_template_without_main_is_an_error(self):
        with self.assertRaises(ValueError):
            render.assemble("<html><body>x</body></html>", "<p>x</p>")


class RoundTrip(unittest.TestCase):
    """Assembling a template's own body back into it reproduces the document."""

    def test_resume_markdown_matches_golden(self):
        merged = render.assemble(RESUME.read_text(**READ), body_of(RESUME))
        self.assertEqual(h2m.convert(merged), GOLDEN.read_text(**READ))

    def test_letter_loses_no_text(self):
        merged = render.assemble(LETTER.read_text(**READ), body_of(LETTER))
        self.assertEqual(h2m.missing_text(merged, h2m.convert(merged)), [])


class PdfPages(unittest.TestCase):
    def tmp(self, text):
        fd = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        fd.write(text.encode("latin-1"))
        fd.close()
        self.addCleanup(Path(fd.name).unlink)
        return Path(fd.name)

    def test_outermost_count_wins(self):
        self.assertEqual(render.pdf_pages(self.tmp("/Count 1 ... /Count 3")), 3)

    def test_falls_back_to_page_objects(self):
        pdf = self.tmp("/Type /Page\n/Type /Pages\n/Type /Page\n")
        self.assertEqual(render.pdf_pages(pdf), 2)

    def test_unknown_when_nothing_declared(self):
        self.assertIsNone(render.pdf_pages(self.tmp("%PDF-1.7 no page tree")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
