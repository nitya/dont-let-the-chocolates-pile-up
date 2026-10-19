from __future__ import annotations

import json

from app.data import DataStore, fmt_duration, parse_chapters
from app.drafts import DraftStore
from app.render import render_archive, render_markdown


def test_real_dataset_loads(client):
    data = client.app.state.services.data
    eps = data.episodes()
    assert len(eps) >= 40
    assert len({e["id"] for e in eps}) == len(eps)
    assert data.episode("s4-e05")["season"] == 4
    assert data.episode("S4-E05") is not None
    assert [s["season"] for s in data.seasons()][:2] == [1, 2]
    assert data.page_markdown(data.episode("s4-e05")).count("../banners/") >= 1


def test_search_and_stats(client):
    data = client.app.state.services.data
    hits = data.search("speech voice agents", limit=5)
    assert hits and "s4-e09" in [h["id"] for h in hits[:3]]
    stats = data.stats()
    assert stats["episodes_total"] == len(data.episodes())
    assert sum(stats["episodes_per_season"].values()) == stats["episodes_total"]
    assert stats["total_views"] > 0 and stats["total_hours"] > 0
    assert len(stats["most_viewed"]) == 5
    views = [m["views"] for m in stats["most_viewed"]]
    assert views == sorted(views, reverse=True)


def test_chapters_and_helpers():
    chapters = parse_chapters("Hello\n0:00:00 - Intro\n0:01:54 - News\n1:00:32 - Wrap-up\nnot a chapter")
    assert [c["seconds"] for c in chapters] == [0, 114, 3632]
    assert chapters[1]["title"] == "News"
    assert parse_chapters("Mentioned at 3:15 - once") == []
    assert fmt_duration(3704) == "1:01:44" and fmt_duration(65) == "1:05" and fmt_duration(None) == ""


def test_transcript_picked_up_at_runtime(mini_data):
    data = DataStore(mini_data)
    ep = data.episode("s1-e01")
    assert data.transcript(ep) is None
    assert data.chapters(ep)[-1] == {"seconds": 3723, "label": "1:02:03", "title": "Wrap-up"}
    (mini_data / "youtube" / "transcripts" / "vid123.txt").write_text("[00:00:00] welcome to widgets with gizmos\n")
    assert "gizmos" in data.transcript(ep)
    assert data.search("gizmos")[0]["id"] == "s1-e01"
    assert data.stats()["transcripts_available"] == 1


def test_data_reloads_when_file_changes(mini_data):
    data = DataStore(mini_data)
    assert data.episode("s1-e01")["title"] == "Hands on With Widgets"
    doc = json.loads((mini_data / "episodes.json").read_text())
    doc["episodes"][0]["title"] = "Renamed Widgets Episode!"
    (mini_data / "episodes.json").write_text(json.dumps(doc))
    assert data.episode("s1-e01")["title"] == "Renamed Widgets Episode!"


def test_markdown_is_sanitized_and_banners_rewritten():
    html = render_markdown('Hi <script>alert(1)</script> <a href="javascript:alert(1)" onclick="x()">x</a> ![b](../banners/S1-E1.webp)')
    assert "<script" not in html and "javascript:" not in html and "onclick" not in html
    assert 'src="/banners/S1-E1.webp"' in html
    assert "Imported" not in render_archive("<!-- Imported from x -->\n# Title")


def test_drafts_store_persists_and_resets(tmp_path):
    store = DraftStore(tmp_path / "s")
    epoch = store.epoch
    d = store.create({"episode_id": "s1-e01", "kind": "recap", "title": "t", "content_markdown": "m",
                      "author_agent": "a", "sources": ["x"], "content_html": None})
    assert DraftStore(tmp_path / "s").get(d["id"])["status"] == "pending"
    store.review(d["id"], "approved", "ok")
    assert store.approved_for("s1-e01")["recap"]["reviewer_note"] == "ok"
    assert [c["id"] for c in store.changes("2000-01-01T00:00:00Z")] == [d["id"]]
    store.reset()
    assert store.all() == [] and store.epoch != epoch
