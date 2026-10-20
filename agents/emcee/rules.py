"""Framework-free rules shared by the real agents, the mock brains, the guardrail middleware and the tests.

Nothing here imports agent_framework, so it can be unit-tested with any Python.
"""

from __future__ import annotations

import importlib.util
import re
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO_ROOT / ".github" / "skills"
CHECK_SCRIPT = SKILLS_DIR / "mm-recap" / "scripts" / "check.py"
RENDER_SCRIPT = SKILLS_DIR / "mm-deck" / "scripts" / "render.py"


def _load_placeholder_rx() -> re.Pattern[str]:
    """Reuse the skill's own placeholder definition so there is a single source of truth."""
    path = SKILLS_DIR / "mm-recap" / "scripts" / "context.py"
    try:
        spec = importlib.util.spec_from_file_location("_mm_recap_context", path)
        module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        return module.PLACEHOLDER_RX
    except (Exception, SystemExit):
        return re.compile(r"^https?://aka\.ms/model-mondays/?$", re.I)


PLACEHOLDER_RX = _load_placeholder_rx()
# The same placeholder, but found anywhere in text (bold/italic/punctuation around it, any case, query/fragment).
# Deeper paths such as /discord or /newsletter are real links and stay allowed.
PLACEHOLDER_IN_TEXT_RX = re.compile(r"https?://aka\.ms/model-mondays/?(?![A-Za-z0-9/-])", re.I)
URL_RX = re.compile(r"https?://[^\s)<>\]\"'`]+", re.I)
URL_TRAILING = ".,;:!?*_~'\""
EPISODE_RX = re.compile(r"\bs0*(\d{1,2})\s*[-_: ]?\s*e0*(\d{1,3})\b", re.I)

# Which draft kinds each specialist may submit (enforced by the guardrail middleware).
KINDS_BY_AGENT: dict[str, tuple[str, ...]] = {
    "coordinator": ("brief", "run_of_show"),
    "producer": ("recap", "highlights"),
    "presenter": ("deck",),
    "publisher": ("social", "announcement"),
}

MOCK_TAG = "[mock]"


# --------------------------------------------------------------------------------------------- episode ids


def normalize_episode_id(value: str) -> str | None:
    m = EPISODE_RX.search(value or "")
    return f"s{int(m.group(1))}-e{int(m.group(2)):02d}" if m else None


def episode_label(episode_id: str) -> str:
    m = EPISODE_RX.search(episode_id)
    return f"S{int(m.group(1))}-E{int(m.group(2))}" if m else episode_id.upper()


# --------------------------------------------------------------------------------------------- links


def find_urls(text: str) -> list[str]:
    return [u.rstrip(URL_TRAILING) for u in URL_RX.findall(text or "")]


def is_placeholder(url: str) -> bool:
    url = (url or "").strip().rstrip(URL_TRAILING)
    return bool(PLACEHOLDER_RX.match(url) or re.match(r"https?://aka\.ms/model-mondays/?(?:[?#].*)?$", url, re.I))


def placeholders_in(text: str) -> list[str]:
    return [m.group(0) for m in PLACEHOLDER_IN_TEXT_RX.finditer(text or "")]


def is_valid_source(source: str) -> bool:
    s = (source or "").strip()
    return bool(s) and (s.startswith(("https://", "http://")) or s.startswith("data/")) and not is_placeholder(s)


def submission_problems(
    agent: str, *, kind: str, title: str, content_markdown: str, sources: list[str] | None,
    content_html: str | None = None,
) -> list[str]:
    """Why a submit_draft call must be blocked (empty list = OK). Mirrors the mm-recap / mm-deck rules."""
    problems: list[str] = []
    allowed = KINDS_BY_AGENT.get(agent)
    if allowed and kind not in allowed:
        problems.append(f"{agent} may only submit {', '.join(allowed)} drafts (got {kind!r})")
    if not (title or "").strip():
        problems.append("title is empty")
    if not (content_markdown or "").strip():
        problems.append("content_markdown is empty")
    sources = [s for s in (sources or []) if isinstance(s, str)]
    if not sources:
        problems.append("sources is empty: cite the episode/recording/Learn URLs or data/ paths you actually used")
    for s in sources:
        if is_placeholder(s):
            problems.append(f"placeholder link used as a source: {s} (the series homepage is not a source)")
        elif not is_valid_source(s):
            problems.append(f"source is not a URL or data/ path: {s!r}")
    for url in dict.fromkeys(placeholders_in(content_markdown)):
        problems.append(f"placeholder link in content: {url}")
    if content_html and placeholders_in(content_html):
        problems.append("placeholder link in content_html (re-render the deck from fixed Markdown)")
    if "](" in (content_markdown or "") and re.search(r"\]\(\s*\)", content_markdown):
        problems.append("empty link target in content")
    return problems


# --------------------------------------------------------------------------------------------- requests


@dataclass
class Intent:
    """What the emcee was asked to do, as understood without an LLM (used by mock mode and as a planning hint)."""

    action: str  # prep | wrap | announce
    episode_id: str | None
    raw: str
    wants_next: bool = False
    wants_last: bool = False
    specialists: list[str] = field(default_factory=list)


PLAYBOOK: dict[str, tuple[str, ...]] = {
    "prep": ("coordinator", "presenter", "publisher"),
    "wrap": ("producer", "publisher"),
    "announce": ("coordinator", "publisher"),
}


def parse_request(text: str, only: list[str] | None = None) -> Intent:
    lowered = (text or "").lower()
    if re.search(r"\b(wrap(\s*|-)?up|wrapup|recap|aired|post-?show|after the show)\b", lowered):
        action = "wrap"
    elif re.search(r"\b(announce[sd]?|announcement|new episode|issue)\b", lowered):
        action = "announce"
    else:
        action = "prep"
    episode_id = normalize_episode_id(text)
    wants_next = episode_id is None and bool(re.search(r"\b(next|upcoming)\b", lowered))
    wants_last = episode_id is None and not wants_next and bool(
        re.search(r"\b(last|latest|previous|yesterday'?s?|this week'?s?)\b", lowered))
    specialists = list(PLAYBOOK[action])
    if only:
        specialists = [s for s in specialists if s in only] or [s for s in only if s in KINDS_BY_AGENT]
    return Intent(action=action, episode_id=episode_id, raw=text, wants_next=wants_next, wants_last=wants_last,
                  specialists=specialists)


# --------------------------------------------------------------------------------------------- skills


def load_skill(name: str) -> str:
    """Return a SKILL.md body (front matter stripped) so specialists follow the exact same rules as the skill."""
    path = SKILLS_DIR / name / "SKILL.md"
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"(SKILL.md for {name} not found at {path}; follow the shared rules above.)"
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4 :]
    return text.strip()


def skill_rules(name: str = "mm-recap") -> str:
    """Just the '## Rules' section of a skill (shared by specialists that don't have their own skill)."""
    body = load_skill(name)
    m = re.search(r"^## Rules[^\n]*\n(.*?)(?=^## |\Z)", body, re.M | re.S)
    return (m.group(0) if m else body).strip()
