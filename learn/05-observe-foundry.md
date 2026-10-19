# 05 · Observe + optimize with `microsoft-foundry`

**Playbook:** *Make it better → optimize*, once the crew runs on Foundry.

> **Status: in progress.** Requires lab 06's hosted deployment, or any agent deployed to a Foundry project.

## Outline

1. **Install the skill** from [microsoft/azure-skills](https://github.com/microsoft/azure-skills) (MIT) and run its dependency check.
2. **Ask Copilot:** *"Evaluate my Emcee agent."* The skill's **observe** sub-skill then:
   1. generates an evaluation suite (datasets + rubric evaluators) into `.foundry/`;
   2. runs an agent-target batch eval;
   3. clusters failures so you can pick a category.
3. **Optimize:** *"Optimize the Producer's instructions for the grounding failures."* It uses `prompt_optimize`, then redeploys after your sign-off.
4. **Compare versions** on the same suite, and keep the better one.
5. **Monitor:** enable continuous evaluation in production.
6. **Contrast with lab 04:**

   | | ASSERT | Foundry |
   |---|---|---|
   | Where | local-first | managed |
   | Scope | spec-driven, any model | runs at the platform level |
   | Good for | dev loop and CI | the production loop |

   Use both.
