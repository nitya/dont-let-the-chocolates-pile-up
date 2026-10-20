"""Mutable drafts store: one JSON file in MM_STATE_DIR, atomic writes, thread-safe."""

from __future__ import annotations

import json
import os
import re
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .data import DataStore

KINDS = ("recap", "highlights", "brief", "run_of_show", "social", "deck", "announcement", "episode")
GROUNDED_KINDS = ("recap", "highlights")
STATUSES = ("pending", "approved", "rejected")
EPISODE_ID_RE = re.compile(r"^s\d{1,2}-e\d{2,3}$")
MAX_MARKDOWN = 200_000
MAX_HTML = 3_000_000


class DraftError(ValueError):
    status_code = 400


class DraftNotFound(DraftError):
    status_code = 404


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.strip().replace(" ", "+").replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def summary(draft: dict) -> dict:
    """Draft without the (potentially huge) deck HTML."""
    out = {k: v for k, v in draft.items() if k != "content_html"}
    out["has_html"] = bool(draft.get("content_html"))
    return out


def validate_submission(
    data: DataStore,
    *,
    episode_id: str,
    kind: str,
    title: str,
    content_markdown: str,
    author_agent: str,
    sources: list[str] | None,
    content_html: str | None = None,
) -> dict[str, Any]:
    episode_id = (episode_id or "").strip().lower()
    kind = (kind or "").strip().lower()
    if kind not in KINDS:
        raise DraftError(f"Unknown kind {kind!r}. Use one of: {', '.join(KINDS)}.")
    if kind == "episode":
        if not EPISODE_ID_RE.match(episode_id):
            raise DraftError("Episode proposals need an id like 's4-e13' (season and two-digit episode number).")
    elif not data.episode(episode_id):
        raise DraftNotFound(
            f"Episode {episode_id!r} not found. Call list_episodes or search_episodes to get a valid id like 's4-e05'."
        )
    title = (title or "").strip()
    if not title:
        raise DraftError("title must not be empty.")
    content_markdown = content_markdown or ""
    if not content_markdown.strip() and not content_html:
        raise DraftError("content_markdown must not be empty.")
    if len(content_markdown) > MAX_MARKDOWN:
        raise DraftError(f"content_markdown is too long (max {MAX_MARKDOWN} characters).")
    if content_html and len(content_html) > MAX_HTML:
        raise DraftError(f"content_html is too large (max {MAX_HTML} characters).")
    clean_sources = [s.strip() for s in (sources or []) if isinstance(s, str) and s.strip()]
    if kind in GROUNDED_KINDS and not clean_sources:
        raise DraftError(
            f"A {kind} must be grounded: pass the URLs or data paths you used in `sources` "
            "(e.g. the episode's YouTube URL, 'data/episodes/s4-e05.md', or the transcript path from get_transcript)."
        )
    return {
        "episode_id": episode_id,
        "kind": kind,
        "title": title[:300],
        "content_markdown": content_markdown,
        "content_html": content_html or None,
        "author_agent": (author_agent or "").strip()[:120] or "unknown-agent",
        "sources": clean_sources[:50],
    }


