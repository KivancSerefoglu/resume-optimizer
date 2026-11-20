#!/usr/bin/env python3
"""Regression tests for shared/provenance-check.py.

Stdlib only, matching the other test scripts. Run: python3 scripts/test-provenance-check.py

The service layer runs against a fake watermarks-remover service: a
ThreadingHTTPServer on an ephemeral loopback port that answers /health,
/inspect and /clean with canned JSON and records every request it saw.
Nothing here needs the real service, a browser, or the network.
"""
import base64
import contextlib
import importlib.util
import io
import json
import os
import socket
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "resume-optimizer"

_spec = importlib.util.spec_from_file_location("provenance_check", PLUGIN / "shared" / "provenance-check.py")
pc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pc)

CLEAN_REPLY = {"ok": True, "kind": "container", "report": {"findings": [], "findings_confidence": []},
               "suspicious": {"verdict": False, "classes": {"provenance": {"present": False}}}}
FLAGGED_REPLY = {"ok": True, "kind": "container",
                 "report": {"findings": ["C2PA manifest present", "c2patool unavailable"],
                            "findings_confidence": ["confirmed", "informational"]},
                 "suspicious": {"verdict": True, "classes": {"provenance": {"present": True}}}}


class FakeService:
    """Canned replies; `flagged` names the files /inspect reports as marked."""

    def __init__(self):
        self.requests = []  # (method, path, name, authorization)
        self.flagged = set()
        self.cleaned_bytes = b"CLEANED"
        self.redirect = False
        self.health_status = 200
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def reply(self, payload, status=200):
                body = json.dumps(payload).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                fake.requests.append(("GET", self.path, None, self.headers.get("Authorization")))
                if fake.redirect and self.path == "/health":
                    # Points back at this same server, which would answer "ok":
                    # only a client that refuses redirects reports "skipped".
                    self.send_response(302)
                    self.send_header("Location", "/elsewhere")
                    self.end_headers()
                    return
                if fake.health_status != 200:
                    self.reply({"ok": False, "error": "unauthorized"}, status=fake.health_status)
                    return
                self.reply({"ok": True, "version": "test"})

            def do_POST(self):
                data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                name = data["name"]
                fake.requests.append(("POST", self.path, name, self.headers.get("Authorization")))
                if self.path == "/inspect":
                    self.reply(FLAGGED_REPLY if name in fake.flagged else CLEAN_REPLY)
                elif self.path == "/clean":
                    fake.flagged.discard(name)
                    self.reply({"ok": True, "cleaned": base64.b64encode(fake.cleaned_bytes).decode()})
                else:
                    self.reply({"ok": False}, status=404)

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_port}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()


