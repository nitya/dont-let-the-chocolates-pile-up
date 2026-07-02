# 🎬 Storyboard — Live Demo Arc (9 min)
### *L.U.C.Y at Work: Launch, Update, Coordinate, Yield*

**Setup shot (before Demo 1 — 15 sec, on slide):**
> Three shows on the belt. One funnel: Awareness → Engagement → Adoption. Watch L.U.C.Y — Launch,
> Update, Coordinate, Yield — run all three.

| Show | Funnel stage | Cadence | Chocolate size |
|---|---|---|---|
| 🎙️ **Model Mondays** — weekly podcast | Awareness | Weekly | Small, frequent |
| 🚀 **Model Releases** — capsule per model drop | Engagement | Bursty | Medium, irregular |
| 🎓 **Model Mastery** — 4-hr optimization workshop | Adoption | Quarterly-ish | Large, layered |

Narration spine: *awareness → engagement → adoption.* Each demo is one L.U.C.Y capability doing a
real production task on one of these three shows.

---

## 🍬 Demo 1 — Skill (1.5 min) → **Model Mondays** *(Coordinate)*

**Chocolate:** this week's transcript → recap blog + a drafted News Highlights segment (5-6 URLs).

**Why here:** open with the smallest, most frequent chocolate. Skills are the atomic station on
the line — reusable, callable, composable.

| Beat | Time | Screen | What the audience sees | What I say |
|---|---|---|---|---|
| 1 | 0:00 | Copilot app — Skills library | Two saved skills: `mm-recap-blog` and `mm-news-highlights` | "Model Mondays ships every week. Two skills own the recap." |
| 2 | 0:20 | Chat: invoke `mm-recap-blog` with transcript URL | Streaming recap draft (summary + Q&A) appears in editor canvas | "Skill 1 — turns transcript into a recap post. Same prompt every week." |
| 3 | 0:50 | Chain into `mm-news-highlights` on the same transcript | Draft list of 5-6 News Highlights URLs, pulled from what was mentioned on air | "Skill 2 — drafts next week's News Highlights segment before I've even opened a tab." |
| 4 | 1:15 | Editor canvas — final recap with embedded livestream + links | Recap post ready to publish | "That's one chocolate wrapped. Weekly, on cadence." |

**Handoff line to Demo 2:** *"Skills handle the content. But Model Mondays runs on PM work too — and that's where Lucy really drowns."*

---

## 🛠️ Demo 2 — Workflow (2 min) → **Model Mondays** *(Coordinate)*

**Chocolate:** the PM grind behind every episode — speaker confirms, calendar holds, tech checks, host assignment, Sunday-night rundown.

**Why here:** shifts from content to *ops*. This is the "hidden work in the hat" pile, made visible and automated.

| Beat | Time | Screen | What the audience sees | What I say |
|---|---|---|---|---|
| 1 | 0:00 | Copilot app — Automations tab | Scheduled workflow `mm-sunday-ops`, cron: Sun 22:00 | "Every Sunday night, this runs. Nobody logs in." |
| 2 | 0:20 | Workflow prompt open | Reads: check speaker confirmations, send reminder if unconfirmed, verify calendar hold + tech-check slot, assign host if unassigned | "Speaker coordination, calendar holds, tech checks, host assignment — all in one prompt." |
| 3 | 0:45 | Click **Run now** | Session log streams: speaker status checked, reminder email drafted, tech-check slot confirmed | "I'm faking the clock. Here it goes." |
| 4 | 1:25 | GitHub — new issue in `model-mondays` | Issue: *"Ep 43 rundown — speaker confirmed, host assigned, tech check booked Mon 8am"* | "Monday morning, the producer opens this and everything's already lined up." |
| 5 | 1:50 | Back to slide | Reveal: same pattern also drafts the Sunday rundown from Demo 1's News Highlights | "Coordinate doesn't just file paperwork — it clears Lucy's hat before the belt even starts." |

**Handoff line to Demo 3:** *"Mondays is handled. But a new model just dropped — and Mondays only gives it a headline. Someone still has to build the capsule."*

---

## 🤖 Demo 3 — Coding Agent (2 min) → **Model Releases** *(Launch)*

**Chocolate:** a brand-new Foundry model dropped this morning. We need a capsule — notebook + video script — by end of day.

**Why here:** the flagship capability — **Launch**. Coding agent builds real Engagement-stage content, grounded in the model card and Foundry docs.

| Beat | Time | Screen | What the audience sees | What I say |
|---|---|---|---|---|
| 1 | 0:00 | GitHub — repo `model-releases` | Open issue: *"Build a capsule for Model X (dropped 09:00 today)"* — labeled `copilot`, assigned to Copilot | "Model X shipped 4 hours ago. Here's the issue." |
| 2 | 0:20 | Copilot cloud session spinning up | Session reads the model card + Foundry docs, plans the capsule | "It's reading the model card and the Foundry docs before writing a line." |
| 3 | 0:50 | Session timeline — file edits streaming | Scaffolding: notebook with "hill-climbing" narrative (single frontier model → right-sized multi-model solution), video walkthrough script, README | "Notice the narrative — this isn't 'use one big model for everything.' It's picking the right model per task." |
| 4 | 1:20 | PR opens in `model-releases` | Draft PR with notebook diff, rendered output cells, video script attached | "PR is up. Capsule's ready for a human pass." |
| 5 | 1:45 | I click review, approve one cell, request a tweak on the narrative framing | Copilot pushes a fix in-session | "Human in the loop — I taste-test, L.U.C.Y re-wraps. Not a single chocolate stuffed in a cheek." |

