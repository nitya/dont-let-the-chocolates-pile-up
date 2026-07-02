# 🎬 Storyboard — Live Demo Arc (9 min)
### *Smarter, Faster Lucy: Copilot on the Foundry belt*

**Setup shot (before Demo 1 — 15 sec, on slide):**
> Three shows on the belt. One Lucy. Watch the same three projects evolve across five demos.

| Show | Cadence | Chocolate size |
|---|---|---|
| 🎙️ **Model Mondays** — weekly livestream | Weekly | Small, frequent |
| 🚀 **Model Releases** — one demo per model drop | Bursty, high-frequency | Medium, irregular |
| 🎓 **Model Mastery** — deep e2e workshops | Monthly / quarterly | Large, layered |

Narration spine: *news → demos → mastery.* Each demo is Copilot (coding agent) building or maintaining a Foundry (enterprise agent) chocolate for one of these three shows.

---

## 🍬 Demo 1 — Skills (1.5 min) → **Model Mondays**

**Chocolate:** last week's episode → this week's recap + a runnable Foundry agent that demos the new model featured on air.

**Why here:** open with the smallest chocolate on the belt. Skills = the atomic unit of "smarter Lucy." Reusable, callable, composable.

| Beat | Time | Screen | What the audience sees | What I say |
|---|---|---|---|---|
| 1 | 0:00 | Copilot app — Skills library | Two saved skills: `mm-recap-blog` and `mm-agent-scaffold` | "Model Mondays ships every week. Two skills own the recap." |
| 2 | 0:20 | Chat: invoke `mm-recap-blog` with transcript URL | Streaming recap draft appears in editor canvas | "Skill 1 — turns transcript into a recap post. Same prompt every week." |
| 3 | 0:50 | Chain into `mm-agent-scaffold` on the recap | New folder in `model-mondays/ep-42/` with a Foundry agent scaffold demoing this week's featured model | "Skill 2 — scaffolds the Foundry agent for the model we just talked about." |
| 4 | 1:15 | Terminal canvas — `npm run dev` on the scaffolded agent | Agent responds to a sample prompt | "That's one chocolate wrapped. Weekly, on cadence." |

**Handoff line to Demo 2:** *"Skills are great when Lucy knows what's coming. But new models don't ship on a schedule…"*

---

## 🤖 Demo 2 — Coding Agent → Enterprise Agent (2 min) → **Model Releases**

**Chocolate:** a brand-new Foundry model dropped this morning. We need one working sample by end of day.

**Why here:** the flagship capability — **coding agents building enterprise agents.** This is the thesis, live.

| Beat | Time | Screen | What the audience sees | What I say |
|---|---|---|---|---|
| 1 | 0:00 | GitHub — repo `model-releases` | Open issue: *"Build a Foundry demo for Model X (dropped 09:00 today)"* — labeled `copilot`, assigned to Copilot | "Model X shipped 4 hours ago. Here's the issue." |
| 2 | 0:20 | Copilot cloud session spinning up | Session picks up issue, reads model card, plans | "Copilot reads the model card, plans the demo, picks tools." |
| 3 | 0:50 | Session timeline — file edits streaming | Scaffolding project: agent code, tool bindings, `evals/` folder, README | "Notice it's writing evals too — not just happy-path code." |
| 4 | 1:20 | PR opens in `model-releases` | Draft PR with diff, screenshots of eval results, sample chat transcript | "PR is up. Evals ran. Two failures flagged in the description." |
| 5 | 1:45 | I click review, approve one file, request change on another | Copilot pushes a fix in-session | "Human in the loop. I taste-test, Lucy re-wraps." |

**Handoff line to Demo 3:** *"That works for today's model. But how did the issue get filed in the first place?"*

---

## 🛠️ Demo 3 — Workflows (2 min) → **Model Mondays**

**Chocolate:** Sunday night → Monday morning rundown. The show can't ship if nobody notices what dropped.

**Why here:** shifts from *reactive* (Demo 2) to *scheduled*. Now Lucy has a night shift.

| Beat | Time | Screen | What the audience sees | What I say |
|---|---|---|---|---|
| 1 | 0:00 | Copilot app — Automations tab | Scheduled workflow `mm-sunday-rundown`, cron: Sun 22:00 | "Every Sunday night, this runs. Nobody logs in." |
| 2 | 0:20 | Workflow prompt open | Reads: scan Foundry catalog + Azure AI blog + arxiv-cs.LG top 5, summarize, file issue | "The prompt is a skill — same one from Demo 1, wrapped in a trigger." |
| 3 | 0:45 | Click **Run now** | Session log streams: fetching catalog, diffing against last week, drafting rundown | "I'm faking the clock. Here it goes." |
| 4 | 1:25 | GitHub — new issue in `model-mondays` | Issue: *"Ep 43 rundown — 3 new models, 1 breaking change"* + starter branch link | "Rundown issue is filed. Starter branch is pre-scaffolded. Monday's producer opens the app and finds this waiting." |
| 5 | 1:50 | Back to slide | Reveal: this same pattern runs for Model Releases too (watches Foundry release feed) | "Same trigger, different belt." |

