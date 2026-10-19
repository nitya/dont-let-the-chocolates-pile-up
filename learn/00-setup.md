# 00 · Setup

**Goal:** a working environment with the data, the site and its MCP server, and Copilot connected to both MCP servers.

## 1. Open the dev container

Pick one:

- **Codespaces:** *Code → Codespaces → Create codespace on this branch.*
- **Local:** clone the repo, open it in VS Code with Docker running, then *Dev Containers: Reopen in Container*.

The container installs Python 3.12, Node, the Marp CLI, the Azure CLI, `azd` and the GitHub CLI. It also installs the Python requirements for the data skill, the site and the agents (see [`.devcontainer/post-create.sh`](../.devcontainer/post-create.sh)).

## 2. Check the data

```bash
python3 .github/skills/refresh-model-mondays-data/scripts/sync.py check
# check: 50 episodes, 48 linked to YouTube, N with transcripts, 0 errors
```

Optional: refresh from upstream with `sync.py all`. See the [skill](../.github/skills/refresh-model-mondays-data/SKILL.md) for the optional `YOUTUBE_API_KEY` and how transcripts work.

## 3. Start the site + MCP server

```bash
cd site
python scripts/reset_state.py --seed
python -m uvicorn app.main:app --reload --port 8000
```

Open <http://localhost:8000>:
- **Home** shows series stats and the next episode.
- **Episode pages** have video, chapters and stats.
- **Studio** is the review queue where *you* approve what agents draft.

## 4. Connect Copilot to MCP

[`.vscode/mcp.json`](../.vscode/mcp.json) already defines two servers:

| Server | URL | Gives agents |
|---|---|---|
| `model-mondays` | `http://localhost:8000/mcp` | Episodes, transcripts, series stats, and `submit_draft` (no approve tool, by design) |
| `microsoft-learn` | `https://learn.microsoft.com/api/mcp` | Current Microsoft docs search and fetch |

Open the file and click **Start** above each server. In Copilot Chat (**Agent** mode), open the tools picker; you should see both servers' tools.

**Try it:** *"Using the model-mondays MCP server, what are the five most-viewed episodes?"*

✅ **Done when:** the site loads, `sync.py check` reports 0 errors, and Copilot answers from the MCP server.
