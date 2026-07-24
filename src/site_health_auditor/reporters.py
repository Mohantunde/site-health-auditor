from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .models import SiteResult


def _yes_no(value: bool) -> str:
    return "Yes" if value else "No"


def _escape_table(value: str) -> str:
    return value.replace("|", r"\|").replace("\n", " ")


def write_json_report(results: list[SiteResult], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total": len(results),
            "healthy": sum(item.healthy for item in results),
            "errors": sum(bool(item.error) for item in results),
        },
        "results": [item.to_dict() for item in results],
    }
    output_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def write_markdown_report(results: list[SiteResult], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Website Health Report",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        f"- Sites checked: **{len(results)}**",
        f"- Healthy responses: **{sum(item.healthy for item in results)}**",
        f"- Sites with errors: **{sum(bool(item.error) for item in results)}**",
        "",
        "| Site | Status | Time | HTTPS | Title | Description | H1 | Canonical | Robots.txt | Sitemap |",
        "|---|---:|---:|:---:|:---:|:---:|---:|:---:|:---:|:---:|",
    ]

    for item in results:
        time_value = (
            f"{item.response_time_seconds:.2f}s"
            if item.response_time_seconds is not None
            else "—"
        )
        lines.append(
            "| {name} | {status} | {time} | {https} | {title} | {description} | "
            "{h1} | {canonical} | {robots} | {sitemap} |".format(
                name=_escape_table(item.name),
                status=item.status_code if item.status_code is not None else "—",
                time=time_value,
                https=_yes_no(item.uses_https),
                title=_yes_no(bool(item.title)),
                description=_yes_no(bool(item.meta_description)),
                h1=item.h1_count,
                canonical=_yes_no(bool(item.canonical_url)),
                robots=_yes_no(item.robots_txt_found),
                sitemap=_yes_no(item.sitemap_found),
            )
        )

    lines.extend(["", "## Details", ""])

    for item in results:
        lines.extend(
            [
                f"### {item.name}",
                "",
                f"- Requested URL: `{item.url}`",
                f"- Final URL: `{item.final_url or '—'}`",
                f"- Status: `{item.status_code if item.status_code is not None else '—'}`",
                f"- Response time: `{item.response_time_seconds if item.response_time_seconds is not None else '—'} seconds`",
                f"- Title ({item.title_length} characters): {item.title or 'Missing'}",
                f"- Meta description ({item.meta_description_length} characters): {item.meta_description or 'Missing'}",
                f"- H1 count: `{item.h1_count}`",
                f"- Canonical: `{item.canonical_url or 'Missing'}`",
                f"- Robots meta: `{item.robots_meta or 'Not specified'}`",
                f"- Sitemap: `{item.sitemap_url or 'Not found'}`",
                f"- Error: `{item.error or 'None'}`",
                "",
            ]
        )

    output_path.write_text("\n".join(lines), encoding="utf-8")
