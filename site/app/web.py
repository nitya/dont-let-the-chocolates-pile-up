"""Server-rendered pages + JSON API."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from markupsafe import Markup
from pydantic import BaseModel, Field

from .data import fmt_duration
from .drafts import KINDS, DraftError, now_iso, summary
from .render import render_archive, render_markdown
from .services import Services, key_from_headers, key_matches

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
ADMIN_COOKIE = "mm_admin"

# Episode page sections fed by approved drafts: (anchor, label, kinds)
SECTIONS = [
    ("recap", "Recap", ("recap",)),
    ("highlights", "Highlights", ("highlights",)),
    ("deck", "Deck", ("deck",)),
    ("social", "Social", ("social",)),
    ("prep", "Prep", ("brief", "run_of_show", "announcement", "episode")),
]
KIND_LABELS = {
    "recap": "Recap", "highlights": "Highlights", "brief": "Guest brief", "run_of_show": "Run of show",
    "social": "Social post", "deck": "Deck", "announcement": "Announcement", "episode": "Episode proposal",
}


def _fmt_date(value: str | None, fmt: str = "%b %d, %Y") -> str:
    if not value:
        return ""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime(fmt)
    except ValueError:
        return value


def _fmt_num(value: int | None) -> str:
    if value is None:
        return "–"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 10_000:
        return f"{value / 1000:.0f}K"
    if value >= 1_000:
        return f"{value / 1000:.1f}K"
    return str(value)


TEMPLATES.env.filters.update(
    date=_fmt_date,
    num=_fmt_num,
    duration=fmt_duration,
    md=lambda text: Markup(render_markdown(text)),
    kind_label=lambda k: KIND_LABELS.get(k, k),
)


class DraftIn(BaseModel):
    episode_id: str
    kind: str
    title: str
    content_markdown: str = ""
    author_agent: str = "unknown-agent"
    sources: list[str] = Field(default_factory=list)
    content_html: str | None = None


class ReviewIn(BaseModel):
    note: str | None = None


def build_router(services: Services) -> APIRouter:
    router = APIRouter()
    data, drafts, settings = services.data, services.drafts, services.settings

    # ---- auth helpers -------------------------------------------------------------
    def admin_key_from(request: Request) -> str | None:
        return (
            key_from_headers(request.headers, extra="x-admin-key")
            or request.cookies.get(ADMIN_COOKIE)
            or request.query_params.get("key")
        )

    def is_admin(request: Request) -> bool:
        return key_matches(settings.admin_key, admin_key_from(request))

    def require_admin(request: Request) -> None:
        if not is_admin(request):
            raise HTTPException(401, "Admin key required (x-admin-key / Authorization: Bearer header, studio login cookie, or ?key=).")

    def require_writer(request: Request) -> None:
        if not key_matches(settings.write_key, key_from_headers(request.headers)):
            raise HTTPException(401, "Write key required (Authorization: Bearer <key> or x-api-key header).")

    def page(request: Request, name: str, **ctx: Any) -> HTMLResponse:
        ctx.update(
            settings=settings,
            seasons=data.seasons(),
            now=now_iso(),
            epoch=drafts.epoch,
            is_admin=is_admin(request),
            kinds=KINDS,
            kind_labels=KIND_LABELS,
        )
        return TEMPLATES.TemplateResponse(request, name, ctx)

    def episode_or_404(episode_id: str) -> dict:
        ep = data.episode(episode_id)
        if not ep:
            raise HTTPException(404, f"Episode {episode_id!r} not found")
        return ep

    def card(ep: dict) -> dict:
        return {**ep, "display_status": data.display_status(ep)}

    def fresh_from_factory(limit: int = 6) -> list[dict]:
        approved = [d for d in drafts.all() if d["status"] == "approved"]
        approved.sort(key=lambda d: d.get("reviewed_at") or "", reverse=True)
        return [summary(d) for d in approved[:limit]]

    def proposals() -> list[dict]:
        return drafts.approved_proposals({e["id"] for e in data.episodes()})

    # ---- pages --------------------------------------------------------------------
    @router.get("/", response_class=HTMLResponse)
    def home(request: Request):
        eps = sorted(data.episodes(), key=lambda e: e.get("date") or "", reverse=True)
        nxt = data.up_next()
        return page(
            request, "home.html", active="home", episodes=[card(e) for e in eps], up_next=card(nxt) if nxt else None,
            season=None, stats=data.stats(), fresh=fresh_from_factory(), proposals=proposals(),
        )

    @router.get("/seasons/{number}", response_class=HTMLResponse)
    def season_page(request: Request, number: int):
        season = data.season(number)
        if not season:
            raise HTTPException(404, f"Season {number} not found")
        eps = [card(e) for e in data.filter_episodes(season=number)]
        return page(request, "home.html", active="home", episodes=eps, up_next=None, season=season,
                    stats=None, fresh=[], proposals=[])

    @router.get("/episodes/{episode_id}", response_class=HTMLResponse)
    def episode_page(request: Request, episode_id: str):
        ep = data.episode(episode_id)
        if not ep:
            proposal = next((d for d in proposals() if d["episode_id"] == episode_id.lower()), None)
            if not proposal:
                raise HTTPException(404, f"Episode {episode_id!r} not found")
            return page(request, "proposal.html", active="home", draft=proposal)
        approved = drafts.approved_for(ep["id"])
        sections = [
            {"anchor": anchor, "label": label, "drafts": [approved[k] for k in kinds if k in approved]}
            for anchor, label, kinds in SECTIONS
        ]
        eps = data.episodes()
        idx = next(i for i, e in enumerate(eps) if e["id"] == ep["id"])
        return page(
            request, "episode.html", active="home", ep=card(ep), season=data.season(ep.get("season")),
            chapters=data.chapters(ep), sections=sections, has_transcript=data.transcript_path(ep) is not None,
            archive_html=Markup(render_archive(data.page_markdown(ep))),
            prev_ep=eps[idx - 1] if idx > 0 else None, next_ep=eps[idx + 1] if idx + 1 < len(eps) else None,
        )

    @router.get("/studio", response_class=HTMLResponse)
    def studio(request: Request, episode: str | None = None, kind: str | None = None, key: str | None = None):
        if settings.admin_key and key and key_matches(settings.admin_key, key):
            resp = RedirectResponse("/studio", status_code=303)
            resp.set_cookie(ADMIN_COOKIE, key, httponly=True, samesite="lax", secure=request.url.scheme == "https")
            return resp
        if not is_admin(request):
            return page(request, "login.html", active="studio", error=None)
        pending = drafts.list(episode_id=episode or None, status="pending", kind=kind or None)
        titles = {e["id"]: e["title"] for e in data.episodes()}
        return page(
            request, "studio.html", active="studio", pending=pending, recent=drafts.recently_reviewed(12),
            titles=titles, episodes=data.episodes(), f_episode=episode or "", f_kind=kind or "",
        )

    @router.post("/studio/login")
    def studio_login(request: Request, key: str = Form("")):
        if not key_matches(settings.admin_key, key):
            return page(request, "login.html", active="studio", error="That key didn't work.")
        resp = RedirectResponse("/studio", status_code=303)
        if settings.admin_key:
            resp.set_cookie(ADMIN_COOKIE, key, httponly=True, samesite="lax", secure=request.url.scheme == "https")
        return resp

    @router.post("/studio/logout")
    def studio_logout():
        resp = RedirectResponse("/", status_code=303)
        resp.delete_cookie(ADMIN_COOKIE)
        return resp

    @router.post("/studio/drafts/{draft_id}/{action}")
    def studio_review(request: Request, draft_id: str, action: str, note: str = Form(""), return_to: str = Form("/studio")):
        require_admin(request)
        if action not in ("approve", "reject"):
            raise HTTPException(404)
        try:
            drafts.review(draft_id, "approved" if action == "approve" else "rejected", note)
        except DraftError as exc:
            raise HTTPException(exc.status_code, str(exc))
        target = return_to if return_to.startswith("/studio") else "/studio"
        return RedirectResponse(target, status_code=303)

    @router.get("/drafts/{draft_id}/deck")
    def deck(request: Request, draft_id: str):
        try:
            d = drafts.get(draft_id)
        except DraftError:
            raise HTTPException(404)
        if d["status"] != "approved" and not is_admin(request):
            raise HTTPException(404)
        if not d.get("content_html"):
            raise HTTPException(404, "This draft has no HTML deck")
        # CSP sandbox gives the deck an opaque origin even when opened outside the iframe.
        return HTMLResponse(d["content_html"], headers={"Content-Security-Policy": "sandbox allow-scripts", "X-Robots-Tag": "noindex"})

    @router.get("/about", response_class=HTMLResponse)
    def about(request: Request):
        return page(request, "about.html", active="about", source=data.source())

    # ---- JSON API -------------------------------------------------------------------
    @router.get("/api/health")
    def health():
        eps = data.episodes()
        all_drafts = drafts.all()
        return {
            "status": "ok" if eps else "degraded",
            "episodes": len(eps),
            "seasons": len(data.seasons()),
            "transcripts": sum(1 for e in eps if data.transcript_path(e)),
            "drafts": len(all_drafts),
            "pending": sum(1 for d in all_drafts if d["status"] == "pending"),
            "demo_mode": settings.demo_mode,
            "write_key_required": not settings.writes_open,
            "admin_key_required": not settings.reviews_open,
            "mcp": "/mcp",
            "time": now_iso(),
        }

    @router.get("/api/seasons")
    def api_seasons():
        return data.seasons()

    @router.get("/api/episodes")
    def api_episodes(season: int | None = None, status: str | None = None, q: str | None = None):
        return [data.compact(e) for e in data.filter_episodes(season=season, status=status, q=q)]

    @router.get("/api/episodes/{episode_id}")
    def api_episode(episode_id: str):
        return services.episode_detail(episode_or_404(episode_id))

    @router.get("/api/drafts")
    def api_drafts(request: Request, episode_id: str | None = None, status: str | None = None, kind: str | None = None):
        rows = drafts.list(episode_id=episode_id, status=status, kind=kind)
        if not is_admin(request):
            rows = [d for d in rows if d["status"] == "approved"]
        return [summary(d) for d in rows]

    @router.get("/api/drafts/{draft_id}")
    def api_draft(request: Request, draft_id: str):
        try:
            d = drafts.get(draft_id)
        except DraftError as exc:
            raise HTTPException(404, str(exc))
        if d["status"] != "approved" and not is_admin(request):
            raise HTTPException(404, "Draft not found")
        return d

    @router.post("/api/drafts", status_code=201)
    def api_create_draft(request: Request, body: DraftIn):
        require_writer(request)
        try:
            d = services.submit_draft(**body.model_dump())
        except DraftError as exc:
            raise HTTPException(exc.status_code, str(exc))
        base = services.base_url(str(request.base_url))
        return {**summary(d), "studio_url": f"{base}/studio#draft-{d['id']}"}

    def _review(request: Request, draft_id: str, status: str, body: ReviewIn | None):
        require_admin(request)
        try:
            return summary(drafts.review(draft_id, status, body.note if body else None))
        except DraftError as exc:
            raise HTTPException(exc.status_code, str(exc))

    @router.post("/api/drafts/{draft_id}/approve")
    def api_approve(request: Request, draft_id: str, body: ReviewIn | None = Body(None)):
        return _review(request, draft_id, "approved", body)

    @router.post("/api/drafts/{draft_id}/reject")
    def api_reject(request: Request, draft_id: str, body: ReviewIn | None = Body(None)):
        return _review(request, draft_id, "rejected", body)

    @router.get("/api/changes")
    def api_changes(request: Request, since: str | None = Query(None), episode_id: str | None = None):
        now = now_iso()
        changes = drafts.changes(since, episode_id=episode_id) if since else []
        if not is_admin(request):
            changes = [c for c in changes if c["status"] != "pending"]
        return JSONResponse({"now": now, "epoch": drafts.epoch, "changes": changes}, headers={"Cache-Control": "no-store"})

    @router.get("/favicon.ico", include_in_schema=False)
    def favicon():
        return Response(status_code=204)

    return router

