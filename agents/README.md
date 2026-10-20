# Emcee: the Model Mondays content-factory orchestrator

**Emcee** is the master of ceremonies of the Model Mondays content factory (and **M.C.** = **M**odel **C**atalog).
It is the *delegate* (Act 2) and *automate* (Act 4) demo of the talk: one orchestrator plans the work, four specialist
agents draft content grounded in real episode data, and **every draft lands in the site's human review queue**. No
agent can approve or publish anything.

```
request ─► emcee (orchestrator) ── plans with get_episode / search_episodes / get_series_stats
             ├─⇢ coordinator  brief + run_of_show         ─┐
             ├─⇢ producer     recap + highlights           │  each specialist: site MCP tools (+ Learn MCP for the
             ├─⇢ presenter    Marp deck                    │  presenter), check_draft / render_deck / flag_for_human,
             └─⇢ publisher    announcement + social posts ─┘  then submit_draft ─► Studio queue ─► human approves
```

Built on **Microsoft Agent Framework (Python) 1.22.0**:

| What | API (package · version) |
|---|---|
| Agents | `agent_framework.Agent` (agent-framework-core 1.22.0) |
| Delegation | `Agent.as_tool()`: each specialist is a tool of the emcee ("agents as tools") |
| MCP | `agent_framework.MCPStreamableHTTPTool` with `allowed_tools`, `static_headers` (site at `<site>/mcp`, Microsoft Learn at `https://learn.microsoft.com/api/mcp`) |
| Local tools | `@agent_framework.tool` (`flag_for_human`, `check_draft`, `render_deck`) |
| Trace + guardrail | `FunctionMiddleware` (trace, `submit_draft` guardrail), `ChatMiddleware` (model timing) |
| Models | `agent_framework_foundry.FoundryChatClient` (agent-framework-foundry 1.15.0) or `agent_framework_openai.OpenAIChatClient(azure_endpoint=…)` (agent-framework-openai 1.17.0), both with `azure.identity.aio.DefaultAzureCredential` |
| Mock model | a `BaseChatClient` + `FunctionInvocationLayer` + `ChatMiddlewareLayer` + `ChatTelemetryLayer` subclass with scripted "brains" |
| Hosting | `agent_framework_foundry_hosting.ResponsesHostServer` (agent-framework-foundry-hosting 1.0.0b261015, **beta**) |
| Telemetry | built-in OpenTelemetry spans (`invoke_agent`, `chat`, `execute_tool`, MCP `tools/call`) |

## Setup

The agents need their **own virtualenv**: agent-framework 1.22 requires `mcp<2`, while the site pins `mcp==2.3.0`.

```bash
python -m venv agents/.venv
agents/.venv/bin/pip install -r agents/requirements.txt
```

You can still type `python -m agents.emcee …` with any Python: if the current interpreter can't run the agents, the
CLI re-executes itself inside `agents/.venv` (same for the tests and `agents.producer_entry`).

Start the site (see `site/README.md`), e.g. `cd site && python -m uvicorn app.main:app --port 8000`.

## Run it

### Mock mode (no LLM, no credentials)

```bash
python -m agents.emcee "prep S4-E12" --mock
python -m agents.emcee "wrap up S4-E09" --mock
python -m agents.emcee "new episode announced: Spotlight on NVIDIA Models" --mock
python -m agents.emcee "prep next" --mock --only coordinator,presenter
python -m agents.emcee "prep S4-E12" --mock --only publisher --mock-fault placeholder   # watch the guardrail
```

`--mock` swaps the LLM for deterministic scripts but keeps **everything else real**: the Agent Framework function-calling
loop, agent-as-tool delegation, middleware, and the MCP calls to the site (and to Microsoft Learn). The drafts are built
from the real episode data the tools return and are titled `[mock] …` with a banner saying how they were made, so the
Studio and the episode pages update live during the demo.

