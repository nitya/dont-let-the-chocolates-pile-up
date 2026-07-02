# 🎤 Speaker Notes — Don't Let the Chocolate Pile Up
### Tentative spoken script, act by act (25 min total)

*This is a first-pass narration draft — meant to find the voice and pacing, not to be memorized
word-for-word. Bracketed notes `[like this]` are stage directions, not spoken lines.*

---

## Act 1 — The Belt Speeds Up (3:00)

[Slide: Lucy and Ethel at the chocolate line, clip or still image]

"If you've ever seen the *I Love Lucy* chocolate factory episode, you know exactly what's coming.
Lucy and Ethel are on a candy line, wrapping chocolates as they roll by. It starts slow. They've
got this. Then the belt speeds up. And speeds up again. And within about ninety seconds, Lucy is
stuffing chocolates in her hat, her mouth, her blouse — anywhere they'll fit — just so it doesn't
look like she's falling behind.

[Beat — let the image land]

That's DevRel right now. Except the belt isn't chocolates — it's models. Microsoft Foundry ships
new models, new tools, new optimization techniques, on a weekly cadence. Every drop is a
chocolate. And for a long time, I was Lucy — one person, trying to wrap every single one by hand.

[Slide: thesis line]

Here's my thesis for the next 25 minutes: the fix isn't a faster Lucy. It's turning Lucy into a
fleet."

---

## Act 2 — The Funnel *Is* the Belt (4:00)

[Slide: three-stage funnel table]

"To show you what I mean, I need to walk you through three real programs I run on the Foundry
DevRel team — because this isn't hypothetical. These are three chocolate sizes on the same belt,
and together they form a funnel: awareness, engagement, adoption.

First — **Model Mondays**. It's a weekly livestream podcast. Every Monday, we cover News
Highlights — five or six things that shipped that week — plus one or two Spotlight deep-dives on
a model or an optimization technique. This is the *awareness* chocolate: small, frequent, always
on schedule, no matter what.

Second — **Model Releases**. When a new model drops, awareness alone doesn't help someone actually
*use* it. So we build a 'capsule' — a notebook plus a video walkthrough — that shows the model in
action, grounded in its model card and the Foundry docs. This is the *engagement* chocolate:
bursty, irregular, one per model drop.

Third — **Model Mastery**. Once someone's engaged, they need depth. This is a four-hour hands-on
workshop — an end-to-end optimization lab, plus a model-specific lab that shows what each model in
a lineup is actually good at. This is the *adoption* chocolate: long-form, layered, and it has to
stay correct for months.

[Show mermaid diagram]

Model drop, News Highlights, capsule, lab — one funnel, three chocolate sizes, same belt. And
here's the thing — these don't run in isolation. Mondays drives traffic to the capsule. The
capsule feeds the playbook the workshop runs on. It's one pipeline."

---

## Act 3 — Where the Chocolates Pile Up (3:00)

[Slide: pile-up table — hat / mouth / blouse / floor]

"So where does it actually break down? Four places, and I bet you'll recognize all of them.

**In the hat** — the hidden work. Nobody sees the PM grind behind Model Mondays: recruiting
speakers, confirming them, booking the studio, sending calendar holds, running tech checks,
assigning a host. None of that is 'content,' but all of it has to happen every single week or the
show doesn't ship.

**In the mouth** — silently swallowed. Models are dropping faster than I can build capsules for
them. Some just... don't get one. Nobody complains. It just quietly doesn't happen.

**In the blouse** — stuffed for later. 'I'll refresh that notebook next sprint.' We've all said
it. It rarely happens on its own.

**On the floor** — dropped outright. A model in a workshop lab gets deprecated, and the lab just
sits there, broken, until a learner hits it live and files a very awkward support ticket.

You cannot out-hustle this belt. I've tried. The only way out is to stop being the only Lucy on
the line."

---

## Act 4 — Meet L.U.C.Y (2:00)

[Slide: L.U.C.Y letters, one at a time]

"So here's what I actually built — not a metaphor, a real fleet of Copilot-powered agents, and
because I couldn't resist, I named it after her: **L.U.C.Y.**

**L** is for **Launch** — scaffolding new content from scratch: a capsule, a recap, a first draft.

**U** is for **Update** — going back and refreshing what's already out there as models and SDKs
change underneath it.

**C** is for **Coordinate** — the PM grind. Scheduling, speaker confirmations, tech checks, all the
'in the hat' work from a minute ago.

**Y** is for **Yield** — scaling one task into many, running it in parallel across an entire model
lineup instead of one at a time.

