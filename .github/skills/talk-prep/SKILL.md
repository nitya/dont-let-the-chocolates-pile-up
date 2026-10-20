---
name: talk-prep
description: "Set up, verify, rehearse and reset the 'Don't Let the Chocolate Pile Up' talk demos. Use when asked to prep or rehearse the talk, set up a fresh Codespace for the demos, run the T-30 setup, check demo readiness, reset between rehearsals, export the deck to PDF/PPTX, or clean up after a demo run."
---

# Talk prep

The full prep routine for the talk, with the outputs and timings you should expect. Demo details and fallbacks are in [demo/RUNBOOK.md](../../../demo/RUNBOOK.md); the per-slide script is in [slides/narrative.md](../../../slides/narrative.md).

## 1. Fresh Codespace: verify the environment

The dev container's `post-create.sh` installs the data and site dependencies, `agents/.venv`, `evals/.venv` and Marp CLI. It does **not** install a browser.

```bash
python3 .github/skills/refresh-model-mondays-data/scripts/sync.py check   # expect: 50 episodes, 48 linked to YouTube, 45 with transcripts, 0 errors
python -m pytest agents/tests -q                                           # expect: 11 passed
which marp || echo "use npx @marp-team/marp-cli instead"
```

If any of these fail, rerun `bash .devcontainer/post-create.sh`.

## 2. Start everything (also the T-30 setup on talk day)

Run each long-running command in its own terminal.

```bash
# Terminal 1: site + MCP server. Use --seed only for rehearsal; without it, the S4-E09 recap appears live on stage.
cd site && python scripts/reset_state.py && python -m uvicorn app.main:app --port 8000

# Terminal 2: presenter view, then open http://localhost:8080/deck.md?view=presenter (or press "p")
cd slides && npx @marp-team/marp-cli --config-file .marprc.yml --server .
```

Then:
- In VS Code, open `.vscode/mcp.json` and click **Start** on `model-mondays` and `microsoft-learn`.
- Switch Copilot Chat to **Agent** mode.
- Open browser tabs: `/studio`, `/episodes/s4-e09`, `/episodes/s4-e11`, `/episodes/s4-e12`.
- Set the editor font to 18+, turn on Zen mode, turn off notifications.

**Check:** `/episodes/s4-e09` shows "No approved recap yet" and `/studio` is empty.

## 3. Stage cheat sheet

**Prompts go in Copilot Chat (Agent mode); commands go in the terminal.** Approvals happen in the browser: `/studio` → Approve → episode page.

