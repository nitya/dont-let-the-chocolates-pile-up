# Build your own agent-powered content factory

A self-guided path that follows the talk *Don't Let the Chocolate Pile Up*. You'll take one real weekly show, [Model Mondays](https://aka.ms/model-mondays), and build its content line with skills, agents, MCP and evals, using the same files you saw on stage.

| Playbook step | Lab | You'll build | Time | Needs |
|---|---|---|---|---|
| — | [00 · Setup](00-setup.md) | Dev container, data, site + MCP server | 15 min | Docker or Codespaces |
| **Make it work** | [01 · Decompose: your first station skill](01-decompose-skill.md) | `mm-recap` → your own skill | 25 min | GitHub Copilot |
| | [02 · Slides as code: Marp + MCP](02-marp-mcp.md) | `mm-deck` with Learn MCP + studio approval | 25 min | GitHub Copilot |
| | [03 · Delegate: an Emcee crew](03-delegate-emcee.md) | Multi-agent orchestrator (Agent Framework) | 30 min | Foundry project *(or `--mock`)* |
| **Make it better** | [04 · Measure with `run-assert-eval`](04-measure-assert.md) | Spec → tests → judge → fix → re-measure | 30 min | Model endpoint |
| | [05 · Observe + optimize with `microsoft-foundry`](05-observe-foundry.md) | Batch evals, failure clusters, prompt optimization | 30 min | Foundry project |
| **Make it scale** | [06 · Automate the belt](06-automate.md) | Hosted agent, routines, CI eval gate | 30 min | Azure subscription |
| — | [07 · Map your own line](07-map-your-line.md) | A worksheet for *your* show, docs or community | 20 min | — |

**Fast path (about 90 min):** 00 → 01 → 03 (`--mock`) → 04. **Full path:** all labs, about 3.5 hours.

## What's in the repo

| Folder | What it is |
|---|---|
| [`data/`](../data/) | Local snapshot of the Model Mondays series: 50 episodes, banners, YouTube stats and transcripts |
| [`.github/skills/`](../.github/skills/) | Station skills: `refresh-model-mondays-data`, `mm-recap`, `mm-deck` |
| [`site/`](../site/) | The "factory window": website + MCP server + studio where humans approve drafts |
| [`agents/`](../agents/) | Emcee and its crew (Coordinator, Producer, Presenter, Publisher) |
| [`evals/`](../evals/) | ASSERT eval configs for the crew |
| [`slides/`](../slides/) | The talk deck (Marp) and generated episode decks |
| [`demo/`](../demo/) | Stage runbook and backups |

> **Status:** labs 00–03 are complete (03 runs fully in `--mock` mode; with a Foundry model it needs real credentials). Labs 04–06 are being finished alongside the December version of the talk; their outlines show what's coming.
