"""Missing value analysis for DataFrames."""

from __future__ import annotations

from typing import List

import pandas as pd


def missing_report(df: pd.DataFrame) -> dict:
    """Generate a full missing value report for a DataFrame.

    Args:
        df: Input DataFrame.

    Returns:
        Dict with per-column missing info and overall summary.
    """
    total_cells = df.shape[0] * df.shape[1]
    total_missing = int(df.isna().sum().sum())

    columns: List[dict] = []
    for col in df.columns:
        missing = int(df[col].isna().sum())
        columns.append({
            "column": col,
            "missing": missing,
            "total": len(df),
            "pct": round(missing / len(df) * 100, 2) if len(df) else 0.0,
            "severity": _severity(missing / len(df) * 100 if len(df) else 0),
        })

    # Sort by missing count descending
    columns.sort(key=lambda x: x["missing"], reverse=True)

    return {
        "total_cells": total_cells,
        "total_missing": total_missing,
        "total_missing_pct": round(total_missing / total_cells * 100, 2) if total_cells else 0.0,
        "columns_with_missing": sum(1 for c in columns if c["missing"] > 0),
        "complete_columns": sum(1 for c in columns if c["missing"] == 0),
        "columns": columns,
    }


def missing_summary_line(df: pd.DataFrame) -> str:
    """Return a one-line summary of missing values.

    Example: "2 columns have missing data (max 9.1% in 'age')"

    Args:
        df: Input DataFrame.

    Returns:
        Human-readable summary string.
    """
    report = missing_report(df)
    n = report["columns_with_missing"]
    if n == 0:
        return "No missing values — dataset is complete"
    worst = report["columns"][0]
    return (
        f"{n} column{'s' if n > 1 else ''} have missing data  "
        f"(worst: '{worst['column']}' at {worst['pct']}%)"
    )


def _severity(pct: float) -> str:
    """Classify missing % into a severity level."""
    if pct == 0:
        return "none"
    if pct < 5:
        return "low"
    if pct < 20:
        return "medium"
    if pct < 50:
        return "high"
    return "critical"
