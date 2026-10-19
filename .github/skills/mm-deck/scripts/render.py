#!/usr/bin/env python3
"""Render a Marp deck with the talk theme, and optionally inline local images.

Usage:
  python3 render.py slides/episodes/s4-e11.md                 # -> slides/episodes/s4-e11.html
  python3 render.py slides/episodes/s4-e11.md --standalone    # images inlined as data URIs (for the site)
  python3 render.py slides/episodes/s4-e11.md --png           # first-slide PNG preview (needs Chrome/Edge)

Uses `marp` if installed, otherwise `npx @marp-team/marp-cli`.
"""

from __future__ import annotations

import argparse
import base64
import mimetypes
import re
import shutil
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "slides" / ".marprc.yml").exists():
            return parent
    sys.exit("Could not find slides/.marprc.yml above this script.")


def marp_cmd() -> list[str]:
    if shutil.which("marp"):
        return ["marp"]
    if shutil.which("npx"):
        return ["npx", "--yes", "@marp-team/marp-cli@latest"]
    sys.exit("Marp CLI not found. Install with: npm install -g @marp-team/marp-cli")


def inline_images(html: str, base: Path) -> str:
    def repl(m: re.Match) -> str:
        attr, quote, src = m.group(1), m.group(2), m.group(3)
        if src.startswith(("http:", "https:", "data:")):
            return m.group(0)
        path = (base / src).resolve()
        if not path.exists():
            return m.group(0)
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if path.suffix == ".svg":
            mime = "image/svg+xml"
        data = base64.b64encode(path.read_bytes()).decode()
        return f'{attr}={quote}data:{mime};base64,{data}{quote}'

    return re.sub(r'(src)=(["\'])([^"\']+)\2', repl, html)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("deck")
    p.add_argument("--standalone", action="store_true", help="inline local images into the HTML")
    p.add_argument("--png", action="store_true", help="also render a PNG of the first slide")
    p.add_argument("-o", "--output")
    args = p.parse_args()

    root = repo_root()
    deck = Path(args.deck).resolve()
    out = Path(args.output).resolve() if args.output else deck.with_suffix(".html")
    base = [*marp_cmd(), "--config-file", str(root / "slides" / ".marprc.yml"), str(deck)]

    subprocess.run([*base, "--html", "-o", str(out)], check=True)
    if args.standalone:
        out.write_text(inline_images(out.read_text(), deck.parent))
    print(f"render: {out.relative_to(root) if out.is_relative_to(root) else out}")

    if args.png:
        png = deck.with_suffix(".png")
        subprocess.run([*base, "--image", "png", "-o", str(png)], check=True)
        print(f"render: {png.relative_to(root)}")


if __name__ == "__main__":
    main()
