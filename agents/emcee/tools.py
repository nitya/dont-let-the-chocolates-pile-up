"""Local function tools shared by the specialists: escalate to a human, lint a draft, render a Marp deck."""

from __future__ import annotations

import asyncio
import re
import shutil
import sys
from pathlib import Path
from typing import Annotated, Any

from agent_framework import tool
from pydantic import Field

from .config import OUT_DIR
from .rules import CHECK_SCRIPT, RENDER_SCRIPT, REPO_ROOT, normalize_episode_id
from .runctx import RunContext


def safe_id(episode_id: str) -> str:
    return normalize_episode_id(episode_id) or re.sub(r"[^a-z0-9-]", "", episode_id.lower())[:20] or "episode"


async def _run(cmd: list[str], timeout: float) -> tuple[int, str]:
    proc = await asyncio.create_subprocess_exec(*cmd, cwd=str(REPO_ROOT), stdout=asyncio.subprocess.PIPE,
                                                stderr=asyncio.subprocess.STDOUT)
    try:
        out, _ = await asyncio.wait_for(proc.communicate(), timeout)
    except TimeoutError:
        proc.kill()
        return 124, f"timed out after {timeout:.0f}s"
    return proc.returncode or 0, out.decode(errors="replace")


def marp_command(mode: str) -> bool:
    """Is a Marp renderer available? `auto` = a `marp` binary on PATH; `npx` = allow npx download; `off` = never."""
    if mode == "off":
        return False
    if shutil.which("marp"):
        return True
    return mode == "npx" and shutil.which("npx") is not None


def make_flag_tool(agent: str, run: RunContext) -> Any:
    @tool(name="flag_for_human", description=(
        "Escalate something a human must decide or fix (missing guest names, no transcript, conflicting data, an "
        "episode that isn't ready, a draft you could not ground). It is listed in Emcee's run report."))
    def flag_for_human(
        reason: Annotated[str, Field(description="One sentence: what the human needs to do and why.")],
        episode_id: Annotated[str, Field(description="Episode id the flag is about, e.g. 's4-e12'.")] = "",
    ) -> str:
        run.ledger.escalations.append((agent, f"{episode_id + ': ' if episode_id else ''}{reason}"))
        return "Flagged for a human reviewer. Continue with the rest of your task."

    return flag_for_human


def make_check_tool(agent: str, run: RunContext) -> Any:
    @tool(name="check_draft", description=(
        "Lint a recap/highlights/deck draft with the mm-recap skill's check.py before submitting: errors on "
        "placeholder links, empty link targets and a missing Sources section; warns on links that aren't in the "
        "episode's allowed sources (fine for Learn URLs you cite)."))
    async def check_draft(
        episode_id: Annotated[str, Field(description="Episode id, e.g. 's4-e09'.")],
        markdown: Annotated[str, Field(description="The full draft Markdown to check.")],
        name: Annotated[str, Field(description="Short file name for the draft, e.g. 'recap' or 'deck'.")] = "draft",
    ) -> str:
        eid = safe_id(episode_id)
        path = OUT_DIR / eid / f"{re.sub(r'[^a-z0-9_-]', '', name.lower()) or 'draft'}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markdown, encoding="utf-8")
        code, out = await _run([sys.executable, str(CHECK_SCRIPT), str(path), "--episode", eid], timeout=60)
        verdict = "PASS" if code == 0 else "FAIL (fix every ERROR before submitting)"
        return f"check.py {verdict}\n{out.strip()}"

    return check_draft


def _render_copy(markdown: str) -> str:
    """The deck is written for slides/episodes/; rewrite relative asset paths for agents/.out/decks/."""
    return markdown.replace("../../data/", "../../../data/").replace("../assets/", "../../../slides/assets/")


def make_render_tool(agent: str, run: RunContext) -> Any:
    @tool(name="render_deck", description=(
        "Render the Marp deck Markdown with the talk's chocolate theme (mm-deck render.py --standalone). Write image "
        "paths as if the deck lived in slides/episodes/ (banner: ../../data/banners/S<n>-E<n>.webp, icons: "
        "../assets/icons/<name>.svg). If rendering works, the standalone HTML is attached automatically when you "
        "call submit_draft(kind='deck'); otherwise the deck is submitted as Markdown only."))
    async def render_deck(
        episode_id: Annotated[str, Field(description="Episode id, e.g. 's4-e12'.")],
        markdown: Annotated[str, Field(description="The full Marp deck Markdown (with front matter).")],
    ) -> str:
        eid = safe_id(episode_id)
        if not marp_command(run.settings.marp):
            return ("Marp CLI is not available here (set EMCEE_MARP=npx to allow `npx @marp-team/marp-cli`). "
                    "Submit the deck as Markdown only and mention it in the reviewer notes.")
        deck = OUT_DIR / "decks" / f"{eid}.md"
        deck.parent.mkdir(parents=True, exist_ok=True)
        deck.write_text(_render_copy(markdown), encoding="utf-8")
        code, out = await _run([sys.executable, str(RENDER_SCRIPT), str(deck), "--standalone"], timeout=240)
        html_path = deck.with_suffix(".html")
        if code != 0 or not html_path.exists():
            return f"Render failed (exit {code}); submit Markdown only.\n{out.strip()[-800:]}"
        html = html_path.read_text(encoding="utf-8")
        run.deck_html[eid] = (markdown, html)
        return (f"Rendered {Path(html_path).relative_to(REPO_ROOT)} ({len(html) // 1024} KB standalone HTML). It will be "
                "attached to your submit_draft(kind='deck') call automatically.")

    return render_deck
