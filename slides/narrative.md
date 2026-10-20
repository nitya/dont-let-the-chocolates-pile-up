# Narrative: the talk, end to end

A presenter's script for [deck.md](deck.md), covering all 25 slides in 30 minutes. For each slide it gives the **speaker notes** (copied word for word from the deck), **presenter guidance** on what to say, do and stress, and a **hand-off** line into the next slide. Demo steps and fallbacks live in [demo/RUNBOOK.md](../demo/RUNBOOK.md); this file covers the *story*.

> If you change the speaker notes in `deck.md`, update them here too. The deck is the source of truth.

---

## The story in one breath

> DevRel is Lucy on the chocolate line: the belt (developer demand for AI content) keeps speeding up, and a one-person team copes the way Lucy did, by **swallowing** work, **hiding it in their hat**, and **dropping it on the floor**. The fix isn't to wrap faster. It's to build a factory: 
> - **make it work** (decompose into skills, delegate to a crew of agents grounded by MCP), then
> - **make it better** (measure the crew against a spec, fix, re-measure), 
> - **make it scale** (triggers and gates, coding agents keeping the labs fresh, humans approving). 
>
> The advocate's job shifts from making every artifact to designing the factory, and the audience shifts from watching instructor-led content to running self-guided learning themselves.

## Key technologies, and why each one is on the line

Every tool has one job on the line and one sentence that explains why it's there. If you only get one line per tool on stage, use the one in the last column.

| Technology | Its job on the line | Where | Why it's here (say this) |
|---|---|---|---|
| **GitHub Copilot (agent mode)** | The hands: runs skills and calls MCP tools from the editor | Slides 5, 10, 14, 18 | "It picks the right skill from its *description*, so the checklist decides how the work gets done, not the prompt." |
| **Agent Skills** (`SKILL.md`) · `mm-recap`, `mm-deck`, `refresh-model-mondays-data` | The **stations**: one repeatable checklist per job, in a folder | Slides 5, 9, 10, 14 | "A skill is the checklist you'd hand a new teammate on day one, and it works in Copilot, Claude Code, Cursor and more." |
| **MCP**: Model Mondays server + Microsoft Learn MCP | The **grounding**: episode facts from our server, product facts from Learn | Slides 5, 12, 13, 14 | "Same trusted sources every episode. And the server has `submit_draft` but **no approve tool**, so humans keep the last word." |
| **Marp** | **Slides as code**: Markdown + a theme | Slides 5, 13, 14 (and this deck) | "Agents write text. Marp turns that text into this deck, and git can diff it." |
| **Microsoft Agent Framework** | The **crew**: Emcee orchestrates four specialists (agents as tools), with middleware guardrails and OpenTelemetry traces | Slides 5, 12, 20, 21 | "Open-source orchestration. The same crew runs on my laptop and as a hosted agent on Foundry." |
| **ASSERT `run-assert-eval`** | The **local inspector**: turns a plain-language risk into evals, judges with evidence, re-measures | Slides 5, 17, 18, 20 | "Turn 'never invent links' into a test you run every week. The before/after delta is the evidence." |
| **`microsoft-foundry` skill** + **Microsoft Foundry** | The **production inspector and host**: deploys the agent, runs evals and continuous monitoring, schedules routines | Slides 5, 17, 20, 21 | "When the crew is deployed, this is where it runs and gets watched, and a skill drives it for you." |
| **Copilot coding agent** | The **maintenance crew**: refreshes labs and samples when SDKs change | Slide 20 (+ 22, 24) | "Labs that keep themselves current mean learners trust them, and they stay curious instead of getting stuck." |
| **GitHub issues + Actions** | **Triggers and gates**: an issue starts the line, and CI fails a PR that regresses an eval | Slides 20, 21 | "Triggers, not reminders. Gates, not heroics." |
| **The studio** (site review queue) | The **human gate**: every draft waits here for a person | Slides 12, 14, 20, 21 | "Agents propose. Humans dispose." |

**How the tools map to the three steps:** 
 - *Make it work* = Copilot + Skills + MCP + Marp + Agent Framework. 
 - *Make it better* = ASSERT + Foundry evals. 
 - *Make it scale* = Foundry routines + GitHub triggers/CI + coding agent
 - ... with the studio as the human gate throughout.

## Abstract check: does the talk deliver what it promised?

