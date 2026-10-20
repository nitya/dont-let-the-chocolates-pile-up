"""Per-run shared state: settings, trace printer, ledger and caches. One instance per Emcee run (or hosted request)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .config import Settings
from .trace import Ledger, Printer


@dataclass
class RunContext:
    settings: Settings
    printer: Printer
    ledger: Ledger = field(default_factory=Ledger)
    # normalized episode_id -> (deck Markdown that was rendered, standalone HTML) from render_deck
    deck_html: dict[str, tuple[str, str]] = field(default_factory=dict)
    learn_available: bool = False
    dry_run_counter: int = 0
    closers: list[Any] = field(default_factory=list)  # async credentials etc. closed with the run

    async def aclose(self) -> None:
        while self.closers:
            try:
                await self.closers.pop().close()
            except Exception:  # noqa: BLE001 - best effort cleanup
                pass
