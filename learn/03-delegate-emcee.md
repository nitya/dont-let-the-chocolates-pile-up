# 03 · Delegate: an Emcee crew

**Playbook:** *Make it work → delegate.* Skills are stations; agents are the crew that runs them.

> **Status: in progress.** Code lives in [`agents/`](../agents/). See [`agents/README.md`](../agents/README.md) for the current run instructions.

## Outline

1. **Meet the crew:**
   - **Emcee** orchestrates;
   - **Coordinator** writes the brief and run-of-show;
   - **Producer** writes recaps and highlights (reuses `mm-recap`);
   - **Presenter** builds the deck (reuses `mm-deck`);
   - **Publisher** writes social posts and announcements.
2. **Run it without a model:**
   ```bash
   python -m agents.emcee "prep S4-E12" --mock
   ```
   This calls the real MCP server and runs the real orchestration, with a scripted planner instead of an LLM.
3. **Run it with a model:** point `agents/.env` at a Foundry project and model deployment, then run without `--mock`.
4. **Read the trace:** see how Emcee hands off to each specialist, which tools each one calls, and what lands in the studio.
5. **Approve in the studio.** Note that agents can't approve anything: the MCP server has no approve tool.
6. **Extend:** add a specialist (e.g. `Translator`) and register it with Emcee.
