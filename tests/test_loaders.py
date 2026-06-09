"""Tests for file loaders — Day 4."""

from __future__ import annotations

from pathlib import Path

import pytest
import pandas as pd

from datasnap.loaders.detect import load_file, supported_formats
from datasnap.loaders.csv_loader import load_csv, _detect_delimiter
from datasnap.loaders.json_loader import load_json

FIXTURES = Path(__file__).parent / "fixtures"


# ── CSV ──────────────────────────────────────────────────────────────────────

def test_load_csv_returns_dataframe():
    df = load_file(FIXTURES / "sample.csv")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 11


def test_load_csv_columns():
    df = load_csv(FIXTURES / "sample.csv")
    assert "name" in df.columns
    assert "salary" in df.columns


def test_detect_delimiter_comma(tmp_path):
    f = tmp_path / "test.csv"
    f.write_text("a,b,c\n1,2,3\n")
    assert _detect_delimiter(f, "utf-8") == ","


def test_detect_delimiter_semicolon(tmp_path):
    f = tmp_path / "test.csv"
    f.write_text("a;b;c\n1;2;3\n")
    assert _detect_delimiter(f, "utf-8") == ";"


def test_semicolon_csv(tmp_path):
    f = tmp_path / "semi.csv"
    f.write_text("name;age;city\nAlice;30;Zagreb\nBob;25;Split\n")
    df = load_csv(f)
    assert list(df.columns) == ["name", "age", "city"]
    assert len(df) == 2


def test_empty_csv_raises(tmp_path):
    f = tmp_path / "empty.csv"
    f.write_text("col1,col2\n")
    with pytest.raises(ValueError, match="empty"):
        load_csv(f)


# ── TSV ───────────────────────────────────────────────────────────────────────

def test_load_tsv():
    df = load_file(FIXTURES / "sample.tsv")
    assert list(df.columns) == ["id", "name", "age", "city"]
    assert len(df) == 3


# ── JSON ─────────────────────────────────────────────────────────────────────

def test_load_json_array():
    df = load_file(FIXTURES / "sample.json")
    assert len(df) == 5
    assert "product" in df.columns


def test_load_json_nested():
    df = load_file(FIXTURES / "nested.json")
    assert len(df) == 3
    assert "name" in df.columns
    assert "score" in df.columns


def test_load_jsonl():
    df = load_file(FIXTURES / "sample.jsonl")
    assert len(df) == 5
    assert "product" in df.columns


def test_json_missing_values_preserved():
    df = load_file(FIXTURES / "sample.json")
    # Gadget Y has null stock
    assert df["stock"].isna().sum() == 1


# ── detect ────────────────────────────────────────────────────────────────────

def test_unsupported_extension_raises():
    with pytest.raises(ValueError, match="Unsupported"):
        load_file(Path("data.xlsx"))


def test_file_not_found_raises():
    with pytest.raises(FileNotFoundError):
        load_file(Path("nonexistent.csv"))


def test_supported_formats_returns_list():
    formats = supported_formats()
    assert ".csv" in formats
    assert ".json" in formats
    assert ".jsonl" in formats
    assert ".tsv" in formats
