"""Pretty terminal output using the rich library."""

from __future__ import annotations

import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.text import Text

console = Console()


def print_report(
    filename: str,
    df: pd.DataFrame,
    summary: dict,
    quality: dict | None,
    plot: bool = False,
) -> None:
    console.print()
    console.print(
        Panel(
            f"[bold]{filename}[/bold]  "
            f"[dim]{summary['rows']:,} rows × {summary['columns']} columns[/dim]",
            style="blue",
            expand=False,
        )
    )

    _print_column_table(summary["column_stats"])

    if quality:
        _print_quality_panel(quality)

    if plot:
        _print_charts(df, summary)


def _print_column_table(col_stats: list[dict]) -> None:
    table = Table(
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style="bold dim",
        pad_edge=False,
    )
    table.add_column("column", style="bold", no_wrap=True)
    table.add_column("type", style="cyan")
    table.add_column("non-null", justify="right")
    table.add_column("missing %", justify="right")
    table.add_column("stats / top values", style="dim")

    for c in col_stats:
        missing_style = "red" if c["missing_pct"] > 20 else "yellow" if c["missing_pct"] > 5 else "green"
        extra = _format_extra(c)
        table.add_row(
            c["name"],
            c["type"],
            str(c["count"]),
            Text(f"{c['missing_pct']}%", style=missing_style),
            extra,
        )

    console.print(table)


def _format_extra(c: dict) -> str:
    t = c["type"]
    if t == "numeric":
        return f"mean={c.get('mean')}  min={c.get('min')}  max={c.get('max')}"
    if t == "categorical":
        tops = ", ".join(v["value"] for v in c.get("top_values", [])[:3])
        return f"{c.get('unique')} unique  top: {tops}"
    if t == "datetime":
        return f"{c.get('min_date')} → {c.get('max_date')}"
    return ""


def _print_quality_panel(quality: dict) -> None:
    score = quality["quality_score"]
    color = "green" if score >= 80 else "yellow" if score >= 60 else "red"

    lines = [
        f"[bold]Quality score: [{color}]{score}/100[/{color}][/bold]",
        f"  Duplicate rows: {quality['duplicate_rows']['count']} ({quality['duplicate_rows']['pct']}%)",
    ]

    if quality["outlier_columns"] := quality.get("outliers"):
        for o in quality["outlier_columns"]:
            lines.append(f"  Outliers in [bold]{o['column']}[/bold]: {o['count']} rows ({o['pct']}%)")

    if quality.get("constant_columns"):
        cols = ", ".join(quality["constant_columns"])
        lines.append(f"  Constant columns: {cols}")

    console.print(Panel("\n".join(lines), title="data quality", border_style=color, expand=False))


def _print_charts(df: pd.DataFrame, summary: dict) -> None:
    try:
        import plotext as plt  # type: ignore
    except ImportError:
        console.print("[yellow]Install plotext to see charts: pip install plotext[/yellow]")
        return

    numeric_cols = [c for c in summary["column_stats"] if c["type"] == "numeric"]
    for col_stat in numeric_cols[:3]:
        col = col_stat["name"]
        values = df[col].dropna().tolist()
        if not values:
            continue
        plt.clf()
        plt.hist(values, bins=20)
        plt.title(f"Distribution: {col}")
        plt.show()
