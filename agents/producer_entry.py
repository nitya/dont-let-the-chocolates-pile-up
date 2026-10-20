"""Synchronous entry point for running the Producer specialist alone (used by the eval harness).

    from agents.producer_entry import run_producer
    markdown = run_producer("Wrap up S4-E09: write the recap and highlights.", mock=True)

* Reads episode data from the Model Mondays site MCP server (`site=` or $EMCEE_SITE_URL, default http://localhost:8000).
* By default it is a **dry run**: the guardrail validates every submit_draft call but nothing is queued on the site
  (pass `submit=True` to really queue drafts).
* Returns the Markdown of the drafts the producer submitted (recap, then highlights), or its final answer if it
  submitted nothing. `run_producer_detailed()` returns the full record (drafts, sources, tool calls, escalations).
* OpenTelemetry: Agent Framework emits `invoke_agent` / `chat` / `execute_tool` spans to the global tracer provider,
  wrapped in an `emcee.producer` span. Configure a provider in the caller, or set OTEL_EXPORTER_OTLP_ENDPOINT and one
  is configured for you.
* Works from any interpreter: if this one can't run Agent Framework (e.g. mcp>=2 is installed), the call is
  transparently executed in agents/.venv through a JSON subprocess (spans are then exported from that process via OTLP).
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import json
import os
import subprocess
import sys
from typing import Any

from agents.emcee._env import REPO_ROOT, SETUP_HINT, agents_env_problem, venv_python

_otel_configured = False


def run_producer(message: str, history: list[dict] | None = None, mock: bool = False, *,
                 site: str | None = None, submit: bool = False, trace: bool = False) -> str:
    """Run the producer on `message` and return the drafted Markdown (see module docstring)."""
    result = run_producer_detailed(message, history, mock, site=site, submit=submit, trace=trace)
    return result["markdown"]


def run_producer_detailed(message: str, history: list[dict] | None = None, mock: bool = False, *,
                          site: str | None = None, submit: bool = False, trace: bool = False) -> dict[str, Any]:
    payload = {"message": message, "history": history or [], "mock": mock, "site": site, "submit": submit,
               "trace": trace}
    if agents_env_problem() is not None:
        return _run_in_venv(payload)
    return _run_sync(_run(payload))


def _run_sync(coro: Any) -> Any:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:  # called from inside an event loop
        return pool.submit(asyncio.run, coro).result()


def _run_in_venv(payload: dict[str, Any]) -> dict[str, Any]:
    python = venv_python()
    if python is None:
        raise RuntimeError(f"Agent Framework can't run in this interpreter ({agents_env_problem()}). {SETUP_HINT}")
    env = {**os.environ, "EMCEE_REEXEC": "1",
           "PYTHONPATH": os.pathsep.join(p for p in (str(REPO_ROOT), os.environ.get("PYTHONPATH", "")) if p)}
    proc = subprocess.run([str(python), "-m", "agents.producer_entry"], input=json.dumps(payload), text=True,
                          capture_output=True, cwd=str(REPO_ROOT), env=env, timeout=900)
    if payload.get("trace") and proc.stderr:
        sys.stderr.write(proc.stderr)
    if proc.returncode != 0:
        raise RuntimeError(f"producer subprocess failed ({proc.returncode}): {proc.stderr[-2000:]}")
    return json.loads(proc.stdout.strip().splitlines()[-1])


def _maybe_configure_otel() -> None:
    global _otel_configured
    if _otel_configured or not os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"):
        return
    from opentelemetry import trace as otel_trace

    if type(otel_trace.get_tracer_provider()).__name__ in ("ProxyTracerProvider", "NoOpTracerProvider"):
        from agent_framework.observability import configure_otel_providers

        configure_otel_providers(service_name="emcee-producer")
    _otel_configured = True


async def _run(payload: dict[str, Any]) -> dict[str, Any]:
    from agent_framework import Message
    from agent_framework.observability import get_tracer

    from agents.emcee.config import Settings
    from agents.emcee.runctx import RunContext
    from agents.emcee.team import build_specialist
    from agents.emcee.trace import Printer, result_text

    _maybe_configure_otel()
    settings = Settings.from_env(site_url=payload.get("site"), mock=bool(payload.get("mock")) or None,
                                 dry_run=not payload.get("submit"))
    run = RunContext(settings=settings, printer=Printer(stream=sys.stderr, color=False,
                                                        quiet=not payload.get("trace")))
    if settings.mock:
        from agents.emcee.mock import producer_brain, MockChatClient

        client = MockChatClient(producer_brain(settings.site_url))
    else:
        from agents.emcee.config import make_chat_client

        client = make_chat_client(settings, run.closers)
    messages = [Message(role=m.get("role", "user"), contents=[str(m.get("content", ""))])
                for m in payload.get("history") or []]
    messages.append(Message(role="user", contents=[payload["message"]]))
    agent = build_specialist("producer", settings, run, client)
    with get_tracer().start_as_current_span("emcee.producer") as span:
        span.set_attribute("emcee.mock", settings.mock)
        span.set_attribute("emcee.dry_run", settings.dry_run)
        try:
            async with agent:
                response = await agent.run(messages)
        finally:
            await run.aclose()
        span.set_attribute("emcee.drafts", len(run.ledger.submitted))
    final = response.text or ""
    drafts = [{k: d.get(k) for k in ("kind", "title", "content_markdown", "sources", "draft_id")}
              for d in run.ledger.submitted]
    markdown = "\n\n".join(d["content_markdown"] for d in drafts if d.get("content_markdown")) or final
    tool_calls = []
    for msg in response.messages:
        for c in msg.contents:
            if c.type == "function_call":
                tool_calls.append({"name": c.name, "arguments": c.arguments})
            elif c.type == "function_result":
                tool_calls.append({"result_for": c.call_id, "result": result_text(c.result)[:500]})
    return {
        "markdown": markdown,
        "final_text": final,
        "drafts": drafts,
        "escalations": [{"agent": a, "reason": r} for a, r in run.ledger.escalations],
        "blocked": [{"agent": a, "kind": k, "problems": p, "resolved": run.ledger.resolved(a, k)}
                    for a, k, p in run.ledger.blocked],
        "errors": [{"agent": a, "error": e} for a, e in run.ledger.errors],
        "tool_calls": tool_calls,
        "mock": settings.mock,
        "dry_run": settings.dry_run,
    }


if __name__ == "__main__":
    data = json.loads(sys.stdin.read())
    print(json.dumps(_run_sync(_run(data)), ensure_ascii=False))
