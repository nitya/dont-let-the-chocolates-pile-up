"""Read-only access to the Model Mondays dataset in MM_DATA_DIR.

Files are re-read when their mtime changes, so a data refresh or a newly
dropped transcript shows up without restarting the server.
"""

from __future__ import annotations

import json
import re
import threading
from datetime import date
from pathlib import Path
from typing import Any

CHAPTER_RE = re.compile(r"^\s*(?:(\d{1,2}):)?(\d{1,2}):(\d{2})\s*[-–—:|]?\s*(.+?)\s*$")
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9.+#-]*")


def fmt_duration(seconds: int | None) -> str:
    if not seconds:
        return ""
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def parse_chapters(description: str | None) -> list[dict[str, Any]]:
    chapters = []
    for line in (description or "").splitlines():
        m = CHAPTER_RE.match(line)
        if not m:
            continue
        h, mi, s, title = m.groups()
        seconds = int(h or 0) * 3600 + int(mi) * 60 + int(s)
        chapters.append({"seconds": seconds, "label": fmt_duration(seconds) or "0:00", "title": title})
    # A real chapter list starts at 0:00 and has at least two entries.
    if len(chapters) < 2 or chapters[0]["seconds"] != 0:
        return []
    return chapters


class DataStore:
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self._lock = threading.Lock()
        self._cache: dict[Path, tuple[tuple[int, int], Any]] = {}

    # ---- low-level cached reads -------------------------------------------------
    def _read(self, path: Path, loader) -> Any:
        try:
            st = path.stat()
        except OSError:
            return None
        key = (st.st_mtime_ns, st.st_size)
        with self._lock:
            hit = self._cache.get(path)
            if hit and hit[0] == key:
                return hit[1]
        value = loader(path)
        with self._lock:
            self._cache[path] = (key, value)
        return value

    def _json(self, rel: str) -> Any:
        return self._read(self.data_dir / rel, lambda p: json.loads(p.read_text(encoding="utf-8")))

    def _text(self, path: Path) -> str | None:
        return self._read(path, lambda p: p.read_text(encoding="utf-8", errors="replace"))

    def _inside(self, rel: str) -> Path | None:
        path = (self.data_dir / rel).resolve()
        root = self.data_dir.resolve()
        return path if path.is_relative_to(root) else None

    # ---- records ----------------------------------------------------------------
    def source(self) -> dict:
        return (self._json("episodes.json") or {}).get("source", {})

    def episodes(self) -> list[dict]:
        eps = (self._json("episodes.json") or {}).get("episodes", [])
        return sorted(eps, key=lambda e: (e.get("season", 0), e.get("episode", 0)))

    def episode(self, episode_id: str) -> dict | None:
        episode_id = (episode_id or "").strip().lower()
        return next((e for e in self.episodes() if e["id"] == episode_id), None)

    def seasons(self) -> list[dict]:
        return (self._json("seasons.json") or {}).get("seasons", [])

    def season(self, number: int) -> dict | None:
        return next((s for s in self.seasons() if s.get("season") == number), None)

    def videos(self) -> dict[str, dict]:
        data = self._json("youtube/videos.json") or {}
        return {v["id"]: v for v in data.get("videos", []) if v.get("id")}

    def video(self, episode: dict) -> dict | None:
        vid = (episode.get("youtube") or {}).get("videoId")
        return self.videos().get(vid) if vid else None

    def youtube_description(self, episode: dict) -> str:
        return (self.video(episode) or {}).get("description") or ""

    def chapters(self, episode: dict) -> list[dict]:
        return parse_chapters(self.youtube_description(episode))

    def page_markdown(self, episode: dict) -> str | None:
        rel = episode.get("page")
        path = self._inside(rel) if rel else None
        return self._text(path) if path else None

    def transcript_path(self, episode: dict) -> Path | None:
        yt = episode.get("youtube") or {}
        candidates = []
        if yt.get("transcript"):
            candidates.append(yt["transcript"])
        if yt.get("videoId"):
            candidates.append(f"youtube/transcripts/{yt['videoId']}.txt")
        for rel in candidates:
            path = self._inside(rel)
            if path and path.is_file():
                return path
        return None

    def transcript(self, episode: dict) -> str | None:
        path = self.transcript_path(episode)
        return self._text(path) if path else None

    # ---- derived views ----------------------------------------------------------
    @staticmethod
    def display_status(episode: dict, today: date | None = None) -> str:
        today_s = (today or date.today()).isoformat()
        yt = episode.get("youtube") or {}
        if yt.get("liveStatus") == "live":
            return "live"
        if episode.get("status") == "cancelled":
            return "cancelled"
        if yt.get("liveStatus") == "upcoming" or (
            episode.get("status") != "completed" and (episode.get("date") or "") >= today_s
        ):
            return "upcoming"
        return "completed"

    def up_next(self, today: date | None = None) -> dict | None:
        upcoming = [e for e in self.episodes() if self.display_status(e, today) in ("live", "upcoming")]
        upcoming.sort(key=lambda e: (self.display_status(e, today) != "live", e.get("date") or "9999"))
        return upcoming[0] if upcoming else None

    def compact(self, episode: dict) -> dict:
        yt = episode.get("youtube") or {}
        return {
            "id": episode["id"],
            "season": episode.get("season"),
            "episode": episode.get("episode"),
            "date": episode.get("date"),
            "title": episode.get("title"),
            "host": episode.get("host") or None,
            "speakers": episode.get("speakers") or [],
            "status": episode.get("status"),
            "display_status": self.display_status(episode),
            "tags": episode.get("tags") or [],
            "video_url": yt.get("url"),
            "views": yt.get("viewCount"),
            "duration": fmt_duration(yt.get("durationSec")) or None,
            "has_transcript": self.transcript_path(episode) is not None,
        }

    def filter_episodes(self, season: int | None = None, status: str | None = None, q: str | None = None) -> list[dict]:
        eps = self.episodes()
        if season is not None:
            eps = [e for e in eps if e.get("season") == season]
        if status:
            status = status.lower()
            eps = [e for e in eps if status in (e.get("status"), self.display_status(e))]
        if q:
            ids = {r["id"] for r in self.search(q, limit=len(eps) or 1)}
            eps = [e for e in eps if e["id"] in ids]
        return eps

    def search(self, query: str, limit: int = 10) -> list[dict]:
        tokens = TOKEN_RE.findall((query or "").lower())
        if not tokens:
            return []
        phrase = " ".join(tokens)
        results = []
        for ep in self.episodes():
            fields = {
                "title": (5.0, ep.get("title") or ""),
                "tags": (3.0, " ".join(ep.get("tags") or [])),
                "speakers": (3.0, " ".join([ep.get("host") or "", *(ep.get("speakers") or [])])),
                "highlights": (2.0, " ".join(h.get("title", "") for h in ep.get("highlights") or [])),
                "spotlight": (2.0, json.dumps(ep.get("spotlight") or "")),
                "description": (1.5, (ep.get("description") or "") + " " + self.youtube_description(ep)),
                "transcript": (0.3, self.transcript(ep) or ""),
            }
            score, matched = 0.0, []
            for name, (weight, text) in fields.items():
                low = text.lower()
                hits = sum(min(low.count(t), 5) for t in tokens)
                if hits:
                    score += weight * hits + (weight * 2 if len(tokens) > 1 and phrase in low else 0)
                    matched.append(name)
            if score:
                row = self.compact(ep)
                row.update(score=round(score, 2), matched=matched)
                results.append(row)
        results.sort(key=lambda r: -r["score"])
        return results[:limit]

    def stats(self) -> dict:
        eps = self.episodes()
        per_season: dict[int, int] = {}
        for e in eps:
            per_season[e.get("season")] = per_season.get(e.get("season"), 0) + 1
        with_video = [e for e in eps if (e.get("youtube") or {}).get("videoId")]
        views = sum((e["youtube"].get("viewCount") or 0) for e in with_video)
        seconds = sum((e["youtube"].get("durationSec") or 0) for e in with_video)
        top = sorted(with_video, key=lambda e: -(e["youtube"].get("viewCount") or 0))[:5]
        return {
            "episodes_total": len(eps),
            "episodes_per_season": {str(k): v for k, v in sorted(per_season.items())},
            "episodes_with_video": len(with_video),
            "total_views": views,
            "total_hours": round(seconds / 3600, 1),
            "most_viewed": [
                {"id": e["id"], "title": e["title"], "views": e["youtube"].get("viewCount"), "url": e["youtube"].get("url")}
                for e in top
            ],
            "transcripts_available": sum(1 for e in eps if self.transcript_path(e)),
            "up_next": self.compact(nxt) if (nxt := self.up_next()) else None,
            "source": self.source(),
        }
