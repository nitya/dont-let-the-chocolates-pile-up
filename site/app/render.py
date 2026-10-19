"""Safe Markdown -> HTML rendering."""

from __future__ import annotations

import re

import nh3
from markdown_it import MarkdownIt

_OPTS = {"html": True, "linkify": False, "typographer": True}
_md = MarkdownIt("commonmark", _OPTS).enable(["table", "strikethrough"])
# Agent drafts (social posts especially) rely on single newlines being line breaks.
_md_breaks = MarkdownIt("commonmark", {**_OPTS, "breaks": True}).enable(["table", "strikethrough"])

_TAGS = set(nh3.ALLOWED_TAGS) | {"img", "details", "summary", "figure", "figcaption", "mark", "kbd"}
_ATTRS = {k: set(v) for k, v in nh3.ALLOWED_ATTRIBUTES.items()}
_ATTRS.setdefault("img", set()).update({"src", "alt", "title", "width", "height", "loading"})
_ATTRS.setdefault("a", set()).update({"href", "title"})
_ATTRS.setdefault("th", set()).add("align")
_ATTRS.setdefault("td", set()).add("align")

_BANNER_RE = re.compile(r"""(\(|["'])(?:\.\./)+banners/""")
_IMPORT_COMMENT_RE = re.compile(r"^\s*<!--.*?-->\s*", re.S)


def rewrite_banners(markdown: str) -> str:
    return _BANNER_RE.sub(r"\1/banners/", markdown)


def render_markdown(markdown: str | None, breaks: bool = True) -> str:
    if not markdown:
        return ""
    html = (_md_breaks if breaks else _md).render(rewrite_banners(markdown))
    return nh3.clean(html, tags=_TAGS, attributes=_ATTRS, url_schemes={"http", "https", "mailto"}, link_rel="noopener noreferrer")


def render_archive(markdown: str | None) -> str:
    return render_markdown(_IMPORT_COMMENT_RE.sub("", markdown or "", count=1), breaks=False)
