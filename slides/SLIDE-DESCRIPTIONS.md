# Slide descriptions (PowerPoint fallback)

Use this to rebuild or edit any slide in PowerPoint on the storyboard template. The Marp source is [deck.md](deck.md); speaker notes are there too.

**Global style**
- **Canvas:** 16:9, 1920×1080.
- **Backgrounds:** cream `#FBF3EA`. Dark slides use plum `#26162F`.
- **Accents:**
  - crimson `#D7263D` for kickers, badges and buttons;
  - amber `#F6B132` for kickers on dark slides and highlights;
  - peach `#FDEBCD` for callouts;
  - white cards with a beige `#EFE3D3` border and 20 px radius.
- **Fonts:**
  - titles: Trebuchet MS Bold, 64–66 pt;
  - body: Calibri, 28–32 pt;
  - kicker: Calibri Bold, 24 pt, ALL CAPS, wide tracking, crimson.
- **Icons:** white line icons (Lucide) inside 120 px crimson or plum circles.

| # | Kicker | Title | Layout & content | Storyboard ref |
|---|---|---|---|---|
| 1 | DEVREL · THE AGENT-POWERED CONTENT FACTORY | Don't Let the Chocolate Pile Up: Scaling DevRel Content with AI Agents | Plum background. Left: kicker, title, subtitle "Turning a one-person DevRel team into a coordinated production line of agents and skills", byline "Nitya Narasimhan \| Senior Cloud Advocate". Right: factory illustration with a crimson offset block behind it. | 1 |
| 2 | WHY CHOCOLATE? | Lucy on the line: the belt speeds up, the chocolate piles up | Left: Lucy/Ethel still, with the credit "I Love Lucy, 'Job Switching' (1952) · Image credit: Tenor". Right: plum card "The scene" with two paragraphs (the scene, then the DevRel parallel in bold). | 2 |
| 3 | THE BELT IS SPEEDING UP | Developers moved to AI fast — and expect more, faster | Three white stat cards: **84%** (crimson) use or plan to use AI tools; **51%** (crimson) of pros use AI daily; **46%** (plum) don't trust AI accuracy. Peach callout: "The DevRel opportunity: developers want AI help — and trusted, human-verified content behind it." Source line: Stack Overflow 2025 Developer Survey. | 3 |
| 4 | THE LUCY MOMENT | One advocate, one weekly show, and the belt keeps speeding up | Left: four badge rows (Coordinate · Create · Present · Distribute) with a one-line description each. Right: plum card "Model Mondays, by the numbers": **50** episodes · 4 seasons, **38 h** of livestreams, **60K+** views, **30+** guests (amber numbers), then the bold line "What if… a virtual team stepped in to balance the load?" | 4 |
| 5 | THE TOOLKIT | An open toolkit: files, protocols and repos | 3×2 card grid. Top row (white): Agents + Agent Skills, MCP, Marp. Bottom row (peach): Microsoft Agent Framework, `run-assert-eval` (ASSERT, MIT), `microsoft-foundry` (skill, MIT). One sentence each. | new |
| 6 | THE PLAYBOOK | Make it work. Make it better. Make it scale. | Three cards with colored header bands: crimson "Make it work" (Acts 1–2, lightbulb icon), plum "Make it better" (Act 3, gauge icon), crimson "Make it scale" (Act 4, trend icon). Each has a bold one-liner plus three bullets. Footnote: "In that order. Automating something that doesn't work just piles up chocolate faster." | 11 (restyled) |
| 7 | ACT 1 · MAKE IT WORK | Decompose the line | Plum divider. Faint large "01" top right, layers icon badge, lede "Break one show into stations. Give each station a skill.", amber line "Pile-up: swallowed — the recap that never gets written." | 13 |
| 8 | THE PRODUCTION LINE | A real system: the weekly livestream content factory | Five numbered cards: 01 Coordinate · 02 Capture · 03 Transform · 04 Present · 05 Distribute, with alternating crimson and plum badges. Footnote: "Every station has a human checkpoint: agents do the heavy lifting, you own the voice." | 6 |
| 9 | SKILLS AS STATIONS | A skill is a station in a folder | Left: plum code block showing `.github/skills/mm-recap/SKILL.md` front matter and four steps. Right: four numbered pill rows: Ground · Summarize · Polish · Review & ship. | 7 |
| 10 | DEMO 01 · MAKE IT WORK | Livestream in, recap out | Demo layout. Left white card "What you'll see" with four numbered steps. Right plum video panel: play button, "Live demo", command chip `recap S4-E09 using the mm-recap skill`. | 14 |
| 11 | ACT 2 · MAKE IT WORK | Delegate to a crew | Plum divider, "02", users icon. Lede "Skills are stations. Agents are the crew that runs them — grounded by MCP." Pile-up: "in the hat". | 13 |
| 12 | FROM WORKER TO FACTORY | Meet Emcee: the M.C. that runs the show | Four specialist cards (Coordinator, Producer, Presenter, Publisher). Below: plum callout "Emcee — master of ceremonies and M.C. = Model Catalog" and peach callout "Grounded by MCP… No approve tool — humans approve." | 5 (reworked) |
| 13 | SLIDES ON THE LINE | Streamlined slide creation with Marp + MCP | Three cards: "Marp builds" (3 bullets), "MCP grounds" (3 bullets), peach "Why it matters" ending "This deck is Marp too." | 8 |
| 14 | DEMO 02 · MAKE IT WORK | A crew member builds next week's deck | Demo layout. Command chip: `build the deck for S4-E11 with the mm-deck skill`. | 15 |
| 15 | ACT 3 · MAKE IT BETTER | Inspect before you ship | Plum divider, "03", search-check icon. Pile-up: "on the floor — mistakes nobody catches until a learner does." | 13 |
| 16 | CAUGHT IN THE ACT | Our own line already dropped chocolates | Left: two peach stat cards, **83** placeholder "News Highlight" links and **11** episode pages affected. Right: four badge rows: Looks fine in review (shows the markdown link) · Agents copy patterns · Developers notice (87% / 81%) · So: measure, don't eyeball. | 9 (reworked) |
| 17 | TWO INSPECTORS ON THE LINE | Observability + optimization, as skills | Two white cards. `run-assert-eval`: Spec → tests · Run + judge with traces · Fix · Re-measure, with chips local-first / any model / any framework / CI gate. `microsoft-foundry`: Evaluate · Analyze · Optimize · Monitor, with chips hosted agents / evals / optimizer / routines. | new |
| 18 | DEMO 03 · MAKE IT BETTER | Measure the Producer, fix it, prove it | Demo layout plus an amber "PREVIEW" pill top right. Command chip: `evaluate the Producer for placeholder or invented links`. | 16 |
| 19 | ACT 4 · MAKE IT SCALE | Automate the belt | Plum divider, "04", repeat icon. Lede "Triggers instead of reminders. Gates instead of heroics." Amber line "Design for the belt, not the burst." | 13 |
| 20 | THE LINE RUNS ITSELF | Humans at the gates, agents on the line | A row of four cards joined by crimson arrows: Trigger → Emcee on Foundry (plum card) → Studio (peach) → Live site. Below: three peach callouts: CI eval gate · Continuous evals · Coding agent. | new |
| 21 | DEMO 04 · MAKE IT SCALE | One issue, the whole line runs | Demo layout plus an "IN PROGRESS" pill. Command chip: `gh issue create --title "S4-E12 announced" --label emcee`. | — |
| 22 | RETHINK DEVREL | From handcrafted to repeatable: DevRel in the age of AI | Left: 4-row table (Content, Learning, Scale, Advocate role) with Handcrafted and Agent-powered columns and a plum header. Right: crimson card with a trend icon and "Build systems, not one-offs…" | 10 |
| 23 | THE DEVREL PLAYBOOK | Make it work → make it better → make it scale | Same three header-band cards as slide 6, now with tool chips: Agent Skills / MCP / Marp · run-assert-eval / microsoft-foundry (amber chips) · Foundry routines / CI gates. | 11 |
| 24 | BUILD YOUR FACTORY | Try it yourself: the whole line is open | Left: five numbered pills (0 Setup … 4 Automate). Right: plum card with a QR code to `github.com/nitya/dont-let-the-chocolates-pile-up` and "Slides · labs · skills · data". | new |
| 25 | KEY TAKEAWAY | Stop chasing the conveyor belt — start running your own agent-powered chocolate factory. | Plum background. Three crimson badge rows: Make it work · Make it better · Make it scale. Amber footer: "Thank you \| Questions? \| Connect with me: in/nityan". | 12 |

**Timing:** intro slides 1–6 (5:00) · Act 1 slides 7–10 (5:00) · Act 2 slides 11–14 (5:00) · Act 3 slides 15–18 (5:00) · Act 4 slides 19–21 (5:00) · wrap slides 22–25 (3:30) · buffer 1:30.
