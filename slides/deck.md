---
marp: true
theme: chocolate
size: 16:9
paginate: false
title: "Don't Let the Chocolate Pile Up: Scaling DevRel Content with AI Agents"
author: Nitya Narasimhan
description: All Things Open 2026 — a DevRel playbook to make it work, make it better, make it scale.
---

<!-- _class: title -->

<div class="text">

###### DevRel · The agent-powered content factory

# Don’t Let the Chocolate Pile Up: Scaling DevRel Content with AI Agents

<p class="subtitle">Turning a one-person DevRel team into a coordinated production line of agents and skills</p>

<p class="byline">Nitya Narasimhan &nbsp;|&nbsp; Senior Cloud Advocate</p>

</div>
<div class="hero"><img src="assets/hero-factory.webp" alt="Robots and a developer advocate packing chocolates, microphones and slides on a factory line"></div>

<!--
[0:00 — INTRO, 5 min total]
Hi everyone. I'm Nitya. I run a weekly livestream, an AMA series, a blog, slides, samples — and for a long time, I ran it mostly by myself.
Today: how I turned that into a production line of agents and skills — and the playbook you can steal.
-->

---

###### Why chocolate?

# Lucy on the line: the belt speeds up, the chocolate piles up

<div class="grid split">
<div style="display:flex;flex-direction:column;gap:14px">
<img src="assets/lucy-line.webp" alt="Lucy and Ethel at the chocolate conveyor belt" style="border-radius:6px;width:100%">
<p class="small muted"><em>I Love Lucy</em>, “Job Switching” (1952) · Image credit: Tenor</p>
</div>
<div class="card dark">
<h3>The scene</h3>
<p>Lucy and Ethel wrap chocolates on a conveyor belt. When it speeds up, they eat them, hide them, and stuff them in their hats.</p>
<p class="mt"><strong>DevRel today: the belt is content demand.</strong> This talk is about bringing in a crew of AI agents so nothing gets stuffed in your hat.</p>
</div>
</div>

<!--
Who's seen this? Lucy and Ethel, the chocolate factory. The belt speeds up. They eat chocolates, hide them in their hats, stuff them in their blouses — anything to look like they're keeping up.
That is DevRel right now. Every week: new models, new SDKs, new tools. Every one is a chocolate on the belt.
-->

---

###### The belt is speeding up

# Developers moved to AI fast — and expect more, faster

<div class="grid cols-3 fit" style="height:500px">
<div class="card"><div class="stat">84%</div><p>of developers use or plan to use AI tools in their workflow (up from 76% in 2024)</p></div>
<div class="card"><div class="stat">51%</div><p>of professional developers use AI tools every day</p></div>
<div class="card"><div class="stat plum">46%</div><p>don't trust the accuracy of AI output (up from 31% in 2024)</p></div>
</div>

<div class="callout"><strong>The DevRel opportunity:</strong> developers want AI help — and trusted, human-verified content behind it.</div>

<p class="source">Source: Stack Overflow <a href="https://survey.stackoverflow.co/2025/">2025 Developer Survey</a> (49,000+ responses)</p>

<!--
Developers moved fast: 84% use or plan to use AI tools; half of pros use them daily.
But trust is going DOWN: 46% don't trust the accuracy. That's the gap DevRel fills: fast AND trustworthy.
Hold on to that word — trust. It comes back in Act 3.
-->

---

###### The Lucy moment

# One advocate, one weekly show, and the belt keeps speeding up

