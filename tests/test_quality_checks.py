"""Tests for the unified quality checks entry point — Day 13."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from datasnap.quality.checks import run_quality_checks
from datasnap.loaders.detect import load_file

FIXTURES = Path(__file__).parent / "fixtures"


def test_returns_all_expected_keys():
    df = load_file(FIXTURES / "sample.csv")
    q = run_quality_checks(df)
    expected_keys = {
        "duplicate_rows", "outliers", "constant_columns",
        "quality_score", "quality_grade", "quality_breakdown",
    }
    assert expected_keys.issubset(q.keys())


def test_duplicate_rows_structure():
    df = load_file(FIXTURES / "sample.csv")
    q = run_quality_checks(df)
    d = q["duplicate_rows"]
    assert "count" in d and "pct" in d and "severity" in d and "indices" in d


def test_quality_score_matches_breakdown():
    df = load_file(FIXTURES / "sample.csv")
    q = run_quality_checks(df)
    dims = q["quality_breakdown"]
    total = sum(d["score"] for d in dims.values())
    assert abs(total - q["quality_score"]) < 1.0


def test_constant_column_detected():
    df = pd.DataFrame({
        "a": [1, 1, 1, 1],
        "b": [1, 2, 3, 4],
    })
    q = run_quality_checks(df)
    assert "a" in q["constant_columns"]
    assert "b" not in q["constant_columns"]


def test_empty_dataframe_does_not_crash():
    df = pd.DataFrame({"a": [], "b": []})
    q = run_quality_checks(df)
    assert q["duplicate_rows"]["count"] == 0


def test_single_row_dataframe():
    df = pd.DataFrame({"a": [1], "b": ["x"]})
    q = run_quality_checks(df)
    assert q["duplicate_rows"]["count"] == 0
    assert 0 <= q["quality_score"] <= 100


def test_all_duplicate_rows():
    df = pd.DataFrame({"a": [1, 1, 1], "b": ["x", "x", "x"]})
    q = run_quality_checks(df)
    assert q["duplicate_rows"]["count"] == 2
    assert q["quality_score"] < 100


def test_grade_consistent_with_score():
    df = load_file(FIXTURES / "sample.csv")
    q = run_quality_checks(df)
    score = q["quality_score"]
    grade = q["quality_grade"]
    if score >= 90:
        assert grade == "A"
    elif score >= 80:
        assert grade == "B"
    elif score >= 70:
        assert grade == "C"
    elif score >= 60:
        assert grade == "D"
    else:
        assert grade == "F"
