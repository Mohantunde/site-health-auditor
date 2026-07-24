from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .auditor import audit_site
from .config import ConfigError, load_sites
from .models import SiteResult
from .reporters import write_json_report, write_markdown_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit website availability and basic SEO health."
    )
    parser.add_argument(
        "--config",
        default="sites.yml",
        help="Path to the YAML configuration file (default: sites.yml).",
    )
    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Directory for generated reports (default: reports).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=15.0,
        help="Request timeout in seconds (default: 15).",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=5,
        help="Maximum concurrent website checks (default: 5).",
    )
    parser.add_argument(
        "--fail-on-error",
        action="store_true",
        help="Return exit code 1 if any site has a request error or bad status.",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    if args.timeout <= 0:
        print("Error: --timeout must be greater than zero.", file=sys.stderr)
        return 2

    if args.workers <= 0:
        print("Error: --workers must be greater than zero.", file=sys.stderr)
        return 2

    try:
        sites = load_sites(args.config)
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    results: list[SiteResult] = []

    with ThreadPoolExecutor(max_workers=min(args.workers, len(sites))) as executor:
        future_map = {
            executor.submit(
                audit_site,
                site["name"],
                site["url"],
                args.timeout,
            ): site
            for site in sites
        }

        for future in as_completed(future_map):
            site = future_map[future]
            try:
                result = future.result()
            except Exception as exc:
                result = SiteResult(
                    name=site["name"],
                    url=site["url"],
                    error=f"Worker error: {exc}",
                )

            results.append(result)
            status = result.status_code if result.status_code is not None else "ERR"
            print(f"[{status}] {result.name} - {result.error or result.final_url}")

    results.sort(key=lambda item: item.name.lower())

    output_dir = Path(args.output_dir)
    markdown_path = output_dir / "site-health-report.md"
    json_path = output_dir / "site-health-report.json"

    write_markdown_report(results, markdown_path)
    write_json_report(results, json_path)

    print(f"\nMarkdown report: {markdown_path}")
    print(f"JSON report:     {json_path}")

    has_failure = any(not item.healthy for item in results)
    return 1 if args.fail_on_error and has_failure else 0


def main() -> int:
    parser = build_parser()
    return run(parser.parse_args())
