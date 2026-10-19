#!/usr/bin/env python3
"""Build a grounded context pack for one Model Mondays episode.

Usage:
  python3 context.py S4-E09            # markdown context pack to stdout
  python3 context.py s4-e09 --json     # same, as JSON
  python3 context.py next              # nearest upcoming episode

Everything printed comes from data/ — the agent must not add facts that are not here
(or in sources it fetches and cites explicitly).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

PLACEHOLDER_RX = re.compile(r"^https?://aka\.ms/model-mondays/?$", re.I)
CHAPTER_RX = re.compile(r"^\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*[-–—]\s*(.+?)\s*$")
URL_RX = re.compile(r"https?://[^\s)>\]]+")


def repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "data" / "episodes.json").exists():
            return parent
    sys.exit("Could not find data/episodes.json above this script.")


ROOT = repo_root()
DATA = ROOT / "data"


def normalize_id(value: str) -> str:
    m = re.match(r"^\s*s0*(\d+)\s*[-:_ ]?\s*e0*(\d+)\s*$", value, re.I)
    if not m:
        sys.exit(f"Unrecognized episode id '{value}'. Use forms like S4-E09, s4e9, s4-e09.")
    return f"s{int(m.group(1))}-e{int(m.group(2)):02d}"


def seconds(stamp: str) -> int:
    parts = [int(p) for p in stamp.split(":")]
    while len(parts) < 3:
        parts.insert(0, 0)
    h, m, s = parts
    return h * 3600 + m * 60 + s


def load():
    episodes = json.loads((DATA / "episodes.json").read_text())["episodes"]
    videos_path = DATA / "youtube" / "videos.json"
    videos = {v["id"]: v for v in json.loads(videos_path.read_text())["videos"]} if videos_path.exists() else {}
    return episodes, videos


def pick(episodes: list[dict], query: str) -> dict:
    if query.lower() in ("next", "upcoming"):
        today = dt.date.today().isoformat()
        upcoming = [e for e in episodes if e["date"] >= today]
        if not upcoming:
            sys.exit("No upcoming episode in data/.")
        return min(upcoming, key=lambda e: e["date"])
    eid = normalize_id(query)
    for e in episodes:
        if e["id"] == eid:
            return e
    sys.exit(f"Episode {eid} not found in data/episodes.json.")


def build(ep: dict, videos: dict) -> dict:
    yt = ep.get("youtube") or {}
    video = videos.get(yt.get("videoId"), {})
    description = video.get("description", "")
    video_url = yt.get("url", "")

    chapters = []
    for line in description.splitlines():
        m = CHAPTER_RX.match(line)
        if m:
            t = seconds(m.group(1))
            chapters.append({"time": m.group(1), "title": m.group(2),
                             "url": f"{video_url}&t={t}s" if video_url else ""})

    transcript_text, transcript_path = "", None
    if yt.get("transcript") and (DATA / yt["transcript"]).exists():
        transcript_path = f"data/{yt['transcript']}"
        transcript_text = (DATA / yt["transcript"]).read_text()

    sources, placeholders = [], []

    def add(url: str, label: str):
        url = url.rstrip(".,;")
        if PLACEHOLDER_RX.match(url):
            placeholders.append({"label": label, "url": url})
        elif url and url not in [s["url"] for s in sources]:
            sources.append({"label": label, "url": url})

    if video_url:
        add(video_url, "Episode recording (YouTube)")
    for c in chapters:
        if c["url"]:
            add(c["url"], f"Recording @ {c['time']} — {c['title']}")
    for h in ep.get("highlights") or []:
        add(h.get("url", ""), f"Highlight: {h.get('title', '')}")
    if ep.get("spotlight"):
        for r in ep["spotlight"].get("resources") or []:
            add(r.get("url", ""), f"Spotlight resource: {r.get('title', '')}")
    for k, v in (ep.get("links") or {}).items():
        add(v, f"Episode link: {k}")
    for url in URL_RX.findall(description):
        add(url, "Linked in video description")
    add(ep["source"]["page"], "Episode page (microsoft/model-mondays)")

    return {
        "id": ep["id"],
        "label": f"S{ep['season']}-E{ep['episode']}",
        "title": ep["title"],
        "date": ep["date"],
        "status": ep["status"],
        "host": ep.get("host", ""),
        "speakers": ep.get("speakers", []),
        "tags": ep.get("tags", []),
        "description": ep.get("description", ""),
        "video": {k: yt.get(k) for k in ("url", "title", "durationSec", "viewCount", "likeCount")} if yt else None,
        "videoDescription": description,
        "chapters": chapters,
        "transcript": {"path": transcript_path, "chars": len(transcript_text)} if transcript_path else None,
        "highlights": ep.get("highlights") or [],
        "spotlight": ep.get("spotlight"),
        "page": f"data/{ep['page']}",
        "allowedSources": sources,
        "placeholderLinksFound": placeholders,
    }


def to_markdown(ctx: dict) -> str:
    out = [f"# Context pack — {ctx['label']}: {ctx['title']}", ""]
    status = ctx["status"]
    if ctx["video"] and ctx["video"].get("durationSec") and status != "completed":
        status += " in source data, but the recording exists — treat as completed"
    out.append(f"- **Date:** {ctx['date']} ({status})")
    out.append(f"- **Host:** {ctx['host'] or 'unknown'}")
    out.append(f"- **Speakers:** {', '.join(ctx['speakers']) or 'not listed in data (check the banner/page; do not guess)'}")
    if ctx["video"]:
        v = ctx["video"]
        if v.get("durationSec"):
            out.append(f"- **Recording:** {v['url']} — {round(v['durationSec'] / 60)} min, {v['viewCount'] or '?'} views")
        else:
            out.append(f"- **Livestream (scheduled, not yet aired):** {v['url']}")
    out.append(f"- **Episode page:** {ctx['page']}")
    out += ["", "## Episode description", "", ctx["description"] or "_none_", ""]
    if ctx["chapters"]:
        out += ["## Chapters (from the YouTube description)", ""]
        out += [f"- [{c['time']}]({c['url']}) {c['title']}" for c in ctx["chapters"]]
        out.append("")
    if ctx["transcript"]:
        out += ["## Transcript", "", f"Available at `{ctx['transcript']['path']}` ({ctx['transcript']['chars']:,} chars, "
                "30-second blocks with [hh:mm:ss] stamps). Read it in full before writing.", ""]
    else:
        out += ["## Transcript", "", "**Not available yet.** Ground the recap in the description and chapters only. "
                "Say so in the recap's notes; do not invent quotes, numbers, or announcements.", ""]
    if ctx["videoDescription"]:
        out += ["## Full video description", "", "```text", ctx["videoDescription"].strip(), "```", ""]
    if ctx["highlights"]:
        out += ["## News Highlights already recorded for this episode", ""]
        out += [f"- {h.get('title')} — {h.get('url') or 'no url'}" for h in ctx["highlights"]]
        out.append("")
    out += ["## Allowed sources (cite only these, or URLs you fetch and verify)", ""]
    out += [f"- {s['label']}: {s['url']}" for s in ctx["allowedSources"]]
    if ctx["placeholderLinksFound"]:
        out += ["", "## ⚠ Placeholder links found in the source data (never reuse)", ""]
        out += [f"- {p['label']}: {p['url']}" for p in ctx["placeholderLinksFound"]]
    return "\n".join(out) + "\n"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("episode", help="Episode id (S4-E09, s4-e09) or 'next'")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    episodes, videos = load()
    ctx = build(pick(episodes, args.episode), videos)
    print(json.dumps(ctx, indent=2, ensure_ascii=False) if args.json else to_markdown(ctx))


if __name__ == "__main__":
    main()
