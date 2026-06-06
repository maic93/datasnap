"""Tests for file loaders."""

from pathlib import Path

import pandas as pd
import pytest

from datasnap.loaders.detect import load_file
from datasnap.loaders.csv_loader import load_csv

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_csv_returns_dataframe():
    df = load_file(FIXTURES / "sample.csv")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 11


def test_load_csv_columns():
    df = load_csv(FIXTURES / "sample.csv")
    assert "name" in df.columns
    assert "salary" in df.columns


def test_unsupported_extension_raises():
    with pytest.raises(ValueError, match="Unsupported"):
        load_file(Path("data.xlsx"))


def test_missing_file_raises():
    with pytest.raises(Exception):
        load_file(Path("nonexistent.csv"))
