from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent.parent


def _default_data_dir() -> Path:
    # Repo layout first (site/../data); fall back to a packaged copy (site/data).
    for candidate in (SITE_DIR.parent / "data", SITE_DIR / "data"):
        if (candidate / "episodes.json").exists():
            return candidate
    return SITE_DIR.parent / "data"


def _resolve(path: str) -> Path:
    p = Path(path).expanduser()
    return p if p.is_absolute() else (SITE_DIR / p).resolve()


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    state_dir: Path
    write_key: str | None = None
    admin_key: str | None = None
    public_url: str | None = None
    allowed_hosts: list[str] = field(default_factory=list)

    @property
    def writes_open(self) -> bool:
        return not self.write_key

    @property
    def reviews_open(self) -> bool:
        return not self.admin_key

    @property
    def demo_mode(self) -> bool:
        return self.writes_open or self.reviews_open

    @classmethod
    def from_env(cls, **overrides) -> "Settings":
        env = os.environ
        data_dir = _resolve(env["MM_DATA_DIR"]) if env.get("MM_DATA_DIR") else _default_data_dir()
        state_dir = _resolve(env.get("MM_STATE_DIR") or ".state")
        public_url = env.get("MM_PUBLIC_URL") or (
            f"https://{env['WEBSITE_HOSTNAME']}" if env.get("WEBSITE_HOSTNAME") else None
        )
        hosts = [h.strip() for h in env.get("MM_ALLOWED_HOSTS", "").split(",") if h.strip()]
        if env.get("WEBSITE_HOSTNAME"):
            hosts.append(env["WEBSITE_HOSTNAME"])
        if env.get("CODESPACE_NAME"):
            domain = env.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN", "app.github.dev")
            port = env.get("PORT", "8000")
            hosts.append(f"{env['CODESPACE_NAME']}-{port}.{domain}")
        values = dict(
            data_dir=data_dir,
            state_dir=state_dir,
            write_key=env.get("MM_WRITE_KEY") or None,
            admin_key=env.get("MM_ADMIN_KEY") or None,
            public_url=public_url.rstrip("/") if public_url else None,
            allowed_hosts=hosts,
        )
        values.update(overrides)
        return cls(**values)