<div class="grid split">
<div class="rows">
<div class="row"><span class="badge"><img src="assets/icons/calendar-check.svg"></span><div><h4>Coordinate</h4><p>Guests, briefs, run-of-show and reminders — every week</p></div></div>
<div class="row"><span class="badge"><img src="assets/icons/video.svg"></span><div><h4>Create</h4><p>Livestream, AMA, recap, highlights, blog</p></div></div>
<div class="row"><span class="badge"><img src="assets/icons/presentation.svg"></span><div><h4>Present</h4><p>Slides and samples that drift out of date</p></div></div>
<div class="row"><span class="badge"><img src="assets/icons/share-2.svg"></span><div><h4>Distribute</h4><p>Site, social, newsletter, community</p></div></div>
</div>
<div class="card dark">
<h3>Model Mondays, by the numbers</h3>
<div class="grid cols-2 fit" style="gap:28px 36px;margin:10px 0 18px">
<div><div class="stat sm" style="color:var(--amber)">50</div><p>episodes · 4 seasons</p></div>
<div><div class="stat sm" style="color:var(--amber)">38 h</div><p>of livestreams</p></div>
<div><div class="stat sm" style="color:var(--amber)">60K+</div><p>YouTube views</p></div>
<div><div class="stat sm" style="color:var(--amber)">30+</div><p>guest speakers</p></div>
</div>
<p><strong>What if, instead of falling behind, a virtual team stepped in to balance the load?</strong></p>
</div>
</div>

<p class="source">Data: <code>data/</code> snapshot of microsoft/model-mondays + the Model Mondays YouTube playlist</p>

<!--
This is my belt: Model Mondays. A weekly livestream about AI models on Microsoft Foundry.
50 episodes, 4 seasons, 38 hours live, 60K views, 30+ guests. Real data — it's in the repo, refreshed by a skill.
Every episode has the same four kinds of work. None of it is hard. All of it is relentless.
-->

---

<!-- _class: dense -->

###### The toolkit

# An open toolkit: files, protocols and repos

<div class="grid cols-3">
<div class="card"><span class="badge sm"><img src="assets/icons/bot.svg"></span><h4>Agents + Agent Skills</h4><p>GitHub Copilot agent mode. Skills are folders with a <code>SKILL.md</code> — portable across Copilot, Claude Code, Cursor &amp; more.</p></div>
<div class="card"><span class="badge sm plum"><img src="assets/icons/network.svg"></span><h4>MCP</h4><p>Open protocol to ground agents in live data: our show's own MCP server + Microsoft Learn MCP.</p></div>
<div class="card"><span class="badge sm"><img src="assets/icons/presentation.svg"></span><h4>Marp</h4><p>Slides as Markdown. Versioned, diffable, themeable — and writable by agents. (This deck!)</p></div>
<div class="card peach"><span class="badge sm plum"><img src="assets/icons/workflow.svg"></span><h4>Microsoft Agent Framework</h4><p>Open-source orchestration for multi-agent workflows — runs locally or hosted on Foundry.</p></div>
<div class="card peach"><span class="badge sm"><img src="assets/icons/search-check.svg"></span><h4><code>run-assert-eval</code></h4><p>ASSERT (MIT): turn a spec into tests, judge with traces, fix, re-measure.</p></div>
<div class="card peach"><span class="badge sm plum"><img src="assets/icons/gauge.svg"></span><h4><code>microsoft-foundry</code></h4><p>Skill (MIT) to build, deploy, evaluate, optimize and schedule agents on Foundry.</p></div>
</div>

<!--
Before the playbook, the toolbox. This is an open-source crowd, so: everything here is a file, a protocol, or a repo.
Top row — the line itself: agents + skills, MCP, Marp.
Bottom row (peach) — the two skills I want you to remember: run-assert-eval from ASSERT, and microsoft-foundry. They're both about the same thing: observability and optimization. We'll meet them in Act 3.
-->

---

###### The playbook

# Make it work. Make it better. Make it scale.

<div class="grid cols-3">
<div class="card band"><div class="head"><div><span class="label">Acts 1–2</span><h3>Make it work</h3></div><img src="assets/icons/lightbulb.svg"></div>
<div class="body"><p><strong>Decompose &amp; delegate.</strong></p><ul class="tight"><li>Break the line into stations</li><li>A skill per station</li><li>A crew of agents to run them</li></ul></div></div>
<div class="card band"><div class="head plum"><div><span class="label">Act 3</span><h3>Make it better</h3></div><img src="assets/icons/gauge.svg"></div>
<div class="body"><p><strong>Optimize.</strong></p><ul class="tight"><li>Measure against your spec</li><li>Find failures with evidence</li><li>Fix and re-measure</li></ul></div></div>
<div class="card band"><div class="head"><div><span class="label">Act 4</span><h3>Make it scale</h3></div><img src="assets/icons/trending-up.svg"></div>
<div class="body"><p><strong>Automate.</strong></p><ul class="tight"><li>Triggers, not reminders</li><li>Gates, not heroics</li><li>Humans approve, agents wrap</li></ul></div></div>
</div>

