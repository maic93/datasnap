"""Compute summary statistics for a DataFrame."""

from __future__ import annotations

from typing import List

import pandas as pd

from datasnap.stats.inference import infer_column_type


def compute_summary(df: pd.DataFrame) -> dict:
    """Return a full summary dict for the given DataFrame.

    Args:
        df: Input DataFrame.

    Returns:
        Dict with row/column counts, per-column stats, and missing value info.
    """
    column_stats: List[dict] = [_column_stat(df[col]) for col in df.columns]

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "total_missing": int(df.isna().sum().sum()),
        "total_missing_pct": round(df.isna().mean().mean() * 100, 2),
        "column_stats": column_stats,
    }


def _column_stat(series: pd.Series) -> dict:
    """Compute stats for a single column."""
    col_type = infer_column_type(series)
    stat: dict = {
        "name": series.name,
        "type": col_type,
        "count": int(series.count()),
        "missing": int(series.isna().sum()),
        "missing_pct": round(series.isna().mean() * 100, 2),
    }
    if col_type == "numeric":
        stat.update(_numeric_stats(series.dropna()))
    elif col_type in ("categorical", "boolean"):
        stat.update(_categorical_stats(series))
    elif col_type == "datetime":
        stat.update(_datetime_stats(series))
    return stat


def _numeric_stats(s: pd.Series) -> dict:
    """Descriptive statistics for numeric columns."""
    q1, median, q3 = s.quantile([0.25, 0.5, 0.75])
    return {
        "mean": round(float(s.mean()), 4),
        "std": round(float(s.std()), 4),
        "min": round(float(s.min()), 4),
        "max": round(float(s.max()), 4),
        "q1": round(float(q1), 4),
        "median": round(float(median), 4),
        "q3": round(float(q3), 4),
    }


def _categorical_stats(s: pd.Series) -> dict:
    """Value counts and unique count for categorical/boolean columns."""
    vc = s.value_counts()
    return {
        "unique": int(s.nunique()),
        "top_values": [
            {"value": str(v), "count": int(c)} for v, c in vc.head(5).items()
        ],
    }


def _datetime_stats(s: pd.Series) -> dict:
    """Date range and unique count for datetime columns."""
    parsed = pd.to_datetime(s, errors="coerce")
    return {
        "min_date": str(parsed.min()),
        "max_date": str(parsed.max()),
        "unique": int(parsed.nunique()),
    }
