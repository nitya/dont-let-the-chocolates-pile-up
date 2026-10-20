---
name: mm-recap
description: "Turn a Model Mondays livestream into a grounded recap post and a News Highlights list. Use when asked to recap, summarize, or write up a Model Mondays episode (e.g. 'recap S4-E09', 'write the recap for last week's episode', 'draft highlights for s4-e08')."
license: MIT
---

# mm-recap — livestream in, recap out

One station on the content line: **Transform**. Input is an episode id; output is a recap and a highlights list that a human reviews before anything ships.

## Rules (non-negotiable)

1. **Ground everything in the context pack.** Every fact must come from the episode data, the transcript, or the video description/chapters. If you fetch an extra page (e.g. Microsoft Learn), cite it.
2. **Never invent or reuse placeholder links.** `https://aka.ms/model-mondays` is the series homepage, not a source for a news item. If you can't find a specific URL, write the item without a link and add it to *Notes for reviewer*.
3. **No transcript, no quotes.** Without a transcript, do not quote speakers, give numbers, or claim announcements — summarize what the chapters and description say the episode *covers*.
4. **Speakers:** use only names present in the data. If none are listed, say "guests" — never guess.
5. **Drafts only.** You never publish. Output goes to files (and optionally the studio queue); a human approves.

## Workflow

1. **Resolve + ground.** Run from the repo root:

   ```bash
   python3 .github/skills/mm-recap/scripts/context.py <episode>     # e.g. S4-E09, or "next"
   ```

   Read the whole context pack. If it lists a transcript path, read the transcript file in full.
   If the `model-mondays` MCP server is available, `get_episode` / `get_transcript` return the same data.

2. **Write the recap** to `content/<episode-id>/recap.md` using the template below. Voice: friendly, practical, second person, short paragraphs. 350–600 words. Link timestamps (`&t=<seconds>s`) from the chapters so readers can jump in.

3. **Write the highlights** to `content/<episode-id>/highlights.md`: 3–6 items. With a transcript, extract what was actually announced in the *News Highlights* segment. Without one, list the segments a viewer should watch, each linking to its chapter timestamp, and say that news items need the transcript.

4. **Check your work** — fix every error before you finish:

   ```bash
   python3 .github/skills/mm-recap/scripts/check.py content/<episode-id>/recap.md --episode <episode>
   python3 .github/skills/mm-recap/scripts/check.py content/<episode-id>/highlights.md --episode <episode>
   ```

5. **Hand off for review.** If the `model-mondays` MCP server is connected, call `submit_draft` once per file (`kind` = `recap` / `highlights`, `author_agent` = `mm-recap`, `sources` = the URLs you cited). Then tell the user: what you wrote, the check results, and anything in *Notes for reviewer*.

## Recap template

```markdown
---
episode: s4-e09
kind: recap
title: "<Recap title — specific, not clickbait>"
generated_by: mm-recap
grounding: transcript | description+chapters
sources:
  - <every URL cited below>
---

# <Recap title>

<2–3 sentence hook: what the episode was about and who it's for.>

## What we covered
- **[<chapter title>](<timestamp url>)** — <one or two sentences>
...

## Key takeaways
1. <practical takeaway grounded in the sources>
...

## Try it yourself
- <next step with a real link from the sources>

## Watch the replay
<recording url> · <runtime> · Hosted by <host>

## Sources
- <label>: <url>

## Notes for reviewer
- <anything uncertain, missing links, missing speaker names, transcript status>
```