<p class="footnote">In that order. Automating something that doesn't work just piles up chocolate faster.</p>

<!--
Here's the whole talk on one slide. Three steps, four acts, five minutes each.
Make it work: decompose and delegate. Make it better: optimize. Make it scale: automate.
The order matters. If you automate before you measure, you just pile chocolate up faster.
[5:00]
-->

---

<!-- _class: divider -->

<div class="act">01</div>
<span class="badge"><img src="assets/icons/layers.svg"></span>

###### Act 1 · Make it work

# Decompose the line

<p class="lede">Break one show into stations. Give each station a skill.</p>
<p class="pile">Pile-up: <strong>swallowed</strong> — the recap that never gets written.</p>

<!--
[5:00 — ACT 1, 5 min]
First chocolate: the recap. Every livestream should get a recap, highlights, a summary. Most weeks it just... doesn't happen. Silently swallowed.
-->

---

###### The production line

# A real system: the weekly livestream content factory

<div class="grid cols-5">
<div class="card center"><span class="badge"><img src="assets/icons/calendar-check.svg"></span><span class="num">01</span><h4>Coordinate</h4><p>Book guests, prep briefs, run-of-show, reminders</p></div>
<div class="card center"><span class="badge plum"><img src="assets/icons/video.svg"></span><span class="num">02</span><h4>Capture</h4><p>Stream the show; transcript + chapters land</p></div>
<div class="card center"><span class="badge"><img src="assets/icons/sparkles.svg"></span><span class="num">03</span><h4>Transform</h4><p>Recaps, highlights, summaries</p></div>
<div class="card center"><span class="badge plum"><img src="assets/icons/presentation.svg"></span><span class="num">04</span><h4>Present</h4><p>Slides with Marp, grounded by MCP</p></div>
<div class="card center"><span class="badge"><img src="assets/icons/share-2.svg"></span><span class="num">05</span><h4>Distribute</h4><p>Site, social, newsletter, community</p></div>
</div>

<p class="footnote mt">Every station has a human checkpoint: agents do the heavy lifting, you own the voice.</p>

<!--
Decompose. Five stations for one show: Coordinate, Capture, Transform, Present, Distribute.
The trick is to make each one small and repeatable — something you'd hand a new teammate on day one with a checklist.
That checklist is a skill.
-->

---

###### Skills as stations

# A skill is a station in a folder

<div class="grid split">
<div>

```markdown
.github/skills/mm-recap/SKILL.md
---
name: mm-recap
description: Turn a Model Mondays livestream
  into a recap + News Highlights. Use when
  asked to recap an episode (e.g. "recap S4-E09").
---
1. Resolve the episode in data/episodes.json
2. Read transcript → else YouTube chapters
3. Draft recap in our voice; cite every claim
4. Never invent links. Save → review queue
```

</div>
<div class="steps">
<div class="step"><span class="badge xs num-badge" style="font-size:28px">1</span><b>Ground</b><span>Episode, transcript, chapters</span></div>
<div class="step"><span class="badge xs num-badge" style="font-size:28px">2</span><b>Summarize</b><span>Questions, answers, takeaways</span></div>
<div class="step"><span class="badge xs plum num-badge" style="font-size:28px">3</span><b>Polish</b><span>Your voice, real links only</span></div>
<div class="step"><span class="badge xs num-badge" style="font-size:28px">4</span><b>Review &amp; ship</b><span>A human approves</span></div>
</div>
</div>

<!--
A skill is just a folder with a SKILL.md: a name, a description that tells the agent WHEN to use it, and the steps.
Specialized, testable, swappable — and reused every single week.
Notice step 4 and the "never invent links" rule. Remember that for Act 3.
-->

