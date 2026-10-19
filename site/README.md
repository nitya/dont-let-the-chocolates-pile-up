# Model Mondays — content factory site + MCP server

The demo "factory window" for the talk **Don't Let the Chocolate Pile Up: Scaling DevRel Content with AI Agents**.

- AI agents connect to the **`model-mondays` MCP server** (Streamable HTTP at `/mcp`), read real episode data, and **submit drafts** (recaps, highlights, briefs, run-of-show, social posts, Marp decks, announcements, episode proposals).
- A human reviews drafts in the **Studio** (`/studio`) and approves or rejects them. There is deliberately no approve tool.
- Approved drafts appear **live** on the episode pages (pages poll every ~4 s and fade new content in).

One FastAPI app serves the website, the JSON API and the MCP endpoint, so a single Azure App Service hosts everything.

## Run locally

```bash
pip install -r site/requirements.txt
cd site
python scripts/reset_state.py --seed        # optional: sample drafts so the UI isn't empty
python -m uvicorn app.main:app --reload --port 8000
```

Open <http://localhost:8000>. Run the tests with `cd site && python -m pytest`.

> The folder is called `site`, which collides with Python's stdlib `site` module. That's why the package is
> `site/app` and everything runs **from inside `site/`**. Never `import site` from this code.

Reset the queue between rehearsals (works while the server runs; open pages reload themselves):

```bash
python site/scripts/reset_state.py          # empty
python site/scripts/reset_state.py --seed   # empty + site/seed/*.json samples
```

## Configuration (environment variables)

| Variable | Default | Purpose |
|---|---|---|
| `MM_DATA_DIR` | `../data` relative to `site/` (falls back to `site/data`) | Read-only dataset (`episodes.json`, `seasons.json`, `banners/`, `episodes/`, `youtube/`) |
| `MM_STATE_DIR` | `site/.state` | Where `drafts.json` lives (mutable, gitignored) |
| `MM_WRITE_KEY` | unset | If set, `submit_draft` (MCP) and `POST /api/drafts` need `Authorization: Bearer <key>` or `x-api-key: <key>` |
| `MM_ADMIN_KEY` | unset | If set, the Studio needs a login (form, or `/studio?key=<key>`), and the approve/reject API needs `x-admin-key` / `Authorization: Bearer` |
| `MM_PUBLIC_URL` | `https://$WEBSITE_HOSTNAME` on Azure, else the request host | Base URL used in links returned to agents (`studio_url`) |
| `MM_ALLOWED_HOSTS` | localhost + `$WEBSITE_HOSTNAME` + Codespaces port 8000 host | Extra comma-separated `Host` values accepted by `/mcp` (DNS-rebinding protection). `*` disables the check |

With neither key set the site runs in **demo mode** (everything open) and shows a small "demo mode" badge.
Transcripts dropped into `MM_DATA_DIR/youtube/transcripts/<videoId>.txt` and data refreshes are picked up without a restart.

## MCP server

Endpoint: `http://localhost:8000/mcp` (Streamable HTTP, stateless, JSON responses). Add it to VS Code in `.vscode/mcp.json`:

```jsonc
{
  "servers": {
    "model-mondays": {
      "type": "http",
      "url": "http://localhost:8000/mcp"
      // when MM_WRITE_KEY is set:
      // "headers": { "Authorization": "Bearer ${input:mm-write-key}" }
    }
  },
  "inputs": [
    { "id": "mm-write-key", "type": "promptString", "description": "Model Mondays write key", "password": true }
  ]
}
```

### Tools

| Tool | Purpose |
|---|---|
| `list_seasons()` | Seasons with title, theme, dates, status, episode count |
| `list_episodes(season: int \| None = None, status: str \| None = None, limit: int = 60)` | Compact episode rows |
| `get_episode(episode_id: str)` | Full record + YouTube description, chapters, transcript availability, approved drafts summary |
| `search_episodes(query: str, limit: int = 10)` | Keyword search over titles, descriptions, tags, people, highlights, transcripts |
| `get_transcript(episode_id: str, start_char: int = 0, max_chars: int = 20000)` | Paged transcript text, or a clear "not available yet" message |
| `get_series_stats()` | Episodes per season, total views/hours, top 5 most viewed, transcripts available, up next |
| `list_drafts(episode_id: str \| None = None, status: str \| None = None, kind: str \| None = None)` | Review queue with previews |
| `submit_draft(episode_id, kind, title, content_markdown, author_agent, sources: list[str], content_html: str \| None = None)` | Queue a draft for human review; returns `draft_id` + `studio_url` |

Kinds: `recap, highlights, brief, run_of_show, social, deck, announcement, episode`. `recap` and `highlights` must cite `sources`.
`episode` drafts may propose a new id (e.g. `s5-e01`). Resource template: `mm://episodes/{episode_id}` returns the episode Markdown page.

## Web pages and API

Pages: `/`, `/seasons/{n}`, `/episodes/{id}`, `/studio`, `/about`. Banners are served from `MM_DATA_DIR/banners` at `/banners/...`.
Deck HTML (`content_html`) is served from `/drafts/{id}/deck` with `Content-Security-Policy: sandbox allow-scripts` and embedded in a sandboxed iframe.

| Method & path | Auth | Notes |
|---|---|---|
| `GET /api/health` | – | Counts, demo mode, key requirements |
| `GET /api/seasons` | – | |
| `GET /api/episodes?season=&status=&q=` | – | Compact rows |
| `GET /api/episodes/{id}` | – | Same payload as `get_episode` |
| `GET /api/drafts?episode_id=&status=&kind=` | admin to see non-approved | |
| `GET /api/drafts/{id}` | admin unless approved | Full draft incl. `content_html` |
| `POST /api/drafts` | write key | JSON body with the `submit_draft` fields |
| `POST /api/drafts/{id}/approve` · `/reject` | admin key | Optional body `{"note": "..."}` |
| `GET /api/changes?since=<iso>&episode_id=` | – (pending only for admin) | Polling feed: `{now, epoch, changes[]}`; a new `epoch` means the store was reset |

Interactive docs: `/api/docs`.

## Azure App Service (Linux, Python 3.12)

- Deploy so that the contents of `site/` are the app root (this is where `requirements.txt` lives), and make the data available either as `site/data` (picked up automatically) or via `MM_DATA_DIR`.
- Startup command: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Set `MM_STATE_DIR=/home/mm-state` so drafts survive restarts and redeploys (`/home` is persistent storage), plus `MM_WRITE_KEY` and `MM_ADMIN_KEY`.
- `WEBSITE_HOSTNAME` is set by App Service and is automatically allowed by the MCP host check and used for `studio_url` links.
- Run a single instance/worker: the drafts store is one JSON file with an in-process lock (fine for a demo, not for scale-out).

## Layout

```
site/
  app/            config.py, data.py, drafts.py, render.py, services.py, web.py, mcp_server.py, main.py
    templates/    Jinja2 pages
    static/       style.css, app.js (polling + toasts)
  scripts/        reset_state.py
  seed/           sample drafts for --seed
  tests/          pytest (pages, API lifecycle, keys, MCP in-process + end-to-end over Streamable HTTP)
```

Data: episode metadata, pages and banners from [microsoft/model-mondays](https://github.com/microsoft/model-mondays) (© Microsoft, MIT); video stats/descriptions from the public YouTube playlist.
