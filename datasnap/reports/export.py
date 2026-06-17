"""Export full data profile reports to JSON and Markdown."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional


def save_report(
    output_path: str,
    summary: dict,
    quality: Optional[dict] = None,
    filename: Optional[str] = None,
) -> Path:
    """Save a data profile report to disk in JSON or Markdown format.

    Args:
        output_path: Destination path. Extension determines format (.json/.md).
        summary: Result from compute_summary().
        quality: Result from run_quality_checks(), optional.
        filename: Original source filename, included in the report header.

    Returns:
        Path object of the saved file.

    Raises:
        ValueError: If the output extension is not supported.
    """
    path = Path(output_path)
    suffix = path.suffix.lower()

    if suffix == ".json":
        content = _to_json(summary, quality, filename)
    elif suffix == ".md":
        content = _to_markdown(summary, quality, filename)
    else:
        raise ValueError(
            f"Unsupported output format '{suffix}'. Use .json or .md"
        )

    path.write_text(content, encoding="utf-8")
    return path


def _to_json(summary: dict, quality: Optional[dict], filename: Optional[str]) -> str:
    """Build a JSON report string."""
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_file": filename,
        "summary": summary,
    }
    if quality:
        payload["quality"] = quality
    return json.dumps(payload, indent=2, default=str)


def _to_markdown(summary: dict, quality: Optional[dict], filename: Optional[str]) -> str:
    """Build a Markdown report string."""
    lines = ["# datasnap report", ""]

    if filename:
        lines.append(f"**Source:** `{filename}`  ")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  ")
    lines.append(
        f"**Rows:** {summary['rows']:,}  **Columns:** {summary['columns']}  "
        f"**Missing overall:** {summary['total_missing_pct']}%"
    )
    lines.append("")

    if quality:
        lines += _quality_section(quality)

    lines += _columns_section(summary["column_stats"])

    return "\n".join(lines) + "\n"


def _quality_section(quality: dict) -> list:
    """Build the quality section of the Markdown report."""
    score = quality.get("quality_score", "—")
    grade = quality.get("quality_grade", "")
    lines = [
        "## Quality",
        "",
        f"**Score:** {score}/100 {f'({grade})' if grade else ''}  ",
        f"**Duplicate rows:** {quality['duplicate_rows']['count']} "
        f"({quality['duplicate_rows']['pct']}%)  ",
    ]

    if quality.get("outliers"):
        lines.append("")
        lines.append("**Outliers:**")
        lines.append("")
        lines.append("| Column | Count | % |")
        lines.append("|--------|-------|---|")
        for o in quality["outliers"]:
            lines.append(f"| {o['column']} | {o['count']} | {o['pct']}% |")

    if quality.get("constant_columns"):
        lines.append("")
        lines.append(f"**Constant columns:** {', '.join(quality['constant_columns'])}")

    lines.append("")
    return lines


def _columns_section(column_stats: list) -> list:
    """Build the per-column table section of the Markdown report."""
    lines = [
        "## Columns",
        "",
        "| # | Column | Type | Missing % | Summary |",
        "|---|--------|------|-----------|---------|",
    ]
    for i, c in enumerate(column_stats, 1):
        summary_txt = c.get("summary", "")
        lines.append(
            f"| {i} | {c['name']} | {c['type']} | {c['missing_pct']}% | {summary_txt} |"
        )
    lines.append("")
    return lines


def load_report(path: str) -> dict:
    """Load a previously saved JSON report from disk.

    Args:
        path: Path to a .json report file.

    Returns:
        The parsed report dict.

    Raises:
        ValueError: If the file is not a .json report.
    """
    p = Path(path)
    if p.suffix.lower() != ".json":
        raise ValueError("load_report only supports .json files")
    return json.loads(p.read_text(encoding="utf-8"))
