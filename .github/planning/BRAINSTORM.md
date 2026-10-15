# 🍫 Talk + Workshop Brainstorm — Working State

> **Status:** Brainstorm only. Do **not** implement until the speaker says **"LETS GO"**.
> Last updated: 2026-10-15

## ⚠️ Source of truth

- **This folder (`.github/planning/`) is the source of truth.** Every decision recorded here was
  made interactively and approved by the speaker. These are final outcomes.
- **`.github/.legacy/` is for legacy reference only.** It holds the earlier L.U.C.Y-based plan,
  which is now dropped. Do not treat anything there as a current decision. Where it conflicts
  with this folder, this folder wins.
- New decisions get added here only after interactive approval.

## Formats

- **Talk:** 25 min, demos pre-recorded (low risk; optional single live "Approve" click)
- **Workshop (later):** 75 min hands-on. The repo is **workshop-first**; the talk is a highlight
  reel over the same checkpoints.
- **Audience:** mixed (DevRel/community + developers/AI engineers)

## Core narrative

Blend of three devices:

1. **The talk makes its own chocolate:** the pipeline produces content (recap, Marp deck, links,
   social) from real show content; closing reveal shows the output.
2. **Orchestration as a factory:** belt = sequential pipeline, extra hands = fan-out/fan-in,
   floor manager = orchestrator, taste tester = evaluator, Lucy = human-in-the-loop gate.
3. **Optimization before/after:** one-big-model v1 vs right-sized, tuned v2/v3, scored on
   quality, cost, latency.

### Human angle

The AI pace causes anxiety, stress, and constant context switching. Lucy's problem wasn't speed;
it was **no control over the belt**. The orchestrator is a **Chief of Staff**, not a supervisor
yelling "speed it up":

- triages incoming work (model drops, AMA questions, speaker threads)
- prioritizes against *your* capacity (`capacity.yaml` "energy budget"), not belt speed
- delegates to specialist agents
- protects focus (one digest instead of constant pings; permission to defer/drop)
- keeps the human where judgment matters (approval gate)

Tone: a shared experience, no clinical claims. "Agents share the load; they don't replace rest."
A short personal moment in the prologue is TBD.

## Structure: three pillars, pun title + pillar subtitle

| Section | Title | Pillar / focus | ~Talk | ~Workshop |
|---|---|---|---|---|
| Prologue | **Melting Point** | The belt speeds up; human cost | 3 min | 10 min (setup + context) |
| Act I | **Hand-Dipped — Make it work** | Agent harnesses | 7 min | 20 min (Lab 1) |
| Act II | **Tempering — Make it better** | Agent optimization | 7 min | 20 min (Lab 2) |
| Act III | **Factory Floor — Make it scale** | Foundry platform | 6 min | 20 min (Lab 3) |
| Close | **Unwrapped** | Fork the factory; DevRel → self-guided learning | 2 min | 5 min |

A nod to Kent Beck's "make it work, make it right, make it fast."

### Act I: Hand-Dipped (Make it work)

- A model alone isn't an agent: **harness = loop + tools + skills + MCP + context/memory +
  checkpoints + human gate**.
- Harness choice: **Copilot SDK** as the harness, using the **foundry-mcp** server, the
  **microsoft-foundry** MCP server, and **assert-run-eval** skills.
- Pipeline built with **Microsoft Agent Framework (Python)**.
- Demo: the Chief of Staff triages a messy week (dispatch/defer/drop), then sends a Model
  Mondays episode down the line; the trace shows the fan-out/fan-in.
- Takeaway: most "the agent doesn't work" problems are harness problems, not model problems.

### Act II: Tempering (Make it better)

- Hill-climb: lock the eval first, then change one variable at a time.
- Levers (all featured):
  - Evals first (rubrics + golden set)
  - Model per station
  - Model router
  - Context engineering (trimming, caching)
  - Prompt optimization (Agent Lightning / DSPy)
- Demo: a v1 → v2 → v3 scoreboard (quality, cost, latency, "chocolates/hour"), plus one slide
  on what *didn't* help.
- Takeaway: "better" means a number went up on an eval you trust. Optimize for *sustainable*,
  not max heat.

### Act III: Factory Floor (Make it scale)

- Same code from laptop to platform, with no rewrite.
- Foundry: model catalog + router, Agent Service / hosted agents, tracing, continuous evals,
  content safety, identity; Container Apps scheduled job for the weekly cadence; `azd up`.
- Demo: `azd up` (time-lapse) → scheduled run → traces in Foundry → **Approve** → PR opens.
- Takeaway: scale is a platform problem; don't solve it with your calendar.

## Pipeline sketch (proposal, not yet approved)

```
Intake (Model Mondays episode / AMA questions)
  → Chief of Staff (triage, prioritize to capacity)
  → Transcriber (bundled transcript for labs; Speech/transcribe model optional)
  → Summarizer (small model, chunked)
  → fan-out ─┬ RecapWriter   → blog markdown
             ├ SlideSmith    → Marp deck (grounded via Learn MCP)
             ├ LinkCurator   → "News Highlights" (validated URLs)
             └ SocialWriter  → posts
  → fan-in → Inspector (LLM judge + link checker + style rubric)
  → Human gate → Publisher (GitHub MCP → PR)
```

Azure: Foundry project + models, Container Apps (API + scheduled job), Service Bus (belt),
Blob (artifacts), App Insights / OTel tracing, managed identity, `azd` template.

## Repo design for long-term value (workshop-ready)

- One lab per act, each with **start** and **solution** checkpoints (these also serve as talk
  demo fallbacks)
- One-command setup: devcontainer/Codespaces + `azd up`
- Sample Model Mondays transcript bundled, so there's no live media dependency
- Config-driven stations/models (`stations.yaml`) so attendees swap models without code edits
- `capacity.yaml` for the Chief of Staff energy budget
- Evals + golden set reused as workshop exercises

Draft layout (proposal, not yet approved):

```
factory/
  agents/        chief_of_staff, transcriber, summarizer, recap_writer, slidesmith,
                 link_curator, social_writer, inspector
  skills/        SKILL.md style guides (recap voice, Marp theme rules)
  workflow.py    Agent Framework graph
  config/        stations.yaml, capacity.yaml
  evals/         rubrics, golden set, optimization runs
  api/           trigger run + approval endpoint
labs/            lab-1-hand-dipped, lab-2-tempering, lab-3-factory-floor (start/solution)
data/            sample Model Mondays transcript
infra/ + azure.yaml
```

## Open questions (re-ask on resume)

- How the Copilot SDK harness relates to the Agent Framework pipeline: does it build/drive/eval
  the pipeline, or replace it?
- Exact roles of foundry-mcp vs microsoft-foundry MCP vs the assert-run-eval skill (verify what
  each provides)
- Checkpoints as git branches/tags or `labs/` folders?
- Which Model Mondays episode; personal story yes/no
- Which Chief of Staff capabilities to show
- Verify current names/status: Foundry Agent Service / hosted agents, model router, Agent
  Lightning, Agent Framework APIs