| Demo | Where | What to type | Expect |
|---|---|---|---|
| 1 · Recap | 💬 Copilot | `recap S4-E09 using the mm-recap skill` | ~1:35. Recap + 5 highlights grounded in the transcript, `check.py` 0 errors, reviewer note "no series-homepage links have been substituted" |
| 2 · Deck | 💬 Copilot, **sent at the end of slide 12** | `build the deck for S4-E11 with the mm-deck skill, then submit it to the studio` | ~2:35. MCP calls to the show server and Learn, deck in the chocolate theme, reviewer note on the episode vs YouTube topic mismatch |
| 3 · Guardrail | ⌨️ Terminal | `python3 .github/skills/mm-recap/scripts/check.py data/episodes/s3-e04.md --episode s3-e04 2>&1 \| grep -v WARN` | `check: 13 links, 9 errors` (8 placeholder links + missing Sources). First error matches slide 16 |
| 3 · Agent caught | ⌨️ Terminal | `python -m agents.emcee "prep S4-E12" --mock --only publisher --mock-fault placeholder --mock-delay 0.8` | ⛔ BLOCKED on `submit_draft`, then a clean resubmit |
| 4 · Whole line | ⌨️ Terminal, Studio open alongside | `python site/scripts/reset_state.py && python -m agents.emcee "prep S4-E12" --mock --mock-delay 0.4` | Emcee hands off to Coordinator, Presenter and Publisher; drafts appear in Studio. After approval, `/episodes/s4-e12` shows Deck, Social and Prep (Recap/Highlights stay empty: the episode hasn't aired) |

**Bake and switch:** if a live demo is still running at 2:15, switch to the backup (`demo/backups/s4-e09/`, `demo/backups/s4-e11/deck.html`).

## 4. Rehearse

Timed run-throughs with presenter view and `slides/narrative.md` open on a second screen. Clock checkpoints:

| End of | Target |
|---|---|
| Slide 6 (intro) | 5:00 |
| Demo 1 | 10:00 |
| Demo 2 | 15:00 |
| Demo 3 | 20:00 |
| Demo 4 | 25:00 |
| Slide 25 | 28:30 |

## 5. Reset (between rehearsals and before the talk)

```bash
python site/scripts/reset_state.py && rm -rf content/s4-e09 && git checkout -- slides/episodes/ data/
```

**Check:** `git status --short` is empty, `sync.py check` reports 0 errors, every episode page shows no factory content, and `/studio` is empty.

Leave these alone: `agents/.out/`, `slides/dist/`, the venvs and caches (all gitignored).

## 6. Export a backup copy of the deck

PDF/PPTX export needs a Chromium. A fresh Codespace has none, so install Playwright's once:

```bash
npx -y playwright install chromium
cd slides && export CHROME_PATH=$(ls -d ~/.cache/ms-playwright/chromium-*/chrome-linux64/chrome | tail -1)
npx @marp-team/marp-cli --config-file .marprc.yml deck.md --pdf  --allow-local-files -o dist/deck.pdf
npx @marp-team/marp-cli --config-file .marprc.yml deck.md --pptx --allow-local-files -o dist/deck.pptx
```

If Chromium fails to launch with missing libraries, use `npx playwright install --with-deps chromium`. Download `slides/dist/*` to your laptop (Explorer → right-click → Download…).

## What's live vs preview (first showing)

| Tool | On stage | Why |
|---|---|---|
| `mm-recap`, `mm-deck`, MCP, Marp | **Live** (Demos 1–2) | Runs in Copilot with no Azure credentials |
| Agent Framework (Emcee crew) | **Live, in mock mode** (Demos 3–4) | Mock replaces only the LLM; delegation, middleware, guardrail and MCP calls are real |
| ASSERT `run-assert-eval` | **Preview**: slide 17 + show `evals/producer/ungrounded_links.yaml` | A real run needs Azure model deployments for the generator and judge (`evals/.env`) |
| `microsoft-foundry` skill / Foundry hosting + routines | **Preview**: slide 20 + `agents/foundry/*.yaml` | Needs an Azure subscription and `azd`. The hosted server is verified locally only |

Optional proof points that run without a model. They show what ASSERT works *with*; they do **not** run ASSERT (no test generation, no judge, no scores):
- `evals/producer/ungrounded_links.yaml`: the plain-language risk ("never use the series homepage…") written as an eval spec.
- `EMCEE_EVAL_MOCK=1 evals/.venv/bin/python -c "from evals.producer.target import chat; print(chat('Recap S4-E09'))"`: calls the function ASSERT invokes for each test. It runs the Producer once with the scripted model (dry run) and prints the draft plus the **Grounding evidence** the judge would cite, in about 1 second.

The real ASSERT and Foundry runs are planned for **Season 5 of Model Mondays (December–January)**.

## Known gotchas

- **Live demo runs dirty the tree.** Demo 1 writes `content/s4-e09/` and may refresh `data/` timestamps; Demo 2 rewrites `slides/episodes/s4-e11.*`. Never commit these; run the reset.
- **The Demo 1 agent may try to re-fetch the transcript and hit the YouTube block.** It falls back to the cached copy. On stage: "YouTube blocks cloud IPs, so it uses the transcript we already cached. That's by design."
- **Demo 2 runs about 2:35 plus approvals,** which is tight for a 3:00 budget. Send the prompt at the end of slide 12 and talk through slide 13 while it works.
- **Keep the committed S4-E11 backup.** A rehearsal run produced a sparser deck with a "Confirm with host" placeholder; the backup in `demo/backups/s4-e11/` is more finished.
- **`--seed` hides the Demo 1 reveal.** It adds an approved S4-E09 recap, so approving the new one changes nothing visible. Only use it for rehearsal.
- **Run Demo 3's guardrail in the terminal, not through Copilot.** Copilot summarizes the output and hides the ⛔ BLOCKED line.
- **Upstream lists S4-E07–E09 as `scheduled`.** That's harmless: the recap skill treats an episode as completed when a recording exists.

## Q&A prep

- **"How much time did this save?"** Have a rough number ready, e.g. recaps went from "never" to about 10 minutes of review.
- **"Will this replace advocates?"** It frees time for what agents can't do: guest relationships, community, live teaching.
- **Portability:** skills also work in Claude Code and Cursor; ASSERT works with any model; mock mode needs no cloud; Act 4 has a plain GitHub Actions fallback.
