"""Export reports to JSON and Markdown."""

from __future__ import annotations
from typing import Optional

import json
from pathlib import Path


def save_report(output_path: str, summary: dict, quality: Optional[dict]) -> None:
    path = Path(output_path)
    payload = {"summary": summary}
    if quality:
        payload["quality"] = quality

    suffix = path.suffix.lower()
    if suffix == ".json":
        path.write_text(json.dumps(payload, indent=2, default=str))
    elif suffix == ".md":
        path.write_text(_to_markdown(summary, quality))
    else:
        raise ValueError(f"Unsupported output format '{suffix}'. Use .json or .md")


def _to_markdown(summary: dict, quality: Optional[dict]) -> str:
    lines = [
        "# datasnap report",
        "",
        f"**Rows:** {summary['rows']:,} &nbsp; **Columns:** {summary['columns']} "
        f"&nbsp; **Missing overall:** {summary['total_missing_pct']}%",
        "",
        "## Columns",
        "",
        "| Column | Type | Missing% | Summary |",
        "|--------|------|----------|---------|",
    ]
    for c in summary["column_stats"]:
        summary_txt = ""
        if c["type"] == "numeric":
            summary_txt = f"mean={c.get('mean')}, max={c.get('max')}"
        elif c["type"] == "categorical":
            summary_txt = f"{c.get('unique')} unique"
        lines.append(f"| {c['name']} | {c['type']} | {c['missing_pct']}% | {summary_txt} |")

    if quality:
        lines += [
            "",
            "## Quality",
            "",
            f"**Score:** {quality['quality_score']}/100  ",
            f"**Duplicates:** {quality['duplicate_rows']['count']}  ",
        ]
        for o in quality.get("outliers", []):
            lines.append(f"**Outliers in `{o['column']}`:** {o['count']} rows  ")

    return "\n".join(lines) + "\n"