**Handoff line to Demo 4:** *"One new model = one demo. But what about the 12 old demos that now break?"*

---

## 🚚 Demo 4 — Fleets (2 min) → **Model Releases**

**Chocolate:** the back catalog. New SDK version dropped → 12 sample apps need upgrading + re-eval'd. Sequentially = 3 days. In parallel = 20 minutes.

**Why here:** scale beat. This is where the audience feels the belt-speed change viscerally.

| Beat | Time | Screen | What the audience sees | What I say |
|---|---|---|---|---|
| 1 | 0:00 | Terminal canvas | `gh copilot fleet run --prompt "upgrade to foundry-sdk@2.0, re-run evals, open PR" --repos model-releases/samples/*` | "One prompt. N repos." |
| 2 | 0:20 | Copilot app — Sessions area | 12 sibling sessions appear, all `in-progress` | "12 workbenches. 12 Lucys. Same shift." |
| 3 | 0:50 | Click into 2 sessions side-by-side | One passing evals, one failing — Copilot investigating the failure | "Each one is independent. This one hit an API rename." |
| 4 | 1:20 | GitHub — PR list on `model-releases` | 11 green PRs, 1 draft with `needs-human` label | "11 wrapped. 1 in the hat — flagged for me, not dropped on the floor." |
| 5 | 1:45 | Back to slide | "Fleet = the moment the belt stops beating you." | "The chocolates got faster. Lucy grew arms." |

**Handoff line to Demo 5:** *"News chocolate — done. Demo chocolate — done. But the deep workshops? They rot slower and hurt more when they do."*

---

## 🔧 Demo 5 — Agentic DevOps (1.5 min) → **Model Mastery**

**Chocolate:** a 6-module workshop repo (fine-tuning → evals → guardrails → deployment). One eval regressed overnight. Site is live at `aka.ms/…`. Learners are hitting it *now*.

**Why here:** closes the loop. Copilot doesn't just build — it operates. This is the "night shift that never sleeps" line landing.

| Beat | Time | Screen | What the audience sees | What I say |
|---|---|---|---|---|
| 1 | 0:00 | GitHub — `model-mastery` repo, red CI badge | Failing eval on Module 4 (guardrails), triggered 2 hours ago | "Overnight regression. I wasn't awake." |
| 2 | 0:15 | Copilot session — triggered by CI failure webhook | Reading logs, bisecting, identifying root cause (upstream model version bump) | "Agentic DevOps: CI failed → session opened itself." |
| 3 | 0:40 | Draft PR appears | Pin model version, update workshop notes, regenerate one screenshot | "Fix + doc update + gallery refresh, one PR." |
| 4 | 1:05 | Preview canvas — workshop site rebuild | Module 4 page shows updated code + new eval numbers | "Site preview. Learners see the corrected page next refresh." |
| 5 | 1:25 | Slide — final loop diagram | Foundry ⇄ Copilot loop: build → eval → deploy → monitor → fix | "Two factories. One loop. Lucy sleeps." |

---

## 🎁 Closing beat (bridge to Act 6, ~10 sec)

Slide: three show logos stacked, five Copilot capabilities beneath, arrows connecting them into a belt.

> *Model Mondays. Model Releases. Model Mastery. One belt, three sizes, five capabilities — and a Lucy who wraps them all.*

---

## Cheat Sheet — Capability × Show Matrix

| Capability | Model Mondays | Model Releases | Model Mastery |
|---|:---:|:---:|:---:|
| 🍬 Skills | **D1** | · | · |
| 🤖 Coding agent → agent | · | **D2** | · |
| 🛠️ Workflows | **D3** | (also runs here) | · |
| 🚚 Fleets | · | **D4** | · |
| 🔧 Agentic DevOps | · | · | **D5** |

Each show appears at least once as a **primary** demo. The narrative arc — **build one → build many → schedule the build → scale the build → operate the build** — mirrors the DevRel maturity ladder: *news → demos → mastery.*

---

## Timing check

| Demo | Show | Budget | Cumulative |
|---|---|---|---|
| D1 — Skills | Model Mondays | 1:30 | 1:30 |
| D2 — Coding agent | Model Releases | 2:00 | 3:30 |
| D3 — Workflows | Model Mondays | 2:00 | 5:30 |
| D4 — Fleets | Model Releases | 2:00 | 7:30 |
| D5 — Agentic DevOps | Model Mastery | 1:30 | 9:00 |

**Total: 9:00.** Matches Act 5 in OUTLINE.md.

---

## Pre-flight checklist

- [ ] Skills `mm-recap-blog` and `mm-agent-scaffold` saved and warmed
- [ ] `model-releases` repo has a queued issue for Demo 2 (real recent model)
- [ ] `mm-sunday-rundown` workflow present and runnable ad-hoc
- [ ] `model-releases/samples/*` has ≥ 12 sample repos ready for fleet fan-out
- [ ] `model-mastery` repo has a deliberately-broken eval on a scratch branch
- [ ] Backup video recordings of D2 and D4 (the two live-network-dependent demos)
- [ ] `aka.ms/model-mondays` open in a tab — use as visual anchor when naming the show
