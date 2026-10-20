# Revisit after the talk

Deferred on 2026-10-19 (the night before the talk). No changes were made to the deck or narrative.

## 1. The restaurant-kitchen analogy

A possible next version of the talk, a blog post, or a Q&A answer. The kitchen models the *solution* well (varied tickets, stations, tasting, the pass); the chocolate line is better at the *problem* (Lucy's eat / hide / drop gives the act structure).

| Kitchen | The line | Notes |
|---|---|---|
| Executive chef | You | Designs the menu, sets the standards, tastes at the pass |
| Expediter / head chef | Copilot / Emcee | Reads tickets, routes work, calls the timing |
| Line cooks (chefs de partie) | Specialist subagents | Not sous-chefs: a kitchen usually has one sous-chef, but each line cook owns a station |
| Stations + prep cards | Skills | The written procedure you hand a new cook |
| Pantry + suppliers | MCP | Ingredients (data), not recipes. Grounding = fresh ingredients, never invented ones |
| Tickets / ticket printer | Requests, issues, schedules, triggers | Automatic triggers = a printer that fires itself |
| The pass | The studio | Nothing leaves until the chef approves: "agents propose, humans dispose" |
| Tasting / health inspection | Evals | The 83 placeholder links = a failed inspection |
| Specialized equipment | Marp (pasta extruder + house plate), ASSERT (thermometer + tasting spoon), Foundry (the commercial kitchen you lease), coding agent (maintenance crew) | The equipment is open source and swappable |
| Ticket rail + calling system | Microsoft Agent Framework | Infrastructure for handoffs, not a single appliance |

Key lines:
- "As pace picks up, we don't make cooks work faster. We add stations."
- "The equipment is open source. The skill is how your kitchen uses it."
- Skills are not equipment: `run-assert-eval` is a skill wrapped around ASSERT; `microsoft-foundry` is a skill wrapped around Foundry.

Lines that work inside the chocolate frame (proposed for narrative.md, not yet added):
- **Slide 5:** "This is the equipment. Swap any of it; the playbook is about how you lay out the line, not which brand of oven you buy."
- **Slide 6:** "Lucy's mistake was trying to wrap faster. The fix isn't faster hands. It's more stations."
- **Slide 12:** "Think of Emcee as the expediter in a restaurant kitchen: it reads the tickets, routes them to stations, and nothing leaves until the chef approves at the pass."

## 2. Audience suggestions not yet written into narrative.md

- **Portability:** say it at least twice. Skills also work in Claude Code and Cursor; ASSERT works with any model; mock mode runs with no cloud; Act 4 has a plain GitHub Actions fallback.
- **OSS maintainers:** "Whether your belt is a livestream, a docs site or an OSS project's release notes, it's the same factory." (slide 4 or 22)
- **Impact number:** a rough time-saved figure for slide 22, e.g. "recaps went from 'never' to 10 minutes of review".
- **Keeping your voice:** the voice rules live in the skill, so you write your voice down once.
- **Replacement fear:** the factory frees time for the human work: guest relationships, community, live teaching.
- **Coding-agent gap (abstract promise #8):** a one-minute clip of a Copilot coding agent PR that updates a lab, for slide 20.
- **Abstract wording:** the deck never says "podcast" or "AMA series".

## 3. Bonus: a real ASSERT + Foundry run (after rehearsals, if time permits)

Nitya has a live Foundry project. Goal: replace "preview" with real evidence.

1. **Dev container:** the `azure-cli` and `azd` features are declared in `.devcontainer/devcontainer.json`, but `az` was missing in the rehearsal Codespace. Fix that, rebuild, then `az login` and `azd auth login`.
2. **ASSERT:** create `evals/.env` (generator + judge deployments; LiteLLM `azure/<deployment>` names in `evals/producer/*.yaml`) and `agents/.env` (the Producer's model). Run `evals/producer/ungrounded_links.yaml`: baseline → fix → `--override run=after-fix` → `assert-ai results compare`. Nothing has validated these configs yet (`assert-ai` has no dry-run), so expect config fixes on the first run.
3. **Foundry:** the `microsoft-foundry` skill: `azd ai agent init --src agents` (container deploy), `azd provision` + `azd deploy`, invoke `"prep next"`, then one routine from `agents/foundry/`.
4. **Talk:** if a run succeeds, use real numbers (screenshot or bake-and-switch) on slides 18/21 and drop the "Preview" / "In progress" labels.
