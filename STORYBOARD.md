# 🎬 Storyboard — Live Demo Arc (9 min)
### *Smarter, Faster Lucy: Copilot on the Foundry belt*

Companion to [OUTLINE.md](./OUTLINE.md), Act 5. Five demos, ~9 minutes total. Every demo threads through one of the three DevRel shows and shows a **coding agent (Copilot) producing or maintaining an enterprise agent (Foundry)** artifact — live.

---

## The three shows

The DevRel belt has three chocolate sizes. The demos ride the same three shows so the audience sees them evolve across the arc.

| Show | One-liner | Belt role |
|---|---|---|
| 🎙️ **Model Mondays** — weekly livestream on the AI model ecosystem ([aka.ms/model-mondays](https://aka.ms/model-mondays)) | Weekly news roundup + featured-model demo, live on air | **News** — small, frequent, time-boxed |
| 🚀 **Model Releases** — one runnable Foundry demo per model drop | Every new model on Foundry ships with a working sample the same day | **Proof** — bursty, high-frequency, irregular |
| 🎓 **Model Mastery** — end-to-end optimization workshops | Fine-tuning → distillation → evals → guardrails → deployment, module by module | **Depth** — monthly / quarterly, long-form |

> **News → Proof → Depth.** Same belt. Same Lucy. Three chocolate sizes.

**Capability × Show map** (each show appears at least once as a primary demo):

| Capability | Model Mondays | Model Releases | Model Mastery |
|---|:---:|:---:|:---:|
| 🍬 Skills | **D1** | · | · |
| 🤖 Coding agent → enterprise agent | · | **D2** | · |
| 🛠️ Workflows | **D3** | · | · |
| 🚚 Fleets | · | **D4** | · |
| 🔧 Agentic DevOps | · | · | **D5** |

---

## Demo 1 — 🍬 Skills · maps to: **Model Mondays** *(1.5 min)*

**The chocolate:** last week's episode → this week's recap blog **plus** a runnable Foundry agent that demos the model featured on air.

**Setup slide (10s):** *"Every Monday I ship a recap and a starter agent. Same two skills. Every week."*

**On-screen sequence:**
1. Copilot app → **Skills** panel. Two saved skills highlighted: `mm-recap-blog`, `mm-agent-scaffold`.
2. Presenter drops the episode transcript URL into chat and invokes `mm-recap-blog`. Editor canvas opens; recap streams in section by section.
3. Presenter chains into `mm-agent-scaffold` referencing the recap. Sidebar lights up with new files under `model-mondays/ep-42/` — Foundry agent code, `evals/`, README.
4. Terminal canvas: `npm run dev`. The scaffolded Foundry agent responds to a live prompt showcasing the week's featured model.
5. Presenter commits from the app. Session panel shows one green commit; recap is ready to publish.

**Payoff line:** *"That's one chocolate wrapped — on cadence, on Monday, before coffee."*

**Fallback:** pre-recorded 45-sec clip of steps 2–4; static screenshot of the running agent responding.

---

## Demo 2 — 🤖 Coding agent builds an enterprise agent · maps to: **Model Releases** *(2 min)*

**The chocolate:** a brand-new Foundry model dropped this morning → one working sample by end of day, PR open, evals attached.

**Setup slide (10s):** *"Model X shipped four hours ago. Watch a coding agent build the enterprise agent."*

**On-screen sequence:**
1. GitHub → `model-releases` repo. Open a fresh issue: *"Build a Foundry demo for Model X (dropped 09:00 today)."* Labels: `copilot`, `model-release`. Assign to Copilot.
2. Cloud session spawns in the Copilot app sidebar — new workbench appears with the issue title. Session starts autonomously.
3. Session timeline streams: reads the model card, plans the demo, picks tools, scaffolds project, wires tool bindings, writes an `evals/` folder alongside the app code.
4. Draft **PR opens** in `model-releases` — diff visible, screenshots of eval results in the PR body, one eval flagged red for human review.
5. Presenter clicks review, approves one file, requests a change on the flagged eval; Copilot pushes a fix commit in-session. PR turns green.

**Payoff line:** *"A coding agent just built an enterprise agent. I supervised — I didn't stuff any in my cheeks."*

**Fallback:** pre-recorded PR-open clip (30 sec) + screenshot gallery of the eval report and the fix commit.

---

## Demo 3 — 🛠️ Workflows · maps to: **Model Mondays** *(2 min)*

**The chocolate:** Sunday-night → Monday-morning rundown. A filed GitHub issue with the week's model landscape + a pre-scaffolded starter branch waiting for the producer.

**Setup slide (10s):** *"The show can't ship if nobody notices what dropped. Give Lucy a night shift."*

**On-screen sequence:**
1. Copilot app → **Automations** tab. Scheduled workflow `mm-sunday-rundown`. Cron: `Sun 22:00`. Trigger: scheduled.
2. Presenter opens the workflow's prompt: scan Foundry catalog, Azure AI blog, arxiv-cs.LG top 5, diff against last week, draft rundown, file issue, cut starter branch.
3. Click **Run now** to fake the clock. Session log streams: fetching catalog, diffing, drafting, filing.
4. GitHub → `model-mondays` repo shows a new issue: *"Ep 43 rundown — 3 new models, 1 breaking change"* plus a linked starter branch `ep-43-scaffold`.
5. Sidebar in the Copilot app: a scheduled-session badge appears under **My work**. Producer opens the app Monday 09:00 and this is what greets them.

**Payoff line:** *"The belt runs on Sunday night. Lucy sleeps. Monday's chocolate is already wrapped."*

**Fallback:** screenshot of the filed issue + a 20-sec loop of the scheduled-session badge appearing in the sidebar.

---

## Demo 4 — 🚚 Fleets · maps to: **Model Releases** *(2 min)*

**The chocolate:** the back catalog. `foundry-sdk@2.0` dropped → 12 sample apps in `model-releases/samples/*` need upgrading and re-eval'd. Sequentially = three days. In a fleet = twenty minutes.

**Setup slide (10s):** *"One new model, twelve old demos that just broke. Fan out."*

**On-screen sequence:**
1. Terminal canvas: `gh copilot fleet run --prompt "upgrade to foundry-sdk@2.0, re-run evals, open PR" --repos "model-releases/samples/*"`.
2. Copilot app → **Sessions** area. **Twelve sibling sessions** appear in a grid, all `in-progress`, each labelled with its sample name.
3. Presenter clicks two sessions to open side-by-side: one is passing evals cleanly; the other hit an API rename and Copilot is investigating.
4. GitHub → `model-releases` PR list refreshes: **11 green PRs open**, 1 draft PR labelled `needs-human`.
5. Sidebar: fleet parent session summarizes — *"11 wrapped · 1 flagged."* Presenter clicks the flagged one; it's queued for review, not lost.

**Payoff line:** *"The chocolates got faster — so Lucy grew arms. Eleven wrapped. One in the hat, on purpose."*

**Fallback:** pre-recorded 60-sec clip of the fleet fan-out + PR list; screenshot of the flagged session's diff.

---

## Demo 5 — 🔧 Agentic DevOps · maps to: **Model Mastery** *(1.5 min)*

**The chocolate:** a 6-module workshop repo (fine-tuning → distillation → evals → guardrails → deployment) with a live docs site. Overnight, an eval regressed on Module 4 because an upstream model bumped versions. Learners are hitting the page **right now**.

**Setup slide (10s):** *"The deep chocolates rot slower — and hurt more when they do. Copilot doesn't just build. It operates."*

**On-screen sequence:**
1. GitHub → `model-mastery` repo. Red CI badge. Failing eval on `modules/04-guardrails/`. Triggered 2 hours ago by an upstream model version bump.
2. Copilot app sidebar: a session has already opened itself in response to the CI webhook. Timeline shows it reading logs, bisecting, identifying the root cause.
3. Draft **fix PR** appears: pin model version, update workshop notes for Module 4, regenerate one screenshot in the gallery.
4. Browser canvas: preview of the rebuilt workshop site. Module 4 page shows the corrected code and updated eval numbers. Green.
5. Slide overlay: the Foundry ⇄ Copilot loop — **build → eval → deploy → monitor → fix** — closes.

**Payoff line:** *"Two factories, one loop. Copilot works the night shift so mastery stays sharp."*

**Fallback:** pre-recorded 40-sec clip of the auto-opened session and PR; screenshot of the fixed workshop page.

---

## Timing check

| Demo | Show | Budget | Cumulative |
|---|---|---|---|
| D1 — Skills | Model Mondays | 1:30 | 1:30 |
| D2 — Coding agent → enterprise agent | Model Releases | 2:00 | 3:30 |
| D3 — Workflows | Model Mondays | 2:00 | 5:30 |
| D4 — Fleets | Model Releases | 2:00 | 7:30 |
| D5 — Agentic DevOps | Model Mastery | 1:30 | 9:00 |

**Total: 9:00.** Matches Act 5 in [OUTLINE.md](./OUTLINE.md).

---

## Pre-flight checklist

- [ ] Skills `mm-recap-blog` and `mm-agent-scaffold` saved and warmed
- [ ] `model-releases` repo has a real, recent model issue queued for Demo 2
- [ ] `mm-sunday-rundown` workflow present and runnable ad-hoc
- [ ] `model-releases/samples/*` has ≥ 12 sample repos ready for fleet fan-out
- [ ] `model-mastery` repo has a deliberately-broken eval on a scratch branch
- [ ] Backup video recordings for D2 and D4 (network-dependent)
- [ ] `aka.ms/model-mondays` open in a tab as a visual anchor

---

## Narrative arc (one sentence)

**Build one → build many → schedule the build → scale the build → operate the build** — mirrors the DevRel maturity ladder from *news* through *proof* to *depth*.
