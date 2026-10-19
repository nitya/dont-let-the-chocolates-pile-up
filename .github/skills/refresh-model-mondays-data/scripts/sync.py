#!/usr/bin/env python3
"""Sync Model Mondays livestream data into this repo's data/ folder.

Subcommands:
  repo     Import seasons, episodes, episode pages and banners from microsoft/model-mondays.
  youtube  Refresh playlist stats, descriptions and transcripts from the YouTube playlist.
  link     Re-match YouTube videos to episodes (uses data/youtube/overrides.json).
  check    Validate data/ integrity.
  all      repo + youtube + check.

Optional environment variables (never commit them):
  YOUTUBE_API_KEY   YouTube Data API v3 key -> descriptions, likes, comments, publish dates.
  YT_PROXY_URL      HTTP(S) proxy for transcript requests (e.g. residential proxy).
  YT_COOKIES_FILE   Netscape cookies.txt for yt-dlp fallback (metadata + captions).
"""

from __future__ import annotations

import argparse
import datetime as dt
import io
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

SOURCE_REPO = "https://github.com/microsoft/model-mondays"
SOURCE_SLUG = "microsoft/model-mondays"
PLAYLIST_ID = "PLmsFUfdnGr3wzz6a4E-Szksg92JPng-AL"
PLAYLIST_URL = f"https://www.youtube.com/playlist?list={PLAYLIST_ID}"

BANNER_SIZE = (1280, 720)
BANNER_QUALITY = 80

SECTION_PREFIXES = (
    "news highlights", "tech spotlight", "summary", "overview", "links", "resources",
    "customer story", "study corner", "key features", "guests", "speaker", "agenda",
)


def find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists():
            return parent
    return Path.cwd()


