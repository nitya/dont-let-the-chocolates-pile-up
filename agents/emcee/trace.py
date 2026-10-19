"""Stage-friendly run trace (plain terminal, optional ANSI color) and the run ledger (drafts, escalations, blocks)."""

from __future__ import annotations

import json
import os
import shutil
import sys
import threading
import time
from dataclasses import dataclass, field
from typing import Any, TextIO

from .rules import episode_label

AGENT_COLORS = {"emcee": "35", "coordinator": "36", "producer": "33", "presenter": "34", "publisher": "32"}
DEPTH = {"emcee": 0}

UNICODE_ICONS = {"start": "▶", "tool": "·", "handoff": "⇢", "return": "⇠", "draft": "✎", "block": "⛔",
                 "flag": "⚑", "error": "✗", "think": "…", "done": "✓", "rule": "━"}
ASCII_ICONS = {"start": ">", "tool": "-", "handoff": "->", "return": "<-", "draft": "*", "block": "X",
               "flag": "!", "error": "x", "think": "~", "done": "ok", "rule": "="}


def parse_result(text: str) -> Any:
    """MCP results arrive as JSON text (lists wrapped as {"result": [...]}); fall back to the raw string."""
    try:
        value = json.loads(text)
    except (TypeError, ValueError):
        return text
    if isinstance(value, dict) and set(value) == {"result"}:
        return value["result"]
    return value


def result_text(result: Any) -> str:
    if result is None:
        return ""
    if isinstance(result, str):
        return result
    if isinstance(result, list):
        parts = []
        for item in result:
            text = getattr(item, "text", None)
            parts.append(text if isinstance(text, str) else str(item))
        return "\n".join(parts)
    text = getattr(result, "text", None)
    return text if isinstance(text, str) else str(result)


def _short(value: Any, limit: int = 32) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def format_call(name: str, args: dict[str, Any]) -> str:
    if name == "submit_draft":
        return f"submit_draft({args.get('kind')}, {_short(args.get('title', ''), 40)!r})"
    if name in ("check_draft", "render_deck"):
        return f"{name}({args.get('episode_id', '')}, {len(args.get('markdown', '') or '')} chars)"
    if name in AGENT_COLORS:
        return f"{name}"
    inner = ", ".join(f"{k}={_short(v, 28)}" for k, v in args.items() if v not in (None, "", []))
    return f"{name}({inner})"


def summarize(name: str, args: dict[str, Any], text: str) -> str:
    data = parse_result(text)
    try:
        if name == "get_episode" and isinstance(data, dict):
            yt = "transcript" if data.get("has_transcript") else "no transcript"
            return (f"{episode_label(data['id'])} “{data.get('title')}” · {data.get('display_status')} "
                    f"{data.get('date')} · {len(data.get('chapters') or [])} chapters · {yt}")
        if name in ("search_episodes", "list_episodes") and isinstance(data, list):
            ids = ", ".join(r.get("id", "?") for r in data[:4])
            return f"{len(data)} episodes: {ids}{'…' if len(data) > 4 else ''}"
        if name == "list_drafts" and isinstance(data, list):
            pending = sum(1 for d in data if d.get("status") == "pending")
            return f"{len(data)} drafts ({pending} pending)"
        if name == "get_transcript":
            return "not available yet → description + chapters" if "not available" in text else f"{len(text):,} chars"
        if name == "get_series_stats" and isinstance(data, dict):
            nxt = (data.get("up_next") or {}).get("id")
            return f"{data.get('episodes_total')} episodes · up next {nxt}"
        if name == "submit_draft" and isinstance(data, dict) and data.get("draft_id"):
            return f"draft {data['draft_id']} · {args.get('kind')} · {data.get('status')}"
        if name == "microsoft_docs_search" and isinstance(data, dict):
            results = data.get("results") or []
            return f"{len(results)} Learn results · {_short(results[0].get('title', ''), 40) if results else ''}"
        if name == "microsoft_docs_fetch":
            return f"{len(text):,} chars of Learn docs"
    except Exception:  # noqa: BLE001 - summaries are cosmetic
        pass
    first = next((line.strip() for line in text.splitlines() if line.strip()), "")
    return _short(first, 90)


