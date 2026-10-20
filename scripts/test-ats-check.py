#!/usr/bin/env python3
"""Regression tests for shared/ats-check.py.

Stdlib only, matching check-links.py. Run: python3 scripts/test-ats-check.py

Nothing here renders a PDF or shells out to an extractor: the HTML checks run on
the assembled templates and on synthetic bodies, and the PDF checks run against
a fake extractor swapped into EXTRACTORS.
"""
import contextlib
import importlib.util
import io
import json
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "resume-optimizer"
RESUME = PLUGIN / "skills/resume-optimizer/assets/resume-template.html"
READ = {"encoding": "utf-8"}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


render = load("render", PLUGIN / "shared" / "render.py")
ats = load("ats_check", PLUGIN / "shared" / "ats-check.py")
TEMPLATE = RESUME.read_text(**READ)


def body_of(template_path):
    html = template_path.read_text(**READ)
    return re.search(r"<main\b[^>]*>(.*?)</main>", html, re.S).group(1)


CONTACT = '<h1 class="name">Jordan Example</h1>\n<p class="contact">Chicago, IL • jordan@example.com</p>\n'


def entry(bullets, org="Example Corp", dates="Jun 2024 – Present"):
    items = "".join(f"<li>{b}</li>" for b in bullets)
    return (
        '<section class="section"><h2>Experience</h2><div class="entry">'
        f'<div class="entry-line"><span class="entry-org">{org}</span><span class="entry-loc">Chicago, IL</span></div>'
        f'<div class="entry-line"><span class="entry-title">Software Engineer</span><span class="entry-dates">{dates}</span></div>'
        f"<ul>{items}</ul></div></section>"
    )


def wrap(body):
    """A body inside the real template, so its CSS (and .entry-line flex) is present."""
    return render.assemble(TEMPLATE, body)


def fails(findings):
    return [f for f in findings if f.level == "fail"]


def run(args):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = ats.main(args)
    return code, out.getvalue()


class Files:
    def tmp(self, content, suffix=".html"):
        fd = tempfile.NamedTemporaryFile(suffix=suffix, delete=False, mode="w", encoding="utf-8")
        fd.write(content)
        fd.close()
        self.addCleanup(Path(fd.name).unlink)
        return fd.name


class TemplateBody(Files, unittest.TestCase):
    def test_template_has_no_failures(self):
        findings = ats.check_html(wrap(body_of(RESUME)), 1)
        self.assertEqual(fails(findings), [])
        self.assertEqual([f.check for f in findings if f.level == "warn"], ["contact"])

    def test_cli_exit_zero(self):
        code, out = run([self.tmp(wrap(body_of(RESUME)))])
        self.assertEqual(code, 0)
        self.assertIn("ats-check: 0 fail", out)


