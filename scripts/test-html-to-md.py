#!/usr/bin/env python3
"""Regression tests for shared/html-to-md.py.

Stdlib only, matching check-links.py. Run: python3 scripts/test-html-to-md.py

The golden test is the point: the resume converter's output must not change
when the script is extended to also handle cover letters.
"""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "resume-optimizer"
SCRIPT = PLUGIN / "shared" / "html-to-md.py"
RESUME = PLUGIN / "skills/resume-optimizer/assets/resume-template.html"
LETTER = PLUGIN / "skills/cover-letter/assets/cover-letter-template.html"
GOLDEN = ROOT / "scripts/fixtures/resume-template.golden.md"

spec = importlib.util.spec_from_file_location("html_to_md", SCRIPT)
h2m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h2m)


class ResumeUnchanged(unittest.TestCase):
    def test_matches_golden(self):
        """The resume conversion is byte-identical to pre-change output."""
        html = RESUME.read_text(encoding="utf-8")
        self.assertEqual(h2m.convert(html), GOLDEN.read_text(encoding="utf-8"))

    def test_no_lost_tokens(self):
        html = RESUME.read_text(encoding="utf-8")
        self.assertEqual(h2m.missing_text(html, h2m.convert(html)), [])


class CoverLetter(unittest.TestCase):
    def setUp(self):
        # Both templates carry non-ASCII (bullet separators, en dashes), so the
        # encoding is explicit -- read_text() otherwise follows the locale and
        # would fail on a non-UTF-8 machine.
        self.html = LETTER.read_text(encoding="utf-8")
        self.md = h2m.convert(self.html)

    def test_no_lost_tokens(self):
        """Every visible word in the letter survives into the markdown."""
        self.assertEqual(h2m.missing_text(self.html, self.md), [])

    def test_name_is_heading(self):
        self.assertTrue(self.md.startswith("# Jordan Example"))

    def test_keeps_salutation_and_closing(self):
        self.assertIn("Dear Marcus Example,", self.md)
        self.assertIn("Kind regards,", self.md)
        self.assertIn("Jordan Example", self.md.split("Kind regards,")[1])

    def test_document_order(self):
        """Date precedes company precedes salutation precedes closing."""
        order = [self.md.index(s) for s in
                 ("March 3, 2026", "Example Water Authority",
                  "Dear Marcus Example,", "Kind regards,")]
        self.assertEqual(order, sorted(order))


if __name__ == "__main__":
    unittest.main(verbosity=2)
