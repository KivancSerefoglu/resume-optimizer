#!/usr/bin/env python3
"""Check exported application files for invisible characters and provenance marks.

Two layers, like ats-check.py.

The local scan always runs, on .html and .md files: it flags characters a
reader cannot see but a parser or a detector can -- zero-width and bidi
controls, soft hyphens, tag characters, variation selectors, private-use
code points, and every space that is not U+0020. These are the "Layer A"
carriers that watermarks-remover (github.com/guillaumemeyer/watermarks-remover,
MIT) strips; the classes mirror its text_unicode.py, re-implemented here so the
plugin keeps its no-install promise. The templates are ASCII and the skills
write ASCII, so any hit is a stray paste or a generated artifact to remove.

The service layer is optional. When a watermarks-remover service answers at
WATERMARKS_SERVICE_URL (default http://127.0.0.1:8765), every file -- the PDF
included -- goes to its /inspect endpoint, which looks for C2PA / Content
Credentials and AI-metadata markers as well as the Unicode carriers. With
--clean, a PDF the service flags is sent to /clean and replaced in place by
the cleaned bytes. Only the PDF: the .html and .md are derived from the body
file the skill writes, so a finding there is fixed in that source and
re-derived, never patched in one copy. When nothing answers, the layer reports
"skipped" and the check still passes: the service is a tool the user runs, not
a requirement. A service that answers but rejects the token is an error.

Plain-text files are never sent: the service rewrites .txt prose with a
paraphrase model, and a résumé's wording is the candidate's, not a model's.

Usage:  python3 provenance-check.py FILE... [--clean] [--json]
Env:    WATERMARKS_SERVICE_URL   service base URL (https required off-loopback)
        WATERMARKS_SERVER_API_KEY  bearer token, when the service requires one
Exit 0 = nothing found (service checked or skipped), 1 = findings remain,
2 = usage error, unreadable file, a refused service URL, or a rejected token.
"""
import argparse
import base64
import json
import os
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_URL = "http://127.0.0.1:8765"
LOOPBACK = {"127.0.0.1", "localhost", "::1"}
TEXT_SUFFIXES = {".html", ".htm", ".md"}
SERVICE_SUFFIXES = {".html", ".htm", ".md", ".pdf"}
CLEANABLE_SUFFIXES = {".pdf"}
AUTH_STATUSES = {401, 403}
HEALTH_TIMEOUT = 2
CALL_TIMEOUT = 120
ALLOWED_CONTROLS = {"\n", "\r", "\t"}


def is_suspicious(ch: str) -> bool:
    """True for a character that renders as nothing, or as an ordinary space."""
    cp = ord(ch)
    if 0xFE00 <= cp <= 0xFE0F or 0xE0100 <= cp <= 0xE01EF:  # variation selectors
        return True
    cat = unicodedata.category(ch)
    if cat == "Zs":
        return ch != " "
    if cat == "Cc":
        return ch not in ALLOWED_CONTROLS
    # Cf: zero-width, bidi, soft hyphen, tag characters (U+E0000-E007F).
    return cat in {"Cf", "Co", "Cs", "Zl", "Zp"}


def scan_text(text: str):
    """[(line, column, 'U+XXXX', name)] for every suspicious character."""
    hits = []
    # split("\n"), not splitlines(): the latter treats U+2028/U+2029 and other
    # separators as line breaks and would swallow exactly what we look for.
    for lineno, line in enumerate(text.split("\n"), 1):
        for col, ch in enumerate(line.rstrip("\r"), 1):
            if is_suspicious(ch):
                hits.append((lineno, col, f"U+{ord(ch):04X}", unicodedata.name(ch, "UNNAMED")))
    return hits


