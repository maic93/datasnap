"""Tests for numeric stats — Day 6."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from datasnap.stats.numeric import numeric_stats, numeric_stats_all, summarise_numeric

FIXTURES = Path(__file__).parent / "fixtures"


# ── numeric_stats ─────────────────────────────────────────────────────────────

def test_basic_stats():
    s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    r = numeric_stats(s)
    assert r["mean"] == 3.0
    assert r["min"] == 1.0
    assert r["max"] == 5.0
    assert r["median"] == 3.0
    assert r["count"] == 5


def test_quartiles():
    s = pd.Series(range(1, 101), dtype=float)
    r = numeric_stats(s)
    assert r["q1"] == 25.75
    assert r["q3"] == 75.25
    assert r["iqr"] == pytest.approx(49.5, rel=1e-2)


def test_std_and_variance():
    s = pd.Series([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
    r = numeric_stats(s)
    # pandas uses sample std (ddof=1), not population std
    assert r["std"] == pytest.approx(2.1381, rel=1e-2)
    assert r["variance"] == pytest.approx(4.5714, rel=1e-2)


def test_range():
    s = pd.Series([10.0, 20.0, 30.0, 40.0])
    r = numeric_stats(s)
    assert r["range"] == 30.0


def test_skewness_symmetric():
    # Symmetric data — skewness near 0
    s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
    r = numeric_stats(s)
    assert abs(r["skewness"]) < 0.1


def test_skewness_right():
    # Right-skewed data
    s = pd.Series([1.0, 1.0, 1.0, 1.0, 10.0, 100.0])
    r = numeric_stats(s)
    assert r["skewness"] > 0


def test_ignores_nulls():
    s = pd.Series([1.0, None, 3.0, None, 5.0])
    r = numeric_stats(s)
    assert r["count"] == 3
    assert r["mean"] == 3.0


def test_all_nulls_returns_empty():
    s = pd.Series([None, None, None])
    r = numeric_stats(s)
    assert r["count"] == 0
    assert r["mean"] is None
    assert r["min"] is None


def test_single_value():
    s = pd.Series([42.0])
    r = numeric_stats(s)
    assert r["mean"] == 42.0
    assert r["min"] == 42.0
    assert r["max"] == 42.0
    assert r["range"] == 0.0


# ── numeric_stats_all ─────────────────────────────────────────────────────────

def test_numeric_stats_all_only_numeric_cols():
    from datasnap.loaders.detect import load_file
    df = load_file(FIXTURES / "sample.csv")
    result = numeric_stats_all(df)
    assert "salary" in result
    assert "age" in result
    assert "name" not in result        # categorical
    assert "department" not in result  # categorical


def test_numeric_stats_all_has_expected_keys():
    from datasnap.loaders.detect import load_file
    df = load_file(FIXTURES / "sample.csv")
    result = numeric_stats_all(df)
    for col_stats in result.values():
        assert "mean" in col_stats
        assert "std" in col_stats
        assert "min" in col_stats
        assert "max" in col_stats
        assert "median" in col_stats
        assert "q1" in col_stats
        assert "q3" in col_stats
        assert "iqr" in col_stats


# ── summarise_numeric ─────────────────────────────────────────────────────────

def test_summarise_numeric_format():
    s = pd.Series([10.0, 20.0, 30.0])
    summary = summarise_numeric(s)
    assert "mean=" in summary
    assert "min=" in summary
    assert "max=" in summary
    assert "median=" in summary


def test_summarise_numeric_empty():
    s = pd.Series([None, None], dtype=float)
    assert summarise_numeric(s) == "no data"