Useful flags: `--site URL` (default `$EMCEE_SITE_URL` or `http://localhost:8000`), `--only a,b`, `--no-learn`,
`--dry-run` (guardrail-validated, nothing queued), `--mock-delay 0.4` (stage pacing), `--json-out ledger.json`,
`--report-md report.md`, `--no-color`, `-q`, `-v` (show every model call). `EMCEE_ASCII=1` gives ASCII-only icons.

### Real models (Microsoft Foundry or Azure OpenAI)

```bash
cp agents/.env.example agents/.env      # then set ONE of:
#   FOUNDRY_PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project>
#   FOUNDRY_MODEL=<deployment name>
# or
#   AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com
#   AZURE_OPENAI_DEPLOYMENT=<deployment name>   [AZURE_OPENAI_API_KEY=… optional]
az login                                 # DefaultAzureCredential (managed identity when hosted)
python -m agents.emcee "prep S4-E12"
```

`AZURE_AI_PROJECT_ENDPOINT` / `AZURE_AI_MODEL_DEPLOYMENT_NAME` (the names `azd ai agent` uses) are accepted as aliases.
GitHub Models endpoints are rejected on purpose. All variables are documented in [`.env.example`](.env.example).
Not yet verified against a live model in this repo: there were no Azure credentials in the dev box. Client construction
and the auth/connection error paths were exercised.

### The trace (what the audience sees)

```
━━━ Emcee · 'prep S4-E12' ━━━
model: mock (scripted, no LLM) · site: http://localhost:8000 · specialists: all
   1.1s  emcee       ▶ plan  → prep S4-E12
   2.1s  emcee       · get_episode(episode_id=s4-e12)  → S4-E12 “Spotlight on NVIDIA Models” · upcoming 2026-11-02 · 0 chapters  13 ms
   2.1s  emcee       ⇢ coordinator  → Write the guest brief and the run-of-show for the upcoming episode S4-E12 …
   2.1s    coordinator · search_episodes(query=NVIDIA, limit=6)  → 4 episodes: s4-e12, s3-e15, s2-e07, s3-e13  21 ms
   2.1s    coordinator · get_episode(episode_id=s4-e09)  → S4-E9 “Spotlight on Speech Models” · completed · 9 chapters  11 ms
   2.1s    coordinator ⚑ flag_for_human  → Add guest names for S4-E12 to the brief and run-of-show.
   2.2s    coordinator ✎ submit_draft(brief, '[mock] Guest brief: S4-E12 Spotlight on…')  → draft b40a79c9 · brief · pending  36 ms
   2.2s  emcee       ⇠ coordinator done  → 2 draft(s)  168 ms
   3.0s    presenter   · microsoft_docs_search(query=NVIDIA models in Microsoft …)  → 10 Learn results · …  802 ms
   3.2s    presenter   · check_draft(s4-e12, 5422 chars)  → check.py PASS  96 ms
   3.2s    presenter   ✎ submit_draft(deck, '[mock] Deck: S4-E12 Spotlight on NVIDIA…')  → draft 056c09b8 · deck · pending
   …
━━━ Run report ━━━
5 draft(s) queued for human review · 23 tool calls · 3.4s
  ✎ brief         b40a79c9   S4-E12  [mock] Guest brief: S4-E12 Spotlight on NVIDIA Models   coordinator
  …
  Studio: http://localhost:8000/studio
Needs a human:
  ⚑ coordinator: s4-e12: Add guest names for S4-E12 to the brief and run-of-show.
```

Icons: `⇢`/`⇠` handoff to/from a specialist, `·` tool call, `✎` draft submitted, `⚑` escalated to a human,
`⛔` blocked by the guardrail, `✗` error, `…` model round-trip (shown when it takes ≥ 0.3 s, i.e. real LLMs).

## How the rules are enforced

* **Same rules as the skills.** The producer's instructions embed `.github/skills/mm-recap/SKILL.md` and the presenter's
  embed `.github/skills/mm-deck/SKILL.md`, loaded **at runtime** (not copied). The coordinator and publisher embed the
  `## Rules` section of mm-recap. Prompts live in [`emcee/prompts/`](emcee/prompts/).
