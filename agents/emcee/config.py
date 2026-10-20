"""Settings from environment / agents/.env, and the chat-client factory (Foundry or Azure OpenAI, never GitHub Models)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .rules import REPO_ROOT

AGENTS_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = AGENTS_DIR / ".out"
LEARN_MCP_URL = "https://learn.microsoft.com/api/mcp"
FORBIDDEN_HOSTS = ("models.github.ai", "models.inference.ai.azure.com", "models.github.com")


def load_dotenv_file() -> None:
    """Load agents/.env (if present) without overriding variables that are already set."""
    path = AGENTS_DIR / ".env"
    if not path.exists():
        return
    try:
        from dotenv import load_dotenv
    except ImportError:  # pragma: no cover - python-dotenv is a dependency of agent-framework-core
        return
    load_dotenv(path, override=False)


def _env(*names: str, default: str | None = None) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value.strip()
    return default


def _flag(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    return default if value is None else value.strip().lower() in ("1", "true", "yes", "on")


@dataclass
class Settings:
    site_url: str = "http://localhost:8000"
    write_key: str | None = None
    mock: bool = False
    learn: bool = True
    learn_url: str = LEARN_MCP_URL
    only: list[str] = field(default_factory=list)
    provider: str = "auto"  # auto | foundry | azure_openai
    foundry_endpoint: str | None = None
    foundry_model: str | None = None
    aoai_endpoint: str | None = None
    aoai_deployment: str | None = None
    aoai_api_key: str | None = None
    aoai_api_version: str | None = None
    marp: str = "auto"  # auto | npx | off
    dry_run: bool = False
    verbose: bool = False
    mock_delay: float = 0.0
    mock_fault: str | None = None  # "placeholder": publisher first tries a forbidden link

    @property
    def mcp_url(self) -> str:
        return self.site_url.rstrip("/") + "/mcp"

    @property
    def studio_url(self) -> str:
        return self.site_url.rstrip("/") + "/studio"

    @classmethod
    def from_env(cls, **overrides: Any) -> "Settings":
        load_dotenv_file()
        s = cls(
            site_url=_env("EMCEE_SITE_URL", "MM_SITE_URL", default="http://localhost:8000") or "http://localhost:8000",
            write_key=_env("MM_WRITE_KEY"),
            mock=_flag("EMCEE_MOCK"),
            learn=_flag("EMCEE_LEARN_MCP", True),
            learn_url=_env("EMCEE_LEARN_MCP_URL", default=LEARN_MCP_URL) or LEARN_MCP_URL,
            provider=(_env("EMCEE_MODEL_PROVIDER", default="auto") or "auto").lower(),
            foundry_endpoint=_env("FOUNDRY_PROJECT_ENDPOINT", "AZURE_AI_PROJECT_ENDPOINT"),
            foundry_model=_env("FOUNDRY_MODEL", "AZURE_AI_MODEL_DEPLOYMENT_NAME"),
            aoai_endpoint=_env("AZURE_OPENAI_ENDPOINT"),
            aoai_deployment=_env("AZURE_OPENAI_DEPLOYMENT", "AZURE_OPENAI_MODEL", "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
            aoai_api_key=_env("AZURE_OPENAI_API_KEY"),
            aoai_api_version=_env("AZURE_OPENAI_API_VERSION"),
            marp=(_env("EMCEE_MARP", default="auto") or "auto").lower(),
            mock_delay=float(_env("EMCEE_MOCK_DELAY", default="0") or 0),
            mock_fault=_env("EMCEE_MOCK_FAULT"),
        )
        for key, value in overrides.items():
            if value is not None:
                setattr(s, key, value)
        s.site_url = s.site_url.rstrip("/")
        return s

    def resolved_provider(self) -> str:
        if self.provider in ("foundry", "azure_openai"):
            return self.provider
        if self.foundry_endpoint and self.foundry_model:
            return "foundry"
        if self.aoai_endpoint and self.aoai_deployment:
            return "azure_openai"
        return "none"

    def model_label(self) -> str:
        if self.mock:
            return "mock (scripted, no LLM)"
        provider = self.resolved_provider()
        if provider == "foundry":
            return f"Foundry · {self.foundry_model}"
        if provider == "azure_openai":
            return f"Azure OpenAI · {self.aoai_deployment}"
        return "not configured"


class ConfigError(RuntimeError):
    pass


def _check_not_github_models(url: str | None) -> None:
    if url and any(host in url for host in FORBIDDEN_HOSTS):
        raise ConfigError(f"{url} is a GitHub Models endpoint; Emcee only runs on Microsoft Foundry / Azure OpenAI.")


def make_chat_client(settings: Settings, closers: list[Any] | None = None) -> Any:
    """Build the real chat client. One instance is shared by all agents (supported by the framework).

    Async credentials it creates are appended to `closers` (call `await c.close()` when the run is over).
    """
    closers = closers if closers is not None else []
    provider = settings.resolved_provider()
    if provider == "none":
        raise ConfigError(
            "No model configured. Set FOUNDRY_PROJECT_ENDPOINT + FOUNDRY_MODEL (Microsoft Foundry) or "
            "AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_DEPLOYMENT (Azure OpenAI) in agents/.env, or run with --mock."
        )
    if provider == "foundry":
        if not (settings.foundry_endpoint and settings.foundry_model):
            raise ConfigError("EMCEE_MODEL_PROVIDER=foundry needs FOUNDRY_PROJECT_ENDPOINT and FOUNDRY_MODEL.")
        _check_not_github_models(settings.foundry_endpoint)
        from azure.identity.aio import DefaultAzureCredential
        from agent_framework_foundry import FoundryChatClient

        credential = DefaultAzureCredential()
        closers.append(credential)
        return FoundryChatClient(
            project_endpoint=settings.foundry_endpoint,
            model=settings.foundry_model,
            credential=credential,
        )
    if not (settings.aoai_endpoint and settings.aoai_deployment):
        raise ConfigError("EMCEE_MODEL_PROVIDER=azure_openai needs AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_DEPLOYMENT.")
    _check_not_github_models(settings.aoai_endpoint)
    from agent_framework_openai import OpenAIChatClient

    kwargs: dict[str, Any] = {"model": settings.aoai_deployment, "azure_endpoint": settings.aoai_endpoint}
    if settings.aoai_api_version:
        kwargs["api_version"] = settings.aoai_api_version
    if settings.aoai_api_key:
        kwargs["api_key"] = settings.aoai_api_key
    else:
        from azure.identity.aio import DefaultAzureCredential

        kwargs["credential"] = DefaultAzureCredential()
        closers.append(kwargs["credential"])
    return OpenAIChatClient(**kwargs)


__all__ = ["Settings", "ConfigError", "make_chat_client", "OUT_DIR", "REPO_ROOT", "AGENTS_DIR"]
