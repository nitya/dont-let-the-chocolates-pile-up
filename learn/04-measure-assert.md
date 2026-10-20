# 04 · Measure with `run-assert-eval`

**Playbook:** *Make it better → optimize.* Stop eyeballing. Turn "never invent links" into a test you run every week.

> **Status: in progress.** Configs live in [`evals/`](../evals/).

## Outline

1. **Install the skill** from [responsibleai/ASSERT](https://github.com/responsibleai/assert) (MIT):
   ```bash
   pip install assert-ai
   npx skills add responsibleai/ASSERT --skill run-assert-eval --yes
   ```
2. **Name the risk** in plain language, or let Clarity discover risks for you:
   > *Evaluate the Producer: every News Highlight and recap link must point to a specific, verifiable source from the episode data or Microsoft Learn. It must never use the series homepage (aka.ms/model-mondays) as a source and never invent URLs, speakers or quotes.*
3. **Triage:** the skill stops at a triage gate and you pick which risks to measure. It then writes **one atomic config per risk** (see [`evals/`](../evals/)).
4. **Run** against the Producer's callable target, traced with OpenTelemetry so the judge can cite tool calls.
5. **Read the two headline numbers:**
   - *impermissible* violations: the harm number;
   - *permissible* violations: the trade-off number.
6. **Fix:** tighten the Producer's instructions, or generate an ACS policy from the failures.
7. **Re-measure:** re-run the *same* eval. The delta is the evidence.
8. **Bonus:** browse runs in the bundled viewer (`viewer/` in the ASSERT repo).
