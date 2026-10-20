# 03 · Delegate: an Emcee crew

**Playbook:** *Make it work → delegate.* Skills are stations; agents are the crew that runs them.

Code: [`agents/`](../agents/). Full reference: [`agents/README.md`](../agents/README.md).

## 1. Meet the crew

| Agent | Drafts | Grounded by |
|---|---|---|
| **Emcee** (orchestrator) | a run report | `get_episode`, `search_episodes`, `get_series_stats` |
| Coordinator | `brief`, `run_of_show` | episode + related past episodes |
| Producer | `recap`, `highlights` | `mm-recap` SKILL.md rules + transcript or chapters |
| Presenter | `deck` | `mm-deck` SKILL.md rules + Microsoft Learn MCP |
| Publisher | `announcement`, `social` | episode page + recording links |

Each specialist is an Agent Framework `Agent`, exposed to Emcee as a tool (`Agent.as_tool()`). All of them call the site's MCP server. A `submit_draft` guardrail blocks placeholder links before they reach the studio.

## 2. Set up the agents' venv

The dev container already does this:

```bash
python -m venv agents/.venv && agents/.venv/bin/pip install -r agents/requirements.txt
```

The agents need their own venv because Agent Framework needs `mcp<2` while the site pins `mcp==2.3`. `python -m agents.emcee` hops into the venv automatically.

## 3. Run the crew without a model

With the site running ([lab 00](00-setup.md)):

```bash
python -m agents.emcee "prep S4-E12" --mock --mock-delay 0.3
```

Read the trace:
- `⇢` hand-offs;
- `·` tool calls, with timings;
- `✎` drafts submitted;
- `⚑` items flagged for a human.

Then open **Studio**: five drafts arrived live. Approve some, and check `/episodes/s4-e12`.

Try the guardrail:

```bash
python -m agents.emcee "prep S4-E12" --mock --only publisher --mock-fault placeholder
```

## 4. Run it with a real model

```bash
cp agents/.env.example agents/.env   # FOUNDRY_PROJECT_ENDPOINT + FOUNDRY_MODEL (or AZURE_OPENAI_*)
az login
python -m agents.emcee "wrap up S4-E09"
```

Compare the real drafts with the mock ones, and with [`demo/backups/s4-e09/`](../demo/backups/s4-e09/).

## 5. Extend

- **Add a specialist:** e.g. a `Translator` that drafts a Spanish recap. Add a prompt in `agents/emcee/prompts/` and register it in `team.py`.
- **Tighten a rule:** edit `agents/emcee/rules.py`, then run `python -m pytest agents/tests -q`.

✅ **Done when:** a run (mock or real) puts drafts in the studio, and you can explain every hand-off in the trace.
