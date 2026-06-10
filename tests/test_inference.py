"""Tests for column type inference — Day 5."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from datasnap.stats.inference import (
    infer_column_type,
    infer_all_columns,
    columns_by_type,
)

FIXTURES = Path(__file__).parent / "fixtures"


# ── infer_column_type ─────────────────────────────────────────────────────────

def test_numeric_float():
    s = pd.Series([1.1, 2.2, 3.3, 4.4], name="price")
    assert infer_column_type(s) == "numeric"


def test_numeric_int():
    s = pd.Series(list(range(100)), name="age")
    assert infer_column_type(s) == "numeric"


def test_categorical_string():
    s = pd.Series(["cat", "dog", "bird", "cat"], name="animal")
    assert infer_column_type(s) == "categorical"


def test_categorical_low_cardinality_int():
    # Only 3 unique values out of 100 → treated as categorical
    s = pd.Series([1, 2, 3] * 33 + [1], name="status")
    assert infer_column_type(s) == "categorical"


def test_boolean_true_false():
    s = pd.Series([True, False, True, False], name="active")
    assert infer_column_type(s) == "boolean"


def test_boolean_yes_no():
    s = pd.Series(["yes", "no", "yes", "yes"], name="confirmed")
    assert infer_column_type(s) == "boolean"


def test_datetime_iso():
    s = pd.Series(["2024-01-01", "2024-06-15", "2023-12-31"], name="date")
    assert infer_column_type(s) == "datetime"


def test_datetime_slash_format():
    s = pd.Series(["01/15/2024", "06/20/2024", "12/31/2023"], name="date")
    assert infer_column_type(s) == "datetime"


def test_unknown_all_nulls():
    s = pd.Series([None, None, None], name="empty")
    assert infer_column_type(s) == "unknown"


def test_mixed_nulls_still_inferred():
    s = pd.Series([1.0, None, 3.0, None, 5.0], name="vals")
    assert infer_column_type(s) == "numeric"


# ── infer_all_columns ─────────────────────────────────────────────────────────

def test_infer_all_columns_returns_dict():
    df = pd.DataFrame({
        "age": [25, 30, 35],
        "name": ["Alice", "Bob", "Carol"],
        "joined": ["2020-01-01", "2021-06-15", "2022-03-10"],
    })
    result = infer_all_columns(df)
    assert result["age"] == "numeric"
    assert result["name"] == "categorical"
    assert result["joined"] == "datetime"


def test_infer_all_columns_sample_csv():
    from datasnap.loaders.detect import load_file
    df = load_file(FIXTURES / "sample.csv")
    types = infer_all_columns(df)
    assert types["salary"] == "numeric"
    assert types["department"] == "categorical"


# ── columns_by_type ───────────────────────────────────────────────────────────

def test_columns_by_type_groups_correctly():
    df = pd.DataFrame({
        "price": [1.1, 2.2, 3.3],
        "category": ["a", "b", "c"],
        "active": [True, False, True],
    })
    grouped = columns_by_type(df)
    assert "price" in grouped["numeric"]
    assert "category" in grouped["categorical"]
    assert "active" in grouped["boolean"]


def test_columns_by_type_all_keys_present():
    df = pd.DataFrame({"x": [1, 2, 3]})
    grouped = columns_by_type(df)
    assert set(grouped.keys()) == {"numeric", "categorical", "datetime", "boolean", "unknown"}
