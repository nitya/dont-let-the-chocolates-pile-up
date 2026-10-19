---
name: mm-deck
description: "Draft a Marp slide deck for a Model Mondays episode, grounded in the show's data and current Microsoft Learn docs, using the talk's chocolate theme. Use when asked to build, draft, or update slides/a deck for an episode (e.g. 'build the deck for S4-E11', 'draft slides for next week's episode')."
license: MIT
---

# mm-deck — the Presenter station

Builds an episode deck as Markdown (Marp), grounded in two sources, rendered with `slides/theme/chocolate.css`, and handed to a human for review.

## Rules

1. **Two grounding sources only:** the episode context pack (show data) and Microsoft Learn (product facts). Every product claim on a slide must trace to a Learn URL listed on the *Resources* slide.
2. **Never invent** speakers, dates, model names, numbers, or links. If the episode page and the YouTube description disagree, cover what both say and flag it in the reviewer notes.
3. **Use the theme's building blocks** (see the classes at the top of `slides/theme/chocolate.css`): `title`, `divider`, `demo` slides; `.grid.cols-N`, `.card`, `.badge`, `.steps`, `.callout`. Icons are in `slides/assets/icons/`.
4. **6–9 slides, one idea per slide, ≤ 30 words of body text per slide.** Put the talk track in speaker notes (`<!-- -->`).
5. **Drafts only** — a human approves before anything is published.

## Workflow

1. **Ground in the show's data** (run from repo root):

   ```bash
   python3 .github/skills/mm-recap/scripts/context.py <episode>      # e.g. S4-E11, or "next"
   ```

   With the `model-mondays` MCP server connected, `get_episode` and `search_episodes` give the same data, plus related past episodes to reference.

2. **Ground in the docs.** With the **Microsoft Learn MCP server** (`microsoft_docs_search`, `microsoft_docs_fetch`), search the episode's topic and read the 2–4 most relevant pages. Without MCP, use `https://learn.microsoft.com/api/search?search=<query>&locale=en-us`.

3. **Write** `slides/episodes/<episode-id>.md`. Copy the structure of [`slides/episodes/s4-e11.md`](../../../slides/episodes/s4-e11.md):
   1. `title` slide — kicker `MODEL MONDAYS · S<n>-E<n>`, episode title, one-line subtitle, host/date byline, banner as `<div class="hero wide">` (`../../data/banners/S<n>-E<n>.webp`)
   2. Why it matters (from the episode description)
   3. 2–3 concept slides (from Learn)
   4. `demo` slide for the live segment
   5. Resources (Learn links + recording)
   6. Up next (from the next episode in data) + community links
   7. Reviewer notes in the first slide's speaker notes

4. **Render + check:**

   ```bash
   python3 .github/skills/mm-deck/scripts/render.py slides/episodes/<id>.md --standalone
   python3 .github/skills/mm-recap/scripts/check.py slides/episodes/<id>.md --episode <id>
   ```

   Learn URLs show up as `WARN not in allowed sources` — fine, as long as each one is listed on the Resources slide. Fix every `ERROR`.

5. **Hand off.** If the `model-mondays` MCP server is connected, call `submit_draft` with `kind="deck"`, `content_markdown` = the deck Markdown, `content_html` = the standalone HTML, `sources` = every URL cited, `author_agent="mm-deck"`. Tell the user the file paths and any reviewer notes.
