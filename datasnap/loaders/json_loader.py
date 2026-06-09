"""JSON and JSONL file loader with validation."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


def load_json(path: Path, orient: Optional[str] = None) -> pd.DataFrame:
    """Load a JSON or JSONL file into a DataFrame.

    Supports:
      - Standard JSON arrays:        [{"a": 1}, {"a": 2}]
      - Newline-delimited JSON:      {"a": 1}\\n{"a": 2}
      - Nested objects (records):    {"data": [{"a": 1}]}

    Args:
        path: Path to the .json or .jsonl file.
        orient: pandas orient hint (auto-detected if None).

    Returns:
        Loaded DataFrame.

    Raises:
        RuntimeError: If the file cannot be parsed.
        ValueError: If the file is empty or not tabular.
    """
    is_jsonl = path.suffix.lower() == ".jsonl"

    if is_jsonl:
        return _load_jsonl(path)

    return _load_json(path, orient)


def _load_jsonl(path: Path) -> pd.DataFrame:
    """Load newline-delimited JSON (one object per line)."""
    try:
        df = pd.read_json(path, lines=True)
    except Exception as exc:
        raise RuntimeError(f"Failed to read JSONL '{path}': {exc}") from exc
    _validate(df, path)
    return df


def _load_json(path: Path, orient: Optional[str]) -> pd.DataFrame:
    """Load a standard JSON file, trying multiple strategies."""
    raw = _read_text(path)

    # Strategy 1: direct read with pandas
    try:
        df = pd.read_json(path, orient=orient)
        if _is_valid(df):
            return df
    except Exception:
        pass

    # Strategy 2: parse via stdlib json, then normalise
    try:
        import json
        data = json.loads(raw)
        df = _normalise(data, path)
        if _is_valid(df):
            return df
    except Exception as exc:
        raise RuntimeError(f"Failed to parse JSON '{path}': {exc}") from exc

    raise ValueError(f"Could not convert '{path}' to a table. Check the structure.")


def _normalise(data: object, path: Path) -> pd.DataFrame:
    """Turn common JSON shapes into a DataFrame."""
    from pandas import json_normalize

    if isinstance(data, list):
        return pd.DataFrame(data)

    if isinstance(data, dict):
        # Try first list value (e.g. {"data": [...], "meta": {...}})
        for v in data.values():
            if isinstance(v, list) and len(v) > 0:
                return pd.DataFrame(v)
        # Flat dict — treat as single row
        return pd.DataFrame([data])

    raise ValueError(f"Unsupported JSON root type '{type(data).__name__}' in '{path}'.")


def _read_text(path: Path) -> str:
    for encoding in ["utf-8", "latin-1", "cp1252"]:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise RuntimeError(f"Cannot decode '{path}' with known encodings.")


def _is_valid(df: pd.DataFrame) -> bool:
    return not df.empty and len(df.columns) > 0


def _validate(df: pd.DataFrame, path: Path) -> None:
    if df.empty:
        raise ValueError(f"'{path}' loaded as empty — no rows found.")
    if len(df.columns) == 0:
        raise ValueError(f"'{path}' has no columns.")
