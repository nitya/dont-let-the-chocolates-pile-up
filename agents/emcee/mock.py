"""--mock mode: a deterministic chat client whose "brain" is a script per agent.

The scripts drive the *real* Agent Framework machinery (function-calling loop, agent-as-tool delegation, middleware)
and the *real* MCP calls to the Model Mondays site, so the end-to-end flow can be demoed and tested without any LLM.
Drafts are built from the real data the tools return (see content.py) and are labeled "[mock]".
"""

from __future__ import annotations

import asyncio
import json
import re
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, ClassVar

from agent_framework import (
    BaseChatClient,
    ChatMiddlewareLayer,
    ChatResponse,
    ChatResponseUpdate,
    Content,
    FunctionInvocationLayer,
    Message,
)
from agent_framework.observability import ChatTelemetryLayer

from . import content as C
from .rules import Intent, episode_label, normalize_episode_id, parse_request
from .trace import parse_result


@dataclass
class Call:
    name: str
    args: dict[str, Any]
    text: str

    @property
    def data(self) -> Any:
        return parse_result(self.text)


@dataclass
class BrainContext:
    task: str
    calls: list[Call] = field(default_factory=list)
    tools: set[str] = field(default_factory=set)

    def find(self, _tool: str, **match: Any) -> Call | None:
        for call in reversed(self.calls):
            if call.name == _tool and all(call.args.get(k) == v for k, v in match.items()):
                return call
        return None

    def has(self, _tool: str, **match: Any) -> bool:
        return self.find(_tool, **match) is not None


@dataclass
class Step:
    name: str | None = None
    args: dict[str, Any] = field(default_factory=dict)
    text: str | None = None


def call(_tool: str, **args: Any) -> Step:
    return Step(name=_tool, args=args)


def say(text: str) -> Step:
    return Step(text=text)


Brain = Callable[[BrainContext], Step]


def _context_from_messages(messages: list[Message], options: dict[str, Any]) -> BrainContext:
    task = ""
    pending: dict[str, tuple[str, dict[str, Any]]] = {}
    ctx = BrainContext(task="")
    for message in messages:
        for item in message.contents:
            if item.type == "text" and message.role == "user":
                task = item.text or ""  # the latest user turn is the task (earlier ones are history)
            elif item.type == "function_call":
                args = item.arguments
                if isinstance(args, str):
                    try:
                        args = json.loads(args or "{}")
                    except ValueError:
                        args = {}
                pending[item.call_id] = (item.name, dict(args or {}))
            elif item.type == "function_result" and item.call_id in pending:
                name, args = pending.pop(item.call_id)
                result = item.result
                text = result if isinstance(result, str) else _text_of(result)
                if item.exception and not text:
                    text = f"Error: {item.exception}"
                ctx.calls.append(Call(name, args, text))
    ctx.task = task
    ctx.tools = {getattr(t, "name", "") for t in (options.get("tools") or [])}
    return ctx


def _text_of(result: Any) -> str:
    if result is None:
        return ""
    if isinstance(result, list):
        return "\n".join(getattr(r, "text", None) or str(r) for r in result)
    return getattr(result, "text", None) or str(result)


