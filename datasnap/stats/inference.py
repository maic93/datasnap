"""Column type inference for DataFrames."""

from __future__ import annotations

from typing import List

import pandas as pd


# Minimum fraction of values that must parse as dates
_DATE_THRESHOLD = 0.8
# Maximum unique ratio for a numeric column to be treated as categorical
_CATEGORICAL_INT_THRESHOLD = 0.05


def infer_column_type(series: pd.Series) -> str:
    """Infer the logical type of a pandas Series.

    Returns one of: 'numeric', 'categorical', 'datetime', 'boolean', 'unknown'

    Args:
        series: A single DataFrame column.

    Returns:
        String label for the inferred type.
    """
    # Drop nulls for type detection
    sample = series.dropna()

    if len(sample) == 0:
        return "unknown"

    # Boolean check first (before numeric)
    if _is_boolean(sample):
        return "boolean"

    # Pandas native numeric
    if pd.api.types.is_numeric_dtype(series):
        return _numeric_or_categorical(series)

    # Pandas native datetime
    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    # String/object dtype — try datetime parse, else categorical
    if series.dtype == object or pd.api.types.is_string_dtype(series):
        if _looks_like_datetime(sample):
            return "datetime"
        return "categorical"

    return "categorical"


def infer_all_columns(df: pd.DataFrame) -> dict[str, str]:
    """Return a mapping of column name → inferred type for all columns.

    Args:
        df: Input DataFrame.

    Returns:
        Dict like {"age": "numeric", "name": "categorical", ...}
    """
    return {col: infer_column_type(df[col]) for col in df.columns}


def columns_by_type(df: pd.DataFrame) -> dict[str, List[str]]:
    """Group column names by their inferred type.

    Args:
        df: Input DataFrame.

    Returns:
        Dict like {"numeric": ["age", "salary"], "categorical": ["name"], ...}
    """
    result: dict[str, List[str]] = {
        "numeric": [],
        "categorical": [],
        "datetime": [],
        "boolean": [],
        "unknown": [],
    }
    for col, col_type in infer_all_columns(df).items():
        result[col_type].append(col)
    return result


# ── helpers ───────────────────────────────────────────────────────────────────

def _is_boolean(sample: pd.Series) -> bool:
    """True if the series looks like a boolean column."""
    if pd.api.types.is_bool_dtype(sample):
        return True
    unique_vals = set(sample.astype(str).str.lower().unique())
    bool_sets = [
        {"true", "false"},
        {"yes", "no"},
        {"1", "0"},
        {"y", "n"},
    ]
    return unique_vals in bool_sets


def _numeric_or_categorical(series: pd.Series) -> str:
    """Decide if a numeric column is really a categorical ID."""
    # Float columns are always numeric
    if pd.api.types.is_float_dtype(series):
        return "numeric"
    # Integer columns with very few unique values relative to total → categorical
    n_unique = series.nunique()
    n_total = len(series.dropna())
    if n_total > 0 and n_unique / n_total <= _CATEGORICAL_INT_THRESHOLD and n_unique <= 20:
        return "categorical"
    return "numeric"


def _looks_like_datetime(sample: pd.Series, min_fraction: float = _DATE_THRESHOLD) -> bool:
    """Return True if enough values in the sample parse as datetimes."""
    DATE_PATTERNS = [
        r"^\d{4}-\d{2}-\d{2}",       # 2024-01-15
        r"^\d{2}/\d{2}/\d{4}",       # 01/15/2024
        r"^\d{2}-\d{2}-\d{4}",       # 15-01-2024
        r"^\d{4}/\d{2}/\d{2}",       # 2024/01/15
        r"^\d{4}-\d{2}-\d{2}T\d{2}", # ISO 8601
    ]
    str_sample = sample.astype(str).head(50)
    n = len(str_sample)
    if n == 0:
        return False

    # Lower threshold for very small samples
    threshold = 0.6 if n < 10 else min_fraction

    for pattern in DATE_PATTERNS:
        if str_sample.str.match(pattern).sum() / n >= threshold:
            return True

    # Fallback: pandas date parser
    try:
        parsed = pd.to_datetime(str_sample, errors="coerce", format="mixed")
        if parsed.notna().sum() / n >= threshold:
            return True
    except Exception:
        pass

    return False
