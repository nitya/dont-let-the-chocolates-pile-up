from __future__ import annotations

import secrets
from collections.abc import Mapping
from dataclasses import dataclass

from .config import Settings
from .data import DataStore
from .drafts import DraftStore, summary, validate_submission


def key_matches(expected: str | None, provided: str | None) -> bool:
    if not expected:
        return True
    return bool(provided) and secrets.compare_digest(expected.encode(), provided.encode())


def key_from_headers(headers: Mapping[str, str] | None, extra: str | None = None) -> str | None:
    """Extract a key from `Authorization: Bearer <key>`, `x-api-key` or an extra header name."""
    if not headers:
        return None
    lower = {k.lower(): v for k, v in headers.items()}
    auth = lower.get("authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return lower.get("x-api-key") or (lower.get(extra) if extra else None)


@dataclass
class Services:
    settings: Settings
    data: DataStore
    drafts: DraftStore

    @classmethod
    def create(cls, settings: Settings) -> "Services":
        return cls(settings, DataStore(settings.data_dir), DraftStore(settings.state_dir))

    def base_url(self, fallback: str | None = None) -> str:
        return (self.settings.public_url or fallback or "http://localhost:8000").rstrip("/")

    def episode_detail(self, episode: dict) -> dict:
        approved = self.drafts.approved_for(episode["id"])
        return {
            **episode,
            "display_status": self.data.display_status(episode),
            "youtube_description": self.data.youtube_description(episode) or None,
            "chapters": self.data.chapters(episode),
            "has_transcript": self.data.transcript_path(episode) is not None,
            "approved_drafts": {
                kind: {k: v for k, v in summary(d).items() if k in ("id", "title", "author_agent", "reviewed_at", "has_html")}
                for kind, d in approved.items()
            },
        }

    def submit_draft(self, **fields) -> dict:
        return self.drafts.create(validate_submission(self.data, **fields))