* **`check_draft`** runs the skill's own `check.py`; **`render_deck`** runs `mm-deck/scripts/render.py --standalone` when
  `marp` is on PATH (`EMCEE_MARP=npx` allows `npx @marp-team/marp-cli`; verified: the HTML with inlined images is
  attached to the deck draft automatically). Without Marp the deck is submitted as Markdown only.
* **Guardrail middleware on every `submit_draft`** (`emcee/middleware.py`): forces `author_agent="emcee/<name>"`,
  restricts each specialist to its kinds, requires non-empty `sources` that are URLs or `data/` paths, rejects
  `https://aka.ms/model-mondays` (same regex as the skill's `context.py`) in sources and content, labels mock drafts.
  A blocked call returns `BLOCKED …` to the model so it can fix and resubmit; the run report lists it.
* **Escalation:** any agent can call `flag_for_human`; the emcee refuses to "wrap up" an episode that hasn't aired or
  "prep" one that has. Everything flagged appears under *Needs a human*.

## Foundry hosted agent

[`emcee/hosted.py`](emcee/hosted.py) serves the emcee over the **Responses protocol** with
`ResponsesHostServer(agent=create_emcee)` (a per-request factory: fresh team, MCP connections and ledger per request).
It listens on `$PORT` or **8088** (the hosted-agent port), exposes `GET /readiness`, and reads the same env vars.

```bash
EMCEE_MOCK=1 python -m agents.emcee.hosted            # or without EMCEE_MOCK, with a model configured
curl -s localhost:8088/responses -H 'content-type: application/json' -d '{"input": "wrap up S4-E09"}'
```

```bash
docker build -f agents/Dockerfile -t emcee .          # build from the REPO ROOT (copies skills + episode data)
docker run --rm -p 8088:8088 --add-host=host.docker.internal:host-gateway \
  -e EMCEE_MOCK=1 -e EMCEE_SITE_URL=http://host.docker.internal:8000 emcee
```

| Status | |
|---|---|
| ✅ Verified locally | `ResponsesHostServer` serving the emcee (mock), `POST /responses` returns `completed` with the tool calls and the run report; the Docker image builds and answers the same request (`--network host`). |
| ⚠️ Not verified | Deploying to a Foundry project, managed-identity access to the model, and routines: no Azure subscription/`azd` in this dev box. `agent-framework-foundry-hosting` is a **beta** (1.0.0b261015) and pins `azure-ai-agentserver-*` pre-releases. |

### Deploy and schedule with the `microsoft-foundry` skill

The [`microsoft-foundry`](https://github.com/microsoft/azure-skills/tree/main/skills/microsoft-foundry) skill (from
`microsoft/azure-skills`) drives `azd` and its `azure.ai.agents` / `azure.ai.routines` extensions. The plan, using its
sub-skills (commands are from the skill docs, **not executed here**):

1. **create** (`foundry-agent/create/create-hosted.md`): onboard the existing code instead of a sample:
   `azd ai agent init --src agents …` (the skill's "existing agent" path), choosing **container** deploy because the
   image needs the skills and data copied from the repo root. Point the generated `azure.yaml` service at
   `agents/Dockerfile` with the repo root as Docker context, and map `FOUNDRY_PROJECT_ENDPOINT` /
   `AZURE_AI_MODEL_DEPLOYMENT_NAME` (both read by Emcee), plus `EMCEE_SITE_URL` and `MM_WRITE_KEY` (as a secret).
   Local inner loop: `azd ai agent run --no-client`, then `azd ai agent invoke --local "prep S4-E12"`.
2. **deploy** (`foundry-agent/deploy/deploy.md`): `azd provision` then `azd deploy` (remote ACR build:
   `docker.remoteBuild: true`). The container must start the server on port 8088 (it does).
3. **invoke** (`foundry-agent/invoke/invoke.md`): smoke test `"prep next"` against the deployed agent.
4. **routine** (`foundry-agent/routine/routine.md`, preview, `azd extension install azure.ai.routines`, azd ≥ 1.27):
   [`foundry/routine-weekly-wrap.yaml`](foundry/routine-weekly-wrap.yaml) (Tuesdays 09:00 ET: "wrap up the latest
   episode"), [`foundry/routine-weekly-prep.yaml`](foundry/routine-weekly-prep.yaml) (Tuesdays 10:00 ET: "prep next"),
   [`foundry/routine-on-issue.yaml`](foundry/routine-on-issue.yaml) (GitHub issue **opened**; needs a GitHub connection
   in the project). Create each with `azd ai routine create <name> --file <manifest>`; fire one now with
   `azd ai routine dispatch <name>`; inspect with `azd ai routine run list <name>`.
   *Unverified:* how the triggering issue's title/body are templated into `action.input` (see the TODO in the manifest).
5. **observe** (`foundry-agent/observe/observe.md`): traces/evaluations in Foundry. The hosted server already emits
   OpenTelemetry (set `APPLICATIONINSIGHTS_CONNECTION_STRING`).

### GitHub Actions fallback (Act 4)

[`workflows/emcee-on-issue.yml`](workflows/emcee-on-issue.yml) runs the CLI when an issue is **labeled `emcee`**
(Foundry's issue trigger only supports opened/closed) against `vars.EMCEE_SITE_URL`, logs in with OIDC for
`DefaultAzureCredential`, and comments the run report on the issue. It lives here, not in `.github/workflows/`, so it
is inactive until copied there. Set `vars.EMCEE_MOCK=1` to rehearse without a model.

## For evals: run the producer alone

```python
from agents.producer_entry import run_producer, run_producer_detailed
md = run_producer("Wrap up S4-E09: recap and highlights.", history=None, mock=False)  # -> recap + highlights Markdown
```

Synchronous; dry run by default (the guardrail validates `submit_draft` but nothing is queued; `submit=True` queues);
`site=` overrides the site URL. `run_producer_detailed` also returns the drafts with sources, tool calls, escalations
and guardrail blocks. Spans (`emcee.producer`, `invoke_agent producer`, `chat`, `execute_tool …`, MCP `tools/call …`)
go to the global OpenTelemetry tracer provider; if none is configured and `OTEL_EXPORTER_OTLP_ENDPOINT` is set, one is
configured for you. From an interpreter without Agent Framework it runs in `agents/.venv` through a JSON subprocess.

## Tests

```bash
python -m pytest agents/tests -q
```

Starts a throwaway site (uvicorn subprocess on a free port, temp `MM_STATE_DIR`; the site interpreter is
`$MM_SITE_PYTHON` or the first Python that can import the site's dependencies), then runs the real CLI in mock mode:
prep S4-E12 and wrap up S4-E09 must queue the expected kinds with non-empty sources and no placeholder links, plus
escalation, `--only`, guardrail, dry-run and `producer_entry` checks.

## Layout

```
agents/
  emcee/
    __main__.py   CLI                       hosted.py   Foundry hosted-agent server (Responses, port 8088)
    team.py       builds the 5 agents       runner.py   one run + run report
    middleware.py trace, guardrail, timing  tools.py    flag_for_human, check_draft, render_deck
    mock.py       scripted chat client      content.py  mock draft builders (real data in, [mock] drafts out)
    rules.py      intents, link rules, skill loading (framework-free)
    config.py     env settings + chat clients   trace.py  printer + ledger   _env.py  venv hop
    prompts/      emcee, coordinator, producer, presenter, publisher
  producer_entry.py   sync entry point for evals
  foundry/        routine manifests        workflows/  GitHub Actions fallback (inactive)
  tests/          pytest (mock end to end) Dockerfile (+ Dockerfile.dockerignore)   .env.example   requirements.txt
```
