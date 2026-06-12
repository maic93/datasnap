"""Compute summary statistics for a DataFrame."""

from __future__ import annotations

from typing import List

import pandas as pd

from datasnap.stats.inference import infer_column_type
from datasnap.stats.numeric import numeric_stats, summarise_numeric
from datasnap.stats.categorical import categorical_stats, summarise_categorical


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
        stat.update(numeric_stats(series))
        stat["summary"] = summarise_numeric(series)
    elif col_type in ("categorical", "boolean"):
        stat.update(categorical_stats(series))
        stat["summary"] = summarise_categorical(series)
    elif col_type == "datetime":
        stat.update(_datetime_stats(series))
        stat["summary"] = _summarise_datetime(series)
    else:
        stat["summary"] = "—"
    return stat


def _datetime_stats(s: pd.Series) -> dict:
    parsed = pd.to_datetime(s, errors="coerce", format="mixed")
    return {
        "min_date": str(parsed.min()),
        "max_date": str(parsed.max()),
        "unique": int(parsed.nunique()),
    }


def _summarise_datetime(s: pd.Series) -> str:
    parsed = pd.to_datetime(s, errors="coerce", format="mixed")
    return f"{parsed.min().date()} → {parsed.max().date()}"
