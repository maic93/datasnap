"""Tests for duplicate detection — Day 9."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from datasnap.quality.duplicates import (
    duplicate_report,
    find_duplicate_groups,
    duplicate_summary_line,
    _severity,
)

FIXTURES = Path(__file__).parent / "fixtures"


# ── _severity ─────────────────────────────────────────────────────────────────

def test_severity_none():
    assert _severity(0) == "none"

def test_severity_low():
    assert _severity(0.5) == "low"

def test_severity_medium():
    assert _severity(3) == "medium"

def test_severity_high():
    assert _severity(10) == "high"

def test_severity_critical():
    assert _severity(25) == "critical"


# ── duplicate_report ──────────────────────────────────────────────────────────

def test_no_duplicates():
    df = pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    r = duplicate_report(df)
    assert r["duplicate_count"] == 0
    assert r["duplicate_pct"] == 0.0
    assert r["severity"] == "none"
    assert r["unique_rows"] == 3


def test_detects_duplicates():
    df = pd.DataFrame({"a": [1, 2, 1], "b": ["x", "y", "x"]})
    r = duplicate_report(df)
    assert r["duplicate_count"] == 1
    assert r["duplicate_pct"] == pytest.approx(33.33, rel=1e-2)


def test_keeps_first_occurrence():
    df = pd.DataFrame({"a": [1, 1, 1]})
    r = duplicate_report(df)
    assert r["duplicate_count"] == 2
    assert r["unique_rows"] == 1


def test_duplicate_indices():
    df = pd.DataFrame({"a": [1, 2, 1], "b": ["x", "y", "x"]})
    r = duplicate_report(df)
    assert 2 in r["duplicate_indices"]
    assert 0 not in r["duplicate_indices"]


def test_sample_rows_returned():
    df = pd.DataFrame({"a": [1, 2, 1, 1], "b": ["x", "y", "x", "x"]})
    r = duplicate_report(df)
    assert len(r["sample"]) > 0
    assert isinstance(r["sample"][0], dict)


def test_subset_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "y", "z"]})
    # Only checking column "a" → row 0 and 1 are dupes
    r = duplicate_report(df, subset=["a"])
    assert r["duplicate_count"] == 1


def test_empty_dataframe():
    df = pd.DataFrame({"a": [], "b": []})
    r = duplicate_report(df)
    assert r["duplicate_count"] == 0
    assert r["total_rows"] == 0


def test_sample_csv_has_one_duplicate():
    from datasnap.loaders.detect import load_file
    df = load_file(FIXTURES / "sample.csv")
    r = duplicate_report(df)
    assert r["duplicate_count"] == 1
    assert r["severity"] == "high"


# ── find_duplicate_groups ─────────────────────────────────────────────────────

def test_finds_groups():
    df = pd.DataFrame({"a": [1, 2, 1, 3, 2], "b": ["x", "y", "x", "z", "y"]})
    groups = find_duplicate_groups(df)
    assert len(groups) == 2


def test_groups_sorted_by_count():
    df = pd.DataFrame({"a": [1, 1, 1, 2, 2]})
    groups = find_duplicate_groups(df)
    assert groups[0]["count"] >= groups[1]["count"]


def test_group_has_indices():
    df = pd.DataFrame({"a": [1, 2, 1]})
    groups = find_duplicate_groups(df)
    assert len(groups) == 1
    assert set(groups[0]["indices"]) == {0, 2}


def test_no_groups_when_unique():
    df = pd.DataFrame({"a": [1, 2, 3]})
    groups = find_duplicate_groups(df)
    assert groups == []


# ── duplicate_summary_line ────────────────────────────────────────────────────

def test_summary_no_duplicates():
    df = pd.DataFrame({"a": [1, 2, 3]})
    line = duplicate_summary_line(df)
    assert "unique" in line.lower() or "no duplicate" in line.lower()


def test_summary_with_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2]})
    line = duplicate_summary_line(df)
    assert "1 duplicate row" in line
    assert "%" in line


def test_summary_plural():
    df = pd.DataFrame({"a": [1, 1, 2, 2, 3]})
    line = duplicate_summary_line(df)
    assert "duplicate rows" in line
