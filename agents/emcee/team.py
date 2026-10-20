"""Builds the Emcee team: four specialist agents (each with the site MCP server, some with Microsoft Learn MCP) exposed
to the Emcee orchestrator as tools via `Agent.as_tool()`."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

from agent_framework import Agent, MCPStreamableHTTPTool

from . import SPECIALISTS
from .config import Settings, make_chat_client
from .middleware import middleware_for
from .rules import load_skill, skill_rules
from .runctx import RunContext
from .tools import make_check_tool, make_flag_tool, make_render_tool

PROMPTS = Path(__file__).resolve().parent / "prompts"

SITE_TOOLS: dict[str, list[str]] = {
    "emcee": ["get_episode", "search_episodes", "list_episodes", "get_series_stats", "list_drafts"],
    "coordinator": ["get_episode", "search_episodes", "list_episodes", "list_drafts", "submit_draft"],
    "producer": ["get_episode", "get_transcript", "list_drafts", "submit_draft"],
    "presenter": ["get_episode", "search_episodes", "list_episodes", "list_drafts", "submit_draft"],
    "publisher": ["get_episode", "list_drafts", "submit_draft"],
}
LEARN_TOOLS = ["microsoft_docs_search", "microsoft_docs_fetch"]

DESCRIPTIONS = {
    "coordinator": "Guest coordinator: writes the guest brief and the run-of-show for an upcoming episode.",
    "producer": "Post-show producer: writes the grounded recap and highlights for an episode that has aired.",
    "presenter": "Presenter: builds the Marp slide deck for an episode, grounded in show data and Microsoft Learn.",
    "publisher": "Publisher: writes the announcement and social posts; run it last so it can reuse other drafts.",
}


def render_prompt(name: str, settings: Settings, **extra: str) -> str:
    text = (PROMPTS / f"{name}.md").read_text(encoding="utf-8")
    values = {
        "today": dt.date.today().isoformat(),
        "site_url": settings.site_url,
        "studio_url": settings.studio_url,
        "shared_rules": skill_rules("mm-recap"),
        "skill_mm_recap": load_skill("mm-recap"),
        "skill_mm_deck": load_skill("mm-deck"),
        "only_clause": "",
        "learn_note": "",
        **extra,
    }
    for key, value in values.items():
        text = text.replace("{" + key + "}", value)
    return text


def site_mcp(settings: Settings, agent: str) -> MCPStreamableHTTPTool:
    headers = {"Authorization": f"Bearer {settings.write_key}"} if settings.write_key else None
    return MCPStreamableHTTPTool(
        name="model-mondays",
        url=settings.mcp_url,
        description="Model Mondays site: episode data and the human review queue",
        allowed_tools=SITE_TOOLS[agent],
        load_prompts=False,
        request_timeout=60,
        static_headers=headers,
    )


def learn_mcp(settings: Settings) -> MCPStreamableHTTPTool:
    return MCPStreamableHTTPTool(
        name="microsoft-learn",
        url=settings.learn_url,
        description="Microsoft Learn documentation search and fetch",
        allowed_tools=LEARN_TOOLS,
        load_prompts=False,
        request_timeout=30,
    )


async def probe_learn(settings: Settings) -> str | None:
    """Return None if the Learn MCP server is reachable, else the reason (the presenter then works without it)."""
    if not settings.learn:
        return "disabled (--no-learn)"
    try:
        async with learn_mcp(settings):
            return None
    except Exception as exc:  # noqa: BLE001 - any failure just means "no Learn grounding this run"
        return f"unreachable ({type(exc).__name__})"


class EmceeAgent(Agent):
    """The orchestrator. Opening it also opens every specialist (and so all their MCP connections)."""

    def __init__(self, *args: Any, team: list[Agent], run: RunContext, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.team = team
        self.run_context = run

    async def open(self) -> "EmceeAgent":
        await super().open()
        self._async_exit_stack.push_async_callback(self.run_context.aclose)
        try:
            for member in self.team:
                await self._async_exit_stack.enter_async_context(member)
        except BaseException:
            await self.close()
            raise
        return self


def _client_factory(settings: Settings, run: RunContext) -> Any:
    if settings.mock:
        from .mock import SPECIALIST_BRAINS, MockChatClient, emcee_brain

        delay = settings.mock_delay

        def make(agent: str) -> Any:
            if agent == "emcee":
                brain = emcee_brain(settings.only, settings.site_url)
            elif agent == "publisher":
                brain = SPECIALIST_BRAINS[agent](settings.site_url, settings.mock_fault)
            else:
                brain = SPECIALIST_BRAINS[agent](settings.site_url)
            return MockChatClient(brain, delay=delay)

        return make
    shared = make_chat_client(settings, run.closers)
    return lambda agent: shared


def build_specialist(name: str, settings: Settings, run: RunContext, client: Any) -> Agent:
    tools: list[Any] = [site_mcp(settings, name), make_flag_tool(name, run)]
    extra: dict[str, str] = {}
    if name in ("producer", "presenter"):
        tools.append(make_check_tool(name, run))
    if name == "presenter":
        tools.append(make_render_tool(name, run))
        if run.learn_available:
            tools.append(learn_mcp(settings))
        else:
            extra["learn_note"] = (" (NOT available in this run: ground product claims in the episode data only and "
                                   "flag_for_human that Learn links must be added)")
    return Agent(
        client,
        render_prompt(name, settings, **extra),
        name=name,
        description=DESCRIPTIONS[name],
        tools=tools,
        middleware=middleware_for(name, run),
    )


def build_emcee(settings: Settings, run: RunContext) -> EmceeAgent:
    """Build the full team. Call `await agent.open()` / `async with agent` before running it."""
    make_client = _client_factory(settings, run)
    names = [s for s in SPECIALISTS if not settings.only or s in settings.only]
    team = [build_specialist(n, settings, run, make_client(n)) for n in names]
    only_clause = ""
    if settings.only:
        only_clause = (f"\n**This run is limited to: {', '.join(names)}.** Only delegate to those specialists, "
                       "even if the playbook lists others.")
    tools: list[Any] = [site_mcp(settings, "emcee"), make_flag_tool("emcee", run)]
    tools += [m.as_tool(name=m.name, description=m.description, arg_name="task",
                        arg_description="Precise task: episode id, what to produce, and anything to watch out for.")
              for m in team]
    return EmceeAgent(
        make_client("emcee"),
        render_prompt("emcee", settings, only_clause=only_clause),
        name="emcee",
        description="Emcee: plans and delegates Model Mondays content work to the specialists and reports back.",
        tools=tools,
        middleware=middleware_for("emcee", run),
        team=team,
        run=run,
    )
