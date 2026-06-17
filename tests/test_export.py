"""Tests for report export — Day 12."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from datasnap.reports.export import save_report, load_report
from datasnap.loaders.detect import load_file
from datasnap.stats.summary import compute_summary
from datasnap.quality.checks import run_quality_checks

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_data():
    df = load_file(FIXTURES / "sample.csv")
    summary = compute_summary(df)
    quality = run_quality_checks(df)
    return summary, quality


# ── JSON export ───────────────────────────────────────────────────────────────

def test_save_json(tmp_path, sample_data):
    summary, quality = sample_data
    out = tmp_path / "report.json"
    saved = save_report(str(out), summary, quality, filename="sample.csv")
    assert saved.exists()
    assert saved.suffix == ".json"


def test_json_content_valid(tmp_path, sample_data):
    summary, quality = sample_data
    out = tmp_path / "report.json"
    save_report(str(out), summary, quality)
    data = json.loads(out.read_text())
    assert "summary" in data
    assert "quality" in data
    assert "generated_at" in data


def test_json_includes_filename(tmp_path, sample_data):
    summary, quality = sample_data
    out = tmp_path / "report.json"
    save_report(str(out), summary, quality, filename="myfile.csv")
    data = json.loads(out.read_text())
    assert data["source_file"] == "myfile.csv"


def test_json_without_quality(tmp_path, sample_data):
    summary, _ = sample_data
    out = tmp_path / "report.json"
    save_report(str(out), summary, None)
    data = json.loads(out.read_text())
    assert "quality" not in data


def test_json_summary_matches(tmp_path, sample_data):
    summary, quality = sample_data
    out = tmp_path / "report.json"
    save_report(str(out), summary, quality)
    data = json.loads(out.read_text())
    assert data["summary"]["rows"] == summary["rows"]
    assert data["summary"]["columns"] == summary["columns"]


# ── Markdown export ───────────────────────────────────────────────────────────

def test_save_markdown(tmp_path, sample_data):
    summary, quality = sample_data
    out = tmp_path / "report.md"
    saved = save_report(str(out), summary, quality)
    assert saved.exists()


def test_markdown_has_header(tmp_path, sample_data):
    summary, quality = sample_data
    out = tmp_path / "report.md"
    save_report(str(out), summary, quality)
    content = out.read_text()
    assert "# datasnap report" in content


def test_markdown_includes_filename(tmp_path, sample_data):
    summary, quality = sample_data
    out = tmp_path / "report.md"
    save_report(str(out), summary, quality, filename="data.csv")
    content = out.read_text()
    assert "data.csv" in content


def test_markdown_has_columns_table(tmp_path, sample_data):
    summary, quality = sample_data
    out = tmp_path / "report.md"
    save_report(str(out), summary, quality)
    content = out.read_text()
    assert "## Columns" in content
    assert "| Column | Type" in content


def test_markdown_has_quality_section(tmp_path, sample_data):
    summary, quality = sample_data
    out = tmp_path / "report.md"
    save_report(str(out), summary, quality)
    content = out.read_text()
    assert "## Quality" in content
    assert "Score:" in content


def test_markdown_without_quality_skips_section(tmp_path, sample_data):
    summary, _ = sample_data
    out = tmp_path / "report.md"
    save_report(str(out), summary, None)
    content = out.read_text()
    assert "## Quality" not in content


def test_markdown_lists_all_columns(tmp_path, sample_data):
    summary, quality = sample_data
    out = tmp_path / "report.md"
    save_report(str(out), summary, quality)
    content = out.read_text()
    for col in summary["column_stats"]:
        assert col["name"] in content


# ── unsupported format ────────────────────────────────────────────────────────

def test_unsupported_extension_raises(tmp_path, sample_data):
    summary, quality = sample_data
    out = tmp_path / "report.txt"
    with pytest.raises(ValueError, match="Unsupported"):
        save_report(str(out), summary, quality)


# ── load_report ───────────────────────────────────────────────────────────────

def test_load_report_roundtrip(tmp_path, sample_data):
    summary, quality = sample_data
    out = tmp_path / "report.json"
    save_report(str(out), summary, quality)
    loaded = load_report(str(out))
    assert loaded["summary"]["rows"] == summary["rows"]


def test_load_report_rejects_non_json(tmp_path):
    out = tmp_path / "report.md"
    out.write_text("# hello")
    with pytest.raises(ValueError, match="json"):
        load_report(str(out))
