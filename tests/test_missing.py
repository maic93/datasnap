"""Tests for missing value report — Day 8."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from datasnap.stats.missing import missing_report, missing_summary_line, _severity

FIXTURES = Path(__file__).parent / "fixtures"


# ── _severity ─────────────────────────────────────────────────────────────────

def test_severity_none():
    assert _severity(0) == "none"

def test_severity_low():
    assert _severity(3) == "low"

def test_severity_medium():
    assert _severity(10) == "medium"

def test_severity_high():
    assert _severity(30) == "high"

def test_severity_critical():
    assert _severity(60) == "critical"


# ── missing_report ────────────────────────────────────────────────────────────

def test_no_missing():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    r = missing_report(df)
    assert r["total_missing"] == 0
    assert r["columns_with_missing"] == 0
    assert r["complete_columns"] == 2
    assert r["total_missing_pct"] == 0.0


def test_detects_missing():
    df = pd.DataFrame({"a": [1, None, 3], "b": ["x", "y", "z"]})
    r = missing_report(df)
    assert r["total_missing"] == 1
    assert r["columns_with_missing"] == 1
    assert r["complete_columns"] == 1


def test_per_column_pct():
    df = pd.DataFrame({"a": [None, None, 1, 1], "b": [1, 2, 3, 4]})
    r = missing_report(df)
    col_a = next(c for c in r["columns"] if c["column"] == "a")
    assert col_a["pct"] == 50.0
    assert col_a["severity"] == "critical"


def test_sorted_by_missing_desc():
    df = pd.DataFrame({
        "a": [None] * 3 + [1] * 7,   # 30% missing
        "b": [None] * 8 + [1] * 2,   # 80% missing
        "c": [1] * 10,                # 0% missing
    })
    r = missing_report(df)
    missing_cols = [c for c in r["columns"] if c["missing"] > 0]
    assert missing_cols[0]["column"] == "b"
    assert missing_cols[1]["column"] == "a"


def test_total_cells():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "c": [5, 6]})
    r = missing_report(df)
    assert r["total_cells"] == 6


def test_total_missing_pct():
    df = pd.DataFrame({"a": [None, None], "b": [1, 2]})
    r = missing_report(df)
    assert r["total_missing_pct"] == 50.0


def test_sample_csv_missing():
    from datasnap.loaders.detect import load_file
    df = load_file(FIXTURES / "sample.csv")
    r = missing_report(df)
    # sample.csv has 1 missing age value
    age_col = next(c for c in r["columns"] if c["column"] == "age")
    assert age_col["missing"] == 1
    assert age_col["severity"] in ("low", "medium")


# ── missing_summary_line ──────────────────────────────────────────────────────

def test_summary_no_missing():
    df = pd.DataFrame({"a": [1, 2, 3]})
    line = missing_summary_line(df)
    assert "complete" in line.lower() or "no missing" in line.lower()


def test_summary_with_missing():
    df = pd.DataFrame({"age": [None, 1, 2], "name": ["a", "b", "c"]})
    line = missing_summary_line(df)
    assert "age" in line
    assert "%" in line


def test_summary_plural():
    df = pd.DataFrame({"a": [None, 1], "b": [None, 2], "c": [1, 2]})
    line = missing_summary_line(df)
    assert "2 columns" in line
