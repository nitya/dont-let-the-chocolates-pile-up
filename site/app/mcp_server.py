"""MCP server "model-mondays": read tools over the dataset + draft submission for human review."""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.mcpserver import Context, MCPServer
from mcp.server.mcpserver.exceptions import ResourceError, ToolError
from mcp.server.transport_security import TransportSecuritySettings
from pydantic import Field

from .drafts import KINDS, STATUSES, DraftError, summary
from .services import Services, key_from_headers, key_matches

INSTRUCTIONS = """\
Model Mondays content factory. Model Mondays is a weekly Microsoft livestream about AI models (Microsoft Foundry,
GitHub Models, open models...). Use the read tools to ground yourself in real episode data, then call submit_draft to
propose content (recaps, highlights, briefs, run-of-show, social posts, Marp decks, announcements, episode proposals).
Every draft lands in a human review queue (the Studio); a person approves or rejects it. You cannot approve drafts.
Typical flow: list_episodes or search_episodes -> get_episode -> get_transcript (if available) -> submit_draft.
Always pass the URLs/paths you actually used in `sources`.
"""


def _request_base(ctx: Context | None) -> str | None:
    try:
        headers = (ctx.headers if ctx else None) or {}
    except Exception:
        return None
    host = headers.get("x-forwarded-host") or headers.get("host")
    if not host:
        return None
    proto = headers.get("x-forwarded-proto") or "http"
    return f"{proto}://{host}"


def transport_security(services: Services) -> TransportSecuritySettings:
    hosts = services.settings.allowed_hosts
    if "*" in hosts:
        return TransportSecuritySettings(enable_dns_rebinding_protection=False)
    allowed = ["127.0.0.1:*", "localhost:*", "[::1]:*", "127.0.0.1", "localhost", "[::1]", *hosts]
    origins = [f"{scheme}://{h}" for h in allowed for scheme in ("http", "https")]
    return TransportSecuritySettings(enable_dns_rebinding_protection=True, allowed_hosts=allowed, allowed_origins=origins)


