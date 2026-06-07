"""JSON / JSONL file loader."""

from pathlib import Path

import pandas as pd


def load_json(path: Path) -> pd.DataFrame:
    """Load a JSON or JSONL file into a DataFrame."""
    try:
        df = pd.read_json(path, lines=path.suffix.lower() == ".jsonl")
    except Exception as exc:
        raise RuntimeError(f"Failed to read JSON '{path}': {exc}") from exc
    if df.empty:
        raise ValueError(f"JSON '{path}' is empty.")
    return df
