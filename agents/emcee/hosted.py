"""Foundry hosted-agent entry point: serves Emcee over the Responses protocol with the Agent Framework hosting adapter.

    python -m agents.emcee.hosted                # listens on $PORT or 8088 (the Foundry hosted-agent port)
    EMCEE_MOCK=1 python -m agents.emcee.hosted   # same, with the scripted mock agents (no model needed)

Then: POST http://localhost:8088/responses  {"input": "prep S4-E12"}

Uses `agent_framework_foundry_hosting.ResponsesHostServer` (agent-framework-foundry-hosting, beta) with a per-request
factory, so every request gets a fresh team, fresh MCP connections and its own run ledger.
"""

from __future__ import annotations

import logging
import os
import sys

from ._env import ensure_agents_env

if __name__ == "__main__":
    ensure_agents_env("agents.emcee.hosted")

from .config import Settings  # noqa: E402
from .runctx import RunContext  # noqa: E402
from .team import build_emcee, probe_learn  # noqa: E402
from .trace import Printer  # noqa: E402

logger = logging.getLogger("emcee.hosted")


async def create_emcee():
    """Per-request factory: the host enters/exits the returned agent (and so the whole team) for each request."""
    settings = Settings.from_env()
    run = RunContext(settings=settings, printer=Printer(stream=sys.stderr, color=False))
    run.learn_available = (await probe_learn(settings)) is None
    return build_emcee(settings, run)


def build_server():
    from agent_framework_foundry_hosting import ResponsesHostServer

    return ResponsesHostServer(agent=create_emcee)


def main() -> None:
    logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
    settings = Settings.from_env()
    logger.info("Emcee hosted agent · model: %s · site: %s", settings.model_label(), settings.site_url)
    build_server().run()


if __name__ == "__main__":
    main()