def local_findings(path: Path):
    hits = scan_text(path.read_text(encoding="utf-8", errors="replace"))
    return [f"{path.name}:{line}:{col}: {code} {name}" for line, col, code, name in hits]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """A redirect could forward the bearer token to another host: refuse it."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, f"refused redirect to {newurl}", headers, fp)


OPENER = urllib.request.build_opener(NoRedirect)


def service_base(raw: str) -> str:
    """The validated base URL; ValueError for anything that could leak the file."""
    parts = urllib.parse.urlsplit(raw.strip())
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise ValueError(f"WATERMARKS_SERVICE_URL must be an http(s) URL, got {raw!r}")
    if parts.scheme == "http" and parts.hostname not in LOOPBACK:
        raise ValueError(
            f"refusing plain http to {parts.hostname}: use https off this machine, "
            "so the file and token are not sent in cleartext"
        )
    return raw.strip().rstrip("/")


def call(base: str, path: str, payload=None, timeout=CALL_TIMEOUT):
    headers = {"Accept": "application/json"}
    token = os.environ.get("WATERMARKS_SERVER_API_KEY")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(base + path, data=data, headers=headers)
    with OPENER.open(req, timeout=timeout) as resp:  # noqa: S310 -- scheme checked in service_base
        return json.load(resp)


class Rejected(Exception):
    """The service answered and refused the credentials."""


def reachable(base: str) -> bool:
    try:
        return bool(call(base, "/health", timeout=HEALTH_TIMEOUT).get("ok"))
    except urllib.error.HTTPError as exc:
        if exc.code in AUTH_STATUSES:
            raise Rejected(f"HTTP {exc.code}") from None
        return False
    except (OSError, ValueError):  # URLError, timeouts and bad JSON all mean "not there"
        return False


def summarize(name: str, result: dict):
    """Finding lines for one /inspect reply; empty when nothing is present."""
    verdict = result.get("suspicious") or {}
    lines = [
        f"{name}: service: {cls} present"
        for cls, info in sorted((verdict.get("classes") or {}).items())
        if isinstance(info, dict) and info.get("present")
    ]
    report = result.get("report") or {}
    confidences = report.get("findings_confidence") or []
    for i, finding in enumerate(report.get("findings") or []):
        level = confidences[i] if i < len(confidences) else ""
        if level in ("informational", "likely_false_positive"):
            continue
        lines.append(f"{name}: service: {finding}" + (f" ({level})" if level else ""))
    if verdict.get("verdict") and not lines:
        lines.append(f"{name}: service: flagged as suspicious")
    return lines


def payload_for(path: Path):
    return {"file": base64.b64encode(path.read_bytes()).decode("ascii"), "name": path.name}


def write_cleaned(path: Path, encoded: str) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(base64.b64decode(encoded, validate=True))
    tmp.replace(path)


def check_service(base: str, paths, clean: bool):
    findings, cleaned = [], []
    for path in paths:
        if path.suffix.lower() not in SERVICE_SUFFIXES:
            continue
        try:
            found = summarize(path.name, call(base, "/inspect", payload_for(path)))
            if found and clean and path.suffix.lower() in CLEANABLE_SUFFIXES:
                reply = call(base, "/clean", payload_for(path))
                if reply.get("ok") and reply.get("cleaned"):
                    write_cleaned(path, reply["cleaned"])
                    cleaned.append(str(path))
                    found = summarize(path.name, call(base, "/inspect", payload_for(path)))
            findings.extend(found)
        except (OSError, ValueError) as exc:
            findings.append(f"{path.name}: service: request failed ({exc})")
    return findings, cleaned


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", nargs="+", metavar="FILE")
    ap.add_argument("--clean", action="store_true",
                    help="replace a PDF the service flags with its cleaned bytes")
    ap.add_argument("--json", action="store_true", help="print one JSON object instead of lines")
    opts = ap.parse_args(argv)

    paths = [Path(f) for f in opts.files]
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        print(f"ERROR: not a file: {', '.join(missing)}", file=sys.stderr)
        return 2
    try:
        base = service_base(os.environ.get("WATERMARKS_SERVICE_URL") or DEFAULT_URL)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    local = []
    for path in paths:
        if path.suffix.lower() in TEXT_SUFFIXES:
            local.extend(local_findings(path))

    service = {"url": base, "status": "skipped", "findings": [], "cleaned": []}
    try:
        up = reachable(base)
    except Rejected as exc:
        print(
            f"ERROR: the service at {base} rejected the request ({exc}): "
            "set WATERMARKS_SERVER_API_KEY to the token it was started with",
            file=sys.stderr,
        )
        return 2
    if up:
        service["status"] = "checked"
        service["findings"], service["cleaned"] = check_service(base, paths, opts.clean)

    failed = bool(local or service["findings"])
    if opts.json:
        print(json.dumps({"ok": not failed, "local": local, "service": service}, indent=2))
        return 1 if failed else 0

    for line in local:
        print(f"FAIL invisible: {line}")
    if not local:
        print("ok   invisible: no hidden or non-standard characters")
    if service["status"] == "skipped":
        print(f"skip service: not running at {base}")
    else:
        for path in service["cleaned"]:
            print(f"     cleaned: {path}")
        for line in service["findings"]:
            print(f"FAIL {line}")
        if not service["findings"]:
            print(f"ok   service: no provenance marks reported ({base})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