---

<!-- _class: demo -->

###### DEMO 01 · Make it work

# Livestream in, recap out

<div class="grid">
<div class="card">
<h3>What you'll see</h3>
<ol>
<li>Ask Copilot to recap last week's episode</li>
<li>The <code>mm-recap</code> skill grounds itself in the show's data</li>
<li>Recap + News Highlights, with sources</li>
<li>Review the draft before it ships</li>
</ol>
</div>
<div class="video"><div class="play"><span></span></div>Live demo<div class="cmd">recap S4-E09 using the mm-recap skill</div></div>
</div>

<!--
[DEMO 1 — 3:00. See demo/RUNBOOK.md]
Open VS Code → Copilot Chat (agent mode). Type: "recap S4-E09 using the mm-recap skill".
Point out: it found the skill from its description; it reads data/episodes.json; it uses transcript if present, otherwise YouTube chapters.
Show output: demo/outputs/s4-e09/recap.md. Highlight the Sources section.
Fallback: open demo/backups/s4-e09/recap.md — "I ran this an hour ago so we're not waiting on the model."
Bridge: "Skills handle the content. But the show also runs on hidden ops work — and that's where Lucy really drowns."
[10:00]
-->

---

<!-- _class: divider -->

<div class="act">02</div>
<span class="badge"><img src="assets/icons/users.svg"></span>

###### Act 2 · Make it work

# Delegate to a crew

<p class="lede">Skills are stations. Agents are the crew that runs them — grounded by MCP.</p>
<p class="pile">Pile-up: <strong>in the hat</strong> — briefs, reminders, run-of-show, slides.</p>

<!--
[10:00 — ACT 2, 5 min]
Second chocolate pile: in the hat. The hidden work nobody sees — the brief, the reminders, the run-of-show, the slides.
-->

---

###### From worker to factory

# Meet Emcee: the M.C. that runs the show

<div class="grid cols-4 fit" style="margin-bottom:34px">
<div class="card"><span class="badge sm"><img src="assets/icons/calendar-check.svg"></span><h4>Coordinator</h4><p>Guest brief, run-of-show, reminder drafts</p></div>
<div class="card"><span class="badge sm plum"><img src="assets/icons/sparkles.svg"></span><h4>Producer</h4><p>Recap, highlights, summary (uses <code>mm-recap</code>)</p></div>
<div class="card"><span class="badge sm"><img src="assets/icons/presentation.svg"></span><h4>Presenter</h4><p>Marp deck, grounded in docs (uses <code>mm-deck</code>)</p></div>
<div class="card"><span class="badge sm plum"><img src="assets/icons/megaphone.svg"></span><h4>Publisher</h4><p>Drafts to the site, social posts, newsletter</p></div>
</div>

<div class="grid cols-2 fit">
<div class="callout dark" style="margin:0"><strong>Emcee</strong> — master of ceremonies <em>and</em> <strong>M.C. = Model Catalog</strong>. Plans the run, hands off to specialists, escalates when unsure.</div>
<div class="callout" style="margin:0"><strong>Grounded by MCP:</strong> the show's own server (episodes, transcripts, drafts) + Microsoft Learn. <strong>No approve tool</strong> — humans approve.</div>
</div>

<!--
Delegate. One orchestrator — I call it Emcee: master of ceremonies, and M.C. for Model Catalog — and four specialists.
Coordinator clears the hat. Producer owns content. Presenter builds slides. Publisher handles distribution.
Each specialist reuses the skills from Act 1. And every one is grounded through MCP.
Key design choice: the MCP server has submit_draft but NO approve tool. Agents propose. Humans dispose.
-->

---

###### Slides on the line

# Streamlined slide creation with Marp + MCP