class HtmlFailures(Files, unittest.TestCase):
    def assert_fail(self, body, check, fragment=None, page_limit=1):
        found = [f for f in fails(ats.check_html(wrap(body), page_limit)) if f.check == check]
        self.assertTrue(found, f"expected a {check} failure")
        if fragment:
            self.assertTrue(any(fragment in f.message for f in found), [f.message for f in found])

    def assert_clean(self, body, page_limit=1):
        self.assertEqual(fails(ats.check_html(wrap(body), page_limit)), [])

    def test_bold_budget(self):
        bullets = [f"Built <strong>data pipeline {i}</strong> for the team." for i in range(11)]
        self.assert_fail(CONTACT + entry(bullets), "bold", "budget is 10")

    def test_ten_tool_bolds_pass(self):
        bullets = [f"Built pipeline {i} in <strong>Python</strong>." for i in range(10)]
        self.assert_clean(CONTACT + entry(bullets))

    def test_page_limit_lifts_budget(self):
        bullets = [f"Built <strong>data pipeline {i}</strong> for the team." for i in range(20)]
        self.assert_clean(CONTACT + entry(bullets), page_limit=2)
        bullets.append("Built <strong>one more pipeline</strong> too.")
        self.assert_fail(CONTACT + entry(bullets), "bold", "budget is 20", page_limit=2)

    def test_two_tool_bolds_in_one_bullet_pass(self):
        self.assert_clean(CONTACT + entry(["Used <strong>Python</strong> and <strong>Airflow</strong> daily."]))

    def test_three_bolds_in_one_bullet(self):
        self.assert_fail(CONTACT + entry(["Used <strong>Python</strong>, <strong>Airflow</strong> and <strong>Docker</strong> daily."]), "bold", "3 bold phrases")

    def test_five_word_bold(self):
        self.assert_fail(CONTACT + entry(["Built <strong>a very long bold phrase here</strong>."]), "bold", "longer than 4")

    def test_whole_bullet_bold(self):
        self.assert_fail(CONTACT + entry(["<strong>Shipped it</strong>"]), "bold", "whole bullet")

    def test_metric_alone(self):
        self.assert_fail(CONTACT + entry(["Cut latency by <strong>40%</strong> on the API."]), "bold", "metric")

    def test_bold_in_heading(self):
        body = CONTACT + entry(["Built x."]).replace("<h2>Experience</h2>", "<h2><strong>Experience</strong></h2>")
        self.assert_fail(body, "bold", "heading")

    def test_bold_in_entry_line(self):
        body = CONTACT + entry(["Built x."], org="<strong>Example Corp</strong>")
        self.assert_fail(body, "bold", "entry header")

    def test_bold_in_skills_value(self):
        body = CONTACT + '<section class="section"><h2>Skills</h2><p class="skills-line"><strong>Technical:</strong> <strong>Python</strong>, SQL</p></section>'
        self.assert_fail(body, "bold", "Skills value")

    def test_skills_label_is_allowed(self):
        self.assert_clean(CONTACT + '<section class="section"><h2>Skills</h2><p class="skills-line"><strong>Technical:</strong> Python, SQL</p></section>')

    def test_image_in_contact(self):
        body = CONTACT.replace("Chicago, IL", '<img src="phone.png"> Chicago, IL')
        self.assert_fail(body, "markup", "<img>")

    def test_table(self):
        self.assert_fail(CONTACT + "<table><tr><td>x</td></tr></table>", "markup", "<table>")

    def test_column_count_css(self):
        self.assert_fail(CONTACT + "<style>.two{column-count:2}</style>", "layout", ".two")

    def test_grid_css(self):
        self.assert_fail(CONTACT + "<style>.g{display: grid}</style>", "layout", ".g")

    def test_inline_float(self):
        self.assert_fail(CONTACT + '<p style="float:left">x</p>', "layout", "inline style")

    def test_entry_line_flex_is_allowed(self):
        self.assert_clean(CONTACT + entry(["Built x."]))

    def test_entry_without_year(self):
        self.assert_fail(CONTACT + entry(["Built x."], dates="Summer"), "dates", "Example Corp")

    def test_non_ascii_flagged_but_urls_skipped(self):
        body = CONTACT.replace("jordan@example.com", "jordan@example.com • github.com/kıvanç") + entry(["Worked with Kıvanç on x."])
        found = [f for f in fails(ats.check_html(wrap(body), 1)) if f.check == "ascii"]
        self.assertEqual(len(found), 1)
        self.assertIn("Kıvanç", found[0].message)
        self.assertNotIn("github", found[0].message)

    def test_missing_email(self):
        self.assert_fail(CONTACT.replace("jordan@example.com", "no email here") + entry(["Built x."]), "contact", "email")


PDF_BODY = CONTACT + (
    '<section class="section"><h2>Education</h2><div class="entry">'
    '<div class="entry-line"><span class="entry-org">Example University</span><span class="entry-dates">May 2024</span></div></div></section>'
    + entry(["Verified data pipelines with Python."])
)
GOOD_TEXT = "Jordan Example\nChicago, IL • jordan@example.com\nEDUCATION\nExample University May 2024\nEXPERIENCE\nExample Corp\nVeriﬁed data pipelines with Python."


