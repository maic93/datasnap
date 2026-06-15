"""Outlier detection using IQR and Z-score methods."""

from __future__ import annotations

from typing import List, Optional

import pandas as pd


def outlier_report(
    df: pd.DataFrame,
    method: str = "iqr",
    threshold: float = 1.5,
    zscore_threshold: float = 3.0,
) -> List[dict]:
    """Detect outliers in all numeric columns.

    Args:
        df: Input DataFrame.
        method: Detection method — 'iqr' or 'zscore'.
        threshold: IQR multiplier (default 1.5, use 3.0 for extreme outliers).
        zscore_threshold: Z-score cutoff (default 3.0).

    Returns:
        List of dicts, one per column with outliers found.
    """
    results = []
    for col in df.select_dtypes(include="number").columns:
        s = df[col].dropna()
        if len(s) < 4:
            continue

        if method == "zscore":
            col_result = _zscore_outliers(s, col, zscore_threshold)
        else:
            col_result = _iqr_outliers(s, col, threshold)

        if col_result and col_result["count"] > 0:
            results.append(col_result)

    return sorted(results, key=lambda x: x["count"], reverse=True)


def outlier_summary(df: pd.DataFrame) -> dict:
    """Return a combined outlier summary across all numeric columns.

    Args:
        df: Input DataFrame.

    Returns:
        Dict with total outlier count, affected columns, and per-column detail.
    """
    iqr_results = outlier_report(df, method="iqr")
    zscore_results = outlier_report(df, method="zscore")

    total_outliers = sum(r["count"] for r in iqr_results)
    affected_cols = len(iqr_results)

    return {
        "total_outliers": total_outliers,
        "affected_columns": affected_cols,
        "iqr": iqr_results,
        "zscore": zscore_results,
    }


def outlier_summary_line(df: pd.DataFrame) -> str:
    """Return a one-line human-readable outlier summary.

    Example: "Outliers found in 2 columns (salary: 3, age: 1)"

    Args:
        df: Input DataFrame.

    Returns:
        Formatted string summary.
    """
    results = outlier_report(df, method="iqr")
    if not results:
        return "No outliers detected"
    n_cols = len(results)
    details = ", ".join(f"{r['column']}: {r['count']}" for r in results[:3])
    return f"Outliers in {n_cols} column{'s' if n_cols > 1 else ''} ({details})"


# ── helpers ───────────────────────────────────────────────────────────────────

def _iqr_outliers(s: pd.Series, col: str, threshold: float) -> Optional[dict]:
    """Detect outliers using the IQR method."""
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return None

    lower = q1 - threshold * iqr
    upper = q3 + threshold * iqr
    mask = (s < lower) | (s > upper)
    outlier_vals = s[mask]

    return {
        "column": col,
        "method": "iqr",
        "count": int(mask.sum()),
        "pct": round(float(mask.sum()) / len(s) * 100, 2),
        "lower_bound": round(float(lower), 4),
        "upper_bound": round(float(upper), 4),
        "min_outlier": round(float(outlier_vals.min()), 4) if len(outlier_vals) else None,
        "max_outlier": round(float(outlier_vals.max()), 4) if len(outlier_vals) else None,
        "indices": s[mask].index.tolist(),
    }


def _zscore_outliers(s: pd.Series, col: str, threshold: float) -> Optional[dict]:
    """Detect outliers using Z-score method."""
    mean = s.mean()
    std = s.std()
    if std == 0:
        return None

    zscores = (s - mean) / std
    mask = zscores.abs() > threshold
    outlier_vals = s[mask]

    return {
        "column": col,
        "method": "zscore",
        "count": int(mask.sum()),
        "pct": round(float(mask.sum()) / len(s) * 100, 2),
        "threshold": threshold,
        "min_outlier": round(float(outlier_vals.min()), 4) if len(outlier_vals) else None,
        "max_outlier": round(float(outlier_vals.max()), 4) if len(outlier_vals) else None,
        "indices": s[mask].index.tolist(),
    }