<div class="grid cols-3">
<div class="card"><span class="badge sm"><img src="assets/icons/presentation.svg"></span><h3>Marp builds</h3><ul><li>Slides written as Markdown in a repo</li><li>Versioned, diffable, reusable themes</li><li>Agents draft decks as plain text</li></ul></div>
<div class="card"><span class="badge sm plum"><img src="assets/icons/network.svg"></span><h3>MCP grounds</h3><ul><li>Episode facts from the show's MCP server</li><li>Current product docs via Learn MCP</li><li>Same trusted sources, every episode</li></ul></div>
<div class="card peach"><h3 class="crimson">Why it matters</h3><p>Slides become code: an agent drafts the deck from grounded sources and you refine the story — no more starting from a blank page.</p><p class="mt"><strong>This deck is Marp too.</strong></p></div>
</div>

<!--
Presenter is my favorite. Slides are Markdown — so agents can write them, git can diff them, and a theme makes them look like this.
MCP grounds them: episode facts from our own server, product facts from Microsoft Learn.
-->

---

<!-- _class: demo -->

###### DEMO 02 · Make it work

# A crew member builds next week's deck

<div class="grid">
<div class="card">
<h3>What you'll see</h3>
<ol>
<li>The Presenter skill drafts a Marp deck for the next episode</li>
<li>Grounded in the show's MCP server + Microsoft Learn</li>
<li>Rendered with this deck's theme</li>
<li>Submitted to the studio — I approve, the site updates</li>
</ol>
</div>
<div class="video"><div class="play"><span></span></div>Live demo<div class="cmd">build the deck for S4-E11 with the mm-deck skill</div></div>
</div>

<!--
[DEMO 2 — 3:00. See demo/RUNBOOK.md]
Prompt: "build the deck for S4-E11 with the mm-deck skill".
Show: MCP tool calls (get_episode, search_episodes, Learn docs) → slides/episodes/s4-e11.md → marp render → preview.
If the site is running: submit_draft → open /studio → Approve → episode page shows the deck.
Fallback: demo/backups/s4-e11/deck.html.
Bridge: "That's two acts of 'make it work'. But how do I know it's any GOOD?"
[15:00]
-->

---

<!-- _class: divider -->

<div class="act">03</div>
<span class="badge"><img src="assets/icons/search-check.svg"></span>

###### Act 3 · Make it better

# Inspect before you ship

<p class="lede">Speed without inspection just moves the pile. Measure against your spec, fix, re-measure.</p>
<p class="pile">Pile-up: <strong>on the floor</strong> — mistakes nobody catches until a learner does.</p>

<!--
[15:00 — ACT 3, 5 min]
Third pile: on the floor. The chocolates you drop and don't notice. Until a learner does.
-->

---

###### Caught in the act

# Our own line already dropped chocolates

