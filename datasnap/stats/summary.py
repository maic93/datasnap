"""Compute summary statistics for a DataFrame."""

from __future__ import annotations

import pandas as pd


def compute_summary(df: pd.DataFrame) -> dict:
    """Return a full summary dict for the given DataFrame."""
    columns = [_column_stat(df[col]) for col in df.columns]
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "total_missing": int(df.isna().sum().sum()),
        "total_missing_pct": round(df.isna().mean().mean() * 100, 2),
        "column_stats": columns,
    }


def _column_stat(series: pd.Series) -> dict:
    col_type = _infer_type(series)
    stat: dict = {
        "name": series.name,
        "type": col_type,
        "count": int(series.count()),
        "missing": int(series.isna().sum()),
        "missing_pct": round(series.isna().mean() * 100, 2),
    }
    if col_type == "numeric":
        stat.update(_numeric_stats(series.dropna()))
    elif col_type == "categorical":
        stat.update(_categorical_stats(series))
    elif col_type == "datetime":
        stat.update(_datetime_stats(series))
    return stat


def _infer_type(series: pd.Series) -> str:
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    if series.dtype == object:
        try:
            pd.to_datetime(series.dropna().head(20), infer_datetime_format=True)
            return "datetime"
        except Exception:
            pass
    return "categorical"


def _numeric_stats(s: pd.Series) -> dict:
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
    vc = s.value_counts()
    return {
        "unique": int(s.nunique()),
        "top_values": [
            {"value": str(v), "count": int(c)} for v, c in vc.head(5).items()
        ],
    }


def _datetime_stats(s: pd.Series) -> dict:
    parsed = pd.to_datetime(s, errors="coerce")
    return {
        "min_date": str(parsed.min()),
        "max_date": str(parsed.max()),
        "unique": int(parsed.nunique()),
    }
