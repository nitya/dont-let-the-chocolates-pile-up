"""Deterministic draft builders for --mock mode (framework-free).

Every builder turns *real* episode data returned by the site's MCP tools into a plausible draft, clearly labeled
"[mock]", that follows the same rules as the LLM specialists: only facts from the data, no invented speakers or quotes,
no placeholder links, and every cited URL listed in `sources`.
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from typing import Any

from .rules import MOCK_TAG, episode_label, is_placeholder

MOCK_BANNER = (
    f"> **{MOCK_TAG}** Drafted by Emcee in mock mode (no LLM): assembled deterministically from real Model Mondays "
    "data so the agent flow can be demoed end to end. Review it like any other draft."
)
COMMUNITY = {
    "Model Mondays repo": "https://github.com/microsoft/model-mondays",
    "Newsletter": "https://aka.ms/model-mondays/newsletter",
    "Discord": "https://aka.ms/model-mondays/discord",
}


@dataclass
class Draft:
    kind: str
    title: str
    content_markdown: str
    sources: list[str] = field(default_factory=list)
    content_html: str | None = None

    def as_args(self, episode_id: str, author_agent: str) -> dict[str, Any]:
        args: dict[str, Any] = {
            "episode_id": episode_id,
            "kind": self.kind,
            "title": self.title,
            "content_markdown": self.content_markdown,
            "author_agent": author_agent,
            "sources": self.sources,
        }
        if self.content_html:
            args["content_html"] = self.content_html
        return args


# --------------------------------------------------------------------------------------------- helpers


def _dedupe(items: list[str]) -> list[str]:
    out: list[str] = []
    for i in items:
        if i and i not in out and not is_placeholder(i):
            out.append(i)
    return out


def recording_url(ep: dict) -> str:
    yt = ep.get("youtube") or {}
    return yt.get("url") or (ep.get("links") or {}).get("recording") or ""


def is_aired(ep: dict) -> bool:
    yt = ep.get("youtube") or {}
    return ep.get("display_status", ep.get("status")) == "completed" or bool(yt.get("durationSec"))


def page_url(site: str, episode_id: str) -> str:
    return f"{site.rstrip('/')}/episodes/{episode_id}"


def source_page(ep: dict) -> str:
    return ((ep.get("source") or {}).get("page")) or ""


def data_page(ep: dict) -> str:
    return f"data/{ep['page']}" if ep.get("page") else ""


def nice_date(ep: dict) -> str:
    try:
        d = dt.date.fromisoformat(ep.get("date", ""))
    except ValueError:
        return ep.get("date", "date TBC")
    return f"{d:%A}, {d:%B} {d.day}, {d.year}"


def short_date(ep: dict) -> str:
    try:
        d = dt.date.fromisoformat(ep.get("date", ""))
    except ValueError:
        return ep.get("date", "")
    return f"{d:%b} {d.day}"


def speakers_text(ep: dict) -> str:
    return ", ".join(ep.get("speakers") or []) or "guests (names not in the data yet; confirm with the host)"


def minutes(ep: dict) -> int | None:
    sec = (ep.get("youtube") or {}).get("durationSec") or 0
    return round(sec / 60) if sec else None


def chapter_url(ep: dict, seconds: int) -> str:
    url = recording_url(ep)
    if not url:
        return ""
    return f"{url}{'&' if '?' in url else '?'}t={int(seconds)}s"


def stamp(seconds: int) -> str:
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}"


def sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", (text or "").replace("\n", " ").strip())
    return [p.strip() for p in parts if len(p.strip()) > 20]


def facts(ep: dict) -> list[str]:
    """Description sentences that state something (drops 'Join us…' style invitations)."""
    invite = re.compile(r"^(join us|tune in|don't miss|register|watch live)", re.I)
    return [s for s in sentences(ep.get("description", "")) if not invite.search(s)]


def content_chapters(ep: dict) -> list[dict]:
    """Chapters minus the boilerplate intro/welcome/wrap-up segments."""
    skip = re.compile(r"introduction|code of conduct|welcome|wrap-?up|closing", re.I)
    return [c for c in ep.get("chapters") or [] if not skip.search(c.get("title", ""))]


def topic_query(ep: dict) -> str:
    title = re.sub(r"\b(spotlight on|model mondays|episode)\b", "", ep.get("title", ""), flags=re.I)
    generic = {"models", "model", "ai", "on", "the", "with", "and", "for", "in", "of", "a", "an", "to", "hands",
               "new", "your", "using", "build", "building"}
    words = [w for w in re.findall(r"[A-Za-z0-9][\w.+-]*", title) if w.lower() not in generic]
    return " ".join(words[:6]) or ep.get("title", "")


def learn_query(ep: dict) -> str:
    return f"{topic_query(ep)} models in Microsoft Foundry"


def notes_block(lines: list[str]) -> str:
    return "## Notes for reviewer\n\n" + "\n".join(f"- {line}" for line in lines) + "\n"


def sources_block(labelled: list[tuple[str, str]]) -> str:
    seen: set[str] = set()
    rows = []
    for label, url in labelled:
        if url and url not in seen and not is_placeholder(url):
            seen.add(url)
            rows.append(f"- {label}: {url}")
    return "## Sources\n\n" + "\n".join(rows) + "\n"


# --------------------------------------------------------------------------------------------- coordinator


def brief(ep: dict, related: list[dict], site: str) -> Draft:
    label = episode_label(ep["id"])
    rec = recording_url(ep)
    lines = [
        f"# {MOCK_TAG} Guest brief: {label} · {ep['title']}",
        "",
        MOCK_BANNER,
        "",
        "## At a glance",
        "",
        "| | |",
        "|---|---|",
        f"| **Date** | {nice_date(ep)} · {ep.get('time') or 'time TBC'} |",
        f"| **Host** | {ep.get('host') or 'not in the data'} |",
        f"| **Guests** | {speakers_text(ep)} |",
        f"| **Livestream** | {rec or 'no livestream link in the data yet'} |",
        f"| **Episode page** | {page_url(site, ep['id'])} |",
        "",
        "## What the episode is about",
        "",
        ep.get("description") or "_No description in the data yet._",
        "",
        "## Talking points (from the episode description)",
        "",
    ]
    lines += [f"- {s}" for s in sentences(ep.get("description", ""))[:4]] or ["- _Description pending._"]
    lines += ["", "## Related past episodes (callbacks and context)", ""]
    if related:
        for r in related[:4]:
            link = r.get("video_url") or ""
            name = f"{episode_label(r['id'])} · {r['title']}"
            lines.append(f"- {'[' + name + '](' + link + ')' if link else name} ({r.get('date', '')}, "
                         f"{r.get('views') or 0} views)")
    else:
        lines.append("- None found by search_episodes.")
    lines += [
        "",
        "## Suggested questions for the guests",
        "",
        "_Suggestions for the host, phrased from the description; not facts from the data._",
        "",
        f"- What does a developer get from \"{ep['title']}\" that they couldn't do before?",
        "- How do you decide whether this is the right model for an agent, and how do you evaluate it?",
        "- What should viewers try first after the stream, and where should they start?",
        "",
        "## Prep checklist",
        "",
        "- [ ] Confirm guest names, titles and pronouns (not in the data yet)." if not ep.get("speakers")
        else "- [ ] Confirm guest titles and pronouns.",
        "- [ ] Collect the demo link(s) and the docs the guests will show.",
        "- [ ] Agree the News Highlights items for this week.",
        "",
    ]
    sources = _dedupe([source_page(ep), data_page(ep), rec, *[r.get("video_url", "") for r in related[:4]]])
    lines.append(sources_block([("Episode page (microsoft/model-mondays)", source_page(ep)),
                                ("Episode data", data_page(ep)), ("Livestream", rec)]
                               + [(f"Related: {episode_label(r['id'])}", r.get("video_url", "")) for r in related[:4]]))
    notes = ["Guests are not listed in the data: add them before sharing the brief." if not ep.get("speakers")
             else "Guest names come from the episode data.",
             "Related episodes were picked by keyword search; drop any that aren't a good callback."]
    lines.append(notes_block(notes))
    return Draft("brief", f"{MOCK_TAG} Guest brief: {label} {ep['title']}", "\n".join(lines), sources)


SEGMENT_RULES = [
    (re.compile(r"introduction|code of conduct", re.I), "Introduction and Code of Conduct", "host"),
    (re.compile(r"welcome|overview of the show|model mondays:", re.I), "Welcome and overview", "host"),
    (re.compile(r"news", re.I), "Weekly News Highlights", "host"),
    (re.compile(r"demo", re.I), "Live demo", "guests"),
    (re.compile(r"q&a|questions|use cases", re.I), "Use cases and audience Q&A", "host + guests"),
    (re.compile(r"wrap|next episode|closing", re.I), "Wrap-up and next episode", "host"),
]


def run_of_show(ep: dict, reference: dict | None, next_ep: dict | None) -> Draft:
    label = episode_label(ep["id"])
    host = ep.get("host") or "host"
    rows: list[tuple[str, str, str, str]] = []
    ref_chapters = (reference or {}).get("chapters") or []
    if ref_chapters:
        spotlight_n = 0
        for c in ref_chapters:
            segment, owner = None, None
            for rx, name, who in SEGMENT_RULES:
                if rx.search(c.get("title", "")):
                    segment, owner = name, who
                    break
            if segment is None:
                spotlight_n += 1
                segment, owner = f"Spotlight {spotlight_n}: {ep['title']}", "guests"
            if segment == "Live demo":
                segment = f"Live demo: {ep['title']}"
            note = f"format from {episode_label(reference['id'])} @ {c.get('label', '')}"
            rows.append((stamp(c.get("seconds", 0)), segment, owner.replace("host", host), note))
    else:
        defaults = [(0, "Introduction and Code of Conduct", host), (60, "Welcome and overview", host),
                    (120, "Weekly News Highlights", host), (480, f"Spotlight: {ep['title']}", "guests"),
                    (900, f"Live demo: {ep['title']}", "guests"), (2700, "Audience Q&A", f"{host} + guests"),
                    (3300, "Wrap-up and next episode", host)]
        rows = [(stamp(s), name, who, "default series format") for s, name, who in defaults]
    lines = [
        f"# {MOCK_TAG} Run of show: {label} · {ep['title']}",
        "",
        MOCK_BANNER,
        "",
        f"**{nice_date(ep)} · {ep.get('time') or 'time TBC'}** · Host: {host} · Guests: {speakers_text(ep)}",
        "",
        "| Start | Segment | Owner | Notes |",
        "|---|---|---|---|",
    ]
    lines += [f"| {t} | {seg} | {who} | {note} |" for t, seg, who, note in rows]
    lines.append("")
    if next_ep:
        lines += [f"**Next episode to announce in the wrap-up:** {episode_label(next_ep['id'])} · {next_ep['title']} "
                  f"({next_ep.get('date', '')}, host {next_ep.get('host') or 'TBC'}).", ""]
    if reference:
        mins = minutes(reference)
        lines += [f"Timings follow the structure of {episode_label(reference['id'])} ({reference['title']}"
                  f"{f', {mins} min' if mins else ''}), the most recent aired episode with chapters.", ""]
    sources = _dedupe([source_page(ep), data_page(ep), recording_url(ep),
                       recording_url(reference) if reference else ""])
    lines.append(sources_block([("Episode page (microsoft/model-mondays)", source_page(ep)),
                                ("Episode data", data_page(ep)), ("Livestream", recording_url(ep))]
                               + ([(f"Format reference {episode_label(reference['id'])}", recording_url(reference))]
                                  if reference else [])))
    lines.append(notes_block(["Segment timings are borrowed from the reference episode; adjust to the guests' plan.",
                              "Guest owners are TBC until names are confirmed." if not ep.get("speakers")
                              else "Owners use the guest names from the data."]))
    return Draft("run_of_show", f"{MOCK_TAG} Run of show: {label} {ep['title']}", "\n".join(lines), sources)


# --------------------------------------------------------------------------------------------- producer


def recap(ep: dict, transcript_available: bool) -> Draft:
    label = episode_label(ep["id"])
    rec = recording_url(ep)
    chapters = content_chapters(ep)
    grounding = "transcript" if transcript_available else "description+chapters"
    title = f"{MOCK_TAG} Recap: {ep['title']}"
    lines = [
        f"# {title}",
        "",
        MOCK_BANNER,
        "",
        f"In {label} of Model Mondays, host {ep.get('host') or 'the host'} and "
        f"{', '.join(ep.get('speakers') or []) or 'guests'} covered **{ep['title']}**. "
        + (sentences(ep.get("description", ""))[0] if sentences(ep.get("description", "")) else ""),
        "",
        "## What we covered",
        "",
    ]
    if chapters:
        lines += [f"- **[{c['title']}]({chapter_url(ep, c['seconds'])})** (at {c.get('label', '')})" for c in chapters]
    else:
        lines += [f"- {s}" for s in sentences(ep.get("description", ""))[:4]]
    lines += ["", "## Key takeaways", ""]
    takeaways = facts(ep)[:3]
    lines += [f"{i}. {s}" for i, s in enumerate(takeaways, 1)] or ["1. See the replay for details."]
    demo = next((c for c in chapters if re.search(r"demo", c["title"], re.I)), None)
    lines += ["", "## Try it yourself", ""]
    if demo:
        lines.append(f"- Rewatch the [live demo]({chapter_url(ep, demo['seconds'])}) and follow along.")
    for h in (ep.get("highlights") or [])[:2]:
        if h.get("url") and not is_placeholder(h["url"]):
            lines.append(f"- {h.get('title')}: {h['url']}")
    lines.append(f"- Explore past episodes and resources: {COMMUNITY['Model Mondays repo']}")
    mins = minutes(ep)
    lines += ["", "## Watch the replay", "",
              f"<{rec}>{f' · {mins} min' if mins else ''} · Hosted by {ep.get('host') or 'the Model Mondays team'}", ""]
    chapter_sources = [chapter_url(ep, c["seconds"]) for c in chapters]
    sources = _dedupe([rec, *chapter_sources, source_page(ep), data_page(ep),
                       *[h.get("url", "") for h in (ep.get("highlights") or [])[:2]], COMMUNITY["Model Mondays repo"]])
    lines.append(sources_block([("Episode recording (YouTube)", rec), ("Episode page", source_page(ep)),
                                ("Episode data", data_page(ep)),
                                ("Chapter timestamps from the video description", rec)]))
    notes = [f"**Grounding:** {grounding}. "
             + ("" if transcript_available else "No transcript yet, so there are no quotes, numbers or specific "
                "announcements. Regenerate once the transcript lands."),
             "**Speakers:** guest names aren't in the data; add them before publishing." if not ep.get("speakers")
             else f"**Speakers:** {', '.join(ep['speakers'])} (from the data).",
             "**Mock mode:** takeaways are sentences from the episode description, not a summary of the stream."]
    lines.append(notes_block(notes))
    front = "\n".join(["---", f"episode: {ep['id']}", "kind: recap", f'title: "{title}"',
                       "generated_by: emcee/producer (mock)", f"grounding: {grounding}", "sources:",
                       *[f"  - {s}" for s in sources], "---", ""])
    return Draft("recap", title, front + "\n".join(lines), sources)


def highlights(ep: dict, transcript_available: bool) -> Draft:
    label = episode_label(ep["id"])
    rec = recording_url(ep)
    chapters = content_chapters(ep)[:6]
    title = f"{MOCK_TAG} {label} highlights: where to jump in"
    lines = [f"# {title}", "", MOCK_BANNER, ""]
    if chapters:
        for i, c in enumerate(chapters, 1):
            extra = " *(Individual news items need the transcript.)*" if re.search(r"news", c["title"], re.I) else ""
            lines.append(f"{i}. **[{stamp(c['seconds'])}: {c['title']}]({chapter_url(ep, c['seconds'])})**{extra}")
    else:
        lines.append(f"1. **[Full replay]({rec})**: chapters aren't in the video description yet.")
    for h in (ep.get("highlights") or [])[:3]:
        if h.get("url") and not is_placeholder(h["url"]):
            lines.append(f"- News: [{h.get('title')}]({h['url']})")
    lines.append("")
    sources = _dedupe([*[chapter_url(ep, c["seconds"]) for c in chapters], rec,
                       *[h.get("url", "") for h in (ep.get("highlights") or [])[:3]]])
    lines.append(sources_block([("Chapter timestamps from the episode's YouTube description", rec)]))
    lines.append(notes_block(["Without the transcript the News Highlights item can't list specific announcements."
                              if not transcript_available else "Transcript available: extract news items from it."]))
    return Draft("highlights", title, "\n".join(lines), sources)


# --------------------------------------------------------------------------------------------- presenter


def _learn_docs(docs: list[dict], limit: int = 3) -> list[dict]:
    out, seen = [], set()
    # Prefer current public-cloud docs over sovereign-cloud and "classic" pages that search often ranks first.
    docs = sorted(docs, key=lambda d: bool(re.search(r"sovereign|-classic|/previous-versions/",
                                                     d.get("contentUrl") or d.get("url") or "")))
    for d in docs:
        url = (d.get("contentUrl") or d.get("url") or "").split("#")[0]
        if url and url not in seen and "learn.microsoft.com" in url:
            seen.add(url)
            out.append({"title": d.get("title") or url, "url": url, "content": d.get("content") or ""})
        if len(out) >= limit:
            break
    return out


def _first_line(text: str, words: int = 18) -> str:
    for line in (text or "").splitlines():
        if line.lstrip().startswith(("#", "|", "-", "*", ">", "!")):
            continue
        line = re.sub(r"[*`>|]", "", line).strip()
        if len(line.split()) >= 6:
            return " ".join(line.split()[:words]) + ("…" if len(line.split()) > words else "")
    return "See the Learn page for details."


def _words(text: str, n: int) -> str:
    words = text.split()
    return " ".join(words[:n]) + ("…" if len(words) > n else "")


def deck(ep: dict, docs: list[dict], next_ep: dict | None, related: list[dict] | None = None) -> Draft:
    label = episode_label(ep["id"])
    n_season, n_ep = ep.get("season"), ep.get("episode")
    rec = recording_url(ep)
    learn = _learn_docs(docs)
    desc = sentences(ep.get("description", ""))
    host = ep.get("host") or "the Model Mondays team"
    notes = [
        "REVIEWER NOTES (generated by emcee/presenter in mock mode, delete before presenting)",
        "- [mock] Built without an LLM from the episode data"
        + (" and the top Microsoft Learn search results." if learn else "; Learn MCP wasn't available."),
        "- Learn pages were picked by search rank: check each one is relevant before presenting." if learn else
        "- Add 2-4 Learn pages for the concept slides.",
        "- Guest names aren't in the data; add them from the banner." if not ep.get("speakers") else
        f"- Guests from data: {', '.join(ep['speakers'])}.",
    ]
    slides = [
        "\n".join([
            "---", "marp: true", "theme: chocolate", "size: 16:9", f'title: "{MOCK_TAG} Model Mondays {label}: {ep["title"]}"',
            "---", "", "<!-- _class: title -->", "", '<div class="text">', "",
            f"###### Model Mondays · {label}", "", f"# {ep['title']}", "",
            f'<p class="subtitle">{desc[0] if desc else ""}</p>', "",
            f'<p class="byline">Hosted by {host} &nbsp;|&nbsp; {nice_date(ep)}</p>', "", "</div>",
            f'<div class="hero wide"><img src="../../data/banners/S{n_season}-E{n_ep}.webp" alt="Model Mondays {label} banner"></div>',
            "", "<!--", *notes, "-->",
        ]),
        "\n".join([
            "###### Why it matters", "", f"# {ep['title']}", "", '<div class="grid cols-3">',
            *[f'<div class="card"><span class="badge sm"><img src="../assets/icons/{icon}.svg"></span><h4>{head}</h4>'
              f'<p>{_words(s, 24)}</p></div>'
              for (icon, head), s in zip([("sparkles", "The topic"), ("layers", "The episode"), ("gauge", "The goal")],
                                         (desc + ["", "", ""])[:3]) if s],
            "</div>", "", "<!--", f"Source: episode description ({data_page(ep)}).", "-->",
        ]),
    ]
    for d in learn:
        slides.append("\n".join([
            "###### From Microsoft Learn", "", f"# {d['title'][:70]}", "",
            f'<div class="callout">{_first_line(d["content"])}</div>', "",
            f'<p class="footnote">Source: {d["url"]}</p>', "", "<!--", f"Source: Learn: {d['url']}", "-->",
        ]))
    related = [r for r in (related or []) if r.get("id") != ep["id"] and r.get("video_url")][:3]
    if related:
        slides.append("\n".join([
            "###### Catch up first", "", "# Earlier on Model Mondays", "", f'<div class="grid cols-{len(related)}">',
            *[f'<div class="card"><h4>{episode_label(r["id"])}</h4><p><a href="{r["video_url"]}">{r["title"]}</a></p>'
              f'</div>' for r in related],
            "</div>", "", "<!--", "Source: search_episodes on the Model Mondays site (related past episodes).", "-->",
        ]))
    demo = next((c for c in content_chapters(ep) if re.search(r"demo", c["title"], re.I)), None)
    slides.append("\n".join([
        "<!-- _class: demo -->", "", "###### Live segment", "", f"# {demo['title'] if demo else ep['title']}", "",
        '<div class="grid">', '<div class="card">', "<h3>What you'll see</h3>", "<ol>",
        *[f"<li>{_words(s, 14)}</li>" for s in desc[:3]], "</ol>", "</div>",
        '<div class="video"><div class="play"><span></span></div>Live demo<div class="cmd">aka.ms/model-mondays/discord · ask questions live</div></div>',
        "</div>",
    ]))
    res_learn = [f'<li><a href="{d["url"]}">{d["title"][:60]}</a></li>' for d in learn] or ["<li>Learn links TBC</li>"]
    slides.append("\n".join([
        "###### Resources", "", "# Keep going after the stream", "", '<div class="grid cols-2">',
        '<div class="card">', "<h4>Microsoft Learn</h4>", '<ul class="small">', *res_learn, "</ul>", "</div>",
        '<div class="card peach">', "<h4>This episode</h4>", '<ul class="small">',
        *([f'<li><a href="{rec}">Livestream + replay</a></li>'] if rec else []),
        *[f'<li><a href="{u}">{k}</a></li>' for k, u in COMMUNITY.items()], "</ul>", "</div>", "</div>", "",
        f'<p class="small muted mt"><strong>Sources:</strong> episode data: {data_page(ep)} · Learn pages listed above</p>',
    ]))
    if next_ep:
        slides.append("\n".join([
            "<!-- _class: dark -->", "", f"###### Up next · {nice_date(next_ep)}", "",
            f"# {episode_label(next_ep['id'])}: {next_ep['title']}", "",
            f'<p class="lede">Hosted by {next_ep.get("host") or "TBC"} · Join live, and bring your questions to the Discord.</p>',
        ]))
    else:
        slides.append("\n".join([
            "<!-- _class: dark -->", "", "###### Thanks for watching", "", "# Stay in the loop", "",
            f'<p class="lede">Newsletter: {COMMUNITY["Newsletter"]} · Discord: {COMMUNITY["Discord"]}</p>',
        ]))
    markdown = "\n\n---\n\n".join(slides) + "\n"
    sources = _dedupe([data_page(ep), source_page(ep), rec, *[d["url"] for d in learn],
                       *[r["video_url"] for r in related], *COMMUNITY.values()])
    return Draft("deck", f"{MOCK_TAG} Deck: {label} {ep['title']}", markdown, sources)


# --------------------------------------------------------------------------------------------- publisher


def announcement(ep: dict, site: str, drafts: list[dict]) -> Draft:
    label = episode_label(ep["id"])
    rec = recording_url(ep)
    page = page_url(site, ep["id"])
    desc = sentences(ep.get("description", ""))
    lines = [
        f"# {MOCK_TAG} Announcing {label}: {ep['title']}",
        "",
        MOCK_BANNER,
        "",
        f"**{nice_date(ep)} · {ep.get('time') or 'time TBC'}** · Hosted by {ep.get('host') or 'the Model Mondays team'}",
        "",
        *desc[:2],
        "",
        f"- ▶️ Watch live (and the replay afterwards): {rec}" if rec else "- ▶️ Livestream link coming soon.",
        f"- 📄 Episode page: {page}",
        f"- 💬 Bring your questions to the Discord: {COMMUNITY['Discord']}",
        f"- 📰 Get the recap in the newsletter: {COMMUNITY['Newsletter']}",
        "",
    ]
    sources = _dedupe([page, rec, source_page(ep), data_page(ep)])
    lines.append(sources_block([("Episode page (site)", page), ("Livestream", rec),
                                ("Episode page (microsoft/model-mondays)", source_page(ep))]))
    pending = [d for d in drafts if d.get("kind") in ("brief", "run_of_show", "deck")]
    lines.append(notes_block(["Guests aren't named in the data; add them before posting." if not ep.get("speakers")
                              else "Guest names come from the data.",
                              f"Related drafts in the queue for this episode: {', '.join(d['id'] for d in pending)}"
                              if pending else "No brief/run-of-show/deck drafts in the queue yet."]))
    return Draft("announcement", f"{MOCK_TAG} Announcement: {label} {ep['title']}", "\n".join(lines), sources)


def social(ep: dict, site: str, after_show: bool, drafts: list[dict]) -> Draft:
    label = episode_label(ep["id"])
    rec = recording_url(ep)
    page = page_url(site, ep["id"])
    link = rec or page
    desc = sentences(ep.get("description", ""))
    hook = desc[0] if desc else ep["title"]
    if after_show:
        demo = next((c for c in content_chapters(ep) if re.search(r"demo", c["title"], re.I)), None)
        x_post = f"Missed #ModelMondays {label}? Catch the replay of “{ep['title']}”. {link}"
        linkedin = [
            f"Replay is up: **{ep['title']}** ({label}) 🎬",
            "",
            hook,
            "",
            *([f"⏩ Jump straight to the live demo: {chapter_url(ep, demo['seconds'])}"] if demo else []),
            f"▶️ Full replay: {link}",
            f"📄 Episode page: {page}",
            "",
            "#ModelMondays #MicrosoftFoundry #AI",
        ]
    else:
        x_post = f"{short_date(ep)} on #ModelMondays: {ep['title']} with {ep.get('host') or 'the team'}. {link}"
        linkedin = [
            f"Next on #ModelMondays: **{ep['title']}** ({label})",
            "",
            hook,
            "",
            f"📅 {nice_date(ep)} · {ep.get('time') or 'time TBC'}",
            f"▶️ {link}",
            f"📄 {page}",
            "",
            "#ModelMondays #MicrosoftFoundry #AI",
        ]
    lines = [
        f"# {MOCK_TAG} Social posts: {label} ({'replay' if after_show else 'save the date'})",
        "",
        MOCK_BANNER,
        "",
        "## X / Bluesky",
        "",
        x_post if len(x_post) <= 280 else x_post[:270] + "… " + link,
        "",
        "## LinkedIn",
        "",
        *linkedin,
        "",
    ]
    sources = _dedupe([link, page, source_page(ep)])
    lines.append(sources_block([("Recording / livestream", rec), ("Episode page (site)", page)]))
    recap_ids = [d["id"] for d in drafts if d.get("kind") in ("recap", "highlights")]
    lines.append(notes_block([
        "Every post links to the episode page or the recording; no placeholder links.",
        f"Recap/highlights drafts to cross-link once approved: {', '.join(recap_ids)}" if recap_ids
        else "No recap/highlights draft found to cross-link yet." if after_show else "Schedule for the morning of the show.",
    ]))
    return Draft("social", f"{MOCK_TAG} Social: {label} {'replay' if after_show else 'save the date'}",
                 "\n".join(lines), sources)
