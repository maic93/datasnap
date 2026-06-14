"""Duplicate row detection and reporting."""

from __future__ import annotations

from typing import List, Optional

import pandas as pd


def duplicate_report(df: pd.DataFrame, subset: Optional[List[str]] = None) -> dict:
    """Generate a full duplicate row report for a DataFrame.

    Args:
        df: Input DataFrame.
        subset: Column names to consider for duplicates.
                If None, all columns are used.

    Returns:
        Dict with duplicate counts, indices, and sample rows.
    """
    if len(df) == 0:
        return _empty_report()

    mask = df.duplicated(subset=subset, keep="first")
    dupe_df = df[mask]
    n_dupes = int(mask.sum())

    return {
        "total_rows": len(df),
        "duplicate_count": n_dupes,
        "duplicate_pct": round(n_dupes / len(df) * 100, 2),
        "unique_rows": len(df) - n_dupes,
        "subset": subset,
        "duplicate_indices": dupe_df.index.tolist(),
        "sample": _sample_rows(dupe_df),
        "severity": _severity(n_dupes / len(df) * 100),
    }


def find_duplicate_groups(
    df: pd.DataFrame, subset: Optional[List[str]] = None
) -> List[dict]:
    """Find groups of rows that are duplicates of each other.

    Args:
        df: Input DataFrame.
        subset: Columns to consider. None means all columns.

    Returns:
        List of groups, each with the shared values and row indices.
    """
    if len(df) == 0:
        return []

    mask = df.duplicated(subset=subset, keep=False)
    dupe_df = df[mask].copy()

    if dupe_df.empty:
        return []

    cols = subset or list(df.columns)
    groups = []

    for _, group in dupe_df.groupby(cols, dropna=False):
        if len(group) > 1:
            groups.append({
                "count": len(group),
                "indices": group.index.tolist(),
                "values": group.iloc[0][cols].to_dict(),
            })

    return sorted(groups, key=lambda g: g["count"], reverse=True)


def duplicate_summary_line(df: pd.DataFrame) -> str:
    """Return a one-line human-readable duplicate summary.

    Example: "3 duplicate rows found (2.7% of data)"

    Args:
        df: Input DataFrame.

    Returns:
        Formatted string summary.
    """
    report = duplicate_report(df)
    n = report["duplicate_count"]
    if n == 0:
        return "No duplicate rows — all rows are unique"
    pct = report["duplicate_pct"]
    return f"{n} duplicate row{'s' if n > 1 else ''} found ({pct}% of data)"


# ── helpers ───────────────────────────────────────────────────────────────────

def _sample_rows(dupe_df: pd.DataFrame, n: int = 3) -> List[dict]:
    """Return up to n sample duplicate rows as dicts."""
    return dupe_df.head(n).to_dict(orient="records")


def _severity(pct: float) -> str:
    """Classify duplicate % into severity."""
    if pct == 0:
        return "none"
    if pct < 1:
        return "low"
    if pct < 5:
        return "medium"
    if pct < 20:
        return "high"
    return "critical"


def _empty_report() -> dict:
    return {
        "total_rows": 0,
        "duplicate_count": 0,
        "duplicate_pct": 0.0,
        "unique_rows": 0,
        "subset": None,
        "duplicate_indices": [],
        "sample": [],
        "severity": "none",
    }
