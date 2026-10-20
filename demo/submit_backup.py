#!/usr/bin/env python3
"""Submit a pre-generated backup (demo/backups/<episode>/<kind>.*) to the site's review queue.

Usage:
  python demo/submit_backup.py s4-e09 recap
  python demo/submit_backup.py s4-e11 deck --site http://localhost:8000

Reads MM_WRITE_KEY from the environment if the site requires it.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent


def front_matter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {}, text
    meta, sources, in_sources = {}, [], False
    for line in m.group(1).splitlines():
        if line.startswith("sources:"):
            in_sources = True
            continue
        if in_sources and line.strip().startswith("- "):
            sources.append(line.strip()[2:].strip())
            continue
        in_sources = False
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"')
    meta["sources"] = sources
    return meta, m.group(2)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("episode")
    p.add_argument("kind", choices=["recap", "highlights", "deck"])
    p.add_argument("--site", default=os.environ.get("MM_SITE_URL", "http://localhost:8000"))
    args = p.parse_args()

    folder = HERE / "backups" / args.episode
    md_path = folder / f"{args.kind}.md"
    if not md_path.exists():
        sys.exit(f"No backup at {md_path}")
    meta, body = front_matter(md_path.read_text())
    html_path = folder / f"{args.kind}.html"
    sources = meta.get("sources") or sorted(set(re.findall(r"https?://[^\s)\"'<>]+", body)))[:20]

    payload = {
        "episode_id": args.episode,
        "kind": args.kind,
        "title": meta.get("title") or f"{args.episode.upper()} {args.kind} (backup)",
        "content_markdown": md_path.read_text() if args.kind == "deck" else body,
        "content_html": html_path.read_text() if html_path.exists() else None,
        "author_agent": f"{meta.get('generated_by', 'mm-' + args.kind)} (backup)",
        "sources": sources,
    }
    req = urllib.request.Request(f"{args.site.rstrip('/')}/api/drafts", data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"}, method="POST")
    if os.environ.get("MM_WRITE_KEY"):
        req.add_header("Authorization", f"Bearer {os.environ['MM_WRITE_KEY']}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.load(resp)
    print(f"submitted {args.kind} for {args.episode}: draft {result.get('id') or result}")
    print(f"review at {args.site.rstrip('/')}/studio")


if __name__ == "__main__":
    main()