ROOT = find_repo_root()
DATA = ROOT / "data"
YT_DIR = DATA / "youtube"


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path, default=None):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return default


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def strip_md(text: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<br\s*/?>", " ", text)
    text = re.sub(r"[*_`]+", "", text)
    return re.sub(r"\s+", " ", text).strip()


# --------------------------------------------------------------------------- repo import


def get_source(source: str | None, ref: str) -> tuple[Path, str, Path | None]:
    if source:
        src = Path(source).resolve()
        sha = subprocess.run(["git", "-C", str(src), "rev-parse", "HEAD"],
                             capture_output=True, text=True).stdout.strip() or ref
        return src, sha, None
    tmp = Path(tempfile.mkdtemp(prefix="mm-src-"))
    subprocess.run(["git", "clone", "--depth", "1", "--branch", ref, "-q", SOURCE_REPO, str(tmp)],
                   check=True)
    sha = subprocess.run(["git", "-C", str(tmp), "rev-parse", "HEAD"],
                         capture_output=True, text=True, check=True).stdout.strip()
    return tmp, sha, tmp


def split_sections(lines: list[str]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {"_preamble": []}
    current = "_preamble"
    for line in lines:
        m = re.match(r"^#{1,4}\s+(.+?)\s*$", line)
        if m:
            current = strip_md(m.group(1)).lower()
            sections.setdefault(current, [])
            continue
        sections[current].append(line)
    return sections


def section(sections: dict[str, list[str]], prefix: str) -> list[str]:
    for name, body in sections.items():
        if name.startswith(prefix):
            return body
    return []


def field(lines: list[str], name: str) -> str:
    rx = re.compile(rf"^\*\*{name}s?:\*\*\s*(.*)$", re.I)
    for line in lines:
        m = rx.match(line.strip())
        if m:
            return m.group(1).strip()
    return ""


def list_after(lines: list[str], name: str) -> list[str]:
    out, active = [], False
    for line in lines:
        s = line.strip()
        if re.match(rf"^\*\*{name}s?:\*\*\s*$", s, re.I):
            active = True
            continue
        if active:
            if re.match(r"^([-*]|\d+\.)\s+", s):
                out.append(re.sub(r"^([-*]|\d+\.)\s+", "", s))
            elif s and out:
                break
    return out


def first_paragraph(lines: list[str]) -> str:
    para: list[str] = []
    for line in lines:
        s = line.strip()
        if not s or s == "---" or s.startswith(("![", "<br")):
            if para:
                break
            continue
        if s.startswith(("**", "-", "*", "|", "1.", "_")) and not para:
            continue
        para.append(s)
    return strip_md(" ".join(para))


def parse_link_item(item: str) -> dict:
    m = re.match(r"^\[([^\]]+)\]\(([^)]+)\)\s*(?:[-–—:]\s*(.*))?$", item.strip())
    if m:
        return {"title": strip_md(m.group(1)), "url": m.group(2).strip(),
                "description": strip_md(m.group(3) or "")}
    return {"title": strip_md(item), "url": "", "description": ""}


def absolutize(url: str, sha: str, page_dir: str = "docs/model-mondays") -> str:
    if not url or re.match(r"^[a-z]+:", url) or url.startswith("#"):
        return url
    if url.startswith("docs/") or url.startswith("data/"):
        path = url
    else:
        path = posixpath.normpath(posixpath.join(page_dir, url))
    return f"https://github.com/{SOURCE_SLUG}/blob/{sha}/{path}"


def raw_url(path: str, sha: str) -> str:
    return f"https://raw.githubusercontent.com/{SOURCE_SLUG}/{sha}/{path}"


def compress_banner(src: Path, dest: Path) -> dict:
    from PIL import Image

    dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im = im.convert("RGB")
        im.thumbnail(BANNER_SIZE, Image.LANCZOS)
        im.save(dest, "WEBP", quality=BANNER_QUALITY, method=6)
        return {"width": im.width, "height": im.height}


def resolve_people(values, speakers_by_id: dict) -> list[str]:
    if not values:
        return []
    if isinstance(values, str):
        values = [values]
    out = []
    for v in values:
        if isinstance(v, dict):
            v = v.get("name") or v.get("id") or ""
        v = speakers_by_id.get(v, {}).get("name", v) if isinstance(v, str) else v
        if v:
            out.append(strip_md(v))
    return out


def dedupe(items: list[str]) -> list[str]:
    seen, out = set(), []
    for i in items:
        key = re.split(r"\s[—–-]\s", i)[0].strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(i)
    return out


def parse_episode_page(path: Path, record: dict, speakers_by_id: dict, sha: str) -> dict:
    m = re.match(r"(\d{4}-\d{2}-\d{2})-s(\d+)-e(\d+)\.md$", path.name)
    date, season, episode = m.group(1), int(m.group(2)), int(m.group(3))
    eid = f"s{season}-e{episode:02d}"
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    sections = split_sections(lines)

    banner_m = re.search(r"!\[[^\]]*\]\((\.\./assets/model-mondays/[^)]+)\)", text)
    banner_src = posixpath.normpath(posixpath.join("docs/model-mondays", banner_m.group(1))) if banner_m else ""

    heading_title = ""
    for line in lines:
        hm = re.match(r"^#{1,2}\s+(.+?)\s*$", line)
        if hm:
            candidate = strip_md(hm.group(1))
            if not candidate.lower().startswith(SECTION_PREFIXES):
                heading_title = candidate
                break

    spot = section(sections, "tech spotlight")
    spotlight_title = strip_md(field(spot, "Title"))
    if not spotlight_title:
        for name in sections:
            if name.startswith("tech spotlight:"):
                spotlight_title = name.split(":", 1)[1].strip().title()
    title = record.get("title") or heading_title or spotlight_title or f"Season {season} Episode {episode}"

    all_lines = lines
    host = strip_md(field(all_lines, "Host")) or ", ".join(resolve_people(record.get("host"), speakers_by_id))

    speakers = resolve_people(record.get("speakers"), speakers_by_id)
    speakers += [strip_md(g) for g in list_after(all_lines, "Guest")]
    speakers += [strip_md(field(spot, "Speaker"))] if field(spot, "Speaker") else []
    speakers += [name.split(":", 1)[1].strip().title() for name in sections
                 if re.match(r"^speaker \d+:", name)]
    if record.get("spotlight"):
        speakers += resolve_people(record["spotlight"].get("speakers"), speakers_by_id)
    speakers = dedupe([s for s in speakers if s])

    description = (record.get("description")
                   or first_paragraph(section(sections, "overview"))
                   or first_paragraph(section(sections, "summary"))
                   or strip_md(field(spot, "Description"))
                   or first_paragraph(sections.get(heading_title.lower(), []))
                   or first_paragraph(sections["_preamble"]))

    highlights = record.get("highlights") or [
        parse_link_item(re.sub(r"^([-*]|\d+\.)\s+", "", line.strip()))
        for line in section(sections, "news highlights")
        if re.match(r"^\s*([-*]|\d+\.)\s+\[", line)
    ]

    spotlight = None
    if spot or record.get("spotlight"):
        rs = record.get("spotlight") or {}
        resources = rs.get("resources") or [parse_link_item(i) for i in list_after(spot, "Resource")]
        spotlight = {
            "title": rs.get("title") or spotlight_title,
            "speakers": resolve_people(rs.get("speakers"), speakers_by_id) or
                        ([strip_md(field(spot, "Speaker"))] if field(spot, "Speaker") else []),
            "description": rs.get("description") or strip_md(field(spot, "Description")) or first_paragraph(spot),
            "resources": resources,
        }

    cs_lines = section(sections, "customer story")
    customer_story = record.get("customerStory") or (
        {"title": strip_md(field(cs_lines, "Title")), "company": strip_md(field(cs_lines, "Company")),
         "description": strip_md(field(cs_lines, "Description"))} if cs_lines else None)

    links: dict[str, str] = {}
    for item in list_after(all_lines, "Link"):
        li = parse_link_item(item)
        if li["url"]:
            links[li["title"].lower()] = absolutize(li["url"], sha)
    for k, v in (record.get("links") or {}).items():
        if v and k.lower() not in links:
            links[k.lower()] = absolutize(v, sha, page_dir="")

    tags = record.get("tags") or [t.strip() for t in strip_md(field(all_lines, "Tag")).split(",") if t.strip()]
    status = record.get("status") or ("completed" if date < dt.date.today().isoformat() else "scheduled")

    return {
        "id": eid,
        "season": season,
        "episode": episode,
        "date": date,
        "time": record.get("time", ""),
        "title": title,
        "description": description,
        "host": host,
        "speakers": speakers,
        "status": status,
        "tags": tags,
        "banner": f"banners/S{season}-E{episode}.webp" if banner_src else "",
        "page": f"episodes/{eid}.md",
        "highlights": highlights,
        "spotlight": spotlight,
        "customerStory": customer_story,
        "studyCorner": record.get("studyCorner") or strip_md(field(all_lines, "Study Corner")) or None,
        "links": links,
        "source": {
            "page": f"https://github.com/{SOURCE_SLUG}/blob/{sha}/docs/model-mondays/{path.name}",
            "banner": raw_url(banner_src, sha) if banner_src else "",
        },
        "_bannerSrc": banner_src,
        "_text": text,
    }


def rewrite_page(ep: dict, sha: str) -> str:
    text = ep["_text"]
    banner_rel = posixpath.relpath(ep["_bannerSrc"], "docs/model-mondays") if ep["_bannerSrc"] else None

    def img(m):
        alt, url = m.group(1), m.group(2)
        if banner_rel and url == banner_rel:
            return f"![{alt}](../{ep['banner']})"
        if re.match(r"^[a-z]+:", url):
            return m.group(0)
        return f"![{alt}]({raw_url(posixpath.normpath(posixpath.join('docs/model-mondays', url)), sha)})"

    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", img, text)
    text = re.sub(r"(?<!!)\[([^\]]+)\]\((\.\.?/[^)]+)\)",
                  lambda m: f"[{m.group(1)}]({absolutize(m.group(2), sha)})", text)
    header = (f"<!-- Imported from {ep['source']['page']} (MIT, (c) Microsoft Corporation). "
              f"Regenerate with the refresh-model-mondays-data skill; local edits are overwritten. -->\n\n")
    return header + text


def cmd_repo(args) -> None:
    src, sha, tmp = get_source(args.source, args.ref)
    try:
        speakers = read_json(src / "data/speakers.json", [])
        speakers_by_id = {s["id"]: s for s in speakers if isinstance(s, dict) and "id" in s}
        records = {r["id"]: r for r in read_json(src / "data/livestreams.json", [])}

        seasons = read_json(src / "data/seasons.json", [])
        for s in seasons:
            s["banner"] = ""
            s.pop("totalAMAs", None)

        pages = sorted((src / "docs/model-mondays").glob("*-s*-e*.md"))
        episodes = []
        banners_dir = DATA / "banners"
        if banners_dir.exists():
            shutil.rmtree(banners_dir)
        episodes_dir = DATA / "episodes"
        if episodes_dir.exists():
            shutil.rmtree(episodes_dir)
        episodes_dir.mkdir(parents=True)

        before = after = 0
        for page in pages:
            m = re.search(r"-s(\d+)-e(\d+)\.md$", page.name)
            rid = f"s{int(m.group(1))}-e{int(m.group(2)):02d}"
            ep = parse_episode_page(page, records.get(rid, {}), speakers_by_id, sha)
            if ep["_bannerSrc"] and (src / ep["_bannerSrc"]).exists():
                before += (src / ep["_bannerSrc"]).stat().st_size
                compress_banner(src / ep["_bannerSrc"], DATA / ep["banner"])
                after += (DATA / ep["banner"]).stat().st_size
            elif ep["banner"]:
                print(f"  ! banner missing for {ep['id']}: {ep['_bannerSrc']}")
                ep["banner"] = ""
            (DATA / ep["page"]).write_text(rewrite_page(ep, sha), encoding="utf-8")
            ep.pop("_bannerSrc")
            ep.pop("_text")
            episodes.append(ep)

        old = {e["id"]: e for e in read_json(DATA / "episodes.json", {}).get("episodes", [])}
        for ep in episodes:
            ep["youtube"] = old.get(ep["id"], {}).get("youtube")

        counts = {}
        for ep in episodes:
            counts[ep["season"]] = counts.get(ep["season"], 0) + 1
        for s in seasons:
            s["episodeCount"] = counts.get(s["season"], 0)

        source_meta = {"repo": SOURCE_REPO, "commit": sha, "importedAt": now_iso(), "license": "MIT"}
        write_json(DATA / "seasons.json", {"source": source_meta, "seasons": seasons})
        write_json(DATA / "episodes.json", {"source": source_meta, "episodes": episodes})
        lic = src / "LICENSE"
        if lic.exists():
            shutil.copy(lic, DATA / "LICENSE-model-mondays.txt")
        print(f"repo: {len(episodes)} episodes, {len(seasons)} seasons from {sha[:7]}; "
              f"banners {before/1e6:.1f} MB -> {after/1e6:.1f} MB")
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)
    link_videos()


# --------------------------------------------------------------------------- youtube


class Blocked(Exception):
    pass


def iso_duration(value: str) -> int | None:
    m = re.match(r"^P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$", value or "")
    if not m:
        return None
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


def api_get(endpoint: str, **params) -> dict:
    params["key"] = os.environ["YOUTUBE_API_KEY"]
    url = f"https://www.googleapis.com/youtube/v3/{endpoint}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.load(resp)


def fetch_with_api() -> list[dict]:
    ids, token = [], None
    while True:
        params = {"part": "contentDetails", "playlistId": PLAYLIST_ID, "maxResults": 50}
        if token:
            params["pageToken"] = token
        page = api_get("playlistItems", **params)
        ids += [i["contentDetails"]["videoId"] for i in page.get("items", [])]
        token = page.get("nextPageToken")
        if not token:
            break
    videos = []
    for i in range(0, len(ids), 50):
        batch = api_get("videos", part="snippet,statistics,contentDetails,liveStreamingDetails",
                        id=",".join(ids[i:i + 50]))
        by_id = {v["id"]: v for v in batch.get("items", [])}
        for vid in ids[i:i + 50]:
            v = by_id.get(vid)
            if not v:
                continue
            sn, st, live = v["snippet"], v.get("statistics", {}), v.get("liveStreamingDetails", {})
            videos.append({
                "id": vid,
                "title": sn.get("title", ""),
                "description": sn.get("description", ""),
                "publishedAt": sn.get("publishedAt", ""),
                "scheduledStartTime": live.get("scheduledStartTime", ""),
                "actualStartTime": live.get("actualStartTime", ""),
                "liveStatus": sn.get("liveBroadcastContent", "none"),
                "durationSec": iso_duration(v.get("contentDetails", {}).get("duration", "")),
                "viewCount": int(st["viewCount"]) if "viewCount" in st else None,
                "likeCount": int(st["likeCount"]) if "likeCount" in st else None,
                "commentCount": int(st["commentCount"]) if "commentCount" in st else None,
                "thumbnail": (sn.get("thumbnails", {}).get("maxres") or sn.get("thumbnails", {}).get("high") or {}).get("url", ""),
                "detailSource": "youtube-data-api",
            })
    return videos


def ytdlp_opts(**extra) -> dict:
    opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    if os.environ.get("YT_COOKIES_FILE"):
        opts["cookiefile"] = os.environ["YT_COOKIES_FILE"]
    opts.update(extra)
    return opts


def fetch_flat() -> list[dict]:
    from yt_dlp import YoutubeDL

    with YoutubeDL(ytdlp_opts(extract_flat="in_playlist")) as ydl:
        info = ydl.extract_info(PLAYLIST_URL, download=False)
    videos = []
    for e in info.get("entries", []):
        videos.append({
            "id": e["id"],
            "title": e.get("title", ""),
            "durationSec": e.get("duration"),
            "viewCount": e.get("view_count"),
            "liveStatus": "upcoming" if e.get("duration") is None else "none",
        })
    return videos


def fetch_detail_ytdlp(video_id: str) -> dict:
    from yt_dlp import YoutubeDL
    from yt_dlp.utils import DownloadError

    try:
        with YoutubeDL(ytdlp_opts()) as ydl:
            d = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
    except DownloadError as exc:
        if "confirm you" in str(exc) or "Sign in" in str(exc):
            raise Blocked(str(exc)) from exc
        raise
    ts = d.get("release_timestamp") or d.get("timestamp")
    return {
        "description": d.get("description", ""),
        "publishedAt": dt.datetime.fromtimestamp(ts, dt.timezone.utc).isoformat() if ts else "",
        "durationSec": d.get("duration"),
        "viewCount": d.get("view_count"),
        "likeCount": d.get("like_count"),
        "commentCount": d.get("comment_count"),
        "thumbnail": d.get("thumbnail", ""),
        "detailSource": "yt-dlp",
    }


def fetch_transcript(video_id: str) -> dict:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api._errors import IpBlocked, RequestBlocked

    proxy = os.environ.get("YT_PROXY_URL")
    if proxy:
        from youtube_transcript_api.proxies import GenericProxyConfig
        api = YouTubeTranscriptApi(proxy_config=GenericProxyConfig(http_url=proxy, https_url=proxy))
    else:
        api = YouTubeTranscriptApi()
    try:
        listing = api.list(video_id)
        try:
            tr = listing.find_manually_created_transcript(["en", "en-US", "en-GB"])
        except Exception:
            tr = listing.find_transcript(["en", "en-US", "en-GB"])
        fetched = tr.fetch()
    except (RequestBlocked, IpBlocked) as exc:
        raise Blocked(str(exc)) from exc
    return {
        "videoId": video_id,
        "language": tr.language_code,
        "isGenerated": tr.is_generated,
        "fetchedAt": now_iso(),
        "segments": [{"start": round(s.start, 2), "duration": round(s.duration, 2), "text": s.text}
                     for s in fetched.snippets],
    }


def transcript_text(tr: dict, every: int = 30) -> str:
    out, bucket, bucket_start = [], [], None
    for seg in tr["segments"]:
        if bucket_start is None:
            bucket_start = seg["start"]
        bucket.append(seg["text"].replace("\n", " "))
        if seg["start"] - bucket_start >= every:
            out.append(f"[{fmt_ts(bucket_start)}] {' '.join(bucket)}")
            bucket, bucket_start = [], None
    if bucket:
        out.append(f"[{fmt_ts(bucket_start)}] {' '.join(bucket)}")
    return "\n".join(out) + "\n"


def fmt_ts(sec: float) -> str:
    sec = int(sec)
    return f"{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


def cmd_youtube(args) -> None:
    store_path = YT_DIR / "videos.json"
    store = read_json(store_path, {"playlistId": PLAYLIST_ID, "playlistUrl": PLAYLIST_URL, "videos": []})
    previous = {v["id"]: v for v in store.get("videos", [])}

    if os.environ.get("YOUTUBE_API_KEY"):
        listing, mode = fetch_with_api(), "youtube-data-api"
    else:
        listing, mode = fetch_flat(), "yt-dlp-flat"
    print(f"youtube: {len(listing)} playlist videos via {mode}")

    videos = []
    for v in listing:
        merged = dict(previous.get(v["id"], {}))
        merged.update({k: val for k, val in v.items() if val not in (None, "")})
        merged["url"] = f"https://www.youtube.com/watch?v={v['id']}"
        merged["statsFetchedAt"] = now_iso()
        videos.append(merged)

    if mode != "youtube-data-api" and not args.no_details:
        blocked = False
        for v in videos:
            if blocked or (v.get("description") and not args.force):
                continue
            try:
                v.update({k: val for k, val in fetch_detail_ytdlp(v["id"]).items() if val not in (None, "")})
            except Blocked:
                blocked = True
                print("  ! YouTube blocked per-video metadata from this IP. "
                      "Set YOUTUBE_API_KEY (preferred) or YT_COOKIES_FILE, or run locally.")
            except Exception as exc:  # noqa: BLE001
                print(f"  ! metadata failed for {v['id']}: {exc}")

    if not args.no_transcripts:
        tdir = YT_DIR / "transcripts"
        tdir.mkdir(parents=True, exist_ok=True)
        got = skipped = 0
        for v in videos:
            jpath = tdir / f"{v['id']}.json"
            if v.get("liveStatus") == "upcoming" or (jpath.exists() and not args.force):
                if jpath.exists():
                    v["transcript"] = f"youtube/transcripts/{v['id']}.txt"
                continue
            try:
                tr = fetch_transcript(v["id"])
            except Blocked:
                print("  ! YouTube blocked transcript requests from this IP. "
                      "Run this refresh from a local machine, or set YT_PROXY_URL.")
                break
            except Exception as exc:  # noqa: BLE001
                skipped += 1
                print(f"  - no transcript for {v['id']}: {type(exc).__name__}")
                continue
            write_json(jpath, tr)
            (tdir / f"{v['id']}.txt").write_text(transcript_text(tr), encoding="utf-8")
            v["transcript"] = f"youtube/transcripts/{v['id']}.txt"
            got += 1
        print(f"  transcripts fetched: {got}, unavailable: {skipped}")

    store.update({"playlistId": PLAYLIST_ID, "playlistUrl": PLAYLIST_URL, "fetchedAt": now_iso(),
                  "listingSource": mode, "videos": videos})
    write_json(store_path, store)
    overrides = YT_DIR / "overrides.json"
    if not overrides.exists():
        write_json(overrides, {"_comment": "Map episode id -> YouTube video id to fix or force a match. "
                                           "Use null to mark an episode as having no recording.",
                               "matches": {}})
    link_videos()


# --------------------------------------------------------------------------- linking

STOP = {"model", "models", "mondays", "monday", "the", "and", "with", "in", "on", "for", "of", "a", "an",
        "to", "spotlight", "hands", "microsoft", "foundry", "azure", "ai", "new", "what", "whats", "s",
        "&", "+", "-", "–", "into", "your", "from", "building", "build"}


def tokens(text: str) -> set[str]:
    text = re.sub(r"open\s+ai", "openai", (text or "").lower())
    words = re.findall(r"[a-z0-9]+", text)
    return {w.rstrip("s") if len(w) > 3 else w for w in words if w not in STOP}


def similarity(ep: dict, video: dict) -> tuple[float, bool]:
    """Return (score, date_confirmed). Title Jaccard in [0,1]; +1 when stream date is within 2 days."""
    ep_text = " ".join([ep["title"], (ep.get("spotlight") or {}).get("title", "")])
    a, b = tokens(ep_text), tokens(video.get("title", ""))
    score = len(a & b) / len(a | b) if a and b else 0.0
    vdate = (video.get("actualStartTime") or video.get("scheduledStartTime") or video.get("publishedAt") or "")[:10]
    if not vdate:
        return score, False
    delta = abs((dt.date.fromisoformat(vdate) - dt.date.fromisoformat(ep["date"])).days)
    if delta <= 2:
        return score + 1.0, True
    return score + (0.3 if delta <= 7 else -0.5), False


def link_videos() -> None:
    ep_path = DATA / "episodes.json"
    doc = read_json(ep_path)
    store = read_json(YT_DIR / "videos.json")
    if not doc or not store:
        return
    episodes, videos = doc["episodes"], {v["id"]: v for v in store["videos"]}
    overrides = (read_json(YT_DIR / "overrides.json", {}) or {}).get("matches", {})
    yt_rx = re.compile(r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/live/)([A-Za-z0-9_-]{11})")

    assigned: dict[str, tuple[str, str, float]] = {}
    used: set[str] = set()
    for ep in episodes:
        if ep["id"] in overrides:
            vid = overrides[ep["id"]]
            if vid:
                assigned[ep["id"]] = (vid, "override", 1.0)
                used.add(vid)
            else:
                assigned[ep["id"]] = (None, "override", 1.0)
    for ep in episodes:
        if ep["id"] in assigned:
            continue
        for url in ep.get("links", {}).values():
            m = yt_rx.search(url or "")
            if m and m.group(1) in videos and m.group(1) not in used:
                assigned[ep["id"]] = (m.group(1), "episode-link", 1.0)
                used.add(m.group(1))
                break

    candidates = []
    for ep in episodes:
        if ep["id"] in assigned:
            continue
        for vid, v in videos.items():
            if vid in used or "coming soon" in v.get("title", "").lower():
                continue
            s, dated = similarity(ep, v)
            if s >= 0.15:
                candidates.append((s, dated, ep["id"], vid))
    for s, dated, eid, vid in sorted(candidates, reverse=True):
        if eid in assigned or vid in used:
            continue
        assigned[eid] = (vid, "date+title-match" if dated else "title-match", round(s, 2))
        used.add(vid)

    unmatched = []
    for ep in episodes:
        vid, how, score = assigned.get(ep["id"], (None, None, 0))
        if not vid:
            ep["youtube"] = None
            if ep["status"] == "completed" and how != "override":
                unmatched.append(ep["id"])
            continue
        v = videos.get(vid, {"id": vid})
        ep["youtube"] = {
            "videoId": vid,
            "url": f"https://www.youtube.com/watch?v={vid}",
            "title": v.get("title", ""),
            "publishedAt": v.get("actualStartTime") or v.get("scheduledStartTime") or v.get("publishedAt", ""),
            "liveStatus": v.get("liveStatus", ""),
            "durationSec": v.get("durationSec"),
            "viewCount": v.get("viewCount"),
            "likeCount": v.get("likeCount"),
            "commentCount": v.get("commentCount"),
            "statsFetchedAt": v.get("statsFetchedAt", ""),
            "transcript": v.get("transcript"),
            "matchedBy": how,
            "matchScore": score,
            "needsReview": how == "title-match" and score < 0.5,
        }
    write_json(ep_path, doc)
    orphans = [v for v in videos if v not in used and "coming soon" not in videos[v].get("title", "").lower()]
    review = [e["id"] for e in episodes if (e.get("youtube") or {}).get("needsReview")]
    print(f"link: {len(used)} videos matched; unmatched completed episodes: {unmatched or 'none'}; "
          f"unused videos: {orphans or 'none'}; needs review: {review or 'none'}")


# --------------------------------------------------------------------------- check


def cmd_check(_args) -> None:
    errors = []
    doc = read_json(DATA / "episodes.json", {"episodes": []})
    ids = [e["id"] for e in doc["episodes"]]
    if len(ids) != len(set(ids)):
        errors.append("duplicate episode ids")
    for e in doc["episodes"]:
        for key in ("banner", "page"):
            if e.get(key) and not (DATA / e[key]).exists():
                errors.append(f"{e['id']}: missing {key} {e[key]}")
        t = (e.get("youtube") or {}).get("transcript")
        if t and not (DATA / t).exists():
            errors.append(f"{e['id']}: missing transcript {t}")
        if not e.get("title"):
            errors.append(f"{e['id']}: empty title")
    linked = sum(1 for e in doc["episodes"] if e.get("youtube"))
    transcripts = sum(1 for e in doc["episodes"] if (e.get("youtube") or {}).get("transcript"))
    print(f"check: {len(ids)} episodes, {linked} linked to YouTube, {transcripts} with transcripts, "
          f"{len(errors)} errors")
    for err in errors:
        print("  !", err)
    if errors:
        sys.exit(1)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("repo", "all"):
        sp = sub.add_parser(name)
        sp.add_argument("--source", help="Use a local clone of microsoft/model-mondays instead of cloning")
        sp.add_argument("--ref", default="main")
    for name in ("youtube", "all"):
        sp = sub.choices[name] if name in sub.choices else sub.add_parser(name)
        sp.add_argument("--force", action="store_true", help="Re-fetch descriptions and transcripts")
        sp.add_argument("--no-details", action="store_true", help="Skip per-video metadata via yt-dlp")
        sp.add_argument("--no-transcripts", action="store_true")
    sub.add_parser("link")
    sub.add_parser("check")
    args = p.parse_args()

    if args.cmd == "repo":
        cmd_repo(args)
    elif args.cmd == "youtube":
        cmd_youtube(args)
    elif args.cmd == "link":
        link_videos()
    elif args.cmd == "check":
        cmd_check(args)
    elif args.cmd == "all":
        cmd_repo(args)
        cmd_youtube(args)
        cmd_check(args)


if __name__ == "__main__":
    main()
