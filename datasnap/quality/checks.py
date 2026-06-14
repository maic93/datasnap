"""Data quality checks: duplicates, outliers, constant columns, quality score."""

from __future__ import annotations

import pandas as pd

from datasnap.quality.duplicates import duplicate_report


def run_quality_checks(df: pd.DataFrame) -> dict:
    """Run all quality checks and return a structured report.

    Args:
        df: Input DataFrame.

    Returns:
        Dict with duplicate, outlier, constant column info, and quality score.
    """
    dupes = duplicate_report(df)
    outliers = _check_outliers(df)
    constants = _check_constant_columns(df)
    score = _compute_score(df, dupes, outliers, constants)

    return {
        "duplicate_rows": {
            "count": dupes["duplicate_count"],
            "pct": dupes["duplicate_pct"],
            "severity": dupes["severity"],
            "indices": dupes["duplicate_indices"],
        },
        "outliers": outliers,
        "constant_columns": constants,
        "quality_score": score,
    }


def _check_outliers(df: pd.DataFrame) -> list:
    """IQR-based outlier detection for numeric columns."""
    results = []
    for col in df.select_dtypes(include="number").columns:
        s = df[col].dropna()
        if len(s) < 4:
            continue
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        n = int(((s < lower) | (s > upper)).sum())
        if n > 0:
            results.append({
                "column": col,
                "count": n,
                "pct": round(n / len(s) * 100, 2),
                "lower_bound": round(float(lower), 4),
                "upper_bound": round(float(upper), 4),
            })
    return results


def _check_constant_columns(df: pd.DataFrame) -> list:
    """Return columns with only one unique non-null value."""
    return [col for col in df.columns if df[col].dropna().nunique() <= 1]


def _compute_score(
    df: pd.DataFrame,
    dupes: dict,
    outliers: list,
    constants: list,
) -> int:
    score = 100.0
    score -= min(30, df.isna().mean().mean() * 100 * 2)
    score -= min(20, dupes["duplicate_pct"] * 2)
    score -= min(20, sum(o["pct"] for o in outliers))
    score -= min(10, len(constants) * 5)
    return max(0, round(score))
