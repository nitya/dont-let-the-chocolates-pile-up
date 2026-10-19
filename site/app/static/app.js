// Live updates: poll /api/changes and re-render [data-live-region] blocks in place.
(() => {
  const body = document.body;

  // Chapter links seek the embedded player instead of leaving the page.
  document.addEventListener("click", (e) => {
    const link = e.target.closest("[data-seek]");
    const player = document.getElementById("yt-player");
    if (!link || !player) return;
    e.preventDefault();
    player.src = `https://www.youtube-nocookie.com/embed/${link.dataset.video}?start=${link.dataset.seek}&autoplay=1`;
    player.scrollIntoView({ behavior: "smooth", block: "center" });
  });

  const mode = body.dataset.live;
  if (!mode) return;
  const POLL_MS = 4000;
  const episodeId = body.dataset.episodeId || "";
  const labels = {
    recap: "Recap", highlights: "Highlights", brief: "Guest brief", run_of_show: "Run of show", social: "Social post",
    deck: "Deck", announcement: "Announcement", episode: "Episode proposal",
  };
  let since = body.dataset.since;
  let epoch = body.dataset.epoch;
  let dirty = false;

  function toast(title, text) {
    const box = document.getElementById("toasts");
    if (!box) return;
    const el = document.createElement("div");
    el.className = "toast";
    const strong = document.createElement("strong");
    strong.textContent = title;
    el.append(strong, document.createTextNode(text));
    box.append(el);
    setTimeout(() => { el.classList.add("out"); setTimeout(() => el.remove(), 450); }, 6000);
  }

  function announce(change) {
    const what = `${labels[change.kind] || change.kind} · ${change.title} (${(change.episode_id || "").toUpperCase()})`;
    if (mode === "studio") {
      if (change.status === "pending") toast(`New draft from ${change.author_agent}`, what);
      else toast(change.status === "approved" ? "Approved" : "Rejected", what);
    } else if (change.status === "approved") {
      toast("Fresh off the line", what);
    }
  }

  function typing() {
    const el = document.activeElement;
    return el && el.closest("[data-live-region]") && /^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName);
  }

  async function refreshRegions() {
    const res = await fetch(location.pathname + location.search, { headers: { Accept: "text/html" }, cache: "no-store" });
    if (!res.ok) return;
    const doc = new DOMParser().parseFromString(await res.text(), "text/html");
    document.querySelectorAll("[data-live-region]").forEach((region) => {
      const next = doc.getElementById(region.id);
      if (!next) return;
      const known = new Set([...region.querySelectorAll("[data-draft-id]")].map((el) => el.dataset.draftId));
      const notes = {};
      region.querySelectorAll("[data-draft-id] input[name=note]").forEach((input) => {
        if (input.value) notes[input.closest("[data-draft-id]").dataset.draftId] = input.value;
      });
      region.innerHTML = next.innerHTML;
      region.querySelectorAll("[data-draft-id]").forEach((el) => {
        if (!known.has(el.dataset.draftId)) el.classList.add("fresh");
        const input = el.querySelector("input[name=note]");
        if (input && notes[el.dataset.draftId]) input.value = notes[el.dataset.draftId];
      });
    });
  }

  async function poll() {
    try {
      const params = new URLSearchParams({ since });
      if (episodeId) params.set("episode_id", episodeId);
      const res = await fetch(`/api/changes?${params}`, { cache: "no-store" });
      if (res.ok) {
        const data = await res.json();
        if (epoch && data.epoch && data.epoch !== epoch) {
          location.reload(); // drafts store was reset
          return;
        }
        epoch = data.epoch || epoch;
        since = data.now || since;
        if (data.changes && data.changes.length) {
          data.changes.forEach(announce);
          dirty = true;
        }
      }
      if (dirty && !typing()) {
        dirty = false;
        await refreshRegions();
      }
    } catch (err) {
      // Network blips are expected (server reloads during the demo); just try again.
    } finally {
      setTimeout(poll, POLL_MS);
    }
  }

  setTimeout(poll, POLL_MS);
})();
