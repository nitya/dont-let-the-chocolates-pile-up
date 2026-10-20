from __future__ import annotations

import asyncio
import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest
from mcp import Client
from mcp.client.streamable_http import streamable_http_client
from mcp.shared._httpx_utils import create_mcp_http_client

SITE_DIR = Path(__file__).resolve().parent.parent
EXPECTED_TOOLS = {
    "list_seasons", "list_episodes", "get_episode", "search_episodes", "get_transcript",
    "get_series_stats", "list_drafts", "submit_draft",
}


def _payload(result):
    assert not result.is_error, result.content
    return result.structured_content if result.structured_content is not None else json.loads(result.content[0].text)


def test_tools_in_process(client):
    services = client.app.state.services

    async def run():
        async with Client(client.app.state.mcp) as mcp:
            names = {t.name for t in (await mcp.list_tools()).tools}
            assert names == EXPECTED_TOOLS  # intentionally no approve tool

            assert len(_payload(await mcp.call_tool("list_seasons", {}))["result"]) >= 4
            rows = _payload(await mcp.call_tool("list_episodes", {"season": 4, "limit": 3}))["result"]
            assert [r["id"] for r in rows] == ["s4-e01", "s4-e02", "s4-e03"]
            ep = _payload(await mcp.call_tool("get_episode", {"episode_id": "s4-e09"}))
            assert ep["chapters"] and ep["youtube"]["videoId"] == "rBFQLt3StVI"
            hits = _payload(await mcp.call_tool("search_episodes", {"query": "Hugging Face"}))["result"]
            assert any(h["id"] in ("s2-e13", "s4-e10", "s3-e15") for h in hits)
            text = (await mcp.call_tool("get_transcript", {"episode_id": "s4-e09"})).content[0].text
            assert "not available yet" in text or "[transcript s4-e09" in text
            assert _payload(await mcp.call_tool("get_series_stats", {}))["episodes_total"] >= 40

            missing = await mcp.call_tool("get_episode", {"episode_id": "s9-e99"})
            assert missing.is_error and "not found" in missing.content[0].text

            bad = await mcp.call_tool("submit_draft", {
                "episode_id": "s4-e09", "kind": "recap", "title": "t", "content_markdown": "m",
                "author_agent": "test", "sources": []})
            assert bad.is_error and "grounded" in bad.content[0].text
            ok = _payload(await mcp.call_tool("submit_draft", {
                "episode_id": "s4-e09", "kind": "highlights", "title": "Top moments", "content_markdown": "- one",
                "author_agent": "test", "sources": ["https://www.youtube.com/watch?v=rBFQLt3StVI"]}))
            assert ok["status"] == "pending" and ok["studio_url"].endswith(f"/studio#draft-{ok['draft_id']}")
            listed = _payload(await mcp.call_tool("list_drafts", {"status": "pending"}))["result"]
            assert [d["id"] for d in listed] == [ok["draft_id"]]

            res = await mcp.read_resource("mm://episodes/s4-e05")
            assert "Claude" in res.contents[0].text

    asyncio.run(run())
    assert [d["kind"] for d in services.drafts.list(status="pending")] == ["highlights"]


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def live_server(tmp_path):
    port = _free_port()
    env = {**os.environ, "MM_STATE_DIR": str(tmp_path / "state"), "MM_WRITE_KEY": "mcp-secret", "MM_ADMIN_KEY": ""}
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=SITE_DIR, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    try:
        for _ in range(100):
            try:
                if httpx.get(f"{base}/api/health", timeout=1).status_code == 200:
                    break
            except httpx.HTTPError:
                time.sleep(0.1)
        else:
            pytest.fail("server did not start")
        yield base
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def test_streamable_http_end_to_end(live_server):
    url = f"{live_server}/mcp"
    draft = {"episode_id": "s4-e10", "kind": "social", "title": "Tune in", "content_markdown": "Today!",
             "author_agent": "e2e", "sources": []}

    async def run():
        async with Client(url) as mcp:
            assert {t.name for t in (await mcp.list_tools()).tools} == EXPECTED_TOOLS
            stats = _payload(await mcp.call_tool("get_series_stats", {}))
            assert stats["episodes_total"] >= 40 and stats["total_views"] > 0
            denied = await mcp.call_tool("submit_draft", draft)
            assert denied.is_error and "Unauthorized" in denied.content[0].text

        async with create_mcp_http_client(headers={"Authorization": "Bearer mcp-secret"}) as http:
            async with Client(streamable_http_client(url, http_client=http)) as mcp:
                ok = _payload(await mcp.call_tool("submit_draft", draft))
                assert ok["studio_url"].startswith(live_server)
        return ok

    ok = asyncio.run(run())
    pending = httpx.get(f"{live_server}/api/changes", params={"since": "2000-01-01T00:00:00Z"}).json()
    assert ok["draft_id"] in [c["id"] for c in pending["changes"]]
