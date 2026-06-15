"""Data quality score computation (0–100)."""

from __future__ import annotations

import pandas as pd


def compute_quality_score(df: pd.DataFrame) -> dict:
    """Compute a detailed quality score breakdown for a DataFrame.

    Scoring breakdown (100 points total):
      - Completeness  (40 pts): penalises missing values
      - Uniqueness    (25 pts): penalises duplicate rows
      - Consistency   (20 pts): penalises outlier-heavy columns
      - Validity      (15 pts): penalises constant/near-constant columns

    Args:
        df: Input DataFrame.

    Returns:
        Dict with total score, grade, and per-dimension breakdown.
    """
    from datasnap.quality.duplicates import duplicate_report
    from datasnap.quality.outliers import outlier_report

    dupes = duplicate_report(df)
    outliers = outlier_report(df)

    completeness = _completeness_score(df)
    uniqueness = _uniqueness_score(dupes)
    consistency = _consistency_score(outliers, df)
    validity = _validity_score(df)

    total = round(completeness["score"] + uniqueness["score"] +
                  consistency["score"] + validity["score"])
    total = max(0, min(100, total))

    return {
        "total": total,
        "grade": _grade(total),
        "dimensions": {
            "completeness": completeness,
            "uniqueness": uniqueness,
            "consistency": consistency,
            "validity": validity,
        },
    }


def quality_score_line(score_result: dict) -> str:
    """Return a one-line summary of the quality score.

    Example: "Quality score: 87/100 (B — Good)"

    Args:
        score_result: Result from compute_quality_score().

    Returns:
        Formatted string.
    """
    total = score_result["total"]
    grade = score_result["grade"]
    label = _grade_label(grade)
    return f"Quality score: {total}/100 ({grade} — {label})"


# ── dimensions ────────────────────────────────────────────────────────────────

def _completeness_score(df: pd.DataFrame) -> dict:
    """Up to 40 points — penalises missing values."""
    missing_pct = df.isna().mean().mean() * 100
    score = max(0.0, 40.0 - missing_pct * 2)
    return {
        "score": round(score, 2),
        "max": 40,
        "missing_pct": round(missing_pct, 2),
        "note": f"{missing_pct:.1f}% of values missing",
    }


def _uniqueness_score(dupes: dict) -> dict:
    """Up to 25 points — penalises duplicate rows."""
    dupe_pct = dupes["duplicate_pct"]
    score = max(0.0, 25.0 - dupe_pct * 2)
    return {
        "score": round(score, 2),
        "max": 25,
        "duplicate_pct": dupe_pct,
        "note": f"{dupes['duplicate_count']} duplicate rows ({dupe_pct}%)",
    }


def _consistency_score(outliers: list, df: pd.DataFrame) -> dict:
    """Up to 20 points — penalises outlier-heavy columns."""
    numeric_cols = len(df.select_dtypes(include="number").columns)
    if numeric_cols == 0:
        return {"score": 20.0, "max": 20, "note": "no numeric columns"}

    total_outlier_pct = sum(o["pct"] for o in outliers)
    score = max(0.0, 20.0 - total_outlier_pct)
    return {
        "score": round(score, 2),
        "max": 20,
        "outlier_columns": len(outliers),
        "note": f"outliers in {len(outliers)} of {numeric_cols} numeric columns",
    }


def _validity_score(df: pd.DataFrame) -> dict:
    """Up to 15 points — penalises constant/near-constant columns."""
    constant = [col for col in df.columns if df[col].dropna().nunique() <= 1]
    near_constant = [
        col for col in df.columns
        if 1 < df[col].dropna().nunique() <= max(2, len(df) * 0.01)
        and col not in constant
    ]
    penalty = len(constant) * 5 + len(near_constant) * 2
    score = max(0.0, 15.0 - penalty)
    return {
        "score": round(score, 2),
        "max": 15,
        "constant_columns": constant,
        "near_constant_columns": near_constant,
        "note": f"{len(constant)} constant, {len(near_constant)} near-constant columns",
    }


# ── grade ─────────────────────────────────────────────────────────────────────

def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def _grade_label(grade: str) -> str:
    return {
        "A": "Excellent",
        "B": "Good",
        "C": "Fair",
        "D": "Poor",
        "F": "Critical",
    }.get(grade, "Unknown")
