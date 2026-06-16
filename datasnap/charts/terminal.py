"""Terminal charts using plotext."""

from __future__ import annotations

from typing import Optional

import pandas as pd


def plot_histogram(
    series: pd.Series,
    bins: int = 20,
    width: int = 60,
    height: int = 15,
    title: Optional[str] = None,
) -> None:
    """Plot a histogram for a numeric column in the terminal.

    Args:
        series: Numeric pandas Series.
        bins: Number of histogram bins.
        width: Terminal chart width in characters.
        height: Terminal chart height in lines.
        title: Chart title. Defaults to column name.
    """
    try:
        import plotext as plt
    except ImportError:
        _missing_plotext()
        return

    values = series.dropna().tolist()
    if not values:
        _warn(f"No data to plot for '{series.name}'")
        return

    plt.clf()
    plt.plotsize(width, height)
    plt.hist(values, bins=bins)
    plt.title(title or f"Distribution: {series.name}")
    plt.xlabel(str(series.name))
    plt.ylabel("Count")
    plt.theme("dark")
    plt.show()


def plot_bar_chart(
    series: pd.Series,
    top_n: int = 10,
    width: int = 60,
    height: int = 15,
    title: Optional[str] = None,
    horizontal: bool = True,
) -> None:
    """Plot a bar chart of value counts for a categorical column.

    Args:
        series: Categorical pandas Series.
        top_n: Number of top values to show.
        width: Terminal chart width in characters.
        height: Terminal chart height in lines.
        title: Chart title. Defaults to column name.
        horizontal: If True, draw horizontal bars (easier to read long labels).
    """
    try:
        import plotext as plt
    except ImportError:
        _missing_plotext()
        return

    vc = series.dropna().value_counts().head(top_n)
    if vc.empty:
        _warn(f"No data to plot for '{series.name}'")
        return

    labels = [str(v) for v in vc.index]
    counts = vc.tolist()

    plt.clf()
    plt.plotsize(width, height)
    plt.title(title or f"Value counts: {series.name} (top {min(top_n, len(vc))})")
    plt.theme("dark")

    if horizontal:
        plt.bar(labels, counts, orientation="horizontal")
    else:
        plt.bar(labels, counts)

    plt.show()


def plot_all_numeric(
    df: pd.DataFrame,
    bins: int = 20,
    width: int = 60,
    height: int = 12,
    max_cols: int = 5,
) -> None:
    """Plot histograms for all numeric columns in a DataFrame.

    Args:
        df: Input DataFrame.
        bins: Histogram bins.
        width: Chart width.
        height: Chart height.
        max_cols: Maximum number of columns to plot.
    """
    from datasnap.stats.inference import infer_column_type

    numeric_cols = [
        col for col in df.columns
        if infer_column_type(df[col]) == "numeric"
    ][:max_cols]

    if not numeric_cols:
        _warn("No numeric columns found to plot")
        return

    for col in numeric_cols:
        plot_histogram(df[col], bins=bins, width=width, height=height)


def plot_all_categorical(
    df: pd.DataFrame,
    top_n: int = 10,
    width: int = 60,
    height: int = 12,
    max_cols: int = 3,
) -> None:
    """Plot bar charts for all categorical columns in a DataFrame.

    Args:
        df: Input DataFrame.
        top_n: Top values per column.
        width: Chart width.
        height: Chart height.
        max_cols: Maximum number of columns to plot.
    """
    from datasnap.stats.inference import infer_column_type

    cat_cols = [
        col for col in df.columns
        if infer_column_type(df[col]) in ("categorical", "boolean")
    ][:max_cols]

    if not cat_cols:
        _warn("No categorical columns found to plot")
        return

    for col in cat_cols:
        plot_bar_chart(df[col], top_n=top_n, width=width, height=height)


def plot_summary(
    df: pd.DataFrame,
    numeric_bins: int = 20,
    top_n: int = 8,
    width: int = 60,
    height: int = 12,
    max_numeric: int = 3,
    max_categorical: int = 2,
) -> None:
    """Plot a summary of charts — numeric histograms then categorical bars.

    Args:
        df: Input DataFrame.
        numeric_bins: Histogram bins for numeric columns.
        top_n: Top-N values for categorical columns.
        width: Chart width.
        height: Chart height.
        max_numeric: Max numeric columns to chart.
        max_categorical: Max categorical columns to chart.
    """
    plot_all_numeric(df, bins=numeric_bins, width=width, height=height, max_cols=max_numeric)
    plot_all_categorical(df, top_n=top_n, width=width, height=height, max_cols=max_categorical)


# ── helpers ───────────────────────────────────────────────────────────────────

def _missing_plotext() -> None:
    try:
        from rich.console import Console
        Console().print(
            "[yellow]plotext not installed. Run: pip install plotext[/yellow]"
        )
    except ImportError:
        print("plotext not installed. Run: pip install plotext")


def _warn(msg: str) -> None:
    try:
        from rich.console import Console
        Console().print(f"[dim]{msg}[/dim]")
    except ImportError:
        print(msg)
