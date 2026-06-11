"""Numeric column statistics."""

from __future__ import annotations

import pandas as pd


def numeric_stats(series: pd.Series) -> dict:
    """Compute descriptive statistics for a numeric column.

    Args:
        series: A numeric pandas Series (may contain NaNs).

    Returns:
        Dict with mean, std, min, max, quartiles, skewness, kurtosis.
    """
    s = series.dropna()

    if len(s) == 0:
        return _empty_stats()

    q1, median, q3 = s.quantile([0.25, 0.5, 0.75])
    iqr = q3 - q1

    return {
        "count": int(len(s)),
        "mean": _r(s.mean()),
        "std": _r(s.std()),
        "variance": _r(s.var()),
        "min": _r(s.min()),
        "max": _r(s.max()),
        "range": _r(float(s.max()) - float(s.min())),
        "q1": _r(q1),
        "median": _r(median),
        "q3": _r(q3),
        "iqr": _r(iqr),
        "skewness": _r(s.skew()),
        "kurtosis": _r(s.kurt()),
    }


def numeric_stats_all(df: pd.DataFrame) -> dict[str, dict]:
    """Compute numeric stats for all numeric columns in a DataFrame.

    Args:
        df: Input DataFrame.

    Returns:
        Dict of {column_name: stats_dict} for numeric columns only.
    """
    from datasnap.stats.inference import infer_column_type

    result = {}
    for col in df.columns:
        if infer_column_type(df[col]) == "numeric":
            result[col] = numeric_stats(df[col])
    return result


def summarise_numeric(series: pd.Series) -> str:
    """Return a one-line human-readable summary of a numeric column.

    Example: "mean=42.3  std=5.1  min=10  max=99  median=41"

    Args:
        series: A numeric pandas Series.

    Returns:
        Formatted string summary.
    """
    s = numeric_stats(series)
    if not s.get("count"):
        return "no data"
    return (
        f"mean={s['mean']}  "
        f"std={s['std']}  "
        f"min={s['min']}  "
        f"max={s['max']}  "
        f"median={s['median']}"
    )


# ── helpers ───────────────────────────────────────────────────────────────────

def _r(value: object, ndigits: int = 4) -> float:
    """Round a value to ndigits decimal places."""
    try:
        return round(float(value), ndigits)
    except (TypeError, ValueError):
        return 0.0


def _empty_stats() -> dict:
    """Return zeroed stats for an empty/all-null column."""
    return {
        "count": 0,
        "mean": None,
        "std": None,
        "variance": None,
        "min": None,
        "max": None,
        "range": None,
        "q1": None,
        "median": None,
        "q3": None,
        "iqr": None,
        "skewness": None,
        "kurtosis": None,
    }
