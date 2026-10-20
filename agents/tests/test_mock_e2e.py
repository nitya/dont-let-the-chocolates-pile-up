"""End to end: the real CLI in --mock mode drives the real Agent Framework loop and real MCP calls against a
throwaway site, and the drafts land in the site's review queue."""

from __future__ import annotations

import re

from agents.emcee.rules import find_urls, is_placeholder

from .conftest import drafts


def _assert_clean(draft: dict) -> None:
    assert draft["status"] == "pending"
    assert draft["author_agent"].startswith("emcee/")
    assert draft["title"].startswith("[mock]")
    assert draft["sources"], f"{draft['kind']} has no sources"
    for src in draft["sources"]:
        assert not is_placeholder(src), src
        assert src.startswith(("http://", "https://", "data/")), src
    for url in find_urls(draft["content_markdown"]):
        assert not is_placeholder(url), f"placeholder link in {draft['kind']}: {url}"


def test_prep_upcoming_episode(run_cli, site_url):
    proc, ledger = run_cli("prep S4-E12")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "Run report" in proc.stdout and "coordinator" in proc.stdout
    queued = drafts(site_url, episode_id="s4-e12", status="pending")
    kinds = {d["kind"] for d in queued}
    assert {"brief", "run_of_show", "deck", "announcement", "social"} <= kinds
    for d in queued:
        _assert_clean(d)
    authors = {d["kind"]: d["author_agent"] for d in queued}
    assert authors["brief"] == "emcee/coordinator"
    assert authors["deck"] == "emcee/presenter"
    assert authors["social"] == "emcee/publisher"
    assert {d["kind"] for d in ledger["drafts"]} == {"brief", "run_of_show", "deck", "announcement", "social"}
    assert any("guest names" in e["reason"].lower() for e in ledger["escalations"])
    deck = next(d for d in queued if d["kind"] == "deck")
    assert deck["content_markdown"].lstrip().startswith("---\nmarp: true")
    assert len(re.findall(r"^---$", deck["content_markdown"], re.M)) >= 6


def test_wrap_up_aired_episode(run_cli, site_url):
    proc, ledger = run_cli("wrap up S4-E09")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    queued = drafts(site_url, episode_id="s4-e09", status="pending")
    by_kind = {d["kind"]: d for d in queued}
    assert {"recap", "highlights", "social"} <= set(by_kind)
    for d in queued:
        _assert_clean(d)
    recap = by_kind["recap"]
    assert "https://www.youtube.com/watch?v=rBFQLt3StVI&t=854s" in recap["content_markdown"]
    assert "## Sources" in recap["content_markdown"] and "## Notes for reviewer" in recap["content_markdown"]
    # S4-E09's transcript is committed, so the recap is transcript-grounded and nothing is escalated for it.
    assert "**Grounding:** transcript." in recap["content_markdown"]
    assert not any("no transcript" in e["reason"].lower() for e in ledger["escalations"])
    social = by_kind["social"]
    assert f"{site_url}/episodes/s4-e09" in social["content_markdown"] or "youtube.com/watch" in social["content_markdown"]


def test_only_and_escalation(run_cli, site_url):
    before = len(drafts(site_url))
    proc, ledger = run_cli("wrap up S4-E12")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert ledger["drafts"] == []
    assert any("hasn't aired" in e["reason"] for e in ledger["escalations"])
    assert len(drafts(site_url)) == before

    proc, ledger = run_cli("prep S4-E11", "--only", "presenter")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert [d["agent"] for d in ledger["drafts"]] == ["presenter"]


def test_guardrail_blocks_placeholder_then_resubmits(run_cli, site_url):
    proc, ledger = run_cli("prep S4-E12", "--only", "publisher", "--mock-fault", "placeholder")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert ledger["blocked"] and ledger["blocked"][0]["resolved"]
    assert "placeholder" in ledger["blocked"][0]["problems"]
    for d in drafts(site_url, episode_id="s4-e12", kind="social"):
        _assert_clean(d)


def test_dry_run_queues_nothing(run_cli, site_url):
    before = len(drafts(site_url))
    proc, ledger = run_cli("wrap up S4-E09", "--dry-run")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert {d["kind"] for d in ledger["drafts"]} == {"recap", "highlights", "social"}
    assert all(d["draft_id"].startswith("dry-run") for d in ledger["drafts"])
    assert len(drafts(site_url)) == before


def test_producer_entry(site_url):
    from agents.producer_entry import run_producer_detailed

    result = run_producer_detailed("Wrap up S4-E09: recap and highlights.", mock=True, site=site_url)
    assert result["dry_run"] and [d["kind"] for d in result["drafts"]] == ["recap", "highlights"]
    assert result["markdown"].startswith("---\nepisode: s4-e09")
    assert not any(is_placeholder(u) for u in find_urls(result["markdown"]))
