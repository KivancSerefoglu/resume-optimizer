#!/usr/bin/env python3
"""Derive optimized-resume.md from optimized-resume.html.

The résumé is authored once, as HTML filling resume-template.html. This converts
that HTML to markdown so the two deliverables cannot drift — SKILL.md requires
them to match exactly, and retyping the résumé is both a token cost and a chance
to introduce a discrepancy.

Handles the template's fixed class vocabulary only. Anything unrecognized falls
through to its plain text rather than being dropped, and the built-in check
asserts that no visible text was lost in translation.

Usage:  python3 html-to-md.py optimized-resume.html [-o optimized-resume.md]
Exits non-zero if any visible text from the HTML is missing from the markdown.
"""
import argparse
import re
import sys
from html.parser import HTMLParser

VOID = {"br", "img", "meta", "link", "hr", "input", "area", "base", "col"}
SKIP = {"style", "script", "head", "title"}


class Node:
    __slots__ = ("tag", "attrs", "children")

    def __init__(self, tag, attrs=None):
        self.tag = tag
        self.attrs = attrs or {}
        self.children = []

    def cls(self):
        return self.attrs.get("class", "").split()

    def find(self, tag=None, cls=None):
        """Depth-first descendants matching tag and/or class."""
        for c in self.children:
            if isinstance(c, Node):
                if (tag is None or c.tag == tag) and (cls is None or cls in c.cls()):
                    yield c
                yield from c.find(tag, cls)


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs))
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(Node(tag, dict(attrs)))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if self.stack[-1].tag not in SKIP:
            self.stack[-1].children.append(data)


def squeeze(s):
    return re.sub(r"\s+", " ", s).strip()


def text(node):
    """Visible text, with element boundaries treated as word separators.

    `<span>Acme</span><span>Boston</span>` carries no whitespace when written on
    one line, and concatenating it would invent the word "AcmeBoston". Every
    caller squeezes or normalizes, so the extra spaces are free.
    """
    if isinstance(node, str):
        return node
    if node.tag in SKIP:
        return ""
    return "".join(
        c if isinstance(c, str) else f" {text(c)} " for c in node.children
    )


def inline(node):
    """Markdown for inline content: strong, em, links."""
    if isinstance(node, str):
        return node
    if node.tag in SKIP:
        return ""
    if node.tag == "br":
        return " "
    inner = "".join(inline(c) for c in node.children)
    if node.tag in ("strong", "b"):
        return f"**{squeeze(inner)}**" if squeeze(inner) else ""
    if node.tag in ("em", "i"):
        return f"*{squeeze(inner)}*" if squeeze(inner) else ""
    if node.tag == "a":
        href, label = node.attrs.get("href", ""), squeeze(inner)
        if not href or not label:
            return label
        # A link whose label already is the URL reads worse as [url](url).
        return label if href.rstrip("/").endswith(label.rstrip("/")) else f"[{label}]({href})"
    return inner


def entry_lines(entry):
    """Two-line entry header -> markdown lines, preserving bold/italic roles."""
    out = []
    for row in entry.find(cls="entry-line"):
        spans = [s for s in row.children if isinstance(s, Node) and s.tag == "span"]
        styled = []
        for span in spans:
            raw = squeeze(inline(span))
            if not raw:
                continue
            c = span.cls()
            if "entry-org" in c:
                styled.append(f"**{raw}**")
            elif "entry-title" in c:
                styled.append(f"*{raw}*")
            else:
                styled.append(raw)
        if styled:
            out.append(" — ".join(styled))
    return out


def convert(html):
    t = Tree()
    t.feed(html)
    main = next(t.root.find("main"), t.root)
    md = []

    for name in main.find(cls="name"):
        md += [f"# {squeeze(inline(name))}", ""]
        break
    for contact in main.find(cls="contact"):
        md += [squeeze(inline(contact)), ""]
        break

    for sec in main.find(cls="section"):
        for h2 in sec.find("h2"):
            md += [f"## {squeeze(text(h2))}", ""]
            break
        for child in sec.children:
            if not isinstance(child, Node):
                continue
            if "entry" in child.cls():
                md += entry_lines(child)
                for note in child.find(cls="entry-note"):
                    md += ["", squeeze(inline(note))]
                items = [squeeze(inline(li)) for li in child.find("li")]
                items = [i for i in items if i]
                if items:
                    md.append("")
                    md += [f"- {i}" for i in items]
                md.append("")
            elif child.tag == "ul":
                md += [f"- {squeeze(inline(li))}" for li in child.find("li")]
                md.append("")
            elif "skills-line" in child.cls():
                md.append(squeeze(inline(child)))
            elif child.tag in ("p", "div") and squeeze(text(child)):
                md += [squeeze(inline(child)), ""]
        if md and md[-1] != "":
            md.append("")

    out = "\n".join(md)
    return re.sub(r"\n{3,}", "\n\n", out).strip() + "\n"


def norm(s):
    """Comparable word tokens: drop punctuation and case.

    Both sides must be normalized the same way — stripping markdown syntax from
    only the output would flag words that legitimately contain those characters
    (`course-scheduling`, `(2023).`) as lost.
    """
    return [w for w in re.sub(r"[^0-9A-Za-zÀ-ÿ]+", " ", s).lower().split() if w]


def missing_text(html, md):
    """Every visible word in the HTML must survive into the markdown."""
    t = Tree()
    t.feed(html)
    main = next(t.root.find("main"), t.root)
    have = set(norm(md))
    return [w for w in norm(text(main)) if w not in have]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("html", help="filled optimized-resume.html")
    ap.add_argument("-o", "--out", help="output path (default: alongside input)")
    ap.add_argument("--stdout", action="store_true", help="print instead of writing")
    args = ap.parse_args()

    html = open(args.html, encoding="utf-8").read()
    md = convert(html)

    lost = missing_text(html, md)
    if lost:
        print(f"ERROR: {len(lost)} token(s) from the HTML are missing in the markdown:",
              file=sys.stderr)
        print("  " + " ".join(lost[:20]), file=sys.stderr)
        return 1

    if args.stdout:
        sys.stdout.write(md)
    else:
        out = args.out or re.sub(r"\.html?$", ".md", args.html)
        open(out, "w", encoding="utf-8").write(md)
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