class PdfPath(Files, unittest.TestCase):
    def fake(self, text_):
        original = ats.EXTRACTORS
        ats.EXTRACTORS = (("fake", lambda p: text_),)
        self.addCleanup(setattr, ats, "EXTRACTORS", original)

    def pdf_fails(self, text_, keywords=()):
        self.fake(text_)
        code, out = run([self.tmp(wrap(PDF_BODY)), "--pdf", self.tmp("%PDF", ".pdf")] + [a for k in keywords for a in ("--keyword", k)])
        return code, out

    def test_clean_text_layer(self):
        code, out = self.pdf_fails(GOOD_TEXT, ["Python", "verified", "Airflow"])
        self.assertEqual(code, 0, out)
        self.assertIn("| Python | covered |", out)
        self.assertIn("| verified | covered |", out)
        self.assertIn("| Airflow | missing |", out)
        self.assertIn("pdf: fake", out)

    def test_cid_garbage(self):
        code, out = self.pdf_fails(GOOD_TEXT.replace("Python", "(cid:12)"))
        self.assertEqual(code, 1)
        self.assertIn("garbage", out)

    def test_replacement_character(self):
        code, out = self.pdf_fails(GOOD_TEXT + " �")
        self.assertEqual(code, 1)

    def test_email_missing(self):
        code, out = self.pdf_fails(GOOD_TEXT.replace("jordan@example.com", "jordan at example"))
        self.assertEqual(code, 1)
        self.assertIn("email", out)

    def test_headings_out_of_order(self):
        swapped = GOOD_TEXT.replace("EDUCATION", "XX").replace("EXPERIENCE", "EDUCATION").replace("XX", "EXPERIENCE")
        code, out = self.pdf_fails(swapped)
        self.assertEqual(code, 1)
        self.assertIn("out of order", out)

    def test_html_only_keyword_fails(self):
        code, out = self.pdf_fails(GOOD_TEXT.replace("Python", "Pyth on"), ["Python"])
        self.assertEqual(code, 1)
        self.assertIn("| Python | html-only |", out)

    def test_unverifiable_keyword(self):
        code, out = self.pdf_fails(GOOD_TEXT, ["C++"])
        self.assertIn("| C++ | unverifiable |", out)

    def test_no_extractor_exits_two(self):
        self.fake(None)
        ats.EXTRACTORS = ()
        code, out = run([self.tmp(wrap(PDF_BODY)), "--pdf", self.tmp("%PDF", ".pdf"), "--keyword", "Python"])
        self.assertEqual(code, 2)
        self.assertIn("UNVERIFIED pdf", out)
        self.assertIn("| Python | covered (pdf unverified) |", out)

    def test_html_failure_outranks_unverified(self):
        ats.EXTRACTORS = ()
        self.addCleanup(setattr, ats, "EXTRACTORS", (("pypdf", ats.extract_pypdf), ("pdftotext", ats.extract_pdftotext)))
        code, _ = run([self.tmp(wrap(PDF_BODY + "<table><tr><td>x</td></tr></table>")), "--pdf", self.tmp("%PDF", ".pdf")])
        self.assertEqual(code, 1)


class Cli(Files, unittest.TestCase):
    def test_keywords_file_and_repeatable_flag(self):
        kw = self.tmp("Python\n\nSQL\n", ".txt")
        code, out = run([self.tmp(wrap(PDF_BODY)), "--keywords", kw, "--keyword", "Airflow"])
        self.assertEqual(code, 0)
        self.assertIn("| Python | covered (pdf unverified) |", out)
        self.assertIn("| SQL | missing |", out)
        self.assertIn("| Airflow | missing |", out)
        self.assertIn("pdf: not checked", out)

    def test_json_output(self):
        code, out = run([self.tmp(wrap(PDF_BODY)), "--keyword", "Python", "--json"])
        data = json.loads(out)
        self.assertEqual(data["exit"], code)
        self.assertEqual(data["keywords"][0]["status"], "covered (pdf unverified)")
        self.assertIsNone(data["extractor"])
        self.assertTrue(all(f["level"] != "fail" for f in data["html"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
