"""Pretty terminal output using rich."""

from __future__ import annotations

import pandas as pd


def _console():
    from rich.console import Console
    return Console()


def print_report(
    filename: str,
    df: pd.DataFrame,
    summary: dict,
    quality: dict | None,
    plot: bool = False,
) -> None:
    from rich.panel import Panel

    console = _console()
    console.print()
    console.print(
        Panel(
            f"[bold]{filename}[/bold]  "
            f"[dim]{summary['rows']:,} rows × {summary['columns']} columns  "
            f"missing overall: {summary['total_missing_pct']}%[/dim]",
            style="blue",
            expand=False,
        )
    )
    _print_column_table(summary["column_stats"])
    if quality:
        _print_quality(quality)
    if plot:
        _print_charts(df, summary)


def _print_column_table(col_stats: list[dict]) -> None:
    from rich.table import Table
    from rich import box
    from rich.text import Text

    console = _console()
    table = Table(box=box.SIMPLE_HEAD, header_style="bold dim", pad_edge=False)
    table.add_column("column", style="bold", no_wrap=True)
    table.add_column("type", style="cyan")
    table.add_column("non-null", justify="right")
    table.add_column("missing%", justify="right")
    table.add_column("summary", style="dim")

    for c in col_stats:
        pct = c["missing_pct"]
        color = "red" if pct > 20 else "yellow" if pct > 5 else "green"
        table.add_row(
            c["name"],
            c["type"],
            str(c["count"]),
            Text(f"{pct}%", style=color),
            _format_summary(c),
        )
    console.print(table)


def _format_summary(c: dict) -> str:
    t = c["type"]
    if t == "numeric":
        return f"mean={c.get('mean')}  min={c.get('min')}  max={c.get('max')}"
    if t == "categorical":
        tops = ", ".join(v["value"] for v in c.get("top_values", [])[:3])
        return f"{c.get('unique')} unique — {tops}"
    if t == "datetime":
        return f"{c.get('min_date')} → {c.get('max_date')}"
    return ""


def _print_quality(quality: dict) -> None:
    from rich.panel import Panel

    console = _console()
    score = quality["quality_score"]
    color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
    lines = [f"[bold]Quality score: [{color}]{score}/100[/{color}][/bold]"]
    d = quality["duplicate_rows"]
    lines.append(f"  Duplicate rows : {d['count']} ({d['pct']}%)")
    for o in quality.get("outliers", []):
        lines.append(
            f"  Outliers in [bold]{o['column']}[/bold]: {o['count']} rows ({o['pct']}%)"
        )
    if quality.get("constant_columns"):
        lines.append(f"  Constant cols  : {', '.join(quality['constant_columns'])}")
    console.print(Panel("\n".join(lines), border_style=color, expand=False))


def _print_charts(df: pd.DataFrame, summary: dict) -> None:
    console = _console()
    try:
        import plotext as plt  # type: ignore
    except ImportError:
        console.print("[yellow]pip install plotext to enable charts[/yellow]")
        return
    numeric = [c for c in summary["column_stats"] if c["type"] == "numeric"]
    for col_stat in numeric[:3]:
        col = col_stat["name"]
        values = df[col].dropna().tolist()
        if not values:
            continue
        plt.clf()
        plt.hist(values, bins=20)
        plt.title(f"Distribution: {col}")
        plt.show()


def print_diff_placeholder() -> None:
    from rich.panel import Panel
    _console().print(Panel("[dim]--diff mode coming on Day 12[/dim]", expand=False))
