"""Data quality checks: duplicates, outliers, constant columns, quality score."""

from __future__ import annotations

import pandas as pd


def run_quality_checks(df: pd.DataFrame) -> dict:
    """Run all quality checks and return a structured report."""
    dupes = _check_duplicates(df)
    outliers = _check_outliers(df)
    constants = _check_constant_columns(df)
    score = _compute_score(df, dupes, outliers, constants)
    return {
        "duplicate_rows": dupes,
        "outliers": outliers,
        "constant_columns": constants,
        "quality_score": score,
    }


def _check_duplicates(df: pd.DataFrame) -> dict:
    n = int(df.duplicated().sum())
    return {"count": n, "pct": round(n / len(df) * 100, 2) if len(df) else 0}


def _check_outliers(df: pd.DataFrame) -> list[dict]:
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


def _check_constant_columns(df: pd.DataFrame) -> list[str]:
    return [col for col in df.columns if df[col].dropna().nunique() <= 1]


def _compute_score(
    df: pd.DataFrame,
    dupes: dict,
    outliers: list[dict],
    constants: list[str],
) -> int:
    score = 100.0
    score -= min(30, df.isna().mean().mean() * 100 * 2)
    score -= min(20, dupes["pct"] * 2)
    score -= min(20, sum(o["pct"] for o in outliers))
    score -= min(10, len(constants) * 5)
    return max(0, round(score))
