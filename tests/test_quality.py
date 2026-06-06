"""Tests for the quality.checks module."""

from pathlib import Path

from datasnap.loaders.detect import load_file
from datasnap.quality.checks import run_quality_checks

FIXTURES = Path(__file__).parent / "fixtures"


def test_detects_duplicate_rows():
    df = load_file(FIXTURES / "sample.csv")
    q = run_quality_checks(df)
    assert q["duplicate_rows"]["count"] == 1


def test_quality_score_between_0_and_100():
    df = load_file(FIXTURES / "sample.csv")
    q = run_quality_checks(df)
    assert 0 <= q["quality_score"] <= 100


def test_outlier_report_is_list():
    df = load_file(FIXTURES / "sample.csv")
    q = run_quality_checks(df)
    assert isinstance(q["outliers"], list)


def test_constant_columns_is_list():
    df = load_file(FIXTURES / "sample.csv")
    q = run_quality_checks(df)
    assert isinstance(q["constant_columns"], list)
