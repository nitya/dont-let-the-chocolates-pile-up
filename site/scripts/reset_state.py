"""Wipe the drafts store between demo rehearsals.

Usage (from the repo root or from site/):
    python site/scripts/reset_state.py           # empty queue
    python site/scripts/reset_state.py --seed    # empty queue + sample drafts from site/seed/

Honors MM_STATE_DIR / MM_DATA_DIR like the app. A running server picks up the reset
automatically (open pages reload themselves).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SITE_DIR))

from app.config import Settings  # noqa: E402
from app.data import DataStore  # noqa: E402
from app.drafts import DraftStore, validate_submission  # noqa: E402

SEED_DIR = SITE_DIR / "seed"
FIELDS = ("episode_id", "kind", "title", "content_markdown", "author_agent", "sources", "content_html")


def load_seed(seed_dir: Path = SEED_DIR) -> list[dict]:
    items: list[dict] = []
    for path in sorted(seed_dir.glob("*.json")):
        items.extend(json.loads(path.read_text(encoding="utf-8")))
    return items


def reset(settings: Settings, seed: bool = False) -> int:
    data, store = DataStore(settings.data_dir), DraftStore(settings.state_dir)
    store.reset()
    count = 0
    if seed:
        for item in load_seed():
            fields = validate_submission(data, **{k: item.get(k) for k in FIELDS})
            draft = store.create(fields, status=item.get("status", "pending"))
            if item.get("reviewer_note") and draft["status"] != "pending":
                store.review(draft["id"], draft["status"], item["reviewer_note"])
            count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", action="store_true", help="load sample drafts from site/seed/*.json")
    args = parser.parse_args()
    settings = Settings.from_env()
    n = reset(settings, seed=args.seed)
    print(f"Reset drafts store at {settings.state_dir / 'drafts.json'}" + (f" with {n} seed drafts" if args.seed else ""))


if __name__ == "__main__":
    main()