@dataclass
class DraftRecord:
    agent: str
    episode_id: str
    kind: str
    title: str
    draft_id: str
    status: str
    studio_url: str
    sources: int
    has_html: bool


@dataclass
class Ledger:
    drafts: list[DraftRecord] = field(default_factory=list)
    escalations: list[tuple[str, str]] = field(default_factory=list)  # (agent, reason)
    blocked: list[tuple[str, str, str]] = field(default_factory=list)  # (agent, kind, problems)
    errors: list[tuple[str, str]] = field(default_factory=list)  # (agent, error)
    tool_calls: int = 0
    submitted: list[dict[str, Any]] = field(default_factory=list)  # full submit_draft args (for tests/evals)

    def resolved(self, agent: str, kind: str) -> bool:
        """A blocked draft counts as resolved once the same agent got the same kind through."""
        return any(d.agent == agent and d.kind == kind for d in self.drafts)

    def open_blocks(self) -> list[tuple[str, str, str]]:
        return [b for b in self.blocked if not self.resolved(b[0], b[1])]

    def to_dict(self) -> dict[str, Any]:
        return {
            "drafts": [d.__dict__ for d in self.drafts],
            "escalations": [{"agent": a, "reason": r} for a, r in self.escalations],
            "blocked": [{"agent": a, "kind": k, "problems": p, "resolved": self.resolved(a, k)}
                        for a, k, p in self.blocked],
            "errors": [{"agent": a, "error": e} for a, e in self.errors],
            "tool_calls": self.tool_calls,
        }


class Printer:
    def __init__(self, stream: TextIO | None = None, *, color: bool | None = None, quiet: bool = False,
                 verbose: bool = False) -> None:
        self.stream = stream or sys.stdout
        self.quiet = quiet
        self.verbose = verbose
        isatty = getattr(self.stream, "isatty", lambda: False)()
        self.color = (isatty and "NO_COLOR" not in os.environ) if color is None else color
        encoding = (getattr(self.stream, "encoding", "") or "").lower()
        ascii_only = os.environ.get("EMCEE_ASCII") == "1" or ("utf" not in encoding and encoding != "")
        self.icons = ASCII_ICONS if ascii_only else UNICODE_ICONS
        self.t0 = time.monotonic()
        self._lock = threading.Lock()
        self.width = max(100, min(shutil.get_terminal_size((140, 40)).columns, 180))

    def _c(self, code: str, text: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self.color else text

    def dim(self, text: str) -> str:
        return self._c("2", text)

    def bold(self, text: str) -> str:
        return self._c("1", text)

    def write(self, text: str = "") -> None:
        if self.quiet:
            return
        with self._lock:
            self.stream.write(text + "\n")
            self.stream.flush()

    def rule(self, title: str) -> None:
        bar = self.icons["rule"] * 3
        self.write(self.bold(f"{bar} {title} {bar}"))

    def event(self, agent: str, icon: str, text: str, *, detail: str = "", seconds: float | None = None,
              code: str | None = None) -> None:
        elapsed = time.monotonic() - self.t0
        indent = "" if DEPTH.get(agent, 1) == 0 else "  "
        who = self._c(AGENT_COLORS.get(agent, "37"), f"{agent:<11}")
        mark = self.icons[icon]
        if code:
            mark = self._c(code, mark)
        timing = f"  {seconds * 1000:.0f} ms" if seconds is not None and seconds < 1 else (
            f"  {seconds:.1f} s" if seconds is not None else "")
        head = f"{elapsed:6.1f}s  {indent}{who} {mark} {text}"
        plain_len = len(f"{elapsed:6.1f}s  {indent}{agent:<11} {self.icons[icon]} {text}")
        room = self.width - plain_len - len(timing) - 4
        if detail and room > 12:
            detail = detail if len(detail) <= room else detail[: room - 1] + "…"
            head += self.dim("  → ") + detail
        self.write(head + self.dim(timing))
