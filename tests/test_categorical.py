"""Tests for categorical stats — Day 7."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from datasnap.stats.categorical import (
    categorical_stats,
    categorical_stats_all,
    summarise_categorical,
    value_counts_table,
)

FIXTURES = Path(__file__).parent / "fixtures"


# ── categorical_stats ─────────────────────────────────────────────────────────

def test_basic_categorical():
    s = pd.Series(["cat", "dog", "cat", "bird", "cat"])
    r = categorical_stats(s)
    assert r["unique"] == 3
    assert r["mode"] == "cat"
    assert r["mode_count"] == 3
    assert r["mode_pct"] == 60.0
    assert r["count"] == 5


def test_top_values_sorted():
    s = pd.Series(["a", "b", "b", "c", "c", "c"])
    r = categorical_stats(s)
    assert r["top_values"][0]["value"] == "c"
    assert r["top_values"][0]["count"] == 3
    assert r["top_values"][1]["value"] == "b"


def test_top_values_include_pct():
    s = pd.Series(["x", "x", "y"])
    r = categorical_stats(s)
    assert r["top_values"][0]["pct"] == pytest.approx(66.67, rel=1e-2)


def test_top_n_respected():
    s = pd.Series(list("abcdefghijklmnop"))
    r = categorical_stats(s, top_n=5)
    assert len(r["top_values"]) == 5


def test_least_common():
    s = pd.Series(["a"] * 10 + ["b"] * 3 + ["c"])
    r = categorical_stats(s)
    assert r["least_common"][0]["value"] == "c"
    assert r["least_common"][0]["count"] == 1


def test_cardinality_ratio():
    s = pd.Series(["a", "b", "c", "d"])  # all unique → ratio 1.0
    r = categorical_stats(s)
    assert r["cardinality_ratio"] == 1.0


def test_low_cardinality_ratio():
    s = pd.Series(["yes", "no"] * 50)  # 2 unique / 100 → 0.02
    r = categorical_stats(s)
    assert r["cardinality_ratio"] == 0.02


def test_ignores_nulls():
    s = pd.Series(["a", None, "b", None, "a"])
    r = categorical_stats(s)
    assert r["count"] == 3
    assert r["unique"] == 2


def test_all_nulls_empty():
    s = pd.Series([None, None, None])
    r = categorical_stats(s)
    assert r["count"] == 0
    assert r["unique"] == 0
    assert r["mode"] is None


def test_boolean_series():
    s = pd.Series([True, False, True, True])
    r = categorical_stats(s)
    assert r["unique"] == 2
    assert r["mode"] == "True"
    assert r["mode_count"] == 3


# ── categorical_stats_all ─────────────────────────────────────────────────────

def test_categorical_stats_all_filters():
    from datasnap.loaders.detect import load_file
    df = load_file(FIXTURES / "sample.csv")
    result = categorical_stats_all(df)
    assert "department" in result
    assert "name" in result
    assert "salary" not in result   # numeric
    assert "age" not in result      # numeric


def test_categorical_stats_all_has_keys():
    from datasnap.loaders.detect import load_file
    df = load_file(FIXTURES / "sample.csv")
    result = categorical_stats_all(df)
    for col_stats in result.values():
        assert "unique" in col_stats
        assert "top_values" in col_stats
        assert "mode" in col_stats


# ── summarise_categorical ─────────────────────────────────────────────────────

def test_summarise_format():
    s = pd.Series(["Engineering"] * 5 + ["Marketing"] * 3 + ["Sales"] * 2)
    summary = summarise_categorical(s)
    assert "3 unique" in summary
    assert "Engineering" in summary
    assert "50.0%" in summary


def test_summarise_empty():
    s = pd.Series([None, None])
    assert summarise_categorical(s) == "no data"


# ── value_counts_table ────────────────────────────────────────────────────────

def test_value_counts_table_structure():
    s = pd.Series(["a", "b", "a", "c", "a"])
    table = value_counts_table(s)
    assert table[0]["value"] == "a"
    assert table[0]["count"] == 3
    assert table[0]["pct"] == 60.0
    assert len(table) == 3


def test_value_counts_table_top_n():
    s = pd.Series(list("abcdefgh"))
    table = value_counts_table(s, top_n=3)
    assert len(table) == 3


def test_value_counts_table_empty():
    s = pd.Series([None, None])
    assert value_counts_table(s) == []
