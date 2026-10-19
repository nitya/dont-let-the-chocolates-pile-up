"""Function/chat middleware: the stage trace, the submit_draft guardrail, and model-call timing."""

from __future__ import annotations

import json
import time
from collections.abc import Awaitable, Callable
from typing import Any

from agent_framework import ChatContext, ChatMiddleware, FunctionInvocationContext, FunctionMiddleware

from . import SPECIALISTS
from .rules import MOCK_TAG, submission_problems
from .runctx import RunContext
from .tools import safe_id
from .trace import DraftRecord, format_call, parse_result, result_text, summarize


def _looks_like_error(text: str) -> bool:
    head = text[:120].lower()
    return head.startswith("error") or (head.startswith("function") and "failed" in head)


class TraceMiddleware(FunctionMiddleware):
    """Prints every tool call / handoff with timing, and records drafts + escalations in the run ledger."""

    def __init__(self, agent: str, run: RunContext) -> None:
        self.agent = agent
        self.run = run

    async def process(self, context: FunctionInvocationContext, call_next: Callable[[], Awaitable[None]]) -> None:
        name = context.function.name
        args = dict(context.arguments or {})
        printer, ledger = self.run.printer, self.run.ledger
        ledger.tool_calls += 1
        is_handoff = name in SPECIALISTS
        if is_handoff:
            printer.event(self.agent, "handoff", printer.bold(name), detail=str(args.get("task", "")))
        start = time.monotonic()
        try:
            await call_next()
        except Exception as exc:
            ledger.errors.append((self.agent, f"{name}: {exc}"))
            printer.event(self.agent, "error", format_call(name, args), detail=str(exc), code="31",
                          seconds=time.monotonic() - start)
            raise
        seconds = time.monotonic() - start
        text = result_text(context.result)
        args = dict(context.arguments or {})  # the guardrail may have rewritten them
        if is_handoff:
            drafts = sum(1 for d in ledger.drafts if d.agent == name)
            printer.event(self.agent, "return", f"{name} done", detail=f"{drafts} draft(s)", seconds=seconds,
                          code="32")
            return
        if text.startswith("BLOCKED"):
            reason = text.split("submitted): ", 1)[-1]
            printer.event(self.agent, "block", format_call(name, args), detail="BLOCKED: " + reason, seconds=seconds,
                          code="31")
            return
        if _looks_like_error(text):
            ledger.errors.append((self.agent, f"{name}: {text[:200]}"))
            printer.event(self.agent, "error", format_call(name, args), detail=text, seconds=seconds, code="31")
            return
        if name == "submit_draft":
            data = parse_result(text)
            if isinstance(data, dict) and data.get("draft_id"):
                ledger.drafts.append(DraftRecord(
                    agent=self.agent, episode_id=str(args.get("episode_id", "")), kind=str(args.get("kind", "")),
                    title=str(args.get("title", "")), draft_id=str(data["draft_id"]),
                    status=str(data.get("status", "")), studio_url=str(data.get("studio_url", "")),
                    sources=len(args.get("sources") or []), has_html=bool(args.get("content_html")),
                ))
                ledger.submitted.append({**args, "draft_id": data["draft_id"]})
                printer.event(self.agent, "draft", format_call(name, args), detail=summarize(name, args, text),
                              seconds=seconds, code="32")
                return
            ledger.errors.append((self.agent, f"submit_draft: {text[:200]}"))
            printer.event(self.agent, "error", format_call(name, args), detail=text, seconds=seconds, code="31")
            return
        if name == "flag_for_human":
            printer.event(self.agent, "flag", "flag_for_human", detail=str(args.get("reason", "")), code="33")
            return
        printer.event(self.agent, "tool", format_call(name, args), detail=summarize(name, args, text), seconds=seconds)


class SubmitGuardrail(FunctionMiddleware):
    """Enforces the skills' rules on every submit_draft before it reaches the site.

    Tags author_agent as emcee/<agent>, checks kinds, sources and placeholder links, labels mock drafts, attaches the
    rendered deck HTML, and (in dry-run mode) short-circuits so nothing is queued.
    """

    def __init__(self, agent: str, run: RunContext) -> None:
        self.agent = agent
        self.run = run

    async def process(self, context: FunctionInvocationContext, call_next: Callable[[], Awaitable[None]]) -> None:
        if context.function.name != "submit_draft":
            await call_next()
            return
        args: dict[str, Any] = dict(context.arguments or {})
        args["author_agent"] = f"emcee/{self.agent}"
        args["sources"] = [s.strip() for s in (args.get("sources") or []) if isinstance(s, str) and s.strip()]
        if self.run.settings.mock and not str(args.get("title", "")).startswith(MOCK_TAG):
            args["title"] = f"{MOCK_TAG} {args.get('title', '')}".strip()
        kind = str(args.get("kind", ""))
        markdown = str(args.get("content_markdown", ""))
        if kind == "deck" and not args.get("content_html"):
            rendered = self.run.deck_html.get(safe_id(str(args.get("episode_id", ""))))
            if rendered and rendered[0] == markdown:
                args["content_html"] = rendered[1]
            elif rendered:
                self.run.ledger.blocked.append((self.agent, kind, "deck changed after render_deck"))
                context.result = ("BLOCKED by the Emcee guardrail (nothing was submitted): the deck Markdown changed "
                                  "after render_deck, so the rendered HTML is stale. Call render_deck with the final "
                                  "Markdown, then submit_draft again.")
                return
        problems = submission_problems(
            self.agent, kind=kind, title=str(args.get("title", "")), content_markdown=markdown,
            sources=args["sources"], content_html=args.get("content_html"),
        )
        if problems:
            joined = "; ".join(problems)
            self.run.ledger.blocked.append((self.agent, str(args.get("kind", "")), joined))
            context.result = (f"BLOCKED by the Emcee guardrail (nothing was submitted): {joined}. "
                              "Fix the draft and call submit_draft again, or call flag_for_human if you can't.")
            return
        context.arguments = args
        if self.run.settings.dry_run:
            self.run.dry_run_counter += 1
            draft_id = f"dry-run-{self.run.dry_run_counter}"
            context.result = json.dumps({
                "draft_id": draft_id, "status": "dry-run",
                "studio_url": f"{self.run.settings.studio_url}#draft-{draft_id}",
                "message": "Dry run: validated by the guardrail but NOT queued on the site.",
            })
            return
        await call_next()


class ModelTiming(ChatMiddleware):
    """Shows model round-trips in the trace (only when they take noticeable time, i.e. real LLM calls)."""

    def __init__(self, agent: str, run: RunContext) -> None:
        self.agent = agent
        self.run = run

    async def process(self, context: ChatContext, call_next: Callable[[], Awaitable[None]]) -> None:
        start = time.monotonic()
        await call_next()
        seconds = time.monotonic() - start
        if seconds >= 0.3 or self.run.printer.verbose:
            usage = getattr(context.result, "usage_details", None)
            tokens = ""
            if usage:
                total = getattr(usage, "total_token_count", None) or (usage.get("total_token_count")
                                                                        if isinstance(usage, dict) else None)
                tokens = f"{total} tokens" if total else ""
            self.run.printer.event(self.agent, "think", self.run.printer.dim("model"), detail=tokens, seconds=seconds)


def middleware_for(agent: str, run: RunContext) -> list[Any]:
    return [TraceMiddleware(agent, run), SubmitGuardrail(agent, run), ModelTiming(agent, run)]