def free_port_url():
    """A loopback URL nothing listens on."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    return f"http://127.0.0.1:{port}"


def run(args, env=None):
    out = io.StringIO()
    with mock.patch.dict(os.environ, env or {}, clear=False), contextlib.redirect_stdout(out), \
            contextlib.redirect_stderr(io.StringIO()):
        code = pc.main(args)
    return code, out.getvalue()


class Workdir(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)

    def write(self, name, content):
        path = self.dir / name
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        return str(path)


class Scan(unittest.TestCase):
    def codes(self, text):
        return [code for _, _, code, _ in pc.scan_text(text)]

    def test_ascii_is_clean(self):
        self.assertEqual(pc.scan_text("Jordan Park\n\tPython, SQL - 2024\r\n"), [])

    def test_visible_non_ascii_is_not_this_checks_business(self):
        # ats-check owns letters; dashes and accents are visible, so not flagged here.
        self.assertEqual(pc.scan_text("2023 – Present — café"), [])

    def test_each_carrier_class(self):
        text = "a​b c d e‮f g\U000e0041h i­j k️l mn"
        self.assertEqual(
            self.codes(text),
            ["U+200B", "U+00A0", "U+202E", "U+E0041", "U+00AD", "U+FE0F", "U+E000"],
        )

    def test_line_separators_are_found_not_swallowed(self):
        self.assertEqual(self.codes("one two three"), ["U+2028", "U+2029"])

    def test_position_is_reported(self):
        self.assertEqual(pc.scan_text("ok\nab​c")[0][:3], (2, 3, "U+200B"))


class ServiceUrl(unittest.TestCase):
    def test_loopback_http_allowed(self):
        for url in ("http://127.0.0.1:8765", "http://localhost:8765/", "http://[::1]:8765"):
            self.assertTrue(pc.service_base(url).startswith("http://"), url)

    def test_https_anywhere_allowed(self):
        self.assertEqual(pc.service_base("https://wm.example.com/"), "https://wm.example.com")

    def test_plain_http_off_machine_refused(self):
        with self.assertRaises(ValueError):
            pc.service_base("http://wm.example.com")

    def test_other_schemes_refused(self):
        for url in ("ftp://127.0.0.1", "file:///etc/passwd", "127.0.0.1:8765"):
            with self.assertRaises(ValueError, msg=url):
                pc.service_base(url)


class Main(Workdir):
    def test_local_hit_fails_without_service(self):
        md = self.write("r.md", "Jordan​Park\n")
        code, out = run([md], {"WATERMARKS_SERVICE_URL": free_port_url()})
        self.assertEqual(code, 1)
        self.assertIn("FAIL invisible: r.md:1:7: U+200B ZERO WIDTH SPACE", out)
        self.assertIn("skip service", out)

    def test_service_down_is_a_skip_not_a_failure(self):
        md = self.write("r.md", "clean\n")
        code, out = run([md], {"WATERMARKS_SERVICE_URL": free_port_url()})
        self.assertEqual(code, 0)
        self.assertIn("skip service: not running at", out)

    def test_refused_url_is_a_usage_error(self):
        md = self.write("r.md", "clean\n")
        code, _ = run([md], {"WATERMARKS_SERVICE_URL": "http://wm.example.com"})
        self.assertEqual(code, 2)

    def test_missing_file_is_a_usage_error(self):
        code, _ = run([str(self.dir / "nope.md")], {"WATERMARKS_SERVICE_URL": free_port_url()})
        self.assertEqual(code, 2)

    def test_clean_service_passes_and_sees_every_deliverable(self):
        files = [self.write("r.html", "<p>x</p>"), self.write("r.md", "x"),
                 self.write("r.pdf", b"%PDF-1.7"), self.write("notes.txt", "x")]
        with FakeService() as svc:
            code, out = run(files, {"WATERMARKS_SERVICE_URL": svc.url})
        self.assertEqual(code, 0, out)
        self.assertIn("ok   service: no provenance marks reported", out)
        inspected = [name for method, path, name, _ in svc.requests if path == "/inspect"]
        self.assertEqual(inspected, ["r.html", "r.md", "r.pdf"])  # .txt never sent

    def test_flagged_file_fails_and_informational_findings_are_dropped(self):
        pdf = self.write("r.pdf", b"%PDF-1.7 original")
        with FakeService() as svc:
            svc.flagged.add("r.pdf")
            code, out = run([pdf], {"WATERMARKS_SERVICE_URL": svc.url})
        self.assertEqual(code, 1)
        self.assertIn("FAIL r.pdf: service: provenance present", out)
        self.assertIn("C2PA manifest present (confirmed)", out)
        self.assertNotIn("c2patool unavailable", out)
        self.assertEqual(Path(pdf).read_bytes(), b"%PDF-1.7 original")  # no --clean, no write

    def test_clean_replaces_the_file_and_reinspects(self):
        pdf = self.write("r.pdf", b"%PDF-1.7 original")
        with FakeService() as svc:
            svc.flagged.add("r.pdf")
            code, out = run([pdf, "--clean"], {"WATERMARKS_SERVICE_URL": svc.url})
            paths = [path for _, path, _, _ in svc.requests if path != "/health"]
        self.assertEqual(code, 0, out)
        self.assertEqual(Path(pdf).read_bytes(), b"CLEANED")
        self.assertIn("cleaned:", out)
        self.assertEqual(paths, ["/inspect", "/clean", "/inspect"])
        self.assertFalse(Path(pdf + ".tmp").exists())

    def test_clean_never_patches_derived_text_files(self):
        md = self.write("r.md", "original")
        with FakeService() as svc:
            svc.flagged.add("r.md")
            code, out = run([md, "--clean"], {"WATERMARKS_SERVICE_URL": svc.url})
            paths = [path for _, path, _, _ in svc.requests]
        self.assertEqual(code, 1)  # the finding stands: fix the body file, re-derive
        self.assertEqual(Path(md).read_text(encoding="utf-8"), "original")
        self.assertNotIn("/clean", paths)

    def test_rejected_token_is_an_error_not_a_skip(self):
        md = self.write("r.md", "x")
        for status in (401, 403):
            with FakeService() as svc:
                svc.health_status = status
                code, out = run([md], {"WATERMARKS_SERVICE_URL": svc.url})
            self.assertEqual(code, 2, status)
            self.assertNotIn("skip service", out)

    def test_other_health_errors_still_mean_not_running(self):
        md = self.write("r.md", "x")
        with FakeService() as svc:
            svc.health_status = 500
            code, out = run([md], {"WATERMARKS_SERVICE_URL": svc.url})
        self.assertEqual(code, 0)
        self.assertIn("skip service", out)

    def test_bearer_token_is_sent_when_set(self):
        md = self.write("r.md", "x")
        with FakeService() as svc:
            run([md], {"WATERMARKS_SERVICE_URL": svc.url, "WATERMARKS_SERVER_API_KEY": "t0k"})
        self.assertTrue(svc.requests)
        self.assertTrue(all(auth == "Bearer t0k" for *_, auth in svc.requests))

    def test_redirect_is_not_followed(self):
        md = self.write("r.md", "x")
        with FakeService() as svc:
            svc.redirect = True
            code, out = run([md], {"WATERMARKS_SERVICE_URL": svc.url})
        # The health probe is refused, so the service counts as not running.
        self.assertEqual(code, 0)
        self.assertIn("skip service", out)
        self.assertNotIn("/elsewhere", [path for _, path, _, _ in svc.requests])

    def test_json_output(self):
        md = self.write("r.md", "a b")
        code, out = run([md, "--json"], {"WATERMARKS_SERVICE_URL": free_port_url()})
        data = json.loads(out)
        self.assertEqual(code, 1)
        self.assertFalse(data["ok"])
        self.assertEqual(data["service"]["status"], "skipped")
        self.assertEqual(len(data["local"]), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
