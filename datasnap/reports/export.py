"""Export summary reports to various file formats."""

from __future__ import annotations

import json
from pathlib import Path


def save_report(output_path: str, summary: dict, quality: dict | None) -> None:
    path = Path(output_path)
    suffix = path.suffix.lower()

    payload = {"summary": summary}
    if quality:
        payload["quality"] = quality

    if suffix == ".json":
        path.write_text(json.dumps(payload, indent=2, default=str))
    elif suffix == ".md":
        path.write_text(_to_markdown(summary, quality))
    else:
        raise ValueError(f"Unsupported output format '{suffix}'. Use .json or .md")


def _to_markdown(summary: dict, quality: dict | None) -> str:
    lines = [
        "# datasnap report",
        "",
        f"**Rows:** {summary['rows']:,}  **Columns:** {summary['columns']}  "
        f"**Missing overall:** {summary['total_missing_pct']}%",
        "",
        "## Column summary",
        "",
        "| Column | Type | Missing % | Stats |",
        "|--------|------|-----------|-------|",
    ]
    for c in summary["column_stats"]:
        extra = ""
        if c["type"] == "numeric":
            extra = f"mean={c.get('mean')}, max={c.get('max')}"
        elif c["type"] == "categorical":
            extra = f"{c.get('unique')} unique values"
        lines.append(f"| {c['name']} | {c['type']} | {c['missing_pct']}% | {extra} |")

    if quality:
        lines += [
            "",
            "## Quality",
            "",
            f"**Score:** {quality['quality_score']}/100",
            f"**Duplicate rows:** {quality['duplicate_rows']['count']}",
        ]

    return "\n".join(lines) + "\n"
