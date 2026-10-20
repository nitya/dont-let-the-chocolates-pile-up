# 01 · Decompose: your first station skill

**Playbook:** *Make it work → decompose.* Break the line into stations; give each station a skill.

## 1. Read a skill

Open [`.github/skills/mm-recap/SKILL.md`](../.github/skills/mm-recap/SKILL.md). A skill is a folder with:
- **front matter:** `name` + `description`. The description is how the agent decides *when* to use it, so write it like a trigger.
- **rules:** what must always or never happen (grounding, no placeholder links, drafts only).
- **workflow:** numbered steps, including deterministic scripts the agent runs.
- **scripts/:**
  - [`context.py`](../.github/skills/mm-recap/scripts/context.py) builds a grounded *context pack*.
  - [`check.py`](../.github/skills/mm-recap/scripts/check.py) lints the output.

Run the scripts yourself first:

```bash
python3 .github/skills/mm-recap/scripts/context.py S4-E09
python3 .github/skills/mm-recap/scripts/check.py data/episodes/s3-e04.md --episode s3-e04   # 😬 8 errors
```

The second command runs the checker against a real episode page from the upstream repo. It contains 8 placeholder links. That's the "chocolate on the floor" from Act 3.

## 2. Run the station

In Copilot Chat (**Agent** mode):

```text
recap S4-E09 using the mm-recap skill
```

Watch it:
1. find the skill from its description;
2. run `context.py`;
3. write `content/s4-e09/recap.md` and `highlights.md`;
4. run `check.py` and fix any errors.

Compare with [`demo/backups/s4-e09/`](../demo/backups/s4-e09/).

With the site running and MCP started, ask it to **submit the drafts**. Then open <http://localhost:8000/studio>, click **Approve**, and watch `/episodes/s4-e09` update.

## 3. Build your own station

Pick a repetitive step from *your* line and write a skill for it. Ideas that use this repo's data:

| Skill | Input | Output |
|---|---|---|
| `mm-social` | episode id | 3 social posts (LinkedIn, X, Bluesky) linking to the recording |
| `mm-newsletter` | season number | Monthly digest of approved recaps |
| `mm-guest-brief` | upcoming episode | One-page brief for guests: format, timing, past related episodes |

Template:

```markdown
---
name: my-station
description: "<What it does>. Use when asked to <trigger phrases>."
---
# my-station
## Rules
1. Ground every fact in <source>. Never invent <x>.
## Workflow
1. Run `python3 .github/skills/mm-recap/scripts/context.py <episode>`   # reuse stations!
2. Write `content/<id>/<file>.md` using the template below.
3. Run `check.py` and fix every error.
```

✅ **Done when:** your skill runs from a one-line prompt, passes `check.py`, and a draft shows up in the studio.
