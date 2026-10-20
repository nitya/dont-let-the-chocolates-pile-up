"""ASSERT callable target for the Emcee Producer.

ASSERT imports `evals.producer.target:chat` (run from the repo root). The Producer runs through
`agents.producer_entry` in dry-run mode: drafts are validated but never queued on the site.

The agents live in their own venv (Agent Framework needs mcp<2 and openai>=3; ASSERT's LiteLLM needs openai<3),
so the call crosses a process boundary and in-process OTel capture can't see its spans. Until spans are exported to
Phoenix (see evals/README.md), the response carries a "Grounding evidence" appendix — tool calls, sources, guardrail
blocks, and escalations — so the judge can cite how each claim and link was produced.

Env: MM_SITE_URL / EMCEE_SITE_URL (default http://localhost:8000), EMCEE_EVAL_MOCK=1 to use the scripted model.
"""

from __future__ import annotations

import json
import os

from agents.producer_entry import run_producer_detailed

MAX_RESULT_CHARS = 600


def _short(value: object) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return text if len(text) <= MAX_RESULT_CHARS else text[:MAX_RESULT_CHARS] + " …"


def _evidence(result: dict) -> str:
    lines = ["", "---", "## Grounding evidence (appended by the eval target)", "", "### Tool calls"]
    for call in result.get("tool_calls") or []:
        if "name" in call:
            lines.append(f"- call `{call['name']}` {_short(call.get('arguments', {}))}")
        else:
            lines.append(f"  - result: {_short(call.get('result', ''))}")
    for draft in result.get("drafts") or []:
        lines.append(f"\n### Draft `{draft.get('kind')}` sources")
        lines += [f"- {s}" for s in draft.get("sources") or []] or ["- (none)"]
    if result.get("blocked"):
        lines += ["", "### Blocked by guardrail"] + [f"- {_short(b)}" for b in result["blocked"]]
    if result.get("escalations"):
        lines += ["", "### Flagged for a human"] + [f"- {e.get('reason')}" for e in result["escalations"]]
    if result.get("errors"):
        lines += ["", "### Errors"] + [f"- {_short(e)}" for e in result["errors"]]
    return "\n".join(lines)


def chat(message: str, history: list[dict[str, str]] | None = None) -> str:
    result = run_producer_detailed(
        message,
        history or [],
        mock=os.environ.get("EMCEE_EVAL_MOCK") == "1",
        site=os.environ.get("EMCEE_SITE_URL") or os.environ.get("MM_SITE_URL"),
    )
    body = result.get("markdown") or result.get("final_text") or ""
    return body + "\n" + _evidence(result)
