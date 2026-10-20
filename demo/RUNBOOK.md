# Demo runbook

Four demos, one per act. Each one ends with a visible change on the Model Mondays site, which stays open in a browser tab the whole time.

**Rule: bake and switch.** Kick off live, let it stream for about 30 seconds so people see it's real, and if it isn't done by the time budget, switch to the backup and say the bridge line. Don't debug on stage.

| Demo | Act | Budget | Status (first showing) | Backup |
|---|---|---|---|---|
| 01 · `mm-recap` | 1 · Make it work / Decompose | 3:00 | **Live** | [backups/s4-e09/](backups/s4-e09/) |
| 02 · `mm-deck` + MCP + studio | 2 · Make it work / Delegate | 3:00 | **Live** | [backups/s4-e11/deck.html](backups/s4-e11/deck.html) |
| 03 · `run-assert-eval` on the Producer | 3 · Make it better | 3:00 | Preview (slides + walkthrough) | slides 16–18 |
| 04 · Issue → Emcee → studio → site | 4 · Make it scale | 3:30 | In progress (local `--mock` run) | slides 20–21 |

---

## T-30 minutes: setup

1. **Codespace / dev container is up.** Run `python3 .github/skills/refresh-model-mondays-data/scripts/sync.py check`; it should report 0 errors.
2. **Site running** (terminal 1):

   ```bash
   cd site && python scripts/reset_state.py --seed && python -m uvicorn app.main:app --port 8000
   ```

   `--seed` adds one approved S4-E09 recap and one pending S4-E10 social post, so the home page isn't empty. For a cleaner Demo 1 "reveal", run `reset_state.py` without `--seed`.
3. **Browser tabs:**
   - `http://localhost:8000/` (home)
   - `/studio`
   - `/episodes/s4-e09`
   - `/episodes/s4-e11`
   - `slides/deck.md` in presenter view (`cd slides && marp --config-file .marprc.yml --server .`, then press `p`)
4. **VS Code:**
   - Copilot Chat in **Agent** mode.
   - MCP servers started: open `.vscode/mcp.json` and click *Start* on `model-mondays` and `microsoft-learn`.
   - Font size 18+, Zen mode, notifications off.
5. **Clean outputs:** `rm -rf content/s4-e09 slides/episodes/s4-e11.html`. Keep `slides/episodes/s4-e11.md` closed; Demo 2 overwrites it.
6. **Open the backups** in background tabs, ready to switch to: `demo/backups/s4-e09/recap.md` and `demo/backups/s4-e11/deck.html`.

---

## Demo 01: livestream in, recap out (3:00)

**Prompt (Copilot agent mode):**

```text
recap S4-E09 using the mm-recap skill
```

**Narrate as it runs:**
- "It picked the skill from its *description*. That's how agents find stations."
- "First it runs `context.py`, the grounding step: episode data, chapters and the list of *allowed* sources."
- "No transcript yet, so the rules say no quotes and no invented news, only what the chapters support."
- "Then it runs `check.py`, a deterministic guardrail that fails on placeholder links."

**Land it:**
- Open `content/s4-e09/recap.md` and show the Sources and *Notes for reviewer* sections.
- If MCP is connected, it submits drafts. Click **Studio → Approve**, then switch to `/episodes/s4-e09` and the Recap section fades in.

**Fallback (stalled at 2:15):** open `demo/backups/s4-e09/recap.md` and say:
> "I ran this an hour ago so we're not waiting on the model. Same skill, same output."

**Bridge:**
> "Skills handle the content. But the show also runs on hidden ops work, and that's where Lucy really drowns."

---

## Demo 02: a crew member builds next week's deck (3:00)

**Prompt:**

```text
build the deck for S4-E11 with the mm-deck skill, then submit it to the studio
```

**Narrate:**
- **MCP calls:** `get_episode` (show data), then `microsoft_docs_search` / `microsoft_docs_fetch` (Learn).
- **Reviewer notes:** the episode page and YouTube listing disagree (open-model selection vs Fireworks fine-tuning). The skill *flags* this instead of guessing.
- **Render:** `render.py --standalone`. Open the HTML: same theme as this deck.
- **Submit:** `submit_draft(kind="deck")`. Go to **Studio**, preview it, **Approve**, then open `/episodes/s4-e11` and show the Deck tab.

**Meta moment:**
> "This talk's deck is built the same way: Markdown, a theme, and an agent."

**Fallback:** open `demo/backups/s4-e11/deck.html`. If the site is up, `POST` the backup with:

```bash
python demo/submit_backup.py s4-e11 deck
```

**Bridge:**
> "That's two acts of *make it work*. But how do I know it's any good?"

---

## Demo 03: measure, fix, prove (3:00), preview for the first showing

**First showing:**
- Show slide 16 ("Caught in the act").
- Live in the terminal, run this; it errors on 8 placeholder links:

  ```bash
  python3 .github/skills/mm-recap/scripts/check.py data/episodes/s3-e04.md --episode s3-e04
  ```

- Then show the guardrail catching an agent in the act. The Publisher tries a placeholder link, gets **⛔ BLOCKED**, and resubmits:

  ```bash
  python -m agents.emcee "prep S4-E12" --mock --only publisher --mock-fault placeholder --mock-delay 0.4
  ```

- "A guardrail catches *this* one. ASSERT catches the ones a rule can't: a plausible but wrong link, an invented speaker, a claim the transcript doesn't support."
- **Optional (about 15s):** open [`evals/producer/ungrounded_links.yaml`](../evals/producer/ungrounded_links.yaml), the eval spec written for ASSERT. Say: "We start running it for Season 5." Don't run anything; nothing at this showing runs ASSERT.
- Walk slide 17 (the two inspectors). The story to tell is in [slides/narrative.md](../slides/narrative.md#the-two-inspectors-the-assert-and-foundry-story).

**Full version (Season 5 of Model Mondays, December–January):** see [evals/README.md](../evals/README.md).
1. Prompt: `evaluate the Producer for placeholder or invented links`.
2. `run-assert-eval` asks where the risk comes from; supply it yourself.
3. Triage, config, run.
4. Show the two headline numbers (impermissible vs permissible) and one failing transcript with the judge's citation.
5. Fix the Producer instructions, re-run the *same* eval, and show the delta.

**Bridge:**
> "Now it works, and it's measurably better. Last step: stop running it by hand."

---

## Demo 04: one issue, the whole line runs (3:30), in progress for the first showing

**First showing (local):**

```bash
python site/scripts/reset_state.py          # clean studio
python -m agents.emcee "prep S4-E12" --mock --mock-delay 0.4
```

`--mock-delay` paces the trace so the audience can read it. The first run takes a few seconds longer while the agents' venv warms up.

1. Show the trace: Emcee hands off to Coordinator, then Presenter, then Publisher; each one calls `submit_draft`.
2. Switch to **Studio**: three drafts appear live (toast notifications).
3. Approve them, then open `/episodes/s4-e12`.
4. Say: "On Foundry, this same crew runs as a hosted agent, and a routine wakes it on a schedule or a GitHub issue. We're making that real for Season 5 of Model Mondays, starting December–January."

**Full version:**

```bash
gh issue create --title "S4-E12 announced" --label emcee
```

The routine (or the GitHub Actions fallback) runs Emcee on Foundry against the deployed site. Bake and switch to the morning's run.

---

## Reset between rehearsals

```bash
python site/scripts/reset_state.py --seed
rm -rf content/s4-e09 slides/episodes/s4-e11.html
git checkout slides/episodes/s4-e11.md
```
