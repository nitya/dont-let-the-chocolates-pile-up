from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app

SITE_DIR = Path(__file__).resolve().parent.parent


def pytest_configure(config):
    # Keep pytest's tmp dirs inside site/ (gitignored) instead of the system temp dir.
    if not config.option.basetemp:
        config.option.basetemp = str(SITE_DIR / ".pytest_tmp")


@pytest.fixture
def make_client(tmp_path):
    clients: list[TestClient] = []

    def make(**overrides) -> TestClient:
        values = dict(state_dir=tmp_path / "state", write_key=None, admin_key=None, allowed_hosts=["testserver"])
        values.update(overrides)
        client = TestClient(create_app(Settings.from_env(**values)))
        client.__enter__()
        clients.append(client)
        return client

    yield make
    for client in clients:
        client.__exit__(None, None, None)


@pytest.fixture
def client(make_client) -> TestClient:
    return make_client()


@pytest.fixture
def mini_data(tmp_path) -> Path:
    """A tiny synthetic data dir, for tests that need to mutate data files."""
    root = tmp_path / "data"
    (root / "episodes").mkdir(parents=True)
    (root / "youtube" / "transcripts").mkdir(parents=True)
    (root / "banners").mkdir()
    episode = {
        "id": "s1-e01", "season": 1, "episode": 1, "date": "2025-03-10", "time": "", "title": "Hands on With Widgets",
        "description": "Widgets are great.", "host": "Ada", "speakers": ["Grace"], "status": "completed", "tags": ["widgets"],
        "banner": "banners/S1-E1.webp", "page": "episodes/s1-e01.md", "highlights": [], "spotlight": None,
        "customerStory": None, "studyCorner": None, "links": {}, "source": {},
        "youtube": {"videoId": "vid123", "url": "https://www.youtube.com/watch?v=vid123", "durationSec": 600,
                    "viewCount": 10, "likeCount": 1, "commentCount": 0, "transcript": None},
    }
    (root / "episodes.json").write_text(json.dumps({"source": {}, "episodes": [episode]}))
    (root / "seasons.json").write_text(json.dumps({"source": {}, "seasons": [{"season": 1, "title": "Season 1"}]}))
    (root / "youtube" / "videos.json").write_text(json.dumps({"videos": [
        {"id": "vid123", "description": "Intro\n0:00 - Welcome\n1:05 - Widgets deep dive\n1:02:03 - Wrap-up"}]}))
    (root / "episodes" / "s1-e01.md").write_text("![S1-E1](../banners/S1-E1.webp)\n\n# Hands on With Widgets\n")
    return root
