"""Categorical column statistics."""

from __future__ import annotations

from typing import List

import pandas as pd


def categorical_stats(series: pd.Series, top_n: int = 10) -> dict:
    """Compute statistics for a categorical or boolean column.

    Args:
        series: A pandas Series of categorical/string/boolean values.
        top_n: Number of top values to include in frequency table.

    Returns:
        Dict with unique count, top values, frequency table, and mode.
    """
    s = series.dropna()

    if len(s) == 0:
        return _empty_stats()

    vc = s.value_counts()
    total = len(s)

    return {
        "count": total,
        "unique": int(s.nunique()),
        "mode": str(vc.index[0]),
        "mode_count": int(vc.iloc[0]),
        "mode_pct": round(float(vc.iloc[0]) / total * 100, 2),
        "top_values": _top_values(vc, top_n, total),
        "least_common": _top_values(vc.iloc[::-1], min(3, len(vc)), total),
        "cardinality_ratio": round(float(s.nunique()) / total, 4),
    }


def categorical_stats_all(df: pd.DataFrame, top_n: int = 10) -> dict[str, dict]:
    """Compute categorical stats for all categorical/boolean columns.

    Args:
        df: Input DataFrame.
        top_n: Number of top values per column.

    Returns:
        Dict of {column_name: stats_dict} for categorical/boolean columns only.
    """
    from datasnap.stats.inference import infer_column_type

    result = {}
    for col in df.columns:
        col_type = infer_column_type(df[col])
        if col_type in ("categorical", "boolean"):
            result[col] = categorical_stats(df[col], top_n=top_n)
    return result


def summarise_categorical(series: pd.Series) -> str:
    """Return a one-line human-readable summary of a categorical column.

    Example: "3 unique  top: Engineering (45.5%)"

    Args:
        series: A categorical pandas Series.

    Returns:
        Formatted string summary.
    """
    s = series.dropna()
    if len(s) == 0:
        return "no data"

    vc = s.value_counts()
    unique = s.nunique()
    top_val = str(vc.index[0])
    top_pct = round(float(vc.iloc[0]) / len(s) * 100, 1)
    return f"{unique} unique  top: {top_val} ({top_pct}%)"


def value_counts_table(series: pd.Series, top_n: int = 10) -> List[dict]:
    """Return a sorted frequency table as a list of dicts.

    Args:
        series: Any pandas Series.
        top_n: Maximum rows to return.

    Returns:
        List of dicts with value, count, and percentage.
    """
    s = series.dropna()
    total = len(s)
    if total == 0:
        return []

    vc = s.value_counts().head(top_n)
    return [
        {
            "value": str(v),
            "count": int(c),
            "pct": round(float(c) / total * 100, 2),
        }
        for v, c in vc.items()
    ]


# ── helpers ───────────────────────────────────────────────────────────────────

def _top_values(vc: pd.Series, n: int, total: int) -> List[dict]:
    """Build top-N value list from a value_counts Series."""
    return [
        {
            "value": str(v),
            "count": int(c),
            "pct": round(float(c) / total * 100, 2),
        }
        for v, c in vc.head(n).items()
    ]


def _empty_stats() -> dict:
    return {
        "count": 0,
        "unique": 0,
        "mode": None,
        "mode_count": 0,
        "mode_pct": 0.0,
        "top_values": [],
        "least_common": [],
        "cardinality_ratio": 0.0,
    }
