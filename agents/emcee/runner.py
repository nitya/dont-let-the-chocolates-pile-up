"""Run one Emcee request end to end and produce the run report."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx

from .config import ConfigError, Settings
from .rules import episode_label
from .runctx import RunContext
from .team import build_emcee, probe_learn
from .trace import Ledger, Printer


@dataclass
class RunResult:
    request: str
    final_text: str
    ledger: Ledger
    seconds: float
    ok: bool
    error: str | None = None

    def report_markdown(self, settings: Settings) -> str:
        lines = [f"### Emcee run report: {self.request}", ""]
        if self.error:
            lines += [f"**Run failed:** {self.error}", ""]
        mode = "mock mode (no LLM)" if settings.mock else settings.model_label()
        lines.append(f"{len(self.ledger.drafts)} draft(s) queued for human review in {self.seconds:.1f}s "
                     f"({self.ledger.tool_calls} tool calls, {mode}).")
        lines.append("")
        if self.ledger.drafts:
            lines += ["| Kind | Draft | Title | Agent |", "|---|---|---|---|"]
            for d in self.ledger.drafts:
                lines.append(f"| {d.kind} | [{d.draft_id}]({d.studio_url or settings.studio_url}) | "
                             f"{d.title.replace('|', '/')} | {d.agent} |")
            lines.append("")
        lines.append(f"**Review in the Studio:** {settings.studio_url}")
        lines.append("")
        caught = [b for b in self.ledger.blocked if self.ledger.resolved(b[0], b[1])]
        if caught:
            lines.append("**Caught by the guardrail and fixed:** " + "; ".join(f"{a} {k}: {p}" for a, k, p in caught))
            lines.append("")
        lines.append("**Needs a human:**")
        items = [f"- {a}: {r}" for a, r in self.ledger.escalations]
        items += [f"- {a} {k} draft blocked by the guardrail: {p}" for a, k, p in self.ledger.open_blocks()]
        items += [f"- {a} error: {e}" for a, e in self.ledger.errors]
        lines += items or ["- nothing"]
        return "\n".join(lines) + "\n"


def print_report(result: RunResult, settings: Settings, printer: Printer) -> None:
    led = result.ledger
    printer.write()
    printer.rule("Run report")
    if result.error:
        printer.write(printer._c("31", f"Run failed: {result.error}"))
    printer.write(f"{len(led.drafts)} draft(s) queued for human review · {led.tool_calls} tool calls · "
                  f"{result.seconds:.1f}s")
    for d in led.drafts:
        extra = " +html" if d.has_html else ""
        printer.write(f"  {printer.icons['draft']} {d.kind:<13} {d.draft_id:<10} {episode_label(d.episode_id):<7} "
                      f"{d.title[:58]:<58} {printer.dim(d.agent + extra)}")
    printer.write(f"  Studio: {printer.bold(settings.studio_url)}")
    for a, k, p in led.blocked:
        if led.resolved(a, k):
            printer.write(f"  {printer.icons['block']} guardrail caught a {k} draft from {a}, fixed on retry: {p}")
    if led.escalations or led.open_blocks() or led.errors:
        printer.write("Needs a human:")
        for a, r in led.escalations:
            printer.write(f"  {printer.icons['flag']} {a}: {r}")
        for a, k, p in led.open_blocks():
            printer.write(f"  {printer.icons['block']} {a} {k} (guardrail): {p}")
        for a, e in led.errors:
            printer.write(f"  {printer.icons['error']} {a}: {e[:200]}")
    else:
        printer.write("Needs a human: nothing (beyond reviewing the drafts)")


async def check_site(settings: Settings) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{settings.site_url}/api/health")
        resp.raise_for_status()
        return resp.json()


async def run_emcee(request: str, settings: Settings, printer: Printer | None = None) -> RunResult:
    printer = printer or Printer(verbose=settings.verbose)
    run = RunContext(settings=settings, printer=printer)
    start = time.monotonic()
    printer.rule(f"Emcee · {request!r}")
    printer.write(printer.dim(f"model: {settings.model_label()} · site: {settings.site_url} · "
                              f"specialists: {', '.join(settings.only) if settings.only else 'all'}"
                              + (" · DRY RUN (nothing is queued)" if settings.dry_run else "")))
    try:
        health = await check_site(settings)
        if health.get("write_key_required") and not settings.write_key:
            printer.write(printer._c("33", "site requires a write key: set MM_WRITE_KEY or submit_draft will fail"))
    except Exception as exc:  # noqa: BLE001
        return RunResult(request, "", run.ledger, time.monotonic() - start, False,
                         f"Model Mondays site not reachable at {settings.site_url} ({exc})")
    reason = await probe_learn(settings)
    run.learn_available = reason is None
    if reason:
        printer.write(printer.dim(f"Microsoft Learn MCP: {reason}; presenter will flag missing Learn links"))
    printer.event("emcee", "start", printer.bold("plan"), detail=request)
    try:
        agent = build_emcee(settings, run)
        async with agent:
            response = await agent.run(request)
        final = response.text or ""
    except ConfigError as exc:
        return RunResult(request, "", run.ledger, time.monotonic() - start, False, str(exc))
    except Exception as exc:  # noqa: BLE001 - report instead of a stack trace on stage
        run.ledger.errors.append(("emcee", f"{type(exc).__name__}: {exc}"))
        return RunResult(request, "", run.ledger, time.monotonic() - start, False, f"{type(exc).__name__}: {exc}")
    seconds = time.monotonic() - start
    printer.event("emcee", "done", printer.bold("report"), seconds=seconds, code="32")
    ok = not run.ledger.errors
    return RunResult(request, final, run.ledger, seconds, ok)
