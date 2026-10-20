# Evals: make it better

[ASSERT](https://github.com/responsibleai/assert) eval suites for the Emcee crew. The first target is the **Producer**, the agent that writes recaps and News Highlights. Each YAML file tests one atomic behavior.

| Suite | Risk | Why |
|---|---|---|
| [producer/ungrounded_links.yaml](producer/ungrounded_links.yaml) | Placeholder, invented or unsupported links | The upstream data has 83 News Highlight links pointing at the series homepage, and the Producer reads that data |
| [producer/unsupported_claims.yaml](producer/unsupported_claims.yaml) | Invented speakers, quotes, numbers or announcements | Many episodes have no guest names in the data and no transcript yet |

## Setup (separate venv)

ASSERT uses LiteLLM, which pins `openai<3`. The Foundry / Agent Framework stack needs `openai>=3`, so the evals get their own environment:

```bash
python3 -m venv evals/.venv
evals/.venv/bin/pip install -r evals/requirements.txt
cp evals/.env.example evals/.env      # set AZURE_API_BASE / AZURE_API_KEY (or ASSERT_AZURE_USE_AAD=1 after az login)
```

The model strings in the YAML (`azure/gpt-5.4`, `azure/gpt-5.4-mini`) are LiteLLM `azure/<deployment-name>` values. Change them to match your Foundry deployments.

## The target

[`producer/target.py`](producer/target.py) calls the Producer through `agents.producer_entry` in **dry-run** mode: drafts are validated but never queued.

Because the agents and ASSERT need separate venvs, the call crosses a process boundary, and ASSERT can't capture the agent's OpenTelemetry spans in-process. Until they're exported to Phoenix (`OTEL_EXPORTER_OTLP_ENDPOINT` + `trace.backend: phoenix`, planned), the target appends a **Grounding evidence** section to each response for the judge to cite:
- the tool calls and their results;
- each draft's sources;
- guardrail blocks;
- items flagged for a human.

Smoke-test the target without any model:

```bash
EMCEE_EVAL_MOCK=1 evals/.venv/bin/python -c "from evals.producer.target import chat; print(chat('Recap S4-E09')[:800])"
```

For real eval runs, configure `agents/.env` (the Producer's model) **and** `evals/.env` (ASSERT's generator and judge models).

## Run

Guided, with the skill in Copilot agent mode:

```bash
npx skills add responsibleai/ASSERT --skill run-assert-eval --yes
```

Then prompt: *"evaluate the Producer for placeholder or invented links"*.

Or run the CLI directly:

```bash
set -a; . evals/.env; set +a
evals/.venv/bin/assert-ai run --config evals/producer/ungrounded_links.yaml
evals/.venv/bin/assert-ai results list
```

## Read the results

| Number | Meaning |
|---|---|
| **Impermissible behavior violated** | The harm number. Drive this down. |
| **Permissible behavior violated** | The trade-off number (e.g. over-refusing to write a recap at all). Don't let it climb. |

## Fix and re-measure

1. Tighten the Producer's instructions (or `mm-recap/SKILL.md`, which the Producer loads).
2. Re-run with `--override run=after-fix`.
3. Compare: `assert-ai results compare producer-ungrounded-links baseline after-fix`. The delta is the evidence.
4. **CI gate:** wire the same configs into [`responsibleai/assert-ai-action`](https://github.com/responsibleai/assert-ai-action) so a PR that regresses grounding fails.

## Cheap guardrail vs eval

[`check.py`](../.github/skills/mm-recap/scripts/check.py) is a deterministic linter: it catches the *obvious* placeholder link. ASSERT measures what a regex can't, such as:
- a plausible but wrong link;
- an invented guest;
- a claim the transcript doesn't support;
- behavior under pressure ("every item needs a link").

Use both.
