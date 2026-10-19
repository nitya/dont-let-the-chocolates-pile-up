#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip
pip install -r .github/skills/refresh-model-mondays-data/scripts/requirements.txt
[ -f site/requirements.txt ] && pip install -r site/requirements.txt
[ -f agents/requirements.txt ] && pip install -r agents/requirements.txt

npm install -g @marp-team/marp-cli

python .github/skills/refresh-model-mondays-data/scripts/sync.py check || true
echo "Ready. Next: see learn/00-setup.md"
