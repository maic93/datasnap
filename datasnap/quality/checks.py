"""Data quality checks — main entry point."""

from __future__ import annotations

import pandas as pd

from datasnap.quality.duplicates import duplicate_report
from datasnap.quality.outliers import outlier_report
from datasnap.quality.score import compute_quality_score


def run_quality_checks(df: pd.DataFrame) -> dict:
    """Run all quality checks and return a structured report.

    Args:
        df: Input DataFrame.

    Returns:
        Dict with duplicate, outlier, constant column info, and quality score.
    """
    dupes = duplicate_report(df)
    outliers = outlier_report(df)
    constants = _check_constant_columns(df)
    score_result = compute_quality_score(df)

    return {
        "duplicate_rows": {
            "count": dupes["duplicate_count"],
            "pct": dupes["duplicate_pct"],
            "severity": dupes["severity"],
            "indices": dupes["duplicate_indices"],
        },
        "outliers": outliers,
        "constant_columns": constants,
        "quality_score": score_result["total"],
        "quality_grade": score_result["grade"],
        "quality_breakdown": score_result["dimensions"],
    }


def _check_constant_columns(df: pd.DataFrame) -> list:
    """Return columns with only one unique non-null value."""
    return [col for col in df.columns if df[col].dropna().nunique() <= 1]