class MockChatClient(FunctionInvocationLayer, ChatMiddlewareLayer, ChatTelemetryLayer, BaseChatClient):
    """A scripted stand-in for an LLM. One instance per agent, each with its own brain."""

    OTEL_PROVIDER_NAME: ClassVar[str] = "emcee.mock"

    def __init__(self, brain: Brain, *, delay: float = 0.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.brain = brain
        self.delay = delay

    async def _next_contents(self, messages: Any, options: Any) -> list[Content]:
        ctx = _context_from_messages(list(messages), dict(options or {}))
        step = self.brain(ctx)
        if self.delay:
            await asyncio.sleep(self.delay)
        if step.name:
            return [Content.from_function_call(f"call_{uuid.uuid4().hex[:10]}", step.name, arguments=step.args)]
        return [Content.from_text(step.text or "")]

    def _inner_get_response(self, *, messages: Any, stream: bool, options: Any, **kwargs: Any) -> Any:
        if stream:
            async def _updates():
                contents = await self._next_contents(messages, options)
                yield ChatResponseUpdate(role="assistant", contents=contents, model="emcee-mock")

            return self._build_response_stream(_updates())

        async def _respond() -> ChatResponse:
            contents = await self._next_contents(messages, options)
            return ChatResponse(messages=[Message(role="assistant", contents=contents)], model="emcee-mock",
                                response_id=f"mock-{uuid.uuid4().hex[:8]}")

        return _respond()


# --------------------------------------------------------------------------------------------- shared helpers


def _episode(ctx: BrainContext, episode_id: str | None = None) -> dict | None:
    c = ctx.find("get_episode", episode_id=episode_id) if episode_id else ctx.find("get_episode")
    data = c.data if c else None
    return data if isinstance(data, dict) and data.get("id") else None


def _submitted(ctx: BrainContext, kind: str) -> bool:
    return any(c.name == "submit_draft" and c.args.get("kind") == kind and not c.text.startswith("BLOCKED")
               for c in ctx.calls)


def _blocked(ctx: BrainContext, kind: str) -> bool:
    return any(c.name == "submit_draft" and c.args.get("kind") == kind and c.text.startswith("BLOCKED")
               for c in ctx.calls)


def _submit_steps(ctx: BrainContext, episode_id: str, drafts: list[C.Draft], agent: str,
                  fault_kind: str | None = None) -> Step | None:
    for d in drafts:
        if _submitted(ctx, d.kind):
            continue
        if d.kind == fault_kind and not _blocked(ctx, d.kind):
            # Stage demo of the guardrail: the first attempt cites the series homepage, which the rules forbid.
            d = C.Draft(d.kind, d.title, d.content_markdown + "\nMore: https://aka.ms/model-mondays\n",
                        [*d.sources, "https://aka.ms/model-mondays"])
        return call("submit_draft", **d.as_args(episode_id, f"emcee/{agent}"))
    return None


def _final(ctx: BrainContext, agent: str, extra: list[str] | None = None) -> Step:
    lines = []
    for c in ctx.calls:
        if c.name == "submit_draft":
            data = c.data
            if isinstance(data, dict) and data.get("draft_id"):
                lines.append(f"- {c.args.get('kind')}: {c.args.get('title')} → draft {data['draft_id']} "
                             f"({data.get('status')})")
            elif c.text.startswith("BLOCKED"):
                lines.append(f"- guardrail caught a {c.args.get('kind')} draft: {c.text.split(':', 1)[-1][:140].strip()}"
                             + (" (fixed and resubmitted)" if _submitted(ctx, c.args.get("kind")) else ""))
            else:
                lines.append(f"- {c.args.get('kind')}: NOT submitted ({c.text[:160]})")
        elif c.name == "flag_for_human":
            lines.append(f"- flagged for a human: {c.args.get('reason')}")
    lines += extra or []
    return say(f"emcee/{agent} finished.\n" + ("\n".join(lines) or "- nothing submitted"))


def _flag_once(ctx: BrainContext, reason: str, episode_id: str) -> Step | None:
    if any(c.name == "flag_for_human" and c.args.get("reason") == reason for c in ctx.calls):
        return None
    return call("flag_for_human", reason=reason, episode_id=episode_id)


# --------------------------------------------------------------------------------------------- emcee


def emcee_brain(only: list[str] | None, site: str) -> Brain:
    def brain(ctx: BrainContext) -> Step:
        intent: Intent = parse_request(ctx.task, only)
        specialists = [s for s in intent.specialists if s in ctx.tools]
        episode_id = intent.episode_id
        if episode_id is None and intent.wants_next:
            stats = ctx.find("get_series_stats")
            if stats is None:
                return call("get_series_stats")
            episode_id = ((stats.data or {}).get("up_next") or {}).get("id") if isinstance(stats.data, dict) else None
        if episode_id is None and intent.wants_last:
            aired = ctx.find("list_episodes", status="completed")
            if aired is None:
                return call("list_episodes", status="completed", limit=200)
            rows = aired.data if isinstance(aired.data, list) else []
            episode_id = max(rows, key=lambda r: r.get("date", ""))["id"] if rows else None
        if episode_id is None:
            search = ctx.find("search_episodes")
            if search is None:
                return call("search_episodes", query=_search_query(ctx.task), limit=10)
            rows = search.data if isinstance(search.data, list) else []
            upcoming = [r for r in rows if r.get("display_status") in ("upcoming", "live")]
            pick = (upcoming or rows or [None])[0]
            episode_id = pick.get("id") if pick else None
        if episode_id is None:
            step = _flag_once(ctx, "Couldn't identify which episode this request is about; please add the episode id.",
                              "")
            return step or say("### Emcee run report\nNo episode found for this request; flagged for a human.")
        got = ctx.find("get_episode", episode_id=episode_id)
        if got is None:
            return call("get_episode", episode_id=episode_id)
        ep = got.data if isinstance(got.data, dict) else None
        if not ep:
            step = _flag_once(ctx, f"Episode {episode_id} was not found on the site.", episode_id)
            return step or say(f"### Emcee run report\nEpisode {episode_id} not found; flagged for a human.")
        aired = C.is_aired(ep)
        label = episode_label(ep["id"])
        if intent.action == "wrap" and not aired:
            step = _flag_once(ctx, f"{label} hasn't aired yet (status {ep.get('display_status')}); nothing to wrap up.",
                              ep["id"])
            if step:
                return step
            specialists = []
        if intent.action in ("prep", "announce") and aired:
            step = _flag_once(ctx, f"{label} already aired; did you mean 'wrap up {label}'?", ep["id"])
            if step:
                return step
            specialists = []
        for name in specialists:
            if not ctx.has(name):
                return call(name, task=_task_for(name, intent, ep, site))
        return say(_emcee_report(ctx, intent, ep, site))

    return brain


def _search_query(text: str) -> str:
    """Issue title without the 'new episode announced:' preamble or filler words."""
    first = next((line for line in text.splitlines() if line.strip()), text)
    first = first.split(":", 1)[1] if ":" in first else first
    stop = {"new", "episode", "announced", "announce", "join", "us", "on", "the", "a", "an", "and", "with", "for",
            "model", "mondays", "spotlight", "of", "to", "in", "at", "nov", "oct", "dec"}
    words = [w for w in re.findall(r"[A-Za-z0-9][\w.+-]*", first) if w.lower() not in stop and not w.isdigit()]
    return " ".join(words[:8]) or first[:100]


def _task_for(name: str, intent: Intent, ep: dict, site: str) -> str:
    label = f"{episode_label(ep['id'])} (episode_id {ep['id']}, “{ep['title']}”, {ep.get('date')})"
    notes = []
    if not ep.get("speakers"):
        notes.append("guest names are not in the data")
    if not ep.get("has_transcript"):
        notes.append("no transcript yet")
    note = f" Heads-up: {', '.join(notes)}." if notes else ""
    if name == "coordinator":
        return f"Write the guest brief and the run-of-show for the upcoming episode {label}.{note}"
    if name == "producer":
        return f"Wrap up {label}: write the recap and the highlights, grounded in the transcript or chapters.{note}"
    if name == "presenter":
        return f"Build the Marp deck for {label}, grounded in the episode data and Microsoft Learn.{note}"
    when = "after the show (wrap up): replay social posts" if intent.action == "wrap" else \
        "before the show: the announcement and a save-the-date social post"
    return f"Promote {label} {when}. Link the episode page {C.page_url(site, ep['id'])} or the recording.{note}"


def _emcee_report(ctx: BrainContext, intent: Intent, ep: dict, site: str) -> str:
    lines = [f"### Emcee run report: {intent.raw}",
             f"**Episode:** {episode_label(ep['id'])} · {ep['title']} · {ep.get('display_status')} {ep.get('date')}",
             "**Drafted:**"]
    flagged = [c.args.get("reason") for c in ctx.calls if c.name == "flag_for_human"]
    for c in ctx.calls:
        if c.name in ("coordinator", "producer", "presenter", "publisher"):
            if not c.text.startswith("emcee/"):
                flagged.append(f"{c.name} failed: {c.text[:200]}")
                continue
            for line in c.text.splitlines():
                if line.startswith("- ") and "flagged for a human" not in line:
                    lines.append(f"- {c.name}: {line[2:]}")
                elif line.startswith("- flagged for a human:"):
                    flagged.append(f"{c.name}: {line.split(':', 1)[1].strip()}")
    if lines[-1] == "**Drafted:**":
        lines.append("- nothing")
    lines.append(f"**Review them in the Studio:** {site.rstrip('/')}/studio")
    lines.append("**Needs a human:**")
    lines += [f"- {f}" for f in flagged] or ["- nothing"]
    return "\n".join(lines)


# --------------------------------------------------------------------------------------------- specialists


def coordinator_brain(site: str) -> Brain:
    def brain(ctx: BrainContext) -> Step:
        eid = normalize_episode_id(ctx.task) or ""
        ep = _episode(ctx, eid)
        if ep is None:
            if ctx.has("get_episode", episode_id=eid):
                return _final(ctx, "coordinator", [f"- could not load {eid}"])
            return call("get_episode", episode_id=eid)
        if not ctx.has("search_episodes"):
            return call("search_episodes", query=C.topic_query(ep), limit=6)
        if not ctx.has("list_episodes"):
            return call("list_episodes", season=ep["season"], limit=60)
        season = ctx.find("list_episodes").data or []
        season = season if isinstance(season, list) else []
        aired = [r for r in season if r.get("date", "") < ep["date"] and r.get("display_status") == "completed"
                 and r.get("video_url")]
        reference_id = aired[-1]["id"] if aired else None
        if reference_id and not ctx.has("get_episode", episode_id=reference_id):
            return call("get_episode", episode_id=reference_id)
        if not ctx.has("list_drafts"):
            return call("list_drafts", episode_id=eid)
        if not ep.get("speakers"):
            step = _flag_once(ctx, f"Add guest names for {episode_label(eid)} to the brief and run-of-show.", eid)
            if step:
                return step
        search = ctx.find("search_episodes").data
        related = [r for r in (search if isinstance(search, list) else []) if r.get("id") != eid][:4]
        reference = _episode(ctx, reference_id) if reference_id else None
        next_ep = next((r for r in season if r.get("date", "") > ep["date"]), None)
        step = _submit_steps(ctx, eid, [C.brief(ep, related, site), C.run_of_show(ep, reference, next_ep)],
                             "coordinator")
        return step or _final(ctx, "coordinator")

    return brain


def producer_brain(site: str) -> Brain:
    def brain(ctx: BrainContext) -> Step:
        eid = normalize_episode_id(ctx.task) or ""
        ep = _episode(ctx, eid)
        if ep is None:
            if ctx.has("get_episode", episode_id=eid):
                return _final(ctx, "producer", [f"- could not load {eid}"])
            return call("get_episode", episode_id=eid)
        if not C.is_aired(ep):
            step = _flag_once(ctx, f"{episode_label(eid)} hasn't aired yet; no recap possible.", eid)
            return step or _final(ctx, "producer")
        if not ctx.has("get_transcript"):
            return call("get_transcript", episode_id=eid)
        transcript = "not available" not in (ctx.find("get_transcript").text or "not available")
        if not transcript:
            step = _flag_once(ctx, f"No transcript for {episode_label(eid)} yet: recap is grounded in description + "
                                   "chapters only; regenerate when the transcript lands.", eid)
            if step:
                return step
        if not ep.get("speakers"):
            step = _flag_once(ctx, f"Guest names for {episode_label(eid)} aren't in the data; add them to the recap.",
                              eid)
            if step:
                return step
        for draft in (C.recap(ep, transcript), C.highlights(ep, transcript)):
            if ctx.has("submit_draft", kind=draft.kind):
                continue
            check = ctx.find("check_draft", name=draft.kind)
            if check is None:
                return call("check_draft", episode_id=eid, markdown=draft.content_markdown, name=draft.kind)
            if "FAIL" in check.text.splitlines()[0]:
                step = _flag_once(ctx, f"check.py failed for the {draft.kind}; not submitted.", eid)
                if step:
                    return step
                continue
            return call("submit_draft", **draft.as_args(eid, "emcee/producer"))
        return _final(ctx, "producer")

    return brain


def presenter_brain(site: str) -> Brain:
    def brain(ctx: BrainContext) -> Step:
        eid = normalize_episode_id(ctx.task) or ""
        ep = _episode(ctx, eid)
        if ep is None:
            if ctx.has("get_episode", episode_id=eid):
                return _final(ctx, "presenter", [f"- could not load {eid}"])
            return call("get_episode", episode_id=eid)
        if "microsoft_docs_search" in ctx.tools and not ctx.has("microsoft_docs_search"):
            return call("microsoft_docs_search", query=C.learn_query(ep))
        if not ctx.has("search_episodes"):
            return call("search_episodes", query=C.topic_query(ep), limit=6)
        if not ctx.has("list_episodes"):
            return call("list_episodes", season=ep["season"], limit=60)
        related = ctx.find("search_episodes").data
        related = related if isinstance(related, list) else []
        docs_call = ctx.find("microsoft_docs_search")
        docs = (docs_call.data or {}).get("results", []) if docs_call and isinstance(docs_call.data, dict) else []
        season = ctx.find("list_episodes").data
        next_ep = next((r for r in (season if isinstance(season, list) else []) if r.get("date", "") > ep["date"]), None)
        deck = C.deck(ep, docs, next_ep, related)
        if not ctx.has("render_deck"):
            return call("render_deck", episode_id=eid, markdown=deck.content_markdown)
        if not ctx.has("check_draft"):
            return call("check_draft", episode_id=eid, markdown=deck.content_markdown, name="deck")
        if not docs:
            step = _flag_once(ctx, f"The {episode_label(eid)} deck has no Learn pages (Learn MCP unavailable); "
                                   "add 2-4 before presenting.", eid)
            if step:
                return step
        if not ctx.has("submit_draft", kind="deck"):
            if "FAIL" in ctx.find("check_draft").text.splitlines()[0]:
                step = _flag_once(ctx, "check.py failed for the deck; not submitted.", eid)
                return step or _final(ctx, "presenter")
            return call("submit_draft", **deck.as_args(eid, "emcee/presenter"))
        rendered = "rendered" if "Rendered" in ctx.find("render_deck").text else "Markdown only (no Marp here)"
        return _final(ctx, "presenter", [f"- deck output: {rendered}"])

    return brain


def publisher_brain(site: str, fault: str | None = None) -> Brain:
    def brain(ctx: BrainContext) -> Step:
        eid = normalize_episode_id(ctx.task) or ""
        ep = _episode(ctx, eid)
        if ep is None:
            if ctx.has("get_episode", episode_id=eid):
                return _final(ctx, "publisher", [f"- could not load {eid}"])
            return call("get_episode", episode_id=eid)
        if not ctx.has("list_drafts"):
            return call("list_drafts", episode_id=eid)
        drafts = ctx.find("list_drafts").data
        drafts = drafts if isinstance(drafts, list) else []
        after_show = C.is_aired(ep) and any(w in ctx.task.lower() for w in ("after the show", "wrap", "replay"))
        todo = [C.social(ep, site, True, drafts)] if after_show else [
            C.announcement(ep, site, drafts), C.social(ep, site, False, drafts)]
        step = _submit_steps(ctx, eid, todo, "publisher", fault_kind="social" if fault == "placeholder" else None)
        return step or _final(ctx, "publisher")

    return brain


SPECIALIST_BRAINS: dict[str, Callable[..., Brain]] = {
    "coordinator": coordinator_brain,
    "producer": producer_brain,
    "presenter": presenter_brain,
    "publisher": publisher_brain,
}
