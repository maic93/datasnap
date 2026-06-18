"""Integration tests for the CLI — Day 13."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def run_cli(*args: str) -> subprocess.CompletedProcess:
    """Run the datasnap CLI as a subprocess and return the result."""
    return subprocess.run(
        [sys.executable, "-m", "datasnap.cli", *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


# ── basic invocation ──────────────────────────────────────────────────────────

def test_help_flag():
    result = run_cli("--help")
    assert result.returncode == 0
    assert "datasnap" in result.stdout.lower()
    assert "usage" in result.stdout.lower()


def test_version_flag():
    result = run_cli("--version")
    assert result.returncode == 0
    assert "datasnap" in result.stdout.lower()


def test_no_args_shows_error():
    result = run_cli()
    assert result.returncode != 0


def test_profile_csv():
    result = run_cli(str(FIXTURES / "sample.csv"))
    assert result.returncode == 0
    assert "sample.csv" in result.stdout
    assert "rows" in result.stdout.lower() or "row" in result.stdout.lower()


def test_profile_json():
    result = run_cli(str(FIXTURES / "sample.json"))
    assert result.returncode == 0
    assert "sample.json" in result.stdout


def test_profile_missing_file():
    result = run_cli("does_not_exist.csv")
    assert result.returncode != 0
    assert "not found" in result.stderr.lower() or "not found" in result.stdout.lower()


def test_profile_unsupported_extension(tmp_path):
    bad_file = tmp_path / "data.xlsx"
    bad_file.write_text("dummy")
    result = run_cli(str(bad_file))
    assert result.returncode != 0


# ── flags ─────────────────────────────────────────────────────────────────────

def test_no_quality_flag():
    result = run_cli(str(FIXTURES / "sample.csv"), "--no-quality")
    assert result.returncode == 0
    assert "Quality score" not in result.stdout


def test_quality_shown_by_default():
    result = run_cli(str(FIXTURES / "sample.csv"))
    assert result.returncode == 0
    assert "Quality score" in result.stdout


def test_output_json_flag(tmp_path):
    out = tmp_path / "report.json"
    result = run_cli(str(FIXTURES / "sample.csv"), "--output", str(out))
    assert result.returncode == 0
    assert out.exists()
    data = json.loads(out.read_text())
    assert "summary" in data


def test_output_markdown_flag(tmp_path):
    out = tmp_path / "report.md"
    result = run_cli(str(FIXTURES / "sample.csv"), "--output", str(out))
    assert result.returncode == 0
    assert out.exists()
    assert "# datasnap report" in out.read_text()


def test_diff_requires_two_files():
    result = run_cli(str(FIXTURES / "sample.csv"), "--diff")
    assert result.returncode != 0


def test_diff_with_two_files():
    result = run_cli(
        str(FIXTURES / "sample.csv"),
        str(FIXTURES / "sample.csv"),
        "--diff",
    )
    assert result.returncode == 0


# ── multiple files ────────────────────────────────────────────────────────────

def test_multiple_files():
    result = run_cli(str(FIXTURES / "sample.csv"), str(FIXTURES / "sample.json"))
    assert result.returncode == 0
    assert "sample.csv" in result.stdout
    assert "sample.json" in result.stdout
