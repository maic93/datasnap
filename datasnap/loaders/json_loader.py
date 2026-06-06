"""JSON / JSONL file loader."""

from pathlib import Path

import pandas as pd


def load_json(path: Path) -> pd.DataFrame:
    """Load a JSON or JSONL file into a DataFrame."""
    try:
        if path.suffix.lower() == ".jsonl":
            df = pd.read_json(path, lines=True)
        else:
            df = pd.read_json(path)
    except Exception as exc:
        raise RuntimeError(f"Failed to read JSON '{path}': {exc}") from exc

    if df.empty:
        raise ValueError(f"JSON file '{path}' is empty.")

    return df
