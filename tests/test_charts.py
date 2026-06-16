"""Tests for terminal charts — Day 11."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch, MagicMock

import pandas as pd
import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def _mock_plotext():
    """Return a mock plotext module."""
    plt = MagicMock()
    return plt


# ── plot_histogram ────────────────────────────────────────────────────────────

def test_histogram_calls_plotext():
    with patch.dict("sys.modules", {"plotext": _mock_plotext()}):
        from datasnap.charts.terminal import plot_histogram
        s = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0] * 4, name="value")
        plot_histogram(s)  # Should not raise


def test_histogram_empty_series_no_crash():
    with patch.dict("sys.modules", {"plotext": _mock_plotext()}):
        from datasnap.charts.terminal import plot_histogram
        s = pd.Series([None, None], dtype=float, name="empty")
        plot_histogram(s)  # Should handle gracefully


def test_histogram_nulls_ignored():
    with patch.dict("sys.modules", {"plotext": _mock_plotext()}):
        from datasnap.charts.terminal import plot_histogram
        s = pd.Series([1.0, None, 3.0, None, 5.0], name="val")
        plot_histogram(s)  # Should not raise


def test_histogram_custom_title():
    mock_plt = _mock_plotext()
    with patch.dict("sys.modules", {"plotext": mock_plt}):
        from datasnap.charts import terminal
        import importlib
        importlib.reload(terminal)
        s = pd.Series([1.0, 2.0, 3.0], name="score")
        terminal.plot_histogram(s, title="My Custom Title")
        mock_plt.title.assert_called_with("My Custom Title")


# ── plot_bar_chart ────────────────────────────────────────────────────────────

def test_bar_chart_calls_plotext():
    with patch.dict("sys.modules", {"plotext": _mock_plotext()}):
        from datasnap.charts.terminal import plot_bar_chart
        s = pd.Series(["a", "b", "a", "c", "a"], name="category")
        plot_bar_chart(s)  # Should not raise


def test_bar_chart_empty_no_crash():
    with patch.dict("sys.modules", {"plotext": _mock_plotext()}):
        from datasnap.charts.terminal import plot_bar_chart
        s = pd.Series([None, None], name="empty")
        plot_bar_chart(s)  # Should handle gracefully


def test_bar_chart_top_n_respected():
    mock_plt = _mock_plotext()
    with patch.dict("sys.modules", {"plotext": mock_plt}):
        from datasnap.charts import terminal
        import importlib
        importlib.reload(terminal)
        s = pd.Series(list("abcdefghij"), name="col")
        terminal.plot_bar_chart(s, top_n=3)
        # bar was called with 3 labels
        call_args = mock_plt.bar.call_args
        assert len(call_args[0][0]) == 3


# ── plot_all_numeric ──────────────────────────────────────────────────────────

def test_plot_all_numeric_no_crash():
    with patch.dict("sys.modules", {"plotext": _mock_plotext()}):
        from datasnap.charts.terminal import plot_all_numeric
        from datasnap.loaders.detect import load_file
        df = load_file(FIXTURES / "sample.csv")
        plot_all_numeric(df, max_cols=2)  # Should not raise


def test_plot_all_numeric_skips_non_numeric():
    with patch.dict("sys.modules", {"plotext": _mock_plotext()}):
        from datasnap.charts.terminal import plot_all_numeric
        df = pd.DataFrame({"name": ["Alice", "Bob", "Carol"]})
        plot_all_numeric(df)  # no numeric cols — should not raise


# ── plot_all_categorical ──────────────────────────────────────────────────────

def test_plot_all_categorical_no_crash():
    with patch.dict("sys.modules", {"plotext": _mock_plotext()}):
        from datasnap.charts.terminal import plot_all_categorical
        from datasnap.loaders.detect import load_file
        df = load_file(FIXTURES / "sample.csv")
        plot_all_categorical(df, max_cols=2)  # Should not raise


def test_plot_all_categorical_skips_numeric():
    with patch.dict("sys.modules", {"plotext": _mock_plotext()}):
        from datasnap.charts.terminal import plot_all_categorical
        df = pd.DataFrame({"value": [1.0, 2.0, 3.0, 4.0, 5.0]})
        plot_all_categorical(df)  # no categorical cols — should not raise


# ── plot_summary ──────────────────────────────────────────────────────────────

def test_plot_summary_no_crash():
    with patch.dict("sys.modules", {"plotext": _mock_plotext()}):
        from datasnap.charts.terminal import plot_summary
        from datasnap.loaders.detect import load_file
        df = load_file(FIXTURES / "sample.csv")
        plot_summary(df, max_numeric=2, max_categorical=1)


# ── missing plotext ───────────────────────────────────────────────────────────

def test_missing_plotext_no_crash():
    """When plotext is not installed, functions should degrade gracefully."""
    import sys
    original = sys.modules.pop("plotext", None)
    try:
        from datasnap.charts import terminal
        import importlib
        importlib.reload(terminal)
        s = pd.Series([1.0, 2.0, 3.0], name="val")
        terminal.plot_histogram(s)  # Should print warning, not raise
    finally:
        if original is not None:
            sys.modules["plotext"] = original
