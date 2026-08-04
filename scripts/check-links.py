#!/usr/bin/env python3
"""Verify relative markdown links in the plugin tree, and enforce the shared/ layering rule.

Usage: python3 scripts/check-links.py
Exit 0 = clean, 1 = problems (one per line).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = (ROOT / "plugins" / "resume-optimizer").resolve()
SHARED = (PLUGIN / "shared").resolve()
SKILLS = (PLUGIN / "skills").resolve()

LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
EXTERNAL = ("http://", "https://", "mailto:", "#")


def main() -> int:
    problems = []
    for md in sorted(PLUGIN.rglob("*.md")):
        for lineno, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            for target in LINK.findall(line):
                if target.startswith(EXTERNAL):
                    continue
                path = target.split("#", 1)[0]
                if not path:
                    continue
                resolved = (md.parent / path).resolve()
                where = f"{md.relative_to(ROOT)}:{lineno}"
                if not resolved.exists():
                    problems.append(f"{where}: broken link -> {target}")
                elif SHARED in md.parents and SKILLS in resolved.parents:
                    problems.append(
                        f"{where}: layering violation, shared/ must not link into skills/ -> {target}"
                    )

    for problem in problems:
        print(problem)
    print(f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
