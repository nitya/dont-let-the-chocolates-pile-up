#!/usr/bin/env bash
set -euo pipefail

# Three Python environments, because their pins conflict:
#   shared python   -> data skill + site (mcp==2.3)
#   agents/.venv    -> Emcee crew (Agent Framework needs mcp<2, openai>=3)
#   evals/.venv     -> ASSERT (LiteLLM needs openai<3)
python -m pip install --upgrade pip
pip install -r .github/skills/refresh-model-mondays-data/scripts/requirements.txt
pip install -r site/requirements.txt

python -m venv agents/.venv
agents/.venv/bin/pip install -q -r agents/requirements.txt

python -m venv evals/.venv
evals/.venv/bin/pip install -q -r evals/requirements.txt

npm install -g @marp-team/marp-cli

python .github/skills/refresh-model-mondays-data/scripts/sync.py check || true
echo "Ready. Next: see learn/00-setup.md"
