# Infrastructure

`azd up` deploys the **Model Mondays site + MCP server** to Azure App Service. The **Foundry project and the Emcee hosted agent** are added to the same `azure.yaml` with the `microsoft-foundry` skill. That step is part of the talk's Act 4 and of [lab 06](../learn/06-automate.md).

## What `azd up` creates today

| Resource | Purpose |
|---|---|
| Resource group `rg-<env>` | Everything for one environment |
| App Service plan (Linux, B1) + Web App (Python 3.12) | Site, JSON API, `/mcp` endpoint, studio |
| Log Analytics + Application Insights | Telemetry (also used for agent traces later) |

The site is packaged from `site/`. A `prepackage` hook copies `data/` into `site/data` (gitignored), which the app falls back to automatically. Drafts persist in `/home/mm-state`. The app runs as a **single instance**, because the drafts store is one JSON file.

## Deploy the site

```bash
azd auth login
azd env new mm-demo
azd env set MM_WRITE_KEY "$(openssl rand -hex 16)"    # agents need this to submit drafts
azd env set MM_ADMIN_KEY "$(openssl rand -hex 16)"    # you need this to approve in /studio
azd up
azd env get-values | grep MM_                         # MM_SITE_URL, MM_MCP_URL
```

Point VS Code at the deployed MCP server by adding a `headers` entry in `.vscode/mcp.json`. See [site/README.md](../site/README.md#mcp-server).

## Add the Foundry project + Emcee hosted agent (December build)

Use the [`microsoft-foundry`](https://github.com/microsoft/azure-skills/tree/main/skills/microsoft-foundry) skill in Copilot agent mode:

1. **Install the skill:**

   ```bash
   npx skills add microsoft/azure-skills --skill microsoft-foundry --yes
   ```

2. **Create:** *"Create a hosted Foundry agent from the code in agents/ and add it to this azd project."*
   The skill runs `azd ai agent init` and appends two services to `azure.yaml`:
   - `ai-project`, with a model deployment;
   - the `emcee` agent service.
3. **Deploy:** *"Deploy and smoke-test the emcee agent."* This runs `azd provision` + `azd deploy`, then invokes the agent.
4. **Schedule:** *"Add a routine that runs emcee every Wednesday with 'prep next episode', and one triggered by GitHub issues labeled emcee."* This uses the routine sub-skill (`azd ai routine`, preview).
5. **Observe:** *"Evaluate the emcee agent and enable continuous evaluation."* This uses the observe sub-skill (lab 05).

Give the agent the site's `MM_SITE_URL` and `MM_WRITE_KEY` as environment variables, so it submits drafts to the deployed studio.
