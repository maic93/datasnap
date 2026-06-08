"""Tests for file loaders."""

from pathlib import Path
import pytest
import pandas as pd
from datasnap.loaders.detect import load_file
from datasnap.loaders.csv_loader import load_csv, _detect_delimiter

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_csv_returns_dataframe():
    df = load_file(FIXTURES / "sample.csv")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 11


def test_load_csv_columns():
    df = load_csv(FIXTURES / "sample.csv")
    assert "name" in df.columns
    assert "salary" in df.columns


def test_load_json():
    df = load_file(FIXTURES / "sample.json")
    assert len(df) == 5
    assert "product" in df.columns


def test_unsupported_extension_raises():
    with pytest.raises(ValueError, match="Unsupported"):
        load_file(Path("data.xlsx"))


def test_detect_delimiter_comma(tmp_path):
    f = tmp_path / "test.csv"
    f.write_text("a,b,c\n1,2,3\n")
    assert _detect_delimiter(f, "utf-8") == ","


def test_detect_delimiter_semicolon(tmp_path):
    f = tmp_path / "test.csv"
    f.write_text("a;b;c\n1;2;3\n")
    assert _detect_delimiter(f, "utf-8") == ";"


def test_empty_csv_raises(tmp_path):
    f = tmp_path / "empty.csv"
    f.write_text("col1,col2\n")
    with pytest.raises(ValueError, match="empty"):
        load_csv(f)


def test_semicolon_csv(tmp_path):
    f = tmp_path / "semi.csv"
    f.write_text("name;age;city\nAlice;30;Zagreb\nBob;25;Split\n")
    df = load_csv(f)
    assert list(df.columns) == ["name", "age", "city"]
    assert len(df) == 2
