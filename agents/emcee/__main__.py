"""CLI: python -m agents.emcee "prep S4-E12" [--mock] [--site URL] [--only coordinator,presenter]"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

from ._env import ensure_agents_env

ensure_agents_env("agents.emcee")

from . import SPECIALISTS  # noqa: E402
from .config import Settings  # noqa: E402
from .runner import print_report, run_emcee  # noqa: E402
from .trace import Printer  # noqa: E402

EXAMPLES = """examples:
  python -m agents.emcee "prep S4-E12" --mock
  python -m agents.emcee "wrap up S4-E09" --mock --only producer
  python -m agents.emcee "new episode announced: Spotlight on NVIDIA Models" --site https://<site>
  python -m agents.emcee --issue-file issue.md          # request = GitHub issue title + body
"""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="python -m agents.emcee", description="Emcee: the Model Mondays content-factory "
                                "orchestrator (Microsoft Agent Framework).", epilog=EXAMPLES,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("request", nargs="*", help='what to do, e.g. "prep S4-E12", "wrap up S4-E09", "prep next"')
    p.add_argument("--issue-file", type=Path, help="read the request from a file (e.g. a GitHub issue title + body)")
    p.add_argument("--mock", action="store_true", help="scripted agents, no LLM (real MCP calls, [mock] drafts)")
    p.add_argument("--site", help="Model Mondays site base URL (default $EMCEE_SITE_URL or http://localhost:8000)")
    p.add_argument("--only", help=f"comma-separated subset of specialists: {','.join(SPECIALISTS)}")
    p.add_argument("--no-learn", action="store_true", help="don't connect to the Microsoft Learn MCP server")
    p.add_argument("--dry-run", action="store_true", help="validate drafts with the guardrail but don't queue them")
    p.add_argument("--mock-delay", type=float, help="seconds of fake 'thinking' per mock model call (stage pacing)")
    p.add_argument("--mock-fault", choices=["placeholder"],
                   help="mock only: the publisher first cites a placeholder link so the guardrail can be shown")
    p.add_argument("--json-out", type=Path, help="write the run ledger as JSON")
    p.add_argument("--report-md", type=Path, help="write the run report as Markdown (e.g. for an issue comment)")
    p.add_argument("--no-color", action="store_true")
    p.add_argument("-q", "--quiet", action="store_true", help="only print the run report")
    p.add_argument("-v", "--verbose", action="store_true", help="also show every model call")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    request = " ".join(args.request).strip()
    if args.issue_file:
        request = (request + "\n" + args.issue_file.read_text(encoding="utf-8")).strip()
    if not request:
        print("emcee: give a request, e.g. \"prep S4-E12\" (see --help)", file=sys.stderr)
        return 2
    only = [s.strip().lower() for s in (args.only or "").split(",") if s.strip()]
    unknown = [s for s in only if s not in SPECIALISTS]
    if unknown:
        print(f"emcee: unknown specialist(s) {unknown}; choose from {', '.join(SPECIALISTS)}", file=sys.stderr)
        return 2
    settings = Settings.from_env(
        site_url=args.site, mock=True if args.mock else None, only=only or None,
        learn=False if args.no_learn else None, dry_run=True if args.dry_run else None,
        mock_delay=args.mock_delay, mock_fault=args.mock_fault, verbose=args.verbose or None,
    )
    printer = Printer(color=False if args.no_color else None, verbose=settings.verbose)
    quiet_printer = Printer(quiet=True) if args.quiet else printer
    result = asyncio.run(run_emcee(request, settings, quiet_printer))
    if result.final_text and not args.quiet:
        printer.write()
        printer.rule("Emcee says")
        printer.write(result.final_text)
    print_report(result, settings, printer)
    report = result.report_markdown(settings)
    if args.report_md:
        args.report_md.write_text(report, encoding="utf-8")
    if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write(report + "\n")
    if args.json_out:
        args.json_out.write_text(json.dumps({"request": request, "ok": result.ok, "error": result.error,
                                             "seconds": round(result.seconds, 2), **result.ledger.to_dict()},
                                            indent=2), encoding="utf-8")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
