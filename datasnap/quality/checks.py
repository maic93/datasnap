"""Data quality checks: duplicates, outliers, constant columns."""

from __future__ import annotations

import pandas as pd


def run_quality_checks(df: pd.DataFrame) -> dict:
    """Run all quality checks and return a structured report."""
    results = {
        "duplicate_rows": _check_duplicates(df),
        "outliers": _check_outliers(df),
        "constant_columns": _check_constant_columns(df),
        "quality_score": 0,
    }
    results["quality_score"] = _compute_score(df, results)
    return results


def _check_duplicates(df: pd.DataFrame) -> dict:
    n_dupes = int(df.duplicated().sum())
    return {
        "count": n_dupes,
        "pct": round(n_dupes / len(df) * 100, 2) if len(df) else 0,
    }


def _check_outliers(df: pd.DataFrame) -> list[dict]:
    """IQR-based outlier detection for numeric columns."""
    outliers = []
    for col in df.select_dtypes(include="number").columns:
        s = df[col].dropna()
        if len(s) < 4:
            continue
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0:
            continue
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        mask = (s < lower) | (s > upper)
        n = int(mask.sum())
        if n > 0:
            outliers.append({
                "column": col,
                "count": n,
                "pct": round(n / len(s) * 100, 2),
                "lower_bound": round(float(lower), 4),
                "upper_bound": round(float(upper), 4),
            })
    return outliers


def _check_constant_columns(df: pd.DataFrame) -> list[str]:
    """Return columns with only one unique non-null value."""
    return [
        col for col in df.columns
        if df[col].dropna().nunique() <= 1
    ]


def _compute_score(df: pd.DataFrame, results: dict) -> int:
    """Simple 0–100 quality score."""
    score = 100

    # Penalise missing values
    missing_pct = df.isna().mean().mean() * 100
    score -= min(30, missing_pct * 2)

    # Penalise duplicates
    score -= min(20, results["duplicate_rows"]["pct"] * 2)

    # Penalise outlier-heavy columns
    outlier_penalty = sum(o["pct"] for o in results["outliers"])
    score -= min(20, outlier_penalty)

    # Penalise constant columns
    score -= min(10, len(results["constant_columns"]) * 5)

    return max(0, round(score))
