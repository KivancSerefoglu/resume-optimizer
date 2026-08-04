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


# A résumé whose every repeated word survives somewhere else in the document.
# Dropping one instance leaves the *set* of words unchanged, so a set-based
# check sees nothing wrong. Both duplications below are realistic: two stints at
# one employer under the same title, and a project whose name is also a skill.
DUPLICATES_HTML = """<html><body><main>
  <h1 class="name">Jordan Example</h1>
  <section class="section">
    <h2>Experience</h2>
    <div class="entry">
      <div class="entry-line">
        <span class="entry-org">Example Corp</span>
        <span class="entry-loc">Chicago, IL</span>
      </div>
      <div class="entry-line">
        <span class="entry-title">Software Engineer</span>
        <span class="entry-dates">Jun 2024</span>
      </div>
    </div>
    <div class="entry">
      <div class="entry-line">
        <span class="entry-org">Example Corp</span>
        <span class="entry-loc">Chicago, IL</span>
      </div>
      <div class="entry-line">
        <span class="entry-title">Software Engineer</span>
        <span class="entry-dates">Jun 2024</span>
      </div>
    </div>
  </section>
  <section class="section">
    <h2>Skills</h2>
    <p class="skills-line"><strong>Tools:</strong> Course Scheduler, Python</p>
  </section>
  <section class="section">
    <h2>Projects</h2>
    <div class="entry">
      <div class="entry-line">
        <span class="entry-org">Course Scheduler</span>
      </div>
    </div>
  </section>
</main></body></html>"""

# A letter that opens and closes on the same sentence.
REPEATED_LINE_HTML = """<html><body><main>
  <p>Thank you for your consideration.</p>
  <p>I would welcome the chance to talk.</p>
  <p>Thank you for your consideration.</p>
</main></body></html>"""


class DuplicateContentLoss(unittest.TestCase):
    """Losing one instance of repeated content must still be caught.

    missing_text compares word multisets, not sets: a word that survives
    elsewhere does not excuse a dropped copy. Each test deletes one line from
    real convert() output, which is what a converter bug would do.
    """

    def assert_dropping(self, html, line):
        """Delete `line` from the markdown, return what the check reports lost."""
        md = h2m.convert(html)
        self.assertIn(line, md, "fixture drifted: line not in conversion")
        return h2m.missing_text(html, md.replace(line, "", 1))

    def test_intact_conversion_is_not_flagged(self):
        """Repetition alone must not trip the check -- no false positives."""
        for label, html in (("resume", DUPLICATES_HTML), ("letter", REPEATED_LINE_HTML)):
            with self.subTest(fixture=label):
                self.assertEqual(h2m.missing_text(html, h2m.convert(html)), [])

    def test_duplicated_employer_line(self):
        """One of two identical employer lines goes missing."""
        lost = self.assert_dropping(DUPLICATES_HTML, "**Example Corp** — Chicago, IL")
        self.assertEqual(lost, ["example", "corp", "chicago", "il"])

    def test_duplicated_title_line(self):
        """One of two identical title/date lines goes missing."""
        lost = self.assert_dropping(DUPLICATES_HTML, "*Software Engineer* — Jun 2024")
        self.assertEqual(lost, ["software", "engineer", "jun", "2024"])

    def test_project_name_also_in_skills_line(self):
        """The project entry vanishes; its words live on in the skills line."""
        lost = self.assert_dropping(DUPLICATES_HTML, "**Course Scheduler**")
        self.assertEqual(lost, ["course", "scheduler"])

    def test_repeated_closing_line(self):
        """A sentence used twice loses one use."""
        lost = self.assert_dropping(REPEATED_LINE_HTML, "Thank you for your consideration.")
        self.assertEqual(lost, ["thank", "you", "for", "your", "consideration"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