def build_mcp(services: Services) -> MCPServer:
    data, drafts = services.data, services.drafts
    mcp = MCPServer("model-mondays", title="Model Mondays", instructions=INSTRUCTIONS, version="1.0.0")

    def require_episode(episode_id: str) -> dict:
        ep = data.episode(episode_id)
        if not ep:
            raise ToolError(f"Episode {episode_id!r} not found. Use list_episodes or search_episodes to find ids like 's4-e05'.")
        return ep

    @mcp.tool()
    def list_seasons() -> list[dict[str, Any]]:
        """List all Model Mondays seasons with number, title, theme, description, start/end dates, status and episode count."""
        return data.seasons()

    @mcp.tool()
    def list_episodes(
        season: Annotated[int | None, Field(description="Season number (1-4) to filter by; omit for all seasons.")] = None,
        status: Annotated[
            str | None,
            Field(description="Filter by status: completed, scheduled, planned, cancelled, or upcoming/live (computed)."),
        ] = None,
        limit: Annotated[int, Field(description="Maximum rows to return.", ge=1, le=200)] = 60,
    ) -> list[dict[str, Any]]:
        """List episodes as compact rows (id, season, episode, date, title, host, speakers, status, views, duration,
        has_transcript), ordered by season and episode. Use get_episode(id) for the full record."""
        return [data.compact(e) for e in data.filter_episodes(season=season, status=status)][:limit]

    @mcp.tool()
    def get_episode(
        episode_id: Annotated[str, Field(description="Episode id such as 's4-e05' (season 4, episode 5).")],
    ) -> dict[str, Any]:
        """Get the full record for one episode: title, date, host, speakers, description, highlights (news links),
        spotlight and resources, links, YouTube stats, the YouTube description with chapter timestamps (`chapters`),
        whether a transcript exists, and a summary of drafts already approved for this episode (latest per kind)."""
        return services.episode_detail(require_episode(episode_id))

    @mcp.tool()
    def search_episodes(
        query: Annotated[str, Field(description="Keywords, e.g. 'speech voice agents' or a speaker name.")],
        limit: Annotated[int, Field(description="Maximum results.", ge=1, le=50)] = 10,
    ) -> list[dict[str, Any]]:
        """Keyword search across episode titles, descriptions, tags, host/speakers, highlights, spotlight, YouTube
        descriptions and transcripts (when available). Returns compact rows with a relevance `score` and `matched` fields."""
        return data.search(query, limit=limit)

    @mcp.tool()
    def get_transcript(
        episode_id: Annotated[str, Field(description="Episode id such as 's4-e05'.")],
        start_char: Annotated[int, Field(description="Character offset to start from (for paging).", ge=0)] = 0,
        max_chars: Annotated[int, Field(description="Maximum characters to return.", ge=1, le=100_000)] = 20_000,
    ) -> str:
        """Get the episode transcript text ([hh:mm:ss] stamped blocks), paged by character offset. The header line tells
        you the total length and the next start_char. If no transcript exists yet, says so: fall back to get_episode
        (description + chapters) for grounding."""
        ep = require_episode(episode_id)
        text = data.transcript(ep)
        if not text:
            return (
                f"Transcript not available yet for {ep['id']} ('{ep['title']}'). "
                "Use get_episode for the description, chapters and highlights instead, and cite the episode/YouTube URL in sources."
            )
        chunk = text[start_char : start_char + max_chars]
        end = start_char + len(chunk)
        more = f"next start_char={end}" if end < len(text) else "end of transcript"
        path = data.transcript_path(ep)
        rel = path.relative_to(data.data_dir.resolve()).as_posix() if path else ""
        return f"[transcript {ep['id']} data/{rel} chars {start_char}-{end} of {len(text)}; {more}]\n{chunk}"

    @mcp.tool()
    def get_series_stats() -> dict[str, Any]:
        """Series-wide numbers: episode counts per season, total YouTube views, total hours of video, top 5 most-viewed
        episodes, number of transcripts available, and the next upcoming episode."""
        return data.stats()

    @mcp.tool()
    def list_drafts(
        episode_id: Annotated[str | None, Field(description="Only drafts for this episode id.")] = None,
        status: Annotated[str | None, Field(description=f"One of: {', '.join(STATUSES)}.")] = None,
        kind: Annotated[str | None, Field(description=f"One of: {', '.join(KINDS)}.")] = None,
    ) -> list[dict[str, Any]]:
        """List drafts in the review queue (newest first) with status, reviewer note and a short content preview.
        Use it to avoid duplicating work or to see why a draft was rejected."""
        rows = []
        for d in drafts.list(episode_id=episode_id, status=status, kind=kind):
            row = summary(d)
            md = row.pop("content_markdown", "") or ""
            row["preview"] = md[:300] + ("…" if len(md) > 300 else "")
            rows.append(row)
        return rows

    @mcp.tool()
    def submit_draft(
        episode_id: Annotated[str, Field(description="Target episode id, e.g. 's4-e05'. For kind='episode' this may be a NEW id to propose.")],
        kind: Annotated[str, Field(description=f"Draft type, one of: {', '.join(KINDS)}.")],
        title: Annotated[str, Field(description="Short human-readable title for the draft.")],
        content_markdown: Annotated[str, Field(description="The draft content in Markdown (shown to reviewers and, once approved, on the episode page).")],
        author_agent: Annotated[str, Field(description="Who wrote it, e.g. 'emcee/producer' or 'recap-skill'.")],
        sources: Annotated[
            list[str],
            Field(description="URLs or data paths you used for grounding (required, non-empty, for recap and highlights)."),
        ],
        content_html: Annotated[
            str | None,
            Field(description="Optional self-contained HTML (e.g. a Marp-rendered deck). Shown in a sandboxed iframe."),
        ] = None,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Submit a content draft for HUMAN review. It is stored as 'pending' and appears in the Studio review queue;
        only a person can approve it, after which it goes live on the episode page. Kinds: recap, highlights, brief,
        run_of_show, social, deck (put Marp HTML in content_html and the Markdown source in content_markdown),
        announcement, episode (proposal for a new episode). Returns the draft id and the Studio URL to share with the
        reviewer. If the server has a write key, send it as 'Authorization: Bearer <key>' or 'x-api-key'."""
        if services.settings.write_key:
            headers = None
            try:
                headers = ctx.headers if ctx else None
            except Exception:
                headers = None
            if not key_matches(services.settings.write_key, key_from_headers(headers)):
                raise ToolError("Unauthorized: this server requires a write key (Authorization: Bearer <key> or x-api-key header).")
        try:
            draft = services.submit_draft(
                episode_id=episode_id, kind=kind, title=title, content_markdown=content_markdown,
                author_agent=author_agent, sources=sources, content_html=content_html,
            )
        except DraftError as exc:
            raise ToolError(str(exc)) from exc
        base = services.base_url(_request_base(ctx))
        return {
            "draft_id": draft["id"],
            "status": draft["status"],
            "studio_url": f"{base}/studio#draft-{draft['id']}",
            "episode_url": f"{base}/episodes/{draft['episode_id']}",
            "message": "Draft queued for human review in the Studio. It will appear on the episode page once approved.",
        }

    @mcp.resource("mm://episodes/{episode_id}", name="episode-page", mime_type="text/markdown",
                  description="Imported Markdown page for one episode (e.g. mm://episodes/s4-e05).")
    def episode_page(episode_id: str) -> str:
        ep = data.episode(episode_id)
        if not ep:
            raise ResourceError(f"Episode {episode_id!r} not found.")
        return data.page_markdown(ep) or f"# {ep['title']}\n\n{ep.get('description', '')}\n"

    return mcp