**Handoff line to Demo 4:** *"One capsule, one model. But this provider just released six models at once."*

---

## 🚚 Demo 4 — Fleet (2 min) → **Model Releases** *(Yield)*

**Chocolate:** a provider drops six models in one day. Six capsules needed, each grounded in its own model card. Sequentially = a week. In parallel = an afternoon.

**Why here:** scale beat — **Yield**. This is where the audience feels the belt-speed change viscerally.

| Beat | Time | Screen | What the audience sees | What I say |
|---|---|---|---|---|
| 1 | 0:00 | Terminal canvas | `gh copilot fleet run --prompt "build capsule for {model}" --models provider-x/*` | "One prompt. Six models." |
| 2 | 0:20 | Copilot app — Sessions area | Six sibling sessions appear, all `in-progress` | "Six workbenches. Six capsules. Same shift." |
| 3 | 0:50 | Click into 2 sessions side-by-side | One finishing cleanly, one flagging a tool the model doesn't support yet | "Each one is independent. This one hit a missing tool binding." |
| 4 | 1:20 | GitHub — PR list on `model-releases` | 5 green PRs, 1 draft with `needs-human` label | "5 wrapped. 1 in the hat — flagged for me, not dropped on the floor." |
| 5 | 1:45 | Back to slide | "Yield is the moment the belt stops beating you." | "The chocolates got faster. L.U.C.Y grew arms." |

**Handoff line to Demo 5:** *"Awareness — done. Engagement — done at scale. But workshops are where the real damage happens when nobody's watching."*

---

## 🔧 Demo 5 — Agentic DevOps (1.5 min) → **Model Mastery** *(Update)*

**Chocolate:** a 4-hr optimization workshop — e2e lab + model-specific lab. One of the models it depends on just got deprecated overnight.

**Why here:** closes the loop — **Update**. L.U.C.Y doesn't just build — it keeps Adoption-stage content alive.

| Beat | Time | Screen | What the audience sees | What I say |
|---|---|---|---|---|
| 1 | 0:00 | GitHub — `model-mastery` repo, red CI badge | Failing lab step: deprecated model ID in the model-specific lab | "Overnight deprecation. I wasn't awake." |
| 2 | 0:15 | Copilot session — triggered by CI failure webhook | Reading logs, identifying the deprecated model, checking the Optimization Playbook for a replacement | "Agentic DevOps: CI failed → session opened itself, and it already knows the playbook." |
| 3 | 0:40 | Draft PR appears | Swap deprecated model reference, update lab instructions, refresh the e2e lab's benchmark numbers | "Fix + doc update + benchmark refresh, one PR." |
| 4 | 1:05 | Preview canvas — workshop site rebuild | Model-specific lab page shows the updated model and current numbers | "Learners see the corrected lab before the next cohort." |
| 5 | 1:25 | Slide — final loop diagram | Launch → Coordinate → Yield → Update, looping back to Launch on the next drop | "Awareness, Engagement, Adoption. And for once, Lucy clocks out without a single chocolate in her mouth." |

---

## 🎁 Closing beat (bridge to Act 6, ~10 sec)

Slide: three show logos stacked, L.U.C.Y letters beneath, arrows connecting them into a belt.

> *Model Mondays. Model Releases. Model Mastery. One funnel, three chocolate sizes, one fleet — L.U.C.Y — wrapping them all.*

---

## Cheat Sheet — Capability × Show Matrix

| L.U.C.Y capability | Model Mondays | Model Releases | Model Mastery |
|---|:---:|:---:|:---:|
| 🍬 Skill (Coordinate) | **D1** | · | · |
| 🛠️ Workflow (Coordinate) | **D2** | · | · |
| 🤖 Coding agent (Launch) | · | **D3** | · |
| 🚚 Fleet (Yield) | · | **D4** | · |
| 🔧 Agentic DevOps (Update) | · | · | **D5** |

Each funnel stage — Awareness, Engagement, Adoption — gets at least one primary demo, and the
five demos map cleanly onto L.U.C.Y's four letters (Coordinate covers two demos, since Model
Mondays carries both content and PM-ops chocolates).

---

## Timing check

| Demo | Show | L.U.C.Y | Budget | Cumulative |
|---|---|---|---|---|
| D1 — Skill | Model Mondays | Coordinate | 1:30 | 1:30 |
| D2 — Workflow | Model Mondays | Coordinate | 2:00 | 3:30 |
| D3 — Coding agent | Model Releases | Launch | 2:00 | 5:30 |
| D4 — Fleet | Model Releases | Yield | 2:00 | 7:30 |
| D5 — Agentic DevOps | Model Mastery | Update | 1:30 | 9:00 |

**Total: 9:00.** Matches Act 5 in OUTLINE.md.

---

## Pre-flight checklist

- [ ] Skills `mm-recap-blog` and `mm-news-highlights` saved and warmed
- [ ] `mm-sunday-ops` workflow present, runnable ad-hoc, with mock speaker/calendar data
- [ ] `model-releases` repo has a queued issue for Demo 3 (real recent model + model card link)
- [ ] `model-releases/provider-x/*` has 6 models ready for fleet fan-out in Demo 4
- [ ] `model-mastery` repo has a deliberately-deprecated model reference on a scratch branch
- [ ] Backup video recordings of D3 and D4 (the two live-network-dependent demos)
- [ ] `aka.ms/model-mondays` open in a tab — use as visual anchor when naming the show
