# Model Mondays data (local snapshot)

Self-contained data for the talk, demos and labs: the **Model Mondays livestream series** only.

Refresh on demand with the [`refresh-model-mondays-data`](../.github/skills/refresh-model-mondays-data/SKILL.md) skill. Files here are generated; do not hand-edit them, except [`youtube/overrides.json`](youtube/overrides.json).

## Layout

| Path | Contents |
|---|---|
| [`seasons.json`](seasons.json) | Season title, theme, dates, status, episode count |
| [`episodes.json`](episodes.json) | One normalized record per episode (see schema below) |
| [`episodes/`](episodes/) | Episode pages (Markdown), banners re-pointed locally, other links absolutized to the source commit |
| [`banners/`](banners/) | Episode banners `S<season>-E<episode>.webp`, 1280×720 WebP (about 32 MB of PNG → about 2 MB) |
| [`youtube/videos.json`](youtube/videos.json) | Playlist videos with stats; descriptions and dates when credentials are available |
| `youtube/transcripts/` | `<videoId>.json` (timed segments) and `<videoId>.txt` (30-second blocks with `[hh:mm:ss]` stamps) |
| [`youtube/overrides.json`](youtube/overrides.json) | Hand-verified episode → video matches |

## Episode record

```jsonc
{
  "id": "s4-e05", "season": 4, "episode": 5, "date": "2026-09-14", "time": "1:30pm ET",
  "title": "...", "description": "...", "host": "...", "speakers": ["..."],
  "status": "completed | scheduled | planned | cancelled", "tags": [],
  "banner": "banners/S4-E5.webp", "page": "episodes/s4-e05.md",
  "highlights": [{ "title": "", "url": "", "description": "" }],
  "spotlight": { "title": "", "speakers": [], "description": "", "resources": [] } | null,
  "customerStory": {} | null, "studyCorner": "" | null,
  "links": { "recording": "https://...", "slides": "https://..." },
  "source": { "page": "https://github.com/microsoft/model-mondays/blob/<sha>/...", "banner": "..." },
  "youtube": {
    "videoId": "", "url": "", "title": "", "publishedAt": "", "durationSec": 0,
    "viewCount": 0, "likeCount": null, "commentCount": null, "statsFetchedAt": "",
    "transcript": "youtube/transcripts/<id>.txt" | null,
    "matchedBy": "episode-link | override | title-match | date+title-match",
    "matchScore": 1.0, "needsReview": false
  } | null
}
```

Paths in records are relative to this `data/` folder. The source commit is recorded in the `source` block at the top of `episodes.json` and `seasons.json`.

## Attribution

Episode metadata, pages and banners come from [microsoft/model-mondays](https://github.com/microsoft/model-mondays), © Microsoft Corporation, MIT License (see [`LICENSE-model-mondays.txt`](LICENSE-model-mondays.txt)). Video metadata and transcripts come from the public [Model Mondays YouTube playlist](https://aka.ms/model-mondays/playlist).