Same DevRel job. Same belt. New crew. Let me show you L.U.C.Y actually working — five demos, each
one a real production task from Mondays, Releases, or Mastery."

---

## Act 5 — L.U.C.Y at Work: Live Demos (9:00)

### Demo 1 — Skill → Model Mondays (Launch) — 1:30

"Every Monday needs a recap blog and next week's News Highlights list. Watch this."

[Run Demo 1 per STORYBOARD.md beats]

"Skill 1 turns this week's transcript into a recap post — summary, Q&A, the works. Skill 2 chains
right off it and drafts next week's News Highlights before I've opened a single tab. One
chocolate, wrapped, every week, on cadence.

But Mondays isn't just content — it's also where Lucy really drowns in PM work. Let's fix that
next."

### Demo 2 — Workflow → Model Mondays (Coordinate) — 2:00

[Run Demo 2 per STORYBOARD.md beats]

"This runs every Sunday night. Nobody logs in. It checks: is the speaker confirmed? If not, send a
reminder. Is the calendar hold in place? Is the tech check booked? Is a host assigned? By Monday
morning, the rundown issue is already sitting there, done.

Coordinate doesn't just file paperwork — it clears Lucy's hat before the belt even starts moving.

Mondays is handled. But a new model just dropped, and Mondays only gives it a headline. Someone
still has to build the capsule."

### Demo 3 — Coding agent → Model Releases (Launch) — 2:00

[Run Demo 3 per STORYBOARD.md beats]

"Model X shipped four hours ago. I assign an issue: build a capsule. Copilot reads the model
card, reads the Foundry docs, and scaffolds a notebook — not 'use one giant model for everything,'
but a hill-climbing narrative: here's where this model is the right tool for the job, and here's
how it fits into a multi-model solution. Plus a video script. PR's up. I review, tweak the framing
once, approve.

Human in the loop — I taste-test, L.U.C.Y re-wraps. Not a single chocolate stuffed in a cheek.

One capsule, one model. But this provider just released six models at once."

### Demo 4 — Fleet → Model Releases (Yield) — 2:00

[Run Demo 4 per STORYBOARD.md beats]

"One prompt, six models, six parallel sessions — six capsules being built at once. Five finish
clean. One flags a missing tool binding and asks for help instead of quietly failing.

Yield is the moment the belt stops beating you. The chocolates got faster. L.U.C.Y grew arms.

Awareness — done. Engagement — done, at scale. But workshops are where the real damage happens
when nobody's watching."

### Demo 5 — Agentic DevOps → Model Mastery (Update) — 1:30

[Run Demo 5 per STORYBOARD.md beats]

"Overnight, a model behind one of our workshop labs got deprecated. I wasn't awake for it. CI
failed, and that failure alone triggered a session — no one paged it. It reads the Optimization
Playbook, finds the right replacement model, opens a PR: swap the reference, update the
instructions, refresh the benchmark numbers. Learners see the corrected lab before the next
cohort even starts.

Launch, Coordinate, Yield, Update — and the loop closes right back into the next model drop. And
for once, Lucy clocks out without a single chocolate in her mouth."

---

## Act 6 — The Wrap-Up (2:00)

[Slide: three shows + L.U.C.Y letters, belt diagram]

"Model Mondays. Model Releases. Model Mastery. One funnel, three chocolate sizes, one fleet
wrapping them all.

Three things I want you to leave with:

One — **name your chocolates.** You can't automate a pile you haven't inventoried. Map your own
funnel: what's your awareness content, your engagement content, your adoption content?

Two — **design for the belt, not the burst.** A weekly cadence backed by agentic workflows beats a
heroic sprint every time. Heroics don't scale. Systems do.

Three — **delegate to the fleet, curate as human.** L.U.C.Y wraps. You taste-test. Your judgment is
the part that doesn't get automated — and it's the part that matters most.

[Final slide]

It's time to stop chasing the conveyor belt, and start running your own agent-powered chocolate
factory. L.U.C.Y has your hat covered.

Thank you."

---

## Delivery notes

- **Pacing:** Acts 1-4 are narration-heavy — practice them out loud for time; it's easy to run long
  on Act 2/3 since there's a lot of real detail to convey.
- **Energy shift:** Act 5 should feel like a gear change — faster cuts, less talking over the
  screen, let the tool do the talking during each demo beat.
- **Buffer:** 2 min of slack is built into the 25-min budget (see OUTLINE.md timing table) — use it
  to breathe during Act 2/3 or extend Q&A, not to pad the demos.
- **Fallback:** if a live demo stalls, jump straight to the backup recording and pick the narration
  back up at the "handoff line" — don't apologize on stage, just cut.
