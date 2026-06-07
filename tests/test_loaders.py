"""Tests for file loaders."""

from pathlib import Path
import pytest
from datasnap.loaders.detect import load_file

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_csv():
    df = load_file(FIXTURES / "sample.csv")
    assert len(df) == 11
    assert "salary" in df.columns


def test_load_json():
    df = load_file(FIXTURES / "sample.json")
    assert len(df) == 5
    assert "product" in df.columns


def test_unsupported_type_raises():
    with pytest.raises(ValueError, match="Unsupported"):
        load_file(Path("data.xlsx"))
