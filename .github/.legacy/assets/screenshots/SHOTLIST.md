# 📸 Screenshot Shot List

Static fallbacks for every demo beat, used only if backup *video* also fails (AV issues, no
audio output, etc.). Capture these ahead of time from real dry-run sessions. Naming convention:
`demoN-beatM-short-description.png`.

## Demo 1 — Skill (Model Mondays)
- [ ] `demo1-beat1-skills-library.png` — Skills library showing `mm-recap-blog` + `mm-news-highlights`
- [ ] `demo1-beat2-recap-draft.png` — Streaming recap draft in editor canvas
- [ ] `demo1-beat3-news-highlights-draft.png` — Draft News Highlights URL list
- [ ] `demo1-beat4-final-recap.png` — Final recap with embedded livestream + links

## Demo 2 — Workflow (Model Mondays)
- [ ] `demo2-beat1-automations-tab.png` — `mm-sunday-ops` workflow entry, cron schedule visible
- [ ] `demo2-beat2-workflow-prompt.png` — Workflow prompt detail view
- [ ] `demo2-beat3-run-log.png` — Session log streaming during "Run now"
- [ ] `demo2-beat4-rundown-issue.png` — Final GitHub issue with confirmed speaker/host/tech-check

## Demo 3 — Coding Agent (Model Releases)
- [ ] `demo3-beat1-github-issue.png` — Opened issue assigned to Copilot
- [ ] `demo3-beat2-session-planning.png` — Cloud session reading model card/docs
- [ ] `demo3-beat3-file-edits.png` — Session timeline scaffolding notebook/README
- [ ] `demo3-beat4-pr-diff.png` — Draft PR with notebook diff + rendered cells (**primary fallback image**)
- [ ] `demo3-beat5-review-fix.png` — Reviewer comment + Copilot's follow-up push

## Demo 4 — Fleet (Model Releases)
- [ ] `demo4-beat1-fleet-command.png` — Terminal canvas with fleet run command
- [ ] `demo4-beat2-six-sessions.png` — Sessions area, 6 sibling sessions in-progress (**primary fallback image**)
- [ ] `demo4-beat3-side-by-side.png` — Two sessions compared, one flagging an issue
- [ ] `demo4-beat4-pr-list.png` — PR list: 5 green + 1 `needs-human` (**primary fallback image**)

## Demo 5 — Agentic DevOps (Model Mastery)
- [ ] `demo5-beat1-red-ci.png` — Failing CI badge on `model-mastery` (**primary fallback image, "before"**)
- [ ] `demo5-beat2-session-triage.png` — Session triggered by CI webhook, reading logs
- [ ] `demo5-beat3-fix-pr.png` — Draft PR: model swap + doc update + benchmark refresh
- [ ] `demo5-beat4-preview-rebuilt.png` — Preview canvas, corrected lab page (**primary fallback image, "after"**)

## Supporting / non-demo shots
- [ ] `pipeline-diagram-rendered.png` — Static export of the OUTLINE.md mermaid diagram, for
      slides where live markdown rendering isn't available
- [ ] `lucy-original-still.png` — I Love Lucy chocolate factory scene (rights-cleared still or
      licensed clip only — do not use unlicensed footage)

---

**Storage:** commit exported PNGs directly into this folder once captured, matching the file
names above. Reference them from FALLBACK-PLAN.md and presentation slides by relative path
(`assets/screenshots/<name>.png`).
