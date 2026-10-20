#!/usr/bin/env python3
"""Lint a generated recap/highlights/deck file against the episode's grounded sources.

Usage:
  python3 check.py content/s4-e09/recap.md --episode S4-E09

Errors (exit 1): placeholder links, empty link targets, missing "Sources" section.
Warnings: links not in the episode's allowed sources (may be fine if you fetched + verified them).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from context import PLACEHOLDER_RX, build, load, pick  # noqa: E402

LINK_RX = re.compile(r"\[([^\]]*)\]\(([^)\s]*)[^)]*\)")
BARE_RX = re.compile(r"(?<![(\[<])https?://[^\s)>\]\"']+")


def strip_time(url: str) -> str:
    return re.sub(r"[&?]t=\d+s?$", "", url)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file")
    p.add_argument("--episode", required=True)
    args = p.parse_args()

    text = Path(args.file).read_text()
    episodes, videos = load()
    ctx = build(pick(episodes, args.episode), videos)
    allowed = {strip_time(s["url"]) for s in ctx["allowedSources"]}

    errors, warnings = [], []
    links = [(label, url) for label, url in LINK_RX.findall(text)]
    linked_urls = {u for _, u in links}
    links += [("", u) for u in BARE_RX.findall(text) if u not in linked_urls]
    for label, url in links:
        url = url.rstrip(".,;")
        if not url:
            errors.append(f"empty link target for '{label}'")
        elif PLACEHOLDER_RX.match(url):
            errors.append(f"placeholder link: [{label}]({url})")
        elif url.startswith("http") and strip_time(url) not in allowed:
            warnings.append(f"not in allowed sources (verify): {url}")

    if not re.search(r"^#+\s*Sources\b|\bSources:", text, re.M | re.I):
        errors.append("missing a 'Sources' section (or `sources:` front matter)")

    for w in sorted(set(warnings)):
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"check: {len(links)} links, {len(errors)} errors, {len(set(warnings))} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
