---
name: refresh-model-mondays-data
description: "Refresh the local Model Mondays dataset in data/ on demand. Use when asked to refresh, sync, or update Model Mondays episodes, seasons, banners, YouTube stats, video descriptions, or transcripts; to fix an episode-to-video match; or before building site pages, recaps, or slides that need current Model Mondays data."
license: MIT
---

# Refresh Model Mondays data

Keeps `data/` a self-contained, local snapshot of the **Model Mondays livestream series**:

| Source | What we keep | Where |
|---|---|---|
| [microsoft/model-mondays](https://github.com/microsoft/model-mondays) (MIT) | Seasons, all episode records, episode pages, banners (compressed to 1280×720 WebP) | `data/seasons.json`, `data/episodes.json`, `data/episodes/`, `data/banners/` |
| [YouTube playlist](https://aka.ms/model-mondays/playlist) | Video list, views, duration; with credentials also descriptions, likes, comments, publish dates, transcripts | `data/youtube/videos.json`, `data/youtube/transcripts/` |

Only the livestream series is in scope — do not import AMAs, customer stories, blog posts, or labs.

## Setup (once)

```bash
pip install -r .github/skills/refresh-model-mondays-data/scripts/requirements.txt
```

## Commands

Run from the repo root. `SYNC=.github/skills/refresh-model-mondays-data/scripts/sync.py`

| Intent | Command |
|---|---|
| Full refresh | `python3 $SYNC all` |
| Episodes, seasons, banners only | `python3 $SYNC repo` |
| YouTube stats, descriptions, transcripts | `python3 $SYNC youtube` (add `--force` to re-fetch existing transcripts and descriptions) |
| Stats only (fast) | `python3 $SYNC youtube --no-details --no-transcripts` |
| Re-match videos to episodes | `python3 $SYNC link` |
| Validate | `python3 $SYNC check` |

`youtube` merges: a less-privileged run never deletes descriptions or transcripts fetched earlier.

## Credentials (optional, never commit)

YouTube blocks per-video metadata and transcripts from cloud IPs (Codespaces, CI). Without credentials you still get the playlist, durations and approximate view counts.

| Variable | Unlocks | How to get it |
|---|---|---|
| `YOUTUBE_API_KEY` | Descriptions, exact views, likes, comments, publish/stream dates (and better date-based matching) | Google Cloud console → enable **YouTube Data API v3** → Credentials → API key (restrict to that API). Store as a Codespaces secret or in `.env`. |
| `YT_PROXY_URL` | Transcripts from a cloud IP | Any HTTP(S) proxy URL, e.g. a residential proxy. |
| `YT_COOKIES_FILE` | yt-dlp fallback for metadata | Netscape `cookies.txt` exported from a throwaway YouTube login. |

Simplest transcript path: run `python3 $SYNC youtube` once on a local laptop (residential IP, no credentials), then commit `data/youtube/`.

If a run prints `blocked`, stop and tell the user which variable is needed — do not retry in a loop.

## Workflow for the agent

1. Run the requested command(s) above.
2. Read the `link:` line. For every episode in **unmatched completed episodes** or **needs review**:
   - compare `data/episodes.json` (`title`, `date`) with `data/youtube/videos.json` (`title`, dates);
   - the playlist is newest-first, so neighbouring episodes constrain the answer;
   - record verified fixes in `data/youtube/overrides.json` (`"s3-e09": null` = no recording), then run `link`.
   Never guess — leave it unmatched and report it if evidence is ambiguous.
3. Run `check`; it must report 0 errors.
4. Summarize: episodes, linked videos, transcripts, anything blocked or needing human review.

## Contract

- `data/episodes/*.md` and `data/banners/*` are generated — edit the source repo or the script, not the output.
- Episode IDs: `s<season>-e<2-digit episode>`; dates ISO `YYYY-MM-DD`.
- Every imported page carries an attribution header; keep `data/LICENSE-model-mondays.txt`.
- Do not invent descriptions, speakers, or stats — empty is better than fabricated.
