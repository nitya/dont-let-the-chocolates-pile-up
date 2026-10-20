# 02 · Slides as code: Marp + MCP

**Playbook:** *Make it work.* Slides are just another station; MCP grounds them.

## 1. See the theme

- Open [`slides/deck.md`](../slides/deck.md) (the talk itself) with the Marp extension preview.
- Its look comes from [`slides/theme/chocolate.css`](../slides/theme/chocolate.css). The comment at the top lists the building blocks:
  - section classes `title`, `divider`, `demo`, `dark`;
  - components `.card`, `.badge`, `.grid.cols-N`, `.steps`, `.callout`, `.stat`.

## 2. Run the Presenter station

Make sure both MCP servers are started ([lab 00](00-setup.md)), then:

```text
build the deck for S4-E11 with the mm-deck skill, then submit it to the studio
```

Watch the tool calls:

| Call | Grounds |
|---|---|
| `model-mondays/get_episode` | show facts: title, host, date, description |
| `microsoft-learn/microsoft_docs_search` and `microsoft_docs_fetch` | product facts |
| `render.py --standalone` | one HTML file with images inlined |
| `model-mondays/submit_draft(kind="deck")` | the review queue |

Then go to **Studio**, **Approve** the draft, and open `/episodes/s4-e11`. The deck is embedded in the page.

**Look for the reviewer notes** in the first slide's speaker notes. The episode page and the YouTube listing describe different topics. A good station *flags* conflicts instead of picking one.

Compare with [`slides/episodes/s4-e11.md`](../slides/episodes/s4-e11.md).

## 3. Your turn

- Run it for `next` (the nearest upcoming episode).
- Add a slide type to the theme (e.g. a quote slide) and update the skill so it uses it.
- Export: `cd slides && marp --config-file .marprc.yml episodes/<id>.md --pdf`.

✅ **Done when:** a deck you generated is approved in the studio and shows on its episode page.