class DraftStore:
    def __init__(self, state_dir: Path):
        self.state_dir = Path(state_dir)
        self.path = self.state_dir / "drafts.json"
        self._lock = threading.RLock()
        self._key: tuple[int, int] | None = None
        self._doc: dict | None = None

    @staticmethod
    def _fresh(drafts: list[dict] | None = None) -> dict:
        return {"epoch": uuid.uuid4().hex[:12], "updated_at": now_iso(), "drafts": drafts or []}

    def _load(self) -> dict:
        with self._lock:
            try:
                st = self.path.stat()
            except FileNotFoundError:
                self._save(self._fresh())
                return self._doc  # type: ignore[return-value]
            key = (st.st_mtime_ns, st.st_size)
            if self._doc is None or key != self._key:
                try:
                    self._doc = json.loads(self.path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    self._doc = self._fresh()
                self._key = key
            return self._doc

    def _save(self, doc: dict) -> None:
        with self._lock:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            doc["updated_at"] = now_iso()
            tmp = self.path.with_suffix(f".{os.getpid()}.{threading.get_ident()}.tmp")
            tmp.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
            os.replace(tmp, self.path)
            st = self.path.stat()
            self._doc, self._key = doc, (st.st_mtime_ns, st.st_size)

    # ---- reads ------------------------------------------------------------------
    @property
    def epoch(self) -> str:
        return self._load().get("epoch", "")

    def all(self) -> list[dict]:
        return list(self._load().get("drafts", []))

    def list(self, episode_id: str | None = None, status: str | None = None, kind: str | None = None) -> list[dict]:
        out = self.all()
        if episode_id:
            out = [d for d in out if d["episode_id"] == episode_id.strip().lower()]
        if status:
            out = [d for d in out if d["status"] == status.strip().lower()]
        if kind:
            out = [d for d in out if d["kind"] == kind.strip().lower()]
        return sorted(out, key=lambda d: d["created_at"], reverse=True)

    def get(self, draft_id: str) -> dict:
        for d in self.all():
            if d["id"] == draft_id:
                return d
        raise DraftNotFound(f"Draft {draft_id!r} not found.")

    def approved_for(self, episode_id: str) -> dict[str, dict]:
        """Latest approved draft per kind (by approval time)."""
        latest: dict[str, dict] = {}
        for d in self.list(episode_id=episode_id, status="approved"):
            cur = latest.get(d["kind"])
            if cur is None or (d.get("reviewed_at") or "") > (cur.get("reviewed_at") or ""):
                latest[d["kind"]] = d
        return latest

    def approved_proposals(self, known_ids: set[str]) -> list[dict]:
        return [d for d in self.list(kind="episode", status="approved") if d["episode_id"] not in known_ids]

    def recently_reviewed(self, limit: int = 10) -> list[dict]:
        done = [d for d in self.all() if d["status"] != "pending"]
        return sorted(done, key=lambda d: d.get("reviewed_at") or "", reverse=True)[:limit]

    def changes(self, since: str | None, episode_id: str | None = None) -> list[dict]:
        since_dt = parse_iso(since)
        out = []
        for d in self.all():
            if episode_id and d["episode_id"] != episode_id:
                continue
            updated = parse_iso(d.get("updated_at") or d["created_at"])
            if since_dt is None or (updated and updated > since_dt):
                out.append({k: d.get(k) for k in ("id", "episode_id", "kind", "title", "author_agent", "status", "updated_at")})
        return sorted(out, key=lambda d: d["updated_at"] or "")

    # ---- writes -----------------------------------------------------------------
    def create(self, fields: dict[str, Any], status: str = "pending") -> dict:
        ts = now_iso()
        draft = {
            "id": uuid.uuid4().hex[:8],
            **fields,
            "status": status,
            "created_at": ts,
            "updated_at": ts,
            "reviewed_at": ts if status != "pending" else None,
            "reviewer_note": None,
        }
        with self._lock:
            doc = self._load()
            doc.setdefault("drafts", []).append(draft)
            self._save(doc)
        return draft

    def review(self, draft_id: str, status: str, note: str | None = None) -> dict:
        if status not in ("approved", "rejected"):
            raise DraftError("status must be 'approved' or 'rejected'.")
        with self._lock:
            doc = self._load()
            for d in doc.get("drafts", []):
                if d["id"] == draft_id:
                    ts = now_iso()
                    d.update(status=status, reviewed_at=ts, updated_at=ts, reviewer_note=(note or "").strip() or None)
                    self._save(doc)
                    return d
        raise DraftNotFound(f"Draft {draft_id!r} not found.")

    def reset(self, drafts: list[dict] | None = None) -> None:
        self._save(self._fresh(drafts))
