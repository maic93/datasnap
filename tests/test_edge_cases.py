"""Edge case tests across all modules — Day 13."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from datasnap.stats.summary import compute_summary
from datasnap.stats.inference import infer_column_type
from datasnap.quality.checks import run_quality_checks
from datasnap.loaders.detect import load_file

FIXTURES = Path(__file__).parent / "fixtures"


# ── single column edge cases ──────────────────────────────────────────────────

def test_single_column_dataframe():
    df = pd.DataFrame({"only_col": [1, 2, 3, 4, 5]})
    s = compute_summary(df)
    assert s["columns"] == 1
    assert s["rows"] == 5


def test_single_row_dataframe():
    df = pd.DataFrame({"a": [1], "b": ["x"], "c": [1.5]})
    s = compute_summary(df)
    assert s["rows"] == 1


def test_all_missing_column():
    df = pd.DataFrame({"empty": [None, None, None], "ok": [1, 2, 3]})
    s = compute_summary(df)
    empty_col = next(c for c in s["column_stats"] if c["name"] == "empty")
    assert empty_col["missing_pct"] == 100.0
    assert empty_col["type"] == "unknown"


# ── special characters and unicode ───────────────────────────────────────────

def test_unicode_values():
    df = pd.DataFrame({"name": ["Müller", "日本語", "Šime", "François"]})
    s = compute_summary(df)
    name_col = next(c for c in s["column_stats"] if c["name"] == "name")
    assert name_col["unique"] == 4


def test_column_with_special_chars_in_name(tmp_path):
    f = tmp_path / "test.csv"
    f.write_text("col with spaces,col-with-dash,col_underscore\n1,2,3\n")
    df = load_file(f)
    assert "col with spaces" in df.columns


def test_values_with_commas_quoted(tmp_path):
    f = tmp_path / "test.csv"
    f.write_text('name,note\n"Alice","hello, world"\n"Bob","fine"\n')
    df = load_file(f)
    assert len(df) == 2
    assert df.iloc[0]["note"] == "hello, world"


# ── numeric edge cases ────────────────────────────────────────────────────────

def test_negative_numbers():
    df = pd.DataFrame({"val": [-10.0, -5.0, 0.0, 5.0, 10.0]})
    s = compute_summary(df)
    val_col = next(c for c in s["column_stats"] if c["name"] == "val")
    assert val_col["min"] == -10.0
    assert val_col["max"] == 10.0


def test_very_large_numbers():
    df = pd.DataFrame({"val": [1e10, 2e10, 3e10]})
    s = compute_summary(df)
    val_col = next(c for c in s["column_stats"] if c["name"] == "val")
    assert val_col["type"] == "numeric"


def test_very_small_numbers():
    df = pd.DataFrame({"val": [0.0001, 0.0002, 0.0003]})
    s = compute_summary(df)
    val_col = next(c for c in s["column_stats"] if c["name"] == "val")
    assert val_col["type"] == "numeric"


def test_mixed_int_float():
    df = pd.DataFrame({"val": [1, 2.5, 3, 4.5]})
    s = compute_summary(df)
    val_col = next(c for c in s["column_stats"] if c["name"] == "val")
    assert val_col["type"] == "numeric"


# ── quality checks edge cases ────────────────────────────────────────────────

def test_quality_check_single_column():
    df = pd.DataFrame({"a": [1, 2, 3, 4, 5]})
    q = run_quality_checks(df)
    assert 0 <= q["quality_score"] <= 100


def test_quality_check_all_same_value():
    df = pd.DataFrame({"a": [1, 1, 1, 1, 1]})
    q = run_quality_checks(df)
    assert "a" in q["constant_columns"]


def test_quality_check_two_rows():
    df = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    q = run_quality_checks(df)
    assert q["duplicate_rows"]["count"] == 0


# ── inference edge cases ──────────────────────────────────────────────────────

def test_inference_single_value_series():
    s = pd.Series([42])
    result = infer_column_type(s)
    assert result in ("numeric", "categorical")


def test_inference_two_unique_numeric_values():
    s = pd.Series([0, 1, 0, 1, 0, 1] * 10)
    result = infer_column_type(s)
    assert result == "boolean"  # 0/1 is treated as boolean


def test_inference_negative_floats():
    s = pd.Series([-1.5, -2.5, -3.5])
    assert infer_column_type(s) == "numeric"


# ── real file edge cases ──────────────────────────────────────────────────────

def test_full_pipeline_sample_csv():
    """End-to-end smoke test: load → summary → quality, no exceptions."""
    df = load_file(FIXTURES / "sample.csv")
    summary = compute_summary(df)
    quality = run_quality_checks(df)
    assert summary["rows"] > 0
    assert 0 <= quality["quality_score"] <= 100


def test_full_pipeline_sample_json():
    df = load_file(FIXTURES / "sample.json")
    summary = compute_summary(df)
    quality = run_quality_checks(df)
    assert summary["rows"] > 0
    assert 0 <= quality["quality_score"] <= 100


def test_full_pipeline_sample_jsonl():
    df = load_file(FIXTURES / "sample.jsonl")
    summary = compute_summary(df)
    quality = run_quality_checks(df)
    assert summary["rows"] > 0


def test_full_pipeline_nested_json():
    df = load_file(FIXTURES / "nested.json")
    summary = compute_summary(df)
    assert summary["rows"] > 0


def test_full_pipeline_tsv():
    df = load_file(FIXTURES / "sample.tsv")
    summary = compute_summary(df)
    assert summary["rows"] > 0
