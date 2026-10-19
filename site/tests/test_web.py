from __future__ import annotations

import pytest

from scripts.reset_state import reset

RECAP = {
    "episode_id": "s4-e05",
    "kind": "recap",
    "title": "Claude tools recap from the test suite",
    "content_markdown": "## Key moments\n\n- Tools <script>alert('x')</script> **matter**",
    "author_agent": "emcee/producer",
    "sources": ["https://www.youtube.com/watch?v=x5qDSukgTi4"],
}


@pytest.mark.parametrize("path", ["/", "/seasons/1", "/seasons/4", "/episodes/s4-e05", "/episodes/s1-e01", "/studio", "/about", "/api/health"])
def test_pages_ok(client, path):
    assert client.get(path).status_code == 200


def test_not_found(client):
    assert client.get("/episodes/s9-e99", headers={"accept": "text/html"}).status_code == 404
    assert client.get("/seasons/99").status_code == 404
    assert client.get("/api/episodes/nope").status_code == 404


def test_episode_page_content(client):
    html = client.get("/episodes/s4-e09").text
    assert "youtube-nocookie.com/embed/rBFQLt3StVI" in html
    assert "Live Demo: Building a Voice Agent for Finance" in html  # chapter from YouTube description
    assert 'src="/banners/S4-E9.webp"' in html and "../banners/" not in html
    for label in ("Recap", "Highlights", "Deck", "Social", "Prep", "Archive"):
        assert label in html
    assert client.get("/banners/S4-E9.webp").headers["content-type"] == "image/webp"


def test_api_listing(client):
    rows = client.get("/api/episodes", params={"season": 4}).json()
    assert rows and all(r["season"] == 4 for r in rows)
    assert any(r["id"] == "s4-e09" for r in client.get("/api/episodes", params={"q": "speech"}).json())
    assert len(client.get("/api/seasons").json()) >= 4
    detail = client.get("/api/episodes/s4-e09").json()
    assert detail["chapters"] and detail["youtube_description"]


def test_draft_lifecycle(client):
    r = client.post("/api/drafts", json=RECAP)
    assert r.status_code == 201, r.text
    draft = r.json()
    assert draft["status"] == "pending" and "/studio#draft-" in draft["studio_url"]
    assert RECAP["title"] not in client.get("/episodes/s4-e05").text
    assert RECAP["title"] in client.get("/studio").text

    since = draft["created_at"]
    r = client.post(f"/api/drafts/{draft['id']}/approve", json={"note": "Ship it"})
    assert r.status_code == 200 and r.json()["status"] == "approved"

    html = client.get("/episodes/s4-e05").text
    assert RECAP["title"] in html and "<script>alert" not in html and "<strong>matter</strong>" in html
    changes = client.get("/api/changes", params={"since": since, "episode_id": "s4-e05"}).json()
    assert [c["status"] for c in changes["changes"]] == ["approved"]
    assert client.get("/api/episodes/s4-e05").json()["approved_drafts"]["recap"]["id"] == draft["id"]

    # Latest approved per kind wins.
    second = client.post("/api/drafts", json={**RECAP, "title": "Second recap"}).json()
    client.post(f"/api/drafts/{second['id']}/approve")
    html = client.get("/episodes/s4-e05").text
    assert "Second recap" in html and RECAP["title"] not in html

    client.post(f"/api/drafts/{second['id']}/reject", json={"note": "unpublish"})
    assert RECAP["title"] in client.get("/episodes/s4-e05").text


def test_draft_validation(client):
    assert client.post("/api/drafts", json={**RECAP, "episode_id": "s9-e99"}).status_code == 404
    assert client.post("/api/drafts", json={**RECAP, "kind": "poem"}).status_code == 400
    r = client.post("/api/drafts", json={**RECAP, "sources": []})
    assert r.status_code == 400 and "grounded" in r.json()["detail"]
    assert client.post("/api/drafts", json={**RECAP, "kind": "social", "sources": []}).status_code == 201
    proposal = client.post("/api/drafts", json={**RECAP, "kind": "episode", "episode_id": "s5-e01", "title": "Proposal"}).json()
    client.post(f"/api/drafts/{proposal['id']}/approve")
    assert "Proposal" in client.get("/episodes/s5-e01").text
    assert client.post("/api/drafts/nope/approve").status_code == 404


def test_write_key_enforced(make_client):
    c = make_client(write_key="w-secret")
    assert c.post("/api/drafts", json=RECAP).status_code == 401
    assert c.post("/api/drafts", json=RECAP, headers={"x-api-key": "wrong"}).status_code == 401
    assert c.post("/api/drafts", json=RECAP, headers={"Authorization": "Bearer w-secret"}).status_code == 201
    assert c.post("/api/drafts", json=RECAP, headers={"x-api-key": "w-secret"}).status_code == 201
    assert c.get("/api/health").json()["write_key_required"] is True


def test_admin_key_enforced(make_client):
    c = make_client(admin_key="a-secret")
    draft = c.post("/api/drafts", json=RECAP).json()
    assert c.post(f"/api/drafts/{draft['id']}/approve").status_code == 401
    assert c.get("/api/drafts").json() == []  # pending drafts are not public
    assert "Reviewer login" in c.get("/studio").text
    assert RECAP["title"] not in c.get("/studio").text

    r = c.post("/studio/login", data={"key": "a-secret"}, follow_redirects=False)
    assert r.status_code == 303 and "mm_admin" in r.cookies
    assert RECAP["title"] in c.get("/studio").text
    r = c.post(f"/studio/drafts/{draft['id']}/approve", data={"note": "nice"}, follow_redirects=False)
    assert r.status_code == 303
    assert RECAP["title"] in c.get("/episodes/s4-e05").text

    other = make_client(admin_key="a-secret")
    assert other.post(f"/api/drafts/{draft['id']}/reject", headers={"x-admin-key": "a-secret"}).status_code == 200
    assert other.get("/studio", params={"key": "a-secret"}, follow_redirects=False).status_code == 303


def test_deck_is_sandboxed(client):
    deck = {**RECAP, "kind": "deck", "title": "Deck", "sources": [], "content_html": "<html><body><h1>Slide 1</h1></body></html>"}
    draft = client.post("/api/drafts", json=deck).json()
    client.post(f"/api/drafts/{draft['id']}/approve")
    r = client.get(f"/drafts/{draft['id']}/deck")
    assert r.status_code == 200 and "Slide 1" in r.text
    assert r.headers["content-security-policy"] == "sandbox allow-scripts"
    assert f'src="/drafts/{draft["id"]}/deck" sandbox="allow-scripts"' in client.get("/episodes/s4-e05").text


def test_reset_state_script(client):
    services = client.app.state.services
    client.post("/api/drafts", json=RECAP)
    assert reset(services.settings, seed=True) == 2
    statuses = sorted(d["status"] for d in services.drafts.all())
    assert statuses == ["approved", "pending"]
    assert reset(services.settings) == 0 and services.drafts.all() == []
