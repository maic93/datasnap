"""Pretty terminal output using rich."""

from __future__ import annotations

from typing import Optional

import pandas as pd


def _console():
    from rich.console import Console
    return Console()


def print_report(
    filename: str,
    df: pd.DataFrame,
    summary: dict,
    quality: Optional[dict],
    plot: bool = False,
) -> None:
    """Print a full data profile report to the terminal."""
    from rich.panel import Panel

    console = _console()
    console.print()

    # Header panel
    missing_line = f"[yellow]{summary['total_missing_pct']}% missing[/yellow]" \
        if summary['total_missing_pct'] > 0 else "[green]no missing[/green]"

    console.print(Panel(
        f"[bold white]{filename}[/bold white]  "
        f"[dim]{summary['rows']:,} rows × {summary['columns']} columns  "
        f"{missing_line}[/dim]",
        style="blue",
        expand=False,
    ))

    # Column stats table
    _print_column_table(summary["column_stats"])

    # Missing value report
    _print_missing_report(df)

    # Quality panel
    if quality:
        _print_quality(quality)

    # Charts
    if plot:
        _print_charts(df, summary)


def _print_column_table(col_stats: list) -> None:
    """Print the main column summary table."""
    from rich.table import Table
    from rich import box
    from rich.text import Text

    console = _console()
    table = Table(
        box=box.SIMPLE_HEAD,
        header_style="bold dim",
        pad_edge=False,
        show_edge=False,
    )
    table.add_column("#", style="dim", width=3)
    table.add_column("column", style="bold", no_wrap=True)
    table.add_column("type", style="cyan", width=12)
    table.add_column("non-null", justify="right", width=9)
    table.add_column("missing%", justify="right", width=9)
    table.add_column("summary", style="dim")

    for i, c in enumerate(col_stats, 1):
        pct = c["missing_pct"]
        if pct == 0:
            missing_text = Text("0%", style="green")
        elif pct < 5:
            missing_text = Text(f"{pct}%", style="yellow")
        elif pct < 20:
            missing_text = Text(f"{pct}%", style="dark_orange")
        else:
            missing_text = Text(f"{pct}%", style="red")

        table.add_row(
            str(i),
            str(c["name"]),
            c["type"],
            str(c["count"]),
            missing_text,
            c.get("summary", ""),
        )

    console.print(table)


def _print_missing_report(df: pd.DataFrame) -> None:
    """Print missing value breakdown if any columns have missing data."""
    from datasnap.stats.missing import missing_report, missing_summary_line
    from rich.table import Table
    from rich import box
    from rich.text import Text

    report = missing_report(df)
    console = _console()

    if report["columns_with_missing"] == 0:
        console.print(f"  [green]✓[/green] [dim]{missing_summary_line(df)}[/dim]\n")
        return

    # Summary line
    console.print(f"\n  [yellow]Missing values:[/yellow] {missing_summary_line(df)}")

    # Per-column breakdown table
    table = Table(box=box.SIMPLE, pad_edge=False, show_header=True, header_style="dim")
    table.add_column("column", style="bold")
    table.add_column("missing", justify="right")
    table.add_column("of total", justify="right")
    table.add_column("pct", justify="right")
    table.add_column("severity", justify="center")

    severity_colors = {
        "low": "yellow",
        "medium": "dark_orange",
        "high": "red",
        "critical": "bold red",
    }

    for col in report["columns"]:
        if col["missing"] == 0:
            continue
        color = severity_colors.get(col["severity"], "white")
        table.add_row(
            col["column"],
            str(col["missing"]),
            str(col["total"]),
            f"{col['pct']}%",
            Text(col["severity"], style=color),
        )

    console.print(table)


def _print_quality(quality: dict) -> None:
    """Print quality score panel."""
    from rich.panel import Panel

    console = _console()
    score = quality["quality_score"]
    color = "green" if score >= 80 else "yellow" if score >= 60 else "red"

    lines = [f"[bold]Quality score: [{color}]{score}/100[/{color}][/bold]"]
    d = quality["duplicate_rows"]
    lines.append(f"  Duplicate rows : {d['count']} ({d['pct']}%)")
    for o in quality.get("outliers", []):
        lines.append(
            f"  Outliers in [bold]{o['column']}[/bold]: "
            f"{o['count']} rows ({o['pct']}%)"
        )
    if quality.get("constant_columns"):
        lines.append(f"  Constant cols  : {', '.join(quality['constant_columns'])}")

    console.print(Panel("\n".join(lines), border_style=color, expand=False))


def _print_charts(df: pd.DataFrame, summary: dict) -> None:
    """Print terminal charts using plotext."""
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
