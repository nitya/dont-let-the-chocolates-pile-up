"""Framework-free unit tests for intent parsing and the submit_draft guardrail rules."""

from agents.emcee.rules import (
    is_placeholder,
    load_skill,
    normalize_episode_id,
    parse_request,
    skill_rules,
    submission_problems,
)


def test_episode_ids():
    assert normalize_episode_id("prep S4-E12") == "s4-e12"
    assert normalize_episode_id("wrap up s4e9") == "s4-e09"
    assert normalize_episode_id("nothing here") is None


def test_parse_request_playbook():
    assert parse_request("prep S4-E12").specialists == ["coordinator", "presenter", "publisher"]
    wrap = parse_request("wrap up S4-E09")
    assert (wrap.action, wrap.episode_id, wrap.specialists) == ("wrap", "s4-e09", ["producer", "publisher"])
    ann = parse_request("New episode announced: Spotlight on NVIDIA Models")
    assert ann.action == "announce" and ann.episode_id is None
    assert parse_request("prep next").wants_next
    assert parse_request("prep S4-E12", only=["presenter"]).specialists == ["presenter"]


def test_placeholder_rules():
    assert is_placeholder("https://aka.ms/model-mondays")
    assert is_placeholder("https://aka.ms/model-mondays/")
    assert not is_placeholder("https://aka.ms/model-mondays/discord")
    ok = submission_problems("publisher", kind="social", title="t", content_markdown="see https://youtu.be/x",
                             sources=["https://www.youtube.com/watch?v=x"])
    assert ok == []
    bad = submission_problems("publisher", kind="social", title="t",
                              content_markdown="more: https://aka.ms/model-mondays", sources=[])
    assert any("placeholder link in content" in p for p in bad)
    assert any("sources is empty" in p for p in bad)
    wrong_kind = submission_problems("publisher", kind="recap", title="t", content_markdown="x",
                                     sources=["data/episodes/s4-e09.md"])
    assert any("may only submit" in p for p in wrong_kind)


def test_skills_are_loaded_from_the_repo():
    assert "Ground everything in the context pack" in load_skill("mm-recap")
    assert "Marp" in load_skill("mm-deck")
    assert skill_rules().startswith("## Rules")


def test_placeholder_variants_are_caught():
    for text in ("**https://aka.ms/model-mondays**", "_https://aka.ms/model-mondays_", "https://aka.ms/model-mondays!",
                 "HTTPS://aka.ms/model-mondays", "https://aka.ms/model-mondays?x=1", "<https://aka.ms/model-mondays/>"):
        problems = submission_problems("publisher", kind="social", title="t", content_markdown=f"More: {text}",
                                       sources=["https://www.youtube.com/watch?v=x"])
        assert any("placeholder" in p for p in problems), text
    assert is_placeholder("https://aka.ms/model-mondays?ref=x")
    fine = submission_problems("publisher", kind="social", title="t",
                               content_markdown="Discord: **https://aka.ms/model-mondays/discord**",
                               sources=["https://aka.ms/model-mondays/newsletter"])
    assert fine == []
    html = submission_problems("presenter", kind="deck", title="t", content_markdown="ok",
                               sources=["data/episodes/s4-e12.md"],
                               content_html='<a href="https://aka.ms/model-mondays">x</a>')
    assert any("content_html" in p for p in html)
