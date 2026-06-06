"""Tests for the stats.summary module."""

from pathlib import Path

from datasnap.loaders.detect import load_file
from datasnap.stats.summary import compute_summary

FIXTURES = Path(__file__).parent / "fixtures"


def test_summary_shape():
    df = load_file(FIXTURES / "sample.csv")
    s = compute_summary(df)
    assert s["rows"] == 11
    assert s["columns"] == 6


def test_numeric_stats_present():
    df = load_file(FIXTURES / "sample.csv")
    s = compute_summary(df)
    salary = next(c for c in s["column_stats"] if c["name"] == "salary")
    assert salary["type"] == "numeric"
    assert "mean" in salary
    assert "min" in salary
    assert "max" in salary


def test_categorical_stats_present():
    df = load_file(FIXTURES / "sample.csv")
    s = compute_summary(df)
    dept = next(c for c in s["column_stats"] if c["name"] == "department")
    assert dept["type"] == "categorical"
    assert "unique" in dept
    assert "top_values" in dept


def test_missing_count():
    df = load_file(FIXTURES / "sample.csv")
    s = compute_summary(df)
    age = next(c for c in s["column_stats"] if c["name"] == "age")
    assert age["missing"] == 1