The [abstract](../README.md#abstract) is what got people into the room. Each promise below must be **said out loud**, not just shown on a slide.

| # | Abstract promise | Where it lands | Status / what to do |
|---|---|---|---|
| 1 | "Content demand can feel like Lucy on the chocolate factory line" | Slides 2–3 | ✅ |
| 2 | "What if… you had a virtual team step in to balance the load?" | Slide 4 (bold question on the card) | ✅ Same words. Read it out loud. |
| 3 | "Turning a one-person DevRel team into a coordinated production line" | Slide 1 (subtitle), slide 8 | ✅ |
| 4 | "A real-world system behind a **weekly podcast and AMA series**" | Slides 1, 4 | ⚠️ The deck only says "livestream". Say "weekly livestream, which doubles as a podcast, plus an AMA series" on slide 1 or 4. |
| 5 | "**Speaker coordination**, content creation, and distribution broken into stages" | Slides 4, 8, 12 | ✅ Name *speaker coordination* on slide 8 (the Coordinate station). |
| 6 | "Skills… automatically transforming livestreams into **transcripts**, summaries, and polished recaps" | Slides 8 (Capture), 9, 10 | ⚠️ **No transcripts in `data/` yet** (YouTube blocks Codespaces IPs). Fetch them before the talk (see prep), or Demo 1 grounds on chapters only and the "transcripts" promise is only partly met. |
| 7 | "Slide creation… streamlined using tools like **Marp**, grounded by **MCP servers**" | Slides 13–14 | ✅ The strongest match. Demo 2 *is* this promise. |
| 8 | "**Coding agents** reduce maintenance overhead while **sparking curiosity and deeper engagement**" | Slide 20 (one callout), slides 22, 24 | ⚠️ **The weakest point.** It's a single callout with no demo. Land it in words on slides 20 and 24 (guidance below). |
| 9 | "Rethink DevRel… from handcrafted, instructor-led content to scalable, **self-guided learning**" | Slide 22 | ✅ Same words as the table. |
| 10 | "Stop chasing the conveyor belt… without having to **stuff the extra content in your hat**" | Slide 25 | ✅ Use the abstract's full line, *including* the hat. It closes the Lucy loop. |

**Beyond the abstract:** 
- Act 3 (evals) and most of Act 4 (triggers, CI gates) aren't in the abstract. 
- That's a bonus, not a mismatch, but frame them as the answer to the abstract's implied question:
  - "*how do you trust the line?*" (Act 3) and 
  - "*how does it keep running without you?*" (Act 4).

## The spine: Lucy's three coping moves are the three failure modes

Slide 2 isn't just an icebreaker. Everything Lucy does to keep up maps onto an act:

| Lucy… | Pile-up | DevRel version | Act | Fix |
|---|---|---|---|---|
| **eats** the chocolates | *Swallowed* | Recap that never gets written | 1 · Decompose | A skill per station |
| **hides** them  | *In the hat* | Hidden ops work: briefs, reminders, run-of-show, slides | 2 · Delegate | A crew of agents + MCP |
| **drops** them | *On the floor* | Mistakes nobody catches until a learner does | 3 · Optimize | Evals: measure, fix, re-measure |
| …can't slow the **belt** | *The belt itself* | Demand keeps accelerating | 4 · Automate | Triggers, gates, humans approve |

**Plant it on slide 2, pay it off at every act divider.** Each divider slide has a "Pile-up:" line. Read it out loud every time; that repetition is what makes the talk feel like one story instead of four demos.

## Threads to plant and pay off

| Plant | Where | Pay off | Where |
|---|---|---|---|
| "Hold on to that word: **trust**." | Slide 3 | "Remember trust? This is where it breaks." | Slide 16 |
| "**Never invent links**" in the skill | Slide 9 | 83 placeholder links found in our own repo | Slide 16 |
| Two peach cards: `run-assert-eval`, `microsoft-foundry` | Slide 5 | "The two inspectors" | Slide 17 |
| "If you automate before you measure, you pile chocolate up faster." | Slide 6 | Act 4 opens with that exact order | Slide 19 |
| "**No approve tool**: agents propose, humans dispose." | Slide 12 | Studio gate in the automated line | Slides 20–21 |
| "This deck is Marp too." | Slides 5, 13 | Demo 2 renders in this deck's theme | Slide 14 |
| Model Mondays numbers (50 eps, 60K views) | Slide 4 | "Every livestream becomes a reusable asset" | Slide 22 |

## Clock

| Segment | Slides | Starts | Length |
|---|---|---|---|
| Intro: the belt and the playbook | 1–6 | 0:00 | 5:00 |
| Act 1 · Make it work: Decompose | 7–10 | 5:00 | 5:00 (Demo 1: 3:00) |
| Act 2 · Make it work: Delegate | 11–14 | 10:00 | 5:00 (Demo 2: 3:00) |
| Act 3 · Make it better | 15–18 | 15:00 | 5:00 (Demo 3: 3:00) |
| Act 4 · Make it scale | 19–21 | 20:00 | 5:00 (Demo 4: 3:30) |
| Wrap | 22–25 | 25:00 | 3:30 |
| Buffer / Q&A | | 28:30 | 1:30 |

**Checkpoints:** if you're past **10:30** when Demo 1 ends, or **20:30** when Demo 3 ends, switch to the backup sooner in the next demo. Don't trim the wrap.

---

<br/>

## Intro: the belt and the playbook (0:00 → 5:00)

**Goal:** make the audience feel the pile-up, show that you lived it, and give them the three-step map before any tool appears.

### 1 · Title: *Don't Let the Chocolate Pile Up* · 0:00 → 0:30

**On screen:** Title, subtitle, byline, factory hero art.

**Speaker notes:**
> [0:00 — INTRO, 5 min total]
> Hi everyone. I'm Nitya. I run a weekly livestream, an AMA series, a blog, slides, samples — and for a long time, I ran it mostly by myself.
> Today: how I turned that into a production line of agents and skills — and the playbook you can steal.

**Presenter guidance:**
- Short and warm. Don't read the title; the art does the work.
- Stress **"mostly by myself"**. That's the hook everyone in DevRel recognizes.
- **Abstract promise #4:** name the formats the abstract does, "a weekly livestream that doubles as a podcast, and an AMA series", so people who read the abstract hear what they came for.
- "The playbook you can steal" promises them something to take home, which you deliver on slide 24.

**Hand-off →** "But first, a confession about where the chocolate comes in."

### 2 · Why chocolate? Lucy on the line · 0:30 → 1:30

**On screen:** Lucy and Ethel still; "the belt is content demand".

**Speaker notes:**
> Who's seen this? Lucy and Ethel, the chocolate factory. The belt speeds up. They eat chocolates, hide them in their hats, stuff them in their blouses — anything to look like they're keeping up.
> That is DevRel right now. Every week: new models, new SDKs, new tools. Every one is a chocolate on the belt.

**Presenter guidance:**
- **Ask for hands** on "Who's seen this?" and wait a beat. It's the one moment of audience participation and it sets the tone.
- **Plant the spine here.** Count Lucy's moves out slowly on your fingers: *eat… hide… drop*. You'll come back to each one.
- Land the metaphor: "Every new model, SDK and tool is a chocolate on the belt."

**Hand-off →** "And the belt isn't just fast. It's speeding up."

### 3 · The belt is speeding up · 1:30 → 2:15

**On screen:** 84% / 51% / 46% stat cards; "trusted, human-verified content" callout.

**Speaker notes:**
> Developers moved fast: 84% use or plan to use AI tools; half of pros use them daily.
> But trust is going DOWN: 46% don't trust the accuracy. That's the gap DevRel fills: fast AND trustworthy.
> Hold on to that word — trust. It comes back in Act 3.

**Presenter guidance:**
- Read only the three numbers; let the cards carry the rest.
- Turn on **"But"**. The 46% (plum card) is the slide's real point. Adoption is up, trust is down.
- Say "**fast AND trustworthy**" deliberately. That's the tension the whole talk resolves: Acts 1, 2 and 4 are about *fast*, Act 3 is about *trustworthy*.
- Plant: "Hold on to that word: **trust**."

**Hand-off →** "So what does that belt look like for one advocate?"

### 4 · The Lucy moment: one advocate, one weekly show · 2:15 → 3:15

**On screen:** Coordinate / Create / Present / Distribute rows; Model Mondays numbers.

**Speaker notes:**
> This is my belt: Model Mondays. A weekly livestream about AI models on Microsoft Foundry.
> 50 episodes, 4 seasons, 38 hours live, 60K views, 30+ guests. Real data — it's in the repo, refreshed by a skill.
> Every episode has the same four kinds of work. None of it is hard. All of it is relentless.

**Presenter guidance:**
- This is **your credibility slide**. You're not theorizing; you ran this show.
- Mention "real data, refreshed by a skill" in passing. It quietly shows that the factory already exists.
- The line to land: "**None of it is hard. All of it is relentless.**" Pause after it.
- Read the bold question on the card ("What if a virtual team stepped in…?") as the turn into the solution.

**Hand-off →** "Here's the toolbox that virtual team works with."

### 5 · The toolkit: files, protocols and repos · 3:15 → 4:15

**On screen:** Six cards. Top row: Agents + Skills, MCP, Marp. Bottom row (peach): Agent Framework, `run-assert-eval`, `microsoft-foundry`.

**Speaker notes:**
> Before the playbook, the toolbox. This is an open-source crowd, so: everything here is a file, a protocol, or a repo.
> Top row — the line itself: agents + skills, MCP, Marp.
> Bottom row (peach) — the two skills I want you to remember: run-assert-eval from ASSERT, and microsoft-foundry. They're both about the same thing: observability and optimization. We'll meet them in Act 3.

**Presenter guidance:**
- **Don't explain every card.** This is a preview, not a tutorial. Name the top row in one breath, then gesture to the peach row.
- "Everything here is a file, a protocol, or a repo" is the open-source pitch for this audience. Say it with conviction.
- Plant the peach cards: "**the two I want you to remember**."
- If you're running long, this is the slide to shorten to 30 seconds.

**Hand-off →** "Tools are easy. The order you use them in is the hard part."

### 6 · The playbook: Make it work. Make it better. Make it scale. · 4:15 → 5:00

**On screen:** Three banded cards mapped to Acts 1–2, 3, 4; footnote about order.

**Speaker notes:**
> Here's the whole talk on one slide. Three steps, four acts, five minutes each.
> Make it work: decompose and delegate. Make it better: optimize. Make it scale: automate.
> The order matters. If you automate before you measure, you just pile chocolate up faster.
> [5:00]

**Presenter guidance:**
- **This is the map.** Slow down. The audience should be able to repeat the three steps after this slide.
- Say the three steps with a rhythm: work, better, scale.
- Land the warning that justifies the order: "**If you automate before you measure, you just pile chocolate up faster.**"
- **Clock check: 5:00.**

**Hand-off →** "So let's make it work. Starting with the first chocolate Lucy eats."

---

<br/>

## Act 1 · Make it work: Decompose the line (5:00 → 10:00)

**Pile-up: swallowed.** **Goal:** show that one show breaks down into small stations, and that a station is just a skill in a folder.

### 7 · Divider: Act 01, Decompose the line · 5:00 → 5:20

**On screen:** "Break one show into stations. Give each station a skill." · *Pile-up: swallowed.*

**Speaker notes:**
> [5:00 — ACT 1, 5 min]
> First chocolate: the recap. Every livestream should get a recap, highlights, a summary. Most weeks it just... doesn't happen. Silently swallowed.

**Presenter guidance:**
- **Read the pile-up line out loud.** "Swallowed": Lucy eating the chocolate.
- Admit it; it's relatable: "Most weeks it just… doesn't happen."

**Hand-off →** "To fix it, I had to see the whole line first."

### 8 · The production line: five stations · 5:20 → 6:10

**On screen:** Coordinate → Capture → Transform → Present → Distribute; "Every station has a human checkpoint."

**Speaker notes:**
> Decompose. Five stations for one show: Coordinate, Capture, Transform, Present, Distribute.
> The trick is to make each one small and repeatable — something you'd hand a new teammate on day one with a checklist.
> That checklist is a skill.

**Presenter guidance:**
- Sweep left to right with your hand as you name the stations. It's a conveyor belt.
- **Abstract promises #5 and #6:** on *Coordinate*, say "**speaker coordination**: booking guests, briefs, reminders". On *Capture → Transform*, say the abstract's chain: "the livestream becomes a **transcript**, the transcript becomes **summaries and polished recaps**."
- (Slide 4 had four kinds of work; Capture is the station that's mostly automatic. You don't need to call this out.)
- The idea to land: "**something you'd hand a new teammate on day one with a checklist.**" Everyone has onboarded someone, so this makes "skill" concrete.
- Point at the footnote: "**Agents do the heavy lifting, you own the voice.**" This is the first of several human-in-the-loop beats.

**Hand-off →** "That checklist is a skill. Here's one."

### 9 · Skills as stations: a skill is a station in a folder · 6:10 → 7:00

**On screen:** `mm-recap/SKILL.md` code block; Ground → Summarize → Polish → Review & ship.

**Speaker notes:**
> A skill is just a folder with a SKILL.md: a name, a description that tells the agent WHEN to use it, and the steps.
> Specialized, testable, swappable — and reused every single week.
> Notice step 4 and the "never invent links" rule. Remember that for Act 3.

**Presenter guidance:**
- Point at the three parts in order: **name**, **description** ("tells the agent *when*"), **steps**.
- "Just a folder" is the reassurance: anyone in the room can write one tonight.
- **Plant:** physically point at "**Never invent links**" and say "Remember that." It pays off on slide 16.

**Hand-off →** "Let's watch it swallow a recap, for once in the good way."

### 10 · DEMO 01: Livestream in, recap out · 7:00 → 10:00

**On screen:** Demo card; command `recap S4-E09 using the mm-recap skill`.

**Speaker notes:**
> [DEMO 1 — 3:00. See demo/RUNBOOK.md]
> Open VS Code → Copilot Chat (agent mode). Type: "recap S4-E09 using the mm-recap skill".
> Point out: it found the skill from its description; it reads data/episodes.json; it uses transcript if present, otherwise YouTube chapters.
> Show output: demo/outputs/s4-e09/recap.md. Highlight the Sources section.
> Fallback: open demo/backups/s4-e09/recap.md — "I ran this an hour ago so we're not waiting on the model."
> Bridge: "Skills handle the content. But the show also runs on hidden ops work — and that's where Lucy really drowns."
> [10:00]

**Presenter guidance:**
- **Status: Live.** Follow the Demo 01 section of the [RUNBOOK](../demo/RUNBOOK.md).
- Three things to narrate, and only three: (1) it **found the skill from its description**, (2) it **grounded** itself in the show's data, (3) a **guardrail** (`check.py`) blocks placeholder links.
- **Abstract promise #6 (transcripts):** if the S4-E09 transcript has been fetched, say "it's reading the **transcript** of last week's livestream", which is the abstract's exact claim. If not, be honest: "no transcript yet, so the skill's rule kicks in: no quotes, only what the chapters support." That's a good trust moment, but it only partly delivers the promise, so fetch the transcript.
- Landing moment: the **Sources** section, then Studio → Approve → the recap fades into `/episodes/s4-e09`. The human approval click is the visual payoff of slide 8's footnote.
- **Fallback at 2:15:** switch to `demo/backups/s4-e09/recap.md` and stay calm: "Same skill, same output."
- **Clock check: 10:00.**

**Hand-off (bridge) →** "Skills handle the content. But the show also runs on hidden ops work, and that's where Lucy really drowns."

---

<br/>

## Act 2 · Make it work: Delegate to a crew (10:00 → 15:00)

**Pile-up: in the hat.** **Goal:** go from one skill to a crew of agents, grounded by MCP, where agents propose and humans approve.

### 11 · Divider: Act 02, Delegate to a crew · 10:00 → 10:20

**On screen:** "Skills are stations. Agents are the crew that runs them, grounded by MCP." · *Pile-up: in the hat.*

**Speaker notes:**
> [10:00 — ACT 2, 5 min]
> Second chocolate pile: in the hat. The hidden work nobody sees — the brief, the reminders, the run-of-show, the slides.

**Presenter guidance:**
- Read the pile-up line. "In the hat": Lucy hiding chocolate where nobody can see it.
- Make it personal: "Nobody sees this work, so nobody knows when it's piling up, including me."

**Hand-off →** "One skill can't clear the hat. I needed a crew, with someone running it."

### 12 · Meet Emcee: the M.C. that runs the show · 10:20 → 11:20

**On screen:** Coordinator / Producer / Presenter / Publisher; Emcee callout; "No approve tool".

**Speaker notes:**
> Delegate. One orchestrator — I call it Emcee: master of ceremonies, and M.C. for Model Catalog — and four specialists.
> Coordinator clears the hat. Producer owns content. Presenter builds slides. Publisher handles distribution.
> Each specialist reuses the skills from Act 1. And every one is grounded through MCP.
> Key design choice: the MCP server has submit_draft but NO approve tool. Agents propose. Humans dispose.

**Presenter guidance:**
- Enjoy the name: "master of ceremonies, and **M.C. for Model Catalog**" usually gets a smile.
- Map each specialist to a station from slide 8, so the audience sees that Act 2 builds on Act 1 rather than starting over.
- **The line of the act:** "**Agents propose. Humans dispose.**" Say it slowly. It answers the trust concern from slide 3 before anyone asks.

**Hand-off →** "Let me zoom in on my favorite crew member."

### 13 · Slides on the line: Marp + MCP · 11:20 → 12:00

**On screen:** Marp builds / MCP grounds / Why it matters, "This deck is Marp too."

**Speaker notes:**
> Presenter is my favorite. Slides are Markdown — so agents can write them, git can diff them, and a theme makes them look like this.
> MCP grounds them: episode facts from our own server, product facts from Microsoft Learn.

**Presenter guidance:**
- **The meta moment:** gesture at the slide itself: "**a theme makes them look like *this*.**" The audience realizes they've been watching an agent-friendly deck all along.
- Name the two grounding sources: our own server for episode facts, Microsoft Learn for product facts. This is the "trustworthy" half of fast AND trustworthy.
- Keep it short; the demo makes the point better.

**Hand-off →** "Let's have the Presenter build next week's deck."

### 14 · DEMO 02: A crew member builds next week's deck · 12:00 → 15:00

**On screen:** Demo card; command `build the deck for S4-E11 with the mm-deck skill`.

**Speaker notes:**
> [DEMO 2 — 3:00. See demo/RUNBOOK.md]
> Prompt: "build the deck for S4-E11 with the mm-deck skill".
> Show: MCP tool calls (get_episode, search_episodes, Learn docs) → slides/episodes/s4-e11.md → marp render → preview.
> If the site is running: submit_draft → open /studio → Approve → episode page shows the deck.
> Fallback: demo/backups/s4-e11/deck.html.
> Bridge: "That's two acts of 'make it work'. But how do I know it's any GOOD?"
> [15:00]

**Presenter guidance:**
- **Status: Live.** Follow the Demo 02 section of the [RUNBOOK](../demo/RUNBOOK.md).
- Narrate the **MCP calls** as they appear: show data, then Learn docs. That's grounding, visibly.
- **Point out the reviewer note:** the skill *flags* the mismatch between the episode page and the YouTube listing instead of guessing. It's a small moment that sets up Act 3: agents should surface doubt, not hide it.
- Payoff: the rendered deck is in **this deck's theme**. "Same Markdown, same theme, same agent workflow as what you're looking at."
- Approve in Studio, then show the Deck tab on `/episodes/s4-e11`.
- **Fallback:** `demo/backups/s4-e11/deck.html` (+ `python demo/submit_backup.py s4-e11 deck`).
- **Clock check: 15:00.** This is the halfway point and the story's turn.

**Hand-off (bridge) →** "That's two acts of *make it work*. But how do I know it's any **good**?"

---

<br/>

## Act 3 · Make it better: Inspect before you ship (15:00 → 20:00)

**Pile-up: on the floor.** **Goal:** shift from speed to trust. Show a real failure, then show how to measure, fix and prove it.

> **Tone shift.** Acts 1–2 are upbeat ("look what it can do"). Act 3 is the honest turn ("here's where it went wrong"). Slow down and lower your voice a little. This act is what makes the talk credible.

### 15 · Divider: Act 03, Inspect before you ship · 15:00 → 15:20

**On screen:** "Speed without inspection just moves the pile." · *Pile-up: on the floor.*

**Speaker notes:**
> [15:00 — ACT 3, 5 min]
> Third pile: on the floor. The chocolates you drop and don't notice. Until a learner does.

**Presenter guidance:**
- Read the pile-up line. "On the floor": the last of Lucy's three moves. The spine is complete.
- Pause after "**Until a learner does.**"
- Read the lede too: "**Speed without inspection just moves the pile.**" It reframes Acts 1–2. Going faster on its own doesn't fix anything.

**Hand-off →** "And I don't mean hypothetically. Our own line already did it."

### 16 · Caught in the act: our own line already dropped chocolates · 15:20 → 16:20

**On screen:** 83 links, 11 pages, the bad link pattern, 87% / 81% concern stats.

**Speaker notes:**
> True story. While building this talk I imported our own public repo — and found 83 "News Highlights" links across 11 episodes that all point to... the series homepage.
> They look fine in review. They're useless to a learner. And an agent trained on these pages would happily copy the pattern.
> Developers already worry about this: 87% concerned about agent accuracy.
> So we stop eyeballing and start measuring.

**Presenter guidance:**
- **This is the most important slide in the talk.** It's real, it's yours, and it's a little embarrassing. That's why it works.
- Read the code sample out loud: `[Microsoft Agent Framework](https://aka.ms/model-mondays)`. Let them see that it *looks* correct.
- **Pay off two plants at once:**
  - "Remember **never invent links** from the skill? *This* is why that rule exists."
  - "Remember **trust** from the start? 87% of developers are worried about exactly this."
- The key point: "**Agents copy patterns, including the bad ones, at the speed of the belt.**"
- Land the turn: "**So we stop eyeballing and start measuring.**"

**Hand-off →** "For that, the line needs inspectors. Remember the two peach cards?"

### 17 · Two inspectors on the line: observability + optimization · 16:20 → 17:00

**On screen:** `run-assert-eval` card vs `microsoft-foundry` card.

**Speaker notes:**
> Two skills — same idea, different scope.
> run-assert-eval: local-first. You describe a risk in plain English — "highlights must never use placeholder links" — and it generates tests, runs them, judges with trace evidence, proposes a fix, and re-measures. Works with any model, any framework.
> microsoft-foundry: when the crew is deployed. Batch evals, failure clustering, prompt optimization, version comparison, continuous monitoring.
> Both are skills — so your coding agent drives them for you.

**Presenter guidance:**
- **Pay off slide 5:** "These are the two peach cards I asked you to remember."
- Frame them as **two scopes**: "on my laptop" (`run-assert-eval`) and "in production" (`microsoft-foundry`). Don't go through every bullet.
- Use the plain-English risk as the example: "*highlights must never use placeholder links*". It ties directly back to slide 16.
- The closing line is the elegant part: "**Both are skills, so your coding agent drives them for you.**" The inspection tools are themselves stations on the line.

**Hand-off →** "Let's put the Producer under inspection."

### 18 · DEMO 03: Measure the Producer, fix it, prove it · 17:00 → 20:00

**On screen:** Demo card (status: *Preview*); command `evaluate the Producer for placeholder or invented links`.

**Speaker notes:**
> [DEMO 3 — 3:00. See demo/RUNBOOK.md — preview status for the first showing]
> Prompt in Copilot: "evaluate the Producer for placeholder or invented links" → run-assert-eval asks for the risk source → we supply it → triage → config → run.
> Show: two headline numbers — impermissible vs permissible violations. Open one failing transcript with judge citation.
> Fix: tighten Producer instructions + require get_episode sources → re-run same eval → delta.
> Bridge: "Now it works, and it's measurably better. Last step: stop running it by hand."
> [20:00]

**Presenter guidance (first showing: Preview):**
- **Be upfront about the Preview label.** "We're making this system real for **Season 5 of Model Mondays, starting December–January**. Today I'll show you the guardrail half live and walk the eval half."
- **Live:** run `check.py` on `s3-e04`. It flags the **8 placeholder links** (plus a missing Sources section, 9 errors in total), the exact chocolates from slide 16.
- **Live:** the Publisher mock run with `--mock-fault placeholder`. The audience watches the agent get **⛔ BLOCKED** and resubmit. This is the "caught in the act" moment, live.
- **Bridge the gap between guardrails and evals** (the key idea): "A guardrail catches *this* one. ASSERT catches the ones a rule can't: a plausible but wrong link, an invented speaker, a claim the transcript doesn't support."
- **Optional proof points (about 30s, no model needed).** These show what ASSERT works *with*; they don't run ASSERT:
  - Open `evals/producer/ungrounded_links.yaml`: "Here's slide 16's risk in plain English. ASSERT generates the tests from this."
  - Run the eval target in mock mode (command in the RUNBOOK): "This is the function ASSERT calls. Here's the **evidence** its judge reads: every tool call, every source, every human flag."
- Then walk the four steps on the slide: risk → eval config → baseline → fix and re-run the *same* eval. Stress "**the delta is the evidence.**"
- Commands are in the Demo 03 section of the [RUNBOOK](../demo/RUNBOOK.md).
- **Clock check: 20:00.**

**Hand-off (bridge) →** "Now it works, and it's measurably better. Last step: stop running it by hand."

---

<br/>

## Act 4 · Make it scale: Automate the belt (20:00 → 25:00)

**The belt itself.** **Goal:** show that the line runs on triggers, with Act 3's inspectors as gates and humans still approving.

> **Narrative note:** Acts 1–3 each name one of Lucy's piles. Act 4 doesn't add a fourth; it goes after the **belt**, the cause of all three. Say so explicitly. It's what makes Act 4 feel like the resolution rather than another feature.

### 19 · Divider: Act 04, Automate the belt · 20:00 → 20:15

**On screen:** "Triggers instead of reminders. Gates instead of heroics." · *Design for the belt, not the burst.*

**Speaker notes:**
> [20:00 — ACT 4, 5 min]
> Last step: make it scale. Design for the belt, not the burst.

**Presenter guidance:**
- Suggested line: "Three piles: swallowed, in the hat, on the floor. Now we go after the **belt** itself."
- Callback to slide 6: "*Now* we automate, because now we can measure. Automating first would just pile chocolate up faster."
- "**Design for the belt, not the burst**": every week, not just launch week.

**Hand-off →** "Here's the line running on its own."

### 20 · The line runs itself: humans at the gates, agents on the line · 20:15 → 21:30

**On screen:** Trigger → Emcee on Foundry → Studio → Live site; CI eval gate / Continuous evals / Coding agent.

**Speaker notes:**
> Automate. Triggers: a weekly schedule, a GitHub issue that says "new episode announced", a stream that just ended.
> Emcee runs on Foundry as a hosted agent. It never publishes — drafts go to the studio and a human approves.
> And the Act 3 inspectors become gates: ASSERT in CI, Foundry continuous evals in production, and a coding agent that keeps the labs fresh.

**Presenter guidance:**
- Walk the flow left to right. Spend your time on the **peach Studio card**: "It never publishes. A human approves." That's *Agents propose, humans dispose* from slide 12, still true at scale.
- **The synthesis moment:** "And the Act 3 inspectors **become gates**." This is where all three steps meet on one slide: the crew (work), the evals (better), the triggers (scale).
- **Abstract promise #8 (coding agents): give it a full beat. Don't skim the third callout.** Suggested line: "And one more crew member: the **Copilot coding agent**. When an SDK changes, I file an issue and assign it to the agent. It updates the labs and samples and opens a PR. That's the **maintenance** that used to eat my weekends. And labs that always run are what keep learners **curious**: they try the next thing instead of getting stuck on a broken import."
- "**Triggers, not reminders. Gates, not heroics.**" Say it as a pair.

**Hand-off →** "Let's file one issue and watch the whole line run."

### 21 · DEMO 04: One issue, the whole line runs · 21:30 → 25:00

**On screen:** Demo card (status: *In progress*); command `gh issue create --title "S4-E12 announced" --label emcee`.

**Speaker notes:**
> [DEMO 4 — 3:30. In-progress for the first showing: walk the architecture + the local Emcee run instead]
> Kick off live, then switch to the run captured this morning ("bake-and-switch").
> Show: issue → routine → Emcee trace (handoffs) → studio queue fills → approve → page updates.
> Bridge: "So what does this mean for DevRel?"
> [25:00]

**Presenter guidance (first showing: In progress):**
- Run the local Emcee with `--mock --mock-delay 0.4` so the trace is readable. See the Demo 04 section of the [RUNBOOK](../demo/RUNBOOK.md).
- Narrate the **handoffs**: Emcee → Coordinator → Presenter → Publisher, each calling `submit_draft`. This is slide 12 in motion.
- **Switch to Studio** as three drafts appear (toasts). That's the "whole line runs" moment. Approve them and open `/episodes/s4-e12`.
- Then frame the full version honestly: "On Foundry, this same crew runs as a hosted agent, and a routine wakes it on a schedule or a GitHub issue. We're making that real for **Season 5 of Model Mondays, starting December–January**."
- Optional: open `agents/foundry/routine-weekly-prep.yaml`: "Here's the routine that will wake it every Tuesday."
- **Clock check: 25:00.** Don't let this demo eat the wrap.

**Hand-off (bridge) →** "So what does this mean for DevRel?"

---

<br/>

## Wrap: From handcrafted to repeatable (25:00 → 28:30)

**Goal:** zoom out from *my show* to *your job*, repeat the playbook with tools attached, and give them a first step.

### 22 · Rethink DevRel: from handcrafted to repeatable · 25:00 → 26:00

**On screen:** Handcrafted vs agent-powered table; "Build systems, not one-offs."

**Speaker notes:**
> [25:00 — WRAP, 3:30]
> Zoom out. The advocate's job changes: from making every artifact, to designing the factory.
> And learning changes: from instructor-led, to self-guided paths that keep working after the show.

**Presenter guidance:**
- **This is the thesis.** Change your posture and step toward the audience; it's about them now, not your show.
- Read just one row out loud: **Advocate role: "Makes every artifact" → "Designs the factory."** That's the whole talk in five words.
- **Abstract promise #9:** use the abstract's words: "from **handcrafted, instructor-led** content to **scalable, self-guided learning** built on **repeatable systems**."
- Callback to slide 4: "Fifty episodes, 38 hours. With the factory, every one of those becomes a learning asset that keeps working after the show ends."

**Hand-off →** "So here's the playbook one more time, this time with the tools attached."

### 23 · The DevRel playbook: Make it work → make it better → make it scale · 26:00 → 26:45

**On screen:** Slide 6's three cards again, now with tool chips.

**Speaker notes:**
> The playbook, one more time — now with tools attached.
> Make it work: skills, agents, MCP, Marp.
> Make it better: run-assert-eval and microsoft-foundry — observability and optimization.
> Make it scale: routines and gates.

**Presenter guidance:**
- It **mirrors slide 6** on purpose. Say so: "Same three steps from the start, now you've seen each one."
- Fast and rhythmic. Don't explain anything new.

**Hand-off →** "And you can build all of it yourself."

### 24 · Build your factory: the whole line is open · 26:45 → 27:30

**On screen:** Setup → Decompose → Delegate → Optimize → Automate; QR code to the repo.

**Speaker notes:**
> Everything you saw is in this repo: the data, the skills, the site, the crew, the evals, and a self-guided learning path. Start with the dev container. The fast path is about 90 minutes.

**Presenter guidance:**
- **Stop talking for three seconds** so people can scan the QR code. Phones go up here.
- This delivers on slide 1's "**the playbook you can steal**." Say it: "Here's the playbook. Steal it."
- Give one concrete first step: "Open it in a dev container and write your first station skill. It's about 90 minutes on the fast path."
- Point out that the steps match the acts: setup, then the four acts in order.
- **Invite them to follow along:** "Season 5 of Model Mondays starts December–January, and this line is what will run it. Star the repo and watch it go from preview to production."
- **Abstract promise #8, second half (engagement):** "The repo is also a learning path. Learners open it in a dev container with their *own* coding agent and ask it questions about the line. That's the **curiosity and deeper engagement**: they don't just watch the show, they run the factory."

**Hand-off →** (go straight to the closing line)

### 25 · Key takeaway · 27:30 → 28:30

**On screen:** "Stop chasing the conveyor belt — start running your own agent-powered chocolate factory." Thank you / Questions / in/nityan.

**Speaker notes:**
> Stop chasing the conveyor belt. Make it work, make it better, make it scale — and start running your own agent-powered chocolate factory.
> Thank you! [28:30 — 1:30 buffer for Q&A]

**Presenter guidance:**
- **Close the Lucy loop with the abstract's last line.** Suggested close: "Lucy never got to slow down the belt. You can build the factory. So stop chasing the conveyor belt, and start running your own agent-powered chocolate factory… **without having to stuff the extra content in your hat.**"
- Say the takeaway, then the three steps, then **stop**. Let "Thank you" sit before opening for questions.
- Leave this slide up during Q&A; it has your LinkedIn handle.

---

<br/>

## If you need to cut

In order of least damage to the story:

1. **Slide 5 (toolkit):** shrink to 30s; just name the two peach skills.
2. **Slide 13 (Marp + MCP):** say the meta line ("this deck is Marp too") and go straight to Demo 2.
3. **Demo 1 or Demo 2:** switch to the backup at 1:30 instead of 2:15.
4. **Slide 23 (playbook recap):** one sentence, then advance.

**Never cut:** slide 2 (sets up the spine), slide 6 (the map), slide 16 (the honest turn), the coding-agent beat on slide 20 (abstract promise #8), slide 22 (the thesis).
