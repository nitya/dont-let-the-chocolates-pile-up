# 🛟 Fallback Plans — Live Demo Arc

Every live demo can fail: flaky network, a slow model response, a tool that behaves differently
than rehearsal. This doc defines, per demo, what "failure" looks like, what to do the moment it
happens, and the exact line that gets the narration back on track — so a stall never turns into
dead air.

**General rule:** if a demo hasn't produced a visible result within **15 seconds of its
allotted time**, cut. Don't debug live. Don't apologize more than once. Move to the fallback,
land the same punchline the demo would have landed, and keep going.

---

## Demo 1 — Skill (Model Mondays / Launch)

- **Risk:** Skill invocation is slow to stream, or transcript URL fetch fails.
- **Live-network dependent?** Low — mostly local skill invocation, low risk.
- **Fallback:** Have a **pre-run output already saved** in the editor canvas as a second tab
  (`ep-42-recap-PREGENERATED.md`). Switch tabs instead of re-invoking.
- **Bridge line:** *"I ran this exact thing an hour ago so we're not waiting on the transcript
  service live — here's what it produced."*
- **Screenshot needed:** yes (see shot list below) — static fallback if even the pre-run tab
  fails to load.

## Demo 2 — Workflow (Model Mondays / Coordinate)

- **Risk:** Scheduled workflow "Run now" hangs waiting on mock calendar/speaker data source.
- **Live-network dependent?** Medium — depends on mocked external data being reachable.
- **Fallback:** Have a **screen recording of a previous successful run** (30-45 sec, silent,
  ready to play at 1.5x if needed to make time back).
- **Bridge line:** *"Let me switch to a run I captured earlier this week so you can see the full
  log — same workflow, same result."*
- **Screenshot needed:** yes — final GitHub issue output, in case even the recording can't play.

## Demo 3 — Coding Agent (Model Releases / Launch)

- **Risk:** Highest risk demo — cloud session spin-up, model card fetch, and PR creation all
  depend on live network + GitHub availability.
- **Live-network dependent?** High.
- **Fallback:** **Full backup video** of a complete successful run (2:00, matches budget exactly).
  Play from the point matching wherever the live attempt stalled.
- **Bridge line:** *"This one talks to a few live services, so let me switch to a run I captured
  yesterday — everything you're about to see is real output, just not live."*
- **Screenshot needed:** yes — final PR diff view, as an even-lower-bandwidth fallback if video
  playback itself fails (e.g., AV equipment issue).

## Demo 4 — Fleet (Model Releases / Yield)

- **Risk:** Second-highest risk — 6 parallel cloud sessions is the most infrastructure-heavy demo.
- **Live-network dependent?** High.
- **Fallback:** **Full backup video** (2:00). Same play-from-stall-point approach as Demo 3.
- **Bridge line:** *"Same deal — six live sessions is a lot to gamble on conference wifi, so
  here's a capture from a real run."*
- **Screenshot needed:** yes — Sessions area with 6 sibling sessions, and the final PR list
  (5 green + 1 flagged), as static fallback.

## Demo 5 — Agentic DevOps (Model Mastery / Update)

- **Risk:** CI-triggered session may take longer than 1.5 min budget to complete visibly.
- **Live-network dependent?** Medium.
- **Fallback:** Pre-stage the **PR already open** before the talk starts (created earlier that
  day), and narrate through the existing PR + preview canvas instead of triggering live.
- **Bridge line:** *"This one actually already ran — CI failed on this repo about an hour before
  the talk, right on schedule for me. Here's what it did."*
- **Screenshot needed:** yes — red CI badge (before) and rebuilt preview canvas (after).

---

## Day-of checklist (in addition to STORYBOARD.md pre-flight checklist)

- [ ] All 5 backup videos loaded locally on the presenting machine (not streamed) — network at
      venues is not to be trusted.
- [ ] All screenshots from the shot list exported and available offline (see
      `assets/screenshots/SHOTLIST.md`).
- [ ] Laptop presentation mode tested with the exact adapter/dongle being used at the venue.
- [ ] A visible timer (phone or watch) for self-pacing — use the 2-min buffer deliberately, not
      accidentally.
- [ ] One rehearsal run where every live demo is deliberately failed on purpose, to practice the
      bridge lines out loud.
