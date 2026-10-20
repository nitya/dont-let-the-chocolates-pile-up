# Copilot instructions

This repo is the talk **"Don't Let the Chocolate Pile Up: Scaling DevRel Content with AI Agents"** (Nitya Narasimhan, All Things Open 2026) plus the working system it demos: Model Mondays data, skills, a site with an MCP server, the Emcee agent crew, and evals.

## Key files

| What | Where |
|---|---|
| Abstract | [README.md](../README.md#abstract): the narrative must deliver on it |
| Deck (Marp) + speaker notes | [slides/deck.md](../slides/deck.md) |
| Presenter script: story, timing, per-slide guidance | [slides/narrative.md](../slides/narrative.md) |
| Demo steps + fallbacks | [demo/RUNBOOK.md](../demo/RUNBOOK.md) |
| Setup, rehearsal, reset, stage cheat sheet | [skills/talk-prep/SKILL.md](skills/talk-prep/SKILL.md) |
| Ideas deferred until after the talk | [planning/revisit-after-talk.md](planning/revisit-after-talk.md) |

## House rules

- **The deck is frozen for the talk.** Don't edit `slides/deck.md` or `slides/narrative.md` unless asked; propose changes instead. Speaker notes in `narrative.md` must match `deck.md` word for word.
- **Prompts run in Copilot Chat (Agent mode); commands run in the terminal.** Demos 1–2 are Copilot prompts; Demos 3–4 are terminal commands so the audience sees the raw trace.
- **Never commit demo run output:** `content/`, regenerated `slides/episodes/s4-e11.*`, or `data/` changes that are only timestamps or view counts. Restore with `git checkout -- slides/episodes/ data/` and `rm -rf content/s4-e09`.
- **YouTube blocks transcript and metadata fetches from Codespaces IPs.** Transcripts are already committed (45). Don't retry in a loop; refresh them on a local machine.
- **Humans approve.** The MCP server has `submit_draft` but no approve tool. Never approve or publish on the user's behalf.
- **Don't invent links, speakers or stats.** An empty field is better than a fabricated one (this is the talk's Act 3 story).
