"""Interpreter checks (stdlib only).

Agent Framework 1.22 needs `mcp<2`, while the Model Mondays site pins `mcp==2.3`, so the agents live in their own
virtualenv (`agents/.venv`). Entry points call `ensure_agents_env()` to hop into that venv when they are started with
an interpreter that can't run them (for example the shared Python that serves the site).
"""

from __future__ import annotations

import importlib.metadata
import importlib.util
import os
import sys
from pathlib import Path

AGENTS_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = AGENTS_DIR.parent
VENV_DIRS = (AGENTS_DIR / ".venv",)
SETUP_HINT = (
    "python -m venv agents/.venv && agents/.venv/bin/pip install -r agents/requirements.txt"
)


def agents_env_problem() -> str | None:
    """Return why this interpreter can't run the agents, or None if it can."""
    if importlib.util.find_spec("agent_framework") is None:
        return "agent-framework is not installed"
    if importlib.util.find_spec("agent_framework_foundry") is None:
        return "agent-framework-foundry is not installed"
    try:
        mcp_version = importlib.metadata.version("mcp")
    except importlib.metadata.PackageNotFoundError:
        return "mcp is not installed"
    if int(mcp_version.split(".")[0]) >= 2:
        return f"mcp {mcp_version} is installed, but agent-framework needs mcp<2"
    return None


def venv_python() -> Path | None:
    for venv in VENV_DIRS:
        for candidate in (venv / "bin" / "python", venv / "Scripts" / "python.exe"):
            if candidate.exists():
                return candidate
    return None


def ensure_agents_env(module: str) -> None:
    """Re-exec `python -m <module> <args>` inside agents/.venv when the current interpreter can't run the agents."""
    problem = agents_env_problem()
    if problem is None:
        return
    target = venv_python()
    if target is None or os.environ.get("EMCEE_REEXEC") == "1":
        sys.stderr.write(f"emcee: {problem}.\nSet up the agents environment first:\n  {SETUP_HINT}\n")
        raise SystemExit(2)
    env = {**os.environ, "EMCEE_REEXEC": "1"}
    env["PYTHONPATH"] = os.pathsep.join(p for p in (str(REPO_ROOT), env.get("PYTHONPATH", "")) if p)
    sys.stdout.flush()
    sys.stderr.flush()
    os.execve(str(target), [str(target), "-m", module, *sys.argv[1:]], env)
