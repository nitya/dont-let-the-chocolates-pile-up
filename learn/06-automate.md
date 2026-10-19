# 06 · Automate the belt

**Playbook:** *Make it scale → automate.* Triggers instead of reminders; gates instead of heroics.

> **Status: in progress.** Infrastructure lands in `infra/` + `azure.yaml`.

## Outline

1. **Deploy the site** (App Service) **and the crew** (Foundry hosted agent) with `azd up`.
2. **Schedule it:** with the `microsoft-foundry` **routine** sub-skill, add:
   - a weekly trigger: "prep next episode" every Wednesday;
   - a GitHub-issue trigger: an issue labeled `emcee` runs Emcee.
3. **Fallback:** a GitHub Actions workflow on `issues: labeled` that runs the same CLI.
4. **CI eval gate:** [`responsibleai/assert-ai-action`](https://github.com/responsibleai/assert-ai-action) fails a PR if the crew's behavior regresses on the lab 04 evals.
5. **Production:** continuous evals from lab 05, with alerts.
6. **Keep labs fresh:** assign a GitHub issue to the Copilot coding agent when an SDK changes.
7. **End-to-end:**
   1. `gh issue create --title "S4-E12 announced" --label emcee`
   2. Drafts appear in the studio.
   3. Approve them.
   4. The page goes live.