<div class="grid split-r">
<div style="display:flex;flex-direction:column;gap:32px">
<div class="card peach"><div class="stat">83</div><p>“News Highlight” links that point at the series homepage instead of the news</p></div>
<div class="card peach"><div class="stat plum md">11</div><p>episode pages affected (S3-E04 → S3-E15)</p></div>
</div>
<div class="rows">
<div class="row"><span class="badge plum sm"><img src="assets/icons/link-2-off.svg"></span><div><h4>Looks fine in review</h4><p><code>[Microsoft Agent Framework](https://aka.ms/model-mondays)</code></p></div></div>
<div class="row"><span class="badge sm"><img src="assets/icons/triangle-alert.svg"></span><div><h4>Agents copy patterns</h4><p>Including the bad ones — at the speed of the belt</p></div></div>
<div class="row"><span class="badge plum sm"><img src="assets/icons/shield-check.svg"></span><div><h4>Developers notice</h4><p>87% are concerned about agent accuracy; 81% about security &amp; privacy</p></div></div>
<div class="row"><span class="badge sm"><img src="assets/icons/gauge.svg"></span><div><h4>So: measure, don't eyeball</h4><p>Turn “never invent links” into a test you can run every week</p></div></div>
</div>
</div>

<p class="source">Found while importing the public Model Mondays repo for this talk · Stack Overflow 2025 Developer Survey</p>

<!--
True story. While building this talk I imported our own public repo — and found 83 "News Highlights" links across 11 episodes that all point to... the series homepage.
They look fine in review. They're useless to a learner. And an agent trained on these pages would happily copy the pattern.
Developers already worry about this: 87% concerned about agent accuracy.
So we stop eyeballing and start measuring.
-->

---

###### Two inspectors on the line

# Observability + optimization, as skills

<div class="grid cols-2">
<div class="card">
<div class="row" style="gap:24px"><span class="badge sm"><img src="assets/icons/search-check.svg"></span><div><h3><code>run-assert-eval</code></h3><p class="small muted">ASSERT · responsibleai/assert · MIT</p></div></div>
<ul>
<li><strong>Spec → tests:</strong> describe the risk in plain language</li>
<li><strong>Run + judge</strong> with trace evidence (OpenTelemetry)</li>
<li><strong>Fix:</strong> generate a policy from real failures</li>
<li><strong>Re-measure:</strong> the delta is the evidence</li>
</ul>
<div class="chips mt-auto"><span class="chip">local-first</span><span class="chip">any model</span><span class="chip">any framework</span><span class="chip">CI gate</span></div>
</div>
<div class="card">
<div class="row" style="gap:24px"><span class="badge sm plum"><img src="assets/icons/gauge.svg"></span><div><h3><code>microsoft-foundry</code></h3><p class="small muted">microsoft/azure-skills · MIT</p></div></div>
<ul>
<li><strong>Evaluate:</strong> batch evals on a deployed agent</li>
<li><strong>Analyze:</strong> cluster failures, trace to responses</li>
<li><strong>Optimize:</strong> prompt + instruction tuning, compare versions</li>
<li><strong>Monitor:</strong> continuous evals in production</li>
</ul>
<div class="chips mt-auto"><span class="chip">hosted agents</span><span class="chip">evals</span><span class="chip">optimizer</span><span class="chip">routines</span></div>
</div>
</div>

<!--
Two skills — same idea, different scope.
run-assert-eval: local-first. You describe a risk in plain English — "highlights must never use placeholder links" — and it generates tests, runs them, judges with trace evidence, proposes a fix, and re-measures. Works with any model, any framework.
microsoft-foundry: when the crew is deployed. Batch evals, failure clustering, prompt optimization, version comparison, continuous monitoring.
Both are skills — so your coding agent drives them for you.
-->

---

<!-- _class: demo -->

<div class="status">Preview</div>

###### DEMO 03 · Make it better

# Measure the Producer, fix it, prove it

<div class="grid">
<div class="card">
<h3>What you'll see</h3>
<ol>
<li>Describe the risk: “highlights must cite a specific source — never a placeholder”</li>
<li><code>run-assert-eval</code> writes one atomic eval config</li>
<li>Baseline run: violation rate + cited transcripts</li>
<li>Fix → re-run the <em>same</em> eval → compare</li>
</ol>
</div>
<div class="video"><div class="play"><span></span></div>Eval walkthrough<div class="cmd">evaluate the Producer for placeholder or invented links</div></div>
</div>

<!--
[DEMO 3 — 3:00. See demo/RUNBOOK.md — preview status for the first showing]
Prompt in Copilot: "evaluate the Producer for placeholder or invented links" → run-assert-eval asks for the risk source → we supply it → triage → config → run.
Show: two headline numbers — impermissible vs permissible violations. Open one failing transcript with judge citation.
Fix: tighten Producer instructions + require get_episode sources → re-run same eval → delta.
Bridge: "Now it works, and it's measurably better. Last step: stop running it by hand."
[20:00]
-->

---

<!-- _class: divider -->

<div class="act">04</div>
<span class="badge"><img src="assets/icons/repeat-2.svg"></span>

###### Act 4 · Make it scale

# Automate the belt

<p class="lede">Triggers instead of reminders. Gates instead of heroics.</p>
<p class="pile">Design for the belt, not the burst.</p>

<!--
[20:00 — ACT 4, 5 min]
Last step: make it scale. Design for the belt, not the burst.
-->

---

###### The line runs itself

# Humans at the gates, agents on the line

<div class="flow" style="flex:0 0 auto;margin-bottom:36px">
<div class="card"><span class="badge sm"><img src="assets/icons/clock.svg"></span><h4>Trigger</h4><p>Weekly schedule · GitHub issue · stream ended</p></div>
<div class="arrow">→</div>
<div class="card dark"><span class="badge sm"><img src="assets/icons/workflow.svg"></span><h4>Emcee on Foundry</h4><p>Hosted agent runs the crew</p></div>
<div class="arrow">→</div>
<div class="card peach"><span class="badge sm plum"><img src="assets/icons/check-check.svg"></span><h4>Studio</h4><p>A human approves each draft</p></div>
<div class="arrow">→</div>
<div class="card"><span class="badge sm"><img src="assets/icons/radio.svg"></span><h4>Live site</h4><p>Pages, decks, social go out</p></div>
</div>

<div class="grid cols-3 fit">
<div class="callout" style="margin:0"><strong>CI eval gate</strong><br><span class="small">ASSERT action fails the PR if agent behavior regresses</span></div>
<div class="callout" style="margin:0"><strong>Continuous evals</strong><br><span class="small">Foundry monitors the crew in production</span></div>
<div class="callout" style="margin:0"><strong>Coding agent</strong><br><span class="small">Refreshes labs + samples when SDKs change</span></div>
</div>

<!--
Automate. Triggers: a weekly schedule, a GitHub issue that says "new episode announced", a stream that just ended.
Emcee runs on Foundry as a hosted agent. It never publishes — drafts go to the studio and a human approves.
And the Act 3 inspectors become gates: ASSERT in CI, Foundry continuous evals in production, and a coding agent that keeps the labs fresh.
-->

---

<!-- _class: demo -->

<div class="status">In progress</div>

###### DEMO 04 · Make it scale

# One issue, the whole line runs

<div class="grid">
<div class="card">
<h3>What you'll see</h3>
<ol>
<li>File an issue: “S4-E12 announced”</li>
<li>A routine wakes Emcee on Foundry</li>
<li>Brief, deck, social drafts appear in the studio</li>
<li>Approve — the episode page goes live</li>
</ol>
</div>
<div class="video"><div class="play"><span></span></div>End-to-end run<div class="cmd">gh issue create --title "S4-E12 announced" --label emcee</div></div>
</div>

<!--
[DEMO 4 — 3:30. In-progress for the first showing: walk the architecture + the local Emcee run instead]
Kick off live, then switch to the run captured this morning ("bake-and-switch").
Show: issue → routine → Emcee trace (handoffs) → studio queue fills → approve → page updates.
Bridge: "So what does this mean for DevRel?"
[25:00]
-->

---

###### Rethink DevRel

# From handcrafted to repeatable: DevRel in the age of AI

<div class="grid" style="grid-template-columns: 1.85fr 1fr; gap:56px">
<table>
<tr><th>Focus</th><th>Handcrafted</th><th>Agent-powered, self-guided</th></tr>
<tr><td>Content</td><td class="muted">One-off talks and workshops</td><td><strong>Repeatable pipelines per episode</strong></td></tr>
<tr><td>Learning</td><td class="muted">Live, instructor-led sessions</td><td><strong>Self-guided paths, anytime</strong></td></tr>
<tr><td>Scale</td><td class="muted">Limited by advocate hours</td><td><strong>Limited by system design</strong></td></tr>
<tr><td>Advocate role</td><td class="muted">Makes every artifact</td><td><strong>Designs the factory</strong></td></tr>
</table>
<div class="card crimson" style="justify-content:center"><span class="badge plum"><img src="assets/icons/trending-up.svg"></span><p class="big" style="margin-top:20px">Build systems, not one-offs: every livestream becomes a reusable, self-guided learning asset that keeps working long after the show ends.</p></div>
</div>

<!--
[25:00 — WRAP, 3:30]
Zoom out. The advocate's job changes: from making every artifact, to designing the factory.
And learning changes: from instructor-led, to self-guided paths that keep working after the show.
-->

---

###### The DevRel playbook

# Make it work → make it better → make it scale

<div class="grid cols-3">
<div class="card band"><div class="head"><div><span class="label">Step 1</span><h3>Make it work</h3></div><img src="assets/icons/lightbulb.svg"></div>
<div class="body"><p><strong>Decompose &amp; delegate</strong></p><ul class="tight"><li>Map one show's stations</li><li>A skill per station</li><li>A crew + MCP to run them</li></ul><div class="chips"><span class="chip">Agent Skills</span><span class="chip">MCP</span><span class="chip">Marp</span></div></div></div>
<div class="card band"><div class="head plum"><div><span class="label">Step 2</span><h3>Make it better</h3></div><img src="assets/icons/gauge.svg"></div>
<div class="body"><p><strong>Optimize</strong></p><ul class="tight"><li>Write the spec down</li><li>Measure with evidence</li><li>Fix, then re-measure</li></ul><div class="chips"><span class="chip amber">run-assert-eval</span><span class="chip amber">microsoft-foundry</span></div></div></div>
<div class="card band"><div class="head"><div><span class="label">Step 3</span><h3>Make it scale</h3></div><img src="assets/icons/trending-up.svg"></div>
<div class="body"><p><strong>Automate</strong></p><ul class="tight"><li>Triggers, not reminders</li><li>Eval gates in CI + prod</li><li>Humans approve</li></ul><div class="chips"><span class="chip">Foundry routines</span><span class="chip">CI gates</span></div></div></div>
</div>

<!--
The playbook, one more time — now with tools attached.
Make it work: skills, agents, MCP, Marp.
Make it better: run-assert-eval and microsoft-foundry — observability and optimization.
Make it scale: routines and gates.
-->

---

###### Build your factory

# Try it yourself: the whole line is open

<div class="grid" style="grid-template-columns: 1.6fr 1fr; gap:56px">
<div class="steps">
<div class="step"><span class="badge xs num-badge" style="font-size:26px">0</span><b>Setup</b><span>Open in a dev container — data, skills, site included</span></div>
<div class="step"><span class="badge xs num-badge" style="font-size:26px">1</span><b>Decompose</b><span>Write your first station skill</span></div>
<div class="step"><span class="badge xs plum num-badge" style="font-size:26px">2</span><b>Delegate</b><span>Marp + MCP, then an Emcee crew</span></div>
<div class="step"><span class="badge xs num-badge" style="font-size:26px">3</span><b>Optimize</b><span>run-assert-eval + microsoft-foundry</span></div>
<div class="step"><span class="badge xs plum num-badge" style="font-size:26px">4</span><b>Automate</b><span>Routines, CI gates, continuous evals</span></div>
</div>
<div class="card dark center" style="justify-content:center"><img class="qr" src="assets/qr-repo.svg" alt="QR code to the talk repository"><p class="mt"><strong>github.com/nitya/<br>dont-let-the-chocolates-pile-up</strong></p><p class="small">Slides · labs · skills · data</p></div>
</div>

<!--
Everything you saw is in this repo: the data, the skills, the site, the crew, the evals, and a self-guided learning path. Start with the dev container. The fast path is about 90 minutes.
-->

---

<!-- _class: dark -->

###### Key takeaway

# Stop chasing the conveyor belt — start running your own agent-powered chocolate factory.

<div class="grid cols-3 fit mt">
<div class="row"><span class="badge"><img src="assets/icons/lightbulb.svg"></span><h4>Make it work</h4></div>
<div class="row"><span class="badge"><img src="assets/icons/gauge.svg"></span><h4>Make it better</h4></div>
<div class="row"><span class="badge"><img src="assets/icons/trending-up.svg"></span><h4>Make it scale</h4></div>
</div>

<p class="big amber" style="margin-top:110px;font-family:var(--font-head);font-weight:700">Thank you &nbsp;|&nbsp; Questions? &nbsp;|&nbsp; Connect with me: in/nityan</p>

<!--
Stop chasing the conveyor belt. Make it work, make it better, make it scale — and start running your own agent-powered chocolate factory.
Thank you! [28:30 — 1:30 buffer for Q&A]
-->
