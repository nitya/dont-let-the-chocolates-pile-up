"""Fixtures: a throwaway Model Mondays site (uvicorn subprocess on a free port, temp MM_STATE_DIR).

The site needs `mcp>=2` while Agent Framework needs `mcp<2`, so the site runs in a separate interpreter:
$MM_SITE_PYTHON, else the first of (this python, python3, python) that can import the site's dependencies.
The agents run through the real CLI (`python -m agents.emcee`), which hops into agents/.venv when needed.
"""

from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SITE_DIR = REPO_ROOT / "site"
SITE_CHECK = "import fastapi, uvicorn, mcp.server.mcpserver"


def _site_python() -> str | None:
    candidates = [os.environ.get("MM_SITE_PYTHON"), sys.executable, shutil.which("python3"), shutil.which("python")]
    for candidate in dict.fromkeys(c for c in candidates if c):
        ok = subprocess.run([candidate, "-c", SITE_CHECK], capture_output=True, cwd=SITE_DIR).returncode == 0
        if ok:
            return candidate
    return None


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def site_url(tmp_path_factory: pytest.TempPathFactory):
    python = _site_python()
    if python is None:
        pytest.fail("No interpreter with the site's dependencies (pip install -r site/requirements.txt, "
                    "or set MM_SITE_PYTHON).")
    port = _free_port()
    state = tmp_path_factory.mktemp("mm-state")
    env = {**os.environ, "MM_STATE_DIR": str(state), "MM_WRITE_KEY": "", "MM_ADMIN_KEY": ""}
    proc = subprocess.Popen(
        [python, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port), "--log-level", "warning"],
        cwd=SITE_DIR, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
    )
    url = f"http://127.0.0.1:{port}"
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            if httpx.get(f"{url}/api/health", timeout=1).status_code == 200:
                break
        except httpx.HTTPError:
            time.sleep(0.2)
    else:
        proc.kill()
        pytest.fail(f"site did not start: {proc.stderr.read().decode()[-2000:] if proc.stderr else ''}")
    yield url
    proc.terminate()
    try:
        proc.wait(10)
    except subprocess.TimeoutExpired:
        proc.kill()


@pytest.fixture
def run_cli(site_url: str, tmp_path: Path):
    """Run `python -m agents.emcee ... --mock` against the test site; returns (CompletedProcess, ledger dict)."""
    import json

    def _run(*args: str, timeout: int = 180):
        out = tmp_path / f"ledger-{time.monotonic_ns()}.json"
        env = {**os.environ, "NO_COLOR": "1", "EMCEE_MARP": "off"}
        env.pop("EMCEE_REEXEC", None)
        proc = subprocess.run(
            [sys.executable, "-m", "agents.emcee", *args, "--mock", "--site", site_url, "--no-learn",
             "--json-out", str(out)],
            cwd=REPO_ROOT, env=env, capture_output=True, text=True, timeout=timeout,
        )
        ledger = json.loads(out.read_text()) if out.exists() else {}
        return proc, ledger

    return _run


def drafts(site_url: str, **params: str) -> list[dict]:
    resp = httpx.get(f"{site_url}/api/drafts", params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()
