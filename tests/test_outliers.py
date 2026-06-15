"""Tests for outlier detection and quality score — Day 10."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from datasnap.quality.outliers import outlier_report, outlier_summary, outlier_summary_line
from datasnap.quality.score import compute_quality_score, quality_score_line, _grade

FIXTURES = Path(__file__).parent / "fixtures"


# ── outlier_report (IQR) ──────────────────────────────────────────────────────

def test_no_outliers():
    df = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0, 5.0] * 4})
    result = outlier_report(df)
    assert result == []


def test_detects_high_outlier():
    base = list(range(1, 21))  # varied data so IQR > 0
    base.append(1000)  # extreme outlier
    df = pd.DataFrame({"val": [float(x) for x in base]})
    result = outlier_report(df)
    assert len(result) == 1
    assert result[0]["column"] == "val"
    assert result[0]["count"] == 1


def test_detects_low_outlier():
    base = list(range(10, 30))  # varied data
    base.append(-500)
    df = pd.DataFrame({"val": [float(x) for x in base]})
    result = outlier_report(df)
    assert len(result) == 1
    assert result[0]["count"] == 1


def test_outlier_has_bounds():
    base = list(range(1, 21)) + [1000]
    df = pd.DataFrame({"val": [float(x) for x in base]})
    result = outlier_report(df)
    assert "lower_bound" in result[0]
    assert "upper_bound" in result[0]
    assert result[0]["max_outlier"] == 1000.0
    assert result[0]["min_outlier"] == 1000.0


def test_outlier_pct():
    base = list(range(1, 19)) + [1000, 2000]
    df = pd.DataFrame({"val": [float(x) for x in base]})
    result = outlier_report(df)
    assert result[0]["pct"] == pytest.approx(10.0, rel=1e-1)


def test_outlier_indices_returned():
    base = list(range(1, 11)) + [9999]
    df = pd.DataFrame({"val": [float(x) for x in base]})
    result = outlier_report(df)
    assert 10 in result[0]["indices"]


def test_zscore_method():
    base = list(range(1, 21)) + [1000]
    df = pd.DataFrame({"val": [float(x) for x in base]})
    result = outlier_report(df, method="zscore", zscore_threshold=2.0)
    assert len(result) == 1
    assert result[0]["method"] == "zscore"


def test_sorted_by_count_desc():
    df = pd.DataFrame({
        "a": list(range(1,16)) + [9999]*5,
        "b": list(range(1,20)) + [9999],
    })
    result = outlier_report(df)
    assert result[0]["count"] >= result[1]["count"]


def test_skips_cols_with_few_values():
    df = pd.DataFrame({"tiny": [1.0, 2.0, 3.0]})
    result = outlier_report(df)
    assert result == []


def test_skips_non_numeric():
    df = pd.DataFrame({"name": ["Alice", "Bob", "Carol"] * 5})
    result = outlier_report(df)
    assert result == []


# ── outlier_summary ───────────────────────────────────────────────────────────

def test_outlier_summary_structure():
    df = pd.DataFrame({"val": [10.0] * 20 + [9999.0]})
    s = outlier_summary(df)
    assert "total_outliers" in s
    assert "affected_columns" in s
    assert "iqr" in s
    assert "zscore" in s


def test_outlier_summary_line_no_outliers():
    df = pd.DataFrame({"a": [1.0, 2.0, 3.0, 4.0, 5.0] * 4})
    line = outlier_summary_line(df)
    assert "no outliers" in line.lower()


def test_outlier_summary_line_with_outliers():
    df = pd.DataFrame({"salary": [float(i*1000) for i in range(1,21)] + [9999999.0]})
    line = outlier_summary_line(df)
    assert "salary" in line
    assert "1" in line


# ── compute_quality_score ─────────────────────────────────────────────────────

def test_score_range():
    from datasnap.loaders.detect import load_file
    df = load_file(FIXTURES / "sample.csv")
    result = compute_quality_score(df)
    assert 0 <= result["total"] <= 100


def test_score_has_grade():
    from datasnap.loaders.detect import load_file
    df = load_file(FIXTURES / "sample.csv")
    result = compute_quality_score(df)
    assert result["grade"] in ("A", "B", "C", "D", "F")


def test_score_has_dimensions():
    from datasnap.loaders.detect import load_file
    df = load_file(FIXTURES / "sample.csv")
    result = compute_quality_score(df)
    dims = result["dimensions"]
    assert "completeness" in dims
    assert "uniqueness" in dims
    assert "consistency" in dims
    assert "validity" in dims


def test_perfect_score_clean_data():
    df = pd.DataFrame({
        "id": range(1, 51),
        "value": [float(i) for i in range(1, 51)],
        "label": [f"item_{i}" for i in range(1, 51)],
    })
    result = compute_quality_score(df)
    assert result["total"] >= 90
    assert result["grade"] == "A"


def test_grade_function():
    assert _grade(95) == "A"
    assert _grade(85) == "B"
    assert _grade(75) == "C"
    assert _grade(65) == "D"
    assert _grade(50) == "F"


def test_quality_score_line_format():
    from datasnap.loaders.detect import load_file
    df = load_file(FIXTURES / "sample.csv")
    result = compute_quality_score(df)
    line = quality_score_line(result)
    assert "/100" in line
    assert "—" in line
